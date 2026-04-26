import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import delete, select

from app.db.models import Call, Load, NegotiationEvent
from app.db.session import SessionLocal

log = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent / "loads.json"
DEMO_SEED_PREFIX = "seed-call-"
DEMO_BOOKED_LOAD_IDS = {"LD-1001", "LD-1002", "LD-1008"}


def _parse_dt(s: str) -> datetime:
    # tolerate "Z" suffix
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _today_utc_midnight() -> datetime:
    # DB stores naive datetimes; keep comparisons and writes in UTC-naive form.
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)


def _demo_calls(anchor: datetime) -> list[dict]:
    return [
        {
            "external_call_id": f"{DEMO_SEED_PREFIX}1001",
            "mc_number": "1032145",
            "carrier_name": "Redline Transport",
            "load_id": "LD-1001",
            "outcome": "booked",
            "sentiment": "positive",
            "loadboard_rate": 2150.0,
            "initial_offer": 2350.0,
            "final_rate": 2100.0,
            "rounds": 2,
            "summary": "Carrier asked above board, accepted second-round counter and confirmed pickup.",
            "started_at": anchor + timedelta(days=-2, hours=8),
            "ended_at": anchor + timedelta(days=-2, hours=8, minutes=14),
            "created_at": anchor + timedelta(days=-2, hours=8, minutes=14),
        },
        {
            "external_call_id": f"{DEMO_SEED_PREFIX}1002",
            "mc_number": "8852041",
            "carrier_name": "Sunline Reefer",
            "load_id": "LD-1002",
            "outcome": "booked",
            "sentiment": "neutral",
            "loadboard_rate": 1450.0,
            "initial_offer": 1550.0,
            "final_rate": 1425.0,
            "rounds": 2,
            "summary": "Driver wanted fuel cushion, settled slightly below board after quick counter.",
            "started_at": anchor + timedelta(days=-1, hours=6),
            "ended_at": anchor + timedelta(days=-1, hours=6, minutes=11),
            "created_at": anchor + timedelta(days=-1, hours=6, minutes=11),
        },
        {
            "external_call_id": f"{DEMO_SEED_PREFIX}1008",
            "mc_number": "6629104",
            "carrier_name": "Midwest Freight Co",
            "load_id": "LD-1008",
            "outcome": "booked",
            "sentiment": "positive",
            "loadboard_rate": 2100.0,
            "initial_offer": 2250.0,
            "final_rate": 2050.0,
            "rounds": 3,
            "summary": "Long-haul lane closed on final round; carrier committed to same-day pickup.",
            "started_at": anchor + timedelta(hours=7),
            "ended_at": anchor + timedelta(hours=7, minutes=19),
            "created_at": anchor + timedelta(hours=7, minutes=19),
        },
        {
            "external_call_id": f"{DEMO_SEED_PREFIX}1004",
            "mc_number": "7811220",
            "carrier_name": "South Gulf Logistics",
            "load_id": "LD-1004",
            "outcome": "no_agreement",
            "sentiment": "negative",
            "loadboard_rate": 2850.0,
            "initial_offer": 3200.0,
            "final_rate": None,
            "rounds": 3,
            "summary": "Carrier held above ceiling after three rounds; call ended without agreement.",
            "started_at": anchor + timedelta(days=-3, hours=9),
            "ended_at": anchor + timedelta(days=-3, hours=9, minutes=17),
            "created_at": anchor + timedelta(days=-3, hours=9, minutes=17),
        },
        {
            "external_call_id": f"{DEMO_SEED_PREFIX}1010",
            "mc_number": "5591870",
            "carrier_name": "Northwest Flatbed",
            "load_id": "LD-1010",
            "outcome": "carrier_declined",
            "sentiment": "neutral",
            "loadboard_rate": 1350.0,
            "initial_offer": None,
            "final_rate": None,
            "rounds": 0,
            "summary": "Carrier declined lane due to timing mismatch before negotiations started.",
            "started_at": anchor + timedelta(days=-2, hours=12),
            "ended_at": anchor + timedelta(days=-2, hours=12, minutes=6),
            "created_at": anchor + timedelta(days=-2, hours=12, minutes=6),
        },
    ]


