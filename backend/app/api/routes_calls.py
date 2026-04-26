from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.schemas import CallCreate, CallOut
from app.core.security import require_api_key
from app.db.models import Call, Load
from app.db.session import get_db

router = APIRouter(prefix="/calls", tags=["calls"])


ALLOWED_OUTCOMES = {
    "booked",
    "no_agreement",
    "not_eligible",
    "no_matching_load",
    "carrier_declined",
    "escalated",
    "abandoned",
}

ALLOWED_SENTIMENTS = {"positive", "neutral", "negative", "frustrated"}


@router.post("", response_model=CallOut, dependencies=[Depends(require_api_key)])
def create_call(payload: CallCreate, db: Session = Depends(get_db)):
    # Normalize outcome/sentiment to a canonical set so dashboards aren't messy.
    outcome = (payload.outcome or "abandoned").strip().lower()
    if outcome not in ALLOWED_OUTCOMES:
        outcome = "abandoned"

    sentiment = (payload.sentiment or "").strip().lower() or None
    if sentiment and sentiment not in ALLOWED_SENTIMENTS:
        sentiment = "neutral"

    load = db.get(Load, payload.load_id) if payload.load_id else None

    # If booked without an explicit final_rate, treat posted/loadboard rate as final.
    final_rate = payload.final_rate
    if outcome == "booked" and final_rate is None:
        if payload.loadboard_rate is not None:
            final_rate = payload.loadboard_rate
        elif load is not None:
            final_rate = load.loadboard_rate

    # If load_id is provided and matches, mark it booked when the call is booked.
    if load and outcome == "booked" and load.status == "available":
        load.status = "booked"

    call = Call(
        external_call_id=payload.external_call_id,
        mc_number=payload.mc_number,
        carrier_name=payload.carrier_name,
        load_id=payload.load_id,
        outcome=outcome,
        sentiment=sentiment,
        loadboard_rate=payload.loadboard_rate,
        initial_offer=payload.initial_offer,
        final_rate=final_rate,
        rounds=payload.rounds,
        summary=payload.summary,
        transcript_url=payload.transcript_url,
        extracted=payload.extracted,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


@router.get("", response_model=list[CallOut], dependencies=[Depends(require_api_key)])
def list_calls(
    limit: int = Query(100, ge=1, le=500),
    outcome: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    mc_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    stmt = select(Call)
    if outcome:
        stmt = stmt.where(Call.outcome == outcome)
    if sentiment:
        stmt = stmt.where(Call.sentiment == sentiment)
    if mc_number:
        stmt = stmt.where(Call.mc_number == mc_number)
    stmt = stmt.order_by(desc(Call.created_at)).limit(limit)
    return db.execute(stmt).scalars().all()


@router.get("/{call_id}", response_model=CallOut, dependencies=[Depends(require_api_key)])
def get_call(call_id: int, db: Session = Depends(get_db)):
    call = db.get(Call, call_id)
    if not call:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Call not found")
    return call
