"""Business-outcome metrics for the dashboard.

We deliberately compute derived values server-side (conversion, margin,
recommendations) instead of shipping raw rows — the frontend stays thin and
the same numbers can be re-used by a weekly email digest or a Slack bot.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import (
    FunnelPoint,
    LanePerformance,
    MetricsSummary,
    OutcomeBreakdown,
    SentimentBreakdown,
)
from app.core.security import require_api_key
from app.db.models import Call, Load, NegotiationEvent
from app.db.session import get_db

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _since(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


@router.get("/summary", response_model=MetricsSummary, dependencies=[Depends(require_api_key)])
def summary(
    window_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    since = _since(window_days)
    calls = db.execute(select(Call).where(Call.created_at >= since)).scalars().all()

    total = len(calls)
    booked = [c for c in calls if c.outcome == "booked"]
    booked_count = len(booked)
    conversion = (booked_count / total) if total else 0.0

    booked_revenue = sum((c.final_rate or 0) for c in booked)
    booked_final_rates = [c.final_rate for c in booked if c.final_rate is not None]
    booked_loadboard_rates = [c.loadboard_rate for c in booked if c.loadboard_rate is not None]
    avg_final = (
        sum(booked_final_rates) / len(booked_final_rates)
        if booked_final_rates
        else None
    )
    avg_loadboard = (
        sum(booked_loadboard_rates) / len(booked_loadboard_rates)
        if booked_loadboard_rates
        else None
    )
    avg_margin_pct = None
    if booked:
        margins = []
        for c in booked:
            if c.final_rate and c.loadboard_rate:
                margins.append((c.final_rate - c.loadboard_rate) / c.loadboard_rate)
        if margins:
            avg_margin_pct = sum(margins) / len(margins)

    booked_rounds = [c.rounds for c in booked if c.rounds is not None]
    avg_rounds_to_book = (sum(booked_rounds) / len(booked_rounds)) if booked_rounds else None

    lost_pipeline_value = sum(
        (c.loadboard_rate or 0)
        for c in calls
        if c.outcome in {"no_agreement", "carrier_declined", "abandoned"}
    )

    neg_sentiments = sum(1 for c in calls if c.sentiment in {"negative", "frustrated"})
    neg_sentiment_rate = (neg_sentiments / total) if total else 0.0

    # --- Funnel: calls -> eligible -> pitched -> negotiating -> booked
    eligible = sum(1 for c in calls if c.outcome != "not_eligible")
    pitched = sum(1 for c in calls if c.load_id is not None)
    negotiated = sum(1 for c in calls if (c.rounds or 0) >= 1)
    funnel = [
        FunnelPoint(stage="Calls received", count=total),
        FunnelPoint(stage="Carrier eligible", count=eligible),
        FunnelPoint(stage="Matched to a load", count=pitched),
        FunnelPoint(stage="Negotiated", count=negotiated),
        FunnelPoint(stage="Booked", count=booked_count),
    ]

    # --- Outcomes & sentiment ---
    outcomes_map: dict[str, OutcomeBreakdown] = {}
    for c in calls:
        b = outcomes_map.setdefault(
            c.outcome, OutcomeBreakdown(outcome=c.outcome, count=0, revenue=0.0)
        )
        b.count += 1
        if c.outcome == "booked":
            b.revenue += c.final_rate or 0
    outcomes = sorted(outcomes_map.values(), key=lambda x: -x.count)

    sentiment_map: dict[str, SentimentBreakdown] = {}
    for c in calls:
        key = c.sentiment or "unknown"
        sb = sentiment_map.setdefault(key, SentimentBreakdown(sentiment=key, count=0))
        sb.count += 1
    sentiment = sorted(sentiment_map.values(), key=lambda x: -x.count)

    # --- Lane performance (top 5 by call volume) ---
    lanes: dict[tuple[str, str, str], dict] = {}
    for c in calls:
        if not c.load:
            continue
        key = (c.load.origin, c.load.destination, c.load.equipment_type)
        l = lanes.setdefault(
            key,
            {
                "calls": 0,
                "booked": 0,
                "final_rates": [],
                "loadboard_rates": [],
            },
        )
        l["calls"] += 1
        if c.outcome == "booked":
            l["booked"] += 1
            if c.final_rate:
                l["final_rates"].append(c.final_rate)
            if c.loadboard_rate:
                l["loadboard_rates"].append(c.loadboard_rate)

    top_lanes: list[LanePerformance] = []
    for (origin, destination, equip), v in sorted(
        lanes.items(), key=lambda kv: -kv[1]["calls"]
    )[:5]:
        avg_f = sum(v["final_rates"]) / len(v["final_rates"]) if v["final_rates"] else None
        avg_l = (
            sum(v["loadboard_rates"]) / len(v["loadboard_rates"])
            if v["loadboard_rates"]
            else None
        )
        margin = None
        if avg_f and avg_l:
            margin = (avg_f - avg_l) / avg_l
        top_lanes.append(
            LanePerformance(
                origin=origin,
                destination=destination,
                equipment_type=equip,
                calls=v["calls"],
                booked=v["booked"],
                conversion=(v["booked"] / v["calls"]) if v["calls"] else 0.0,
                avg_final_rate=avg_f,
                avg_loadboard_rate=avg_l,
                avg_margin_pct=margin,
            )
        )

    # --- Stale loads (available, never pitched in the window) ---
    stale_cutoff = since
    pitched_ids = {c.load_id for c in calls if c.load_id}
    stale_loads = db.execute(
        select(func.count(Load.load_id)).where(
            Load.status == "available",
            Load.created_at < stale_cutoff,
            ~Load.load_id.in_(pitched_ids) if pitched_ids else True,
        )
    ).scalar_one()

    # --- Recommendations: turn metrics into decisions ---
    recs: list[str] = []

    if total == 0:
        recs.append(
            "No carrier calls received yet. Verify the HappyRobot inbound agent is "
            "pointed at /calls and that the web-call trigger is enabled."
        )
    else:
        if conversion < 0.3:
            recs.append(
                f"Conversion is {conversion * 100:.0f}%. Review the top 'no_agreement' calls — "
                "prompting or floor/ceiling may be off."
            )
        if avg_margin_pct is not None and avg_margin_pct > 0.10:
            recs.append(
                f"Avg booked margin is +{avg_margin_pct * 100:.1f}% above loadboard. "
                "You're leaving rate on the table; consider lowering the ceiling."
            )
        if avg_margin_pct is not None and avg_margin_pct < 0.0:
            recs.append(
                f"Avg booked margin is {avg_margin_pct * 100:.1f}% — you're booking below "
                "loadboard. Raise the floor or pitch higher initial offers."
            )
        if neg_sentiment_rate > 0.2:
            recs.append(
                f"{neg_sentiment_rate * 100:.0f}% of calls are negative/frustrated. "
                "Listen to 3 recent transcripts to spot the pattern (long holds? rigid pitch?)."
            )
        if lost_pipeline_value > 0 and booked_revenue > 0 and lost_pipeline_value > booked_revenue:
            recs.append(
                f"Unbooked pipeline (${lost_pipeline_value:,.0f}) exceeds booked revenue "
                f"(${booked_revenue:,.0f}). Highest-ROI fix is recovering 'no_agreement' calls."
            )
        if stale_loads and stale_loads > 0:
            recs.append(
                f"{stale_loads} loads on the board haven't had a single pitch this window. "
                "Re-post or offer them first on the next matching call."
            )
        # Lane-level recommendation
        best_lane = max(top_lanes, key=lambda l: l.conversion, default=None)
        if best_lane and best_lane.calls >= 3 and best_lane.conversion > 0.5:
            recs.append(
                f"Lane {best_lane.origin} → {best_lane.destination} ({best_lane.equipment_type}) "
                f"converts {best_lane.conversion * 100:.0f}%. Source more of these and prioritise them in the pitch."
            )

    return MetricsSummary(
        window_days=window_days,
        total_calls=total,
        booked_calls=booked_count,
        conversion_rate=conversion,
        booked_revenue=booked_revenue,
        avg_final_rate=avg_final,
        avg_loadboard_rate=avg_loadboard,
        avg_margin_pct=avg_margin_pct,
        avg_rounds_to_book=avg_rounds_to_book,
        lost_pipeline_value=lost_pipeline_value,
        negative_sentiment_rate=neg_sentiment_rate,
        funnel=funnel,
        outcomes=outcomes,
        sentiment=sentiment,
        top_lanes=top_lanes,
        stale_loads=int(stale_loads or 0),
        recommendations=recs,
    )


@router.get("/negotiations", dependencies=[Depends(require_api_key)])
def recent_negotiations(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = (
        db.execute(
            select(NegotiationEvent).order_by(NegotiationEvent.created_at.desc()).limit(limit)
        )
        .scalars()
        .all()
    )
    return [
        {
            "id": r.id,
            "call_external_id": r.call_external_id,
            "load_id": r.load_id,
            "mc_number": r.mc_number,
            "round_number": r.round_number,
            "loadboard_rate": r.loadboard_rate,
            "carrier_offer": r.carrier_offer,
            "broker_response": r.broker_response,
            "broker_counter": r.broker_counter,
            "reasoning": r.reasoning,
            "created_at": r.created_at,
        }
        for r in rows
    ]
