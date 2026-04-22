from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import NegotiateRequest, NegotiateResponse
from app.core.security import require_api_key
from app.db.models import Load, NegotiationEvent
from app.db.session import get_db
from app.services.negotiation import evaluate_offer

router = APIRouter(prefix="/negotiate", tags=["negotiate"])


@router.post("", response_model=NegotiateResponse, dependencies=[Depends(require_api_key)])
def negotiate(payload: NegotiateRequest, db: Session = Depends(get_db)):
    load = db.get(Load, payload.load_id)
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")

    result = evaluate_offer(
        loadboard_rate=load.loadboard_rate,
        carrier_offer=payload.carrier_offer,
        round_number=payload.round_number,
    )

    db.add(
        NegotiationEvent(
            call_external_id=payload.call_id,
            load_id=payload.load_id,
            mc_number=payload.mc_number,
            round_number=result.round_number,
            loadboard_rate=load.loadboard_rate,
            carrier_offer=payload.carrier_offer,
            broker_response=result.decision,
            broker_counter=result.counter_offer,
            reasoning=result.reasoning,
        )
    )
    db.commit()

    return NegotiateResponse(
        decision=result.decision,
        counter_offer=result.counter_offer,
        final_rate=result.final_rate,
        reasoning=result.reasoning,
        round_number=result.round_number,
        max_rounds=result.max_rounds,
        loadboard_rate=result.loadboard_rate,
        max_authorized=result.max_authorized,
        floor=result.floor,
    )