def _demo_negotiations(anchor: datetime) -> list[dict]:
    return [
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1001",
            "load_id": "LD-1001",
            "mc_number": "1032145",
            "round_number": 1,
            "loadboard_rate": 2150.0,
            "carrier_offer": 2350.0,
            "broker_response": "counter",
            "broker_counter": 2125.0,
            "reasoning": "Offer is above ceiling but close enough for a controlled first counter.",
            "created_at": anchor + timedelta(days=-2, hours=8, minutes=6),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1001",
            "load_id": "LD-1001",
            "mc_number": "1032145",
            "round_number": 2,
            "loadboard_rate": 2150.0,
            "carrier_offer": 2125.0,
            "broker_response": "accept",
            "broker_counter": None,
            "reasoning": "Carrier matched broker counter; deal closes inside policy.",
            "created_at": anchor + timedelta(days=-2, hours=8, minutes=11),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1002",
            "load_id": "LD-1002",
            "mc_number": "8852041",
            "round_number": 1,
            "loadboard_rate": 1450.0,
            "carrier_offer": 1550.0,
            "broker_response": "counter",
            "broker_counter": 1425.0,
            "reasoning": "Lane is short-haul; counter set near board with room to close quickly.",
            "created_at": anchor + timedelta(days=-1, hours=6, minutes=4),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1002",
            "load_id": "LD-1002",
            "mc_number": "8852041",
            "round_number": 2,
            "loadboard_rate": 1450.0,
            "carrier_offer": 1450.0,
            "broker_response": "accept",
            "broker_counter": None,
            "reasoning": "Carrier walked down to policy target; accepted.",
            "created_at": anchor + timedelta(days=-1, hours=6, minutes=9),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1008",
            "load_id": "LD-1008",
            "mc_number": "6629104",
            "round_number": 1,
            "loadboard_rate": 2100.0,
            "carrier_offer": 2250.0,
            "broker_response": "counter",
            "broker_counter": 2080.0,
            "reasoning": "Long lane supports a small concession; hold near board.",
            "created_at": anchor + timedelta(hours=7, minutes=5),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1008",
            "load_id": "LD-1008",
            "mc_number": "6629104",
            "round_number": 2,
            "loadboard_rate": 2100.0,
            "carrier_offer": 2140.0,
            "broker_response": "counter",
            "broker_counter": 2050.0,
            "reasoning": "Second counter keeps margin discipline while staying competitive.",
            "created_at": anchor + timedelta(hours=7, minutes=11),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1008",
            "load_id": "LD-1008",
            "mc_number": "6629104",
            "round_number": 3,
            "loadboard_rate": 2100.0,
            "carrier_offer": 2075.0,
            "broker_response": "accept",
            "broker_counter": None,
            "reasoning": "Final offer is inside policy and closes the load.",
            "created_at": anchor + timedelta(hours=7, minutes=17),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1004",
            "load_id": "LD-1004",
            "mc_number": "7811220",
            "round_number": 1,
            "loadboard_rate": 2850.0,
            "carrier_offer": 3200.0,
            "broker_response": "counter",
            "broker_counter": 2950.0,
            "reasoning": "Carrier ask is high; counter within ceiling to test movement.",
            "created_at": anchor + timedelta(days=-3, hours=9, minutes=5),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1004",
            "load_id": "LD-1004",
            "mc_number": "7811220",
            "round_number": 2,
            "loadboard_rate": 2850.0,
            "carrier_offer": 3125.0,
            "broker_response": "counter",
            "broker_counter": 3000.0,
            "reasoning": "Carrier moved slightly; broker gives final structured counter.",
            "created_at": anchor + timedelta(days=-3, hours=9, minutes=10),
        },
        {
            "call_external_id": f"{DEMO_SEED_PREFIX}1004",
            "load_id": "LD-1004",
            "mc_number": "7811220",
            "round_number": 3,
            "loadboard_rate": 2850.0,
            "carrier_offer": 3080.0,
            "broker_response": "reject",
            "broker_counter": None,
            "reasoning": "Third-round ask is still above policy; reject and close out.",
            "created_at": anchor + timedelta(days=-3, hours=9, minutes=15),
        },
    ]


def _roll_seed_dates(rows: list[dict]) -> list[dict]:
    """Shift seed pickup/delivery dates so loads always start from today."""
    if not rows:
        return rows

    template_pickups = [_parse_dt(r["pickup_datetime"]).replace(tzinfo=None) for r in rows]
    template_start = min(template_pickups)
    delta_days = (_today_utc_midnight().date() - template_start.date()).days

    rolled: list[dict] = []
    for r in rows:
        pickup = _parse_dt(r["pickup_datetime"]).replace(tzinfo=None) + timedelta(days=delta_days)
        delivery = _parse_dt(r["delivery_datetime"]).replace(tzinfo=None) + timedelta(days=delta_days)
        copy = dict(r)
        copy["pickup_datetime"] = pickup
        copy["delivery_datetime"] = delivery
        rolled.append(copy)
    return rolled


def seed_if_empty() -> None:
    """Upsert starter data with rolling dates and deterministic demo outcomes."""
    if not SEED_FILE.exists():
        log.warning("No seed file at %s, skipping.", SEED_FILE)
        return

    with SessionLocal() as db:
        anchor = _today_utc_midnight()
        rows = _roll_seed_dates(json.loads(SEED_FILE.read_text()))
        load_ids = [r["load_id"] for r in rows]
        existing_by_id = {
            l.load_id: l for l in db.execute(select(Load).where(Load.load_id.in_(load_ids))).scalars().all()
        }

        upserted = 0
        for r in rows:
            existing = existing_by_id.get(r["load_id"])
            if existing is None:
                db.add(
                    Load(
                        load_id=r["load_id"],
                        origin=r["origin"],
                        destination=r["destination"],
                        pickup_datetime=r["pickup_datetime"],
                        delivery_datetime=r["delivery_datetime"],
                        equipment_type=r["equipment_type"],
                        loadboard_rate=float(r["loadboard_rate"]),
                        notes=r.get("notes"),
                        weight=r.get("weight"),
                        commodity_type=r.get("commodity_type"),
                        num_of_pieces=r.get("num_of_pieces"),
                        miles=r.get("miles"),
                        dimensions=r.get("dimensions"),
                        status="booked" if r["load_id"] in DEMO_BOOKED_LOAD_IDS else "available",
                    )
                )
            else:
                existing.origin = r["origin"]
                existing.destination = r["destination"]
                existing.pickup_datetime = r["pickup_datetime"]
                existing.delivery_datetime = r["delivery_datetime"]
                existing.equipment_type = r["equipment_type"]
                existing.loadboard_rate = float(r["loadboard_rate"])
                existing.notes = r.get("notes")
                existing.weight = r.get("weight")
                existing.commodity_type = r.get("commodity_type")
                existing.num_of_pieces = r.get("num_of_pieces")
                existing.miles = r.get("miles")
                existing.dimensions = r.get("dimensions")
                # Keep demo deterministic on every boot/deploy.
                existing.status = "booked" if r["load_id"] in DEMO_BOOKED_LOAD_IDS else "available"
            upserted += 1

        # Rebuild demo calls/events idempotently so metrics stay coherent each deploy.
        db.execute(
            delete(NegotiationEvent).where(NegotiationEvent.call_external_id.like(f"{DEMO_SEED_PREFIX}%"))
        )
        db.execute(delete(Call).where(Call.external_call_id.like(f"{DEMO_SEED_PREFIX}%")))

        demo_calls = _demo_calls(anchor)
        for c in demo_calls:
            db.add(
                Call(
                    external_call_id=c["external_call_id"],
                    mc_number=c["mc_number"],
                    carrier_name=c["carrier_name"],
                    load_id=c["load_id"],
                    outcome=c["outcome"],
                    sentiment=c["sentiment"],
                    loadboard_rate=c["loadboard_rate"],
                    initial_offer=c["initial_offer"],
                    final_rate=c["final_rate"],
                    rounds=c["rounds"],
                    summary=c["summary"],
                    started_at=c["started_at"],
                    ended_at=c["ended_at"],
                    created_at=c["created_at"],
                )
            )

        demo_negotiations = _demo_negotiations(anchor)
        for n in demo_negotiations:
            db.add(
                NegotiationEvent(
                    call_external_id=n["call_external_id"],
                    load_id=n["load_id"],
                    mc_number=n["mc_number"],
                    round_number=n["round_number"],
                    loadboard_rate=n["loadboard_rate"],
                    carrier_offer=n["carrier_offer"],
                    broker_response=n["broker_response"],
                    broker_counter=n["broker_counter"],
                    reasoning=n["reasoning"],
                    created_at=n["created_at"],
                )
            )

        db.commit()
        log.info(
            "Seeded/refreshed %d loads, %d demo calls, %d demo negotiation events.",
            upserted,
            len(demo_calls),
            len(demo_negotiations),
        )
