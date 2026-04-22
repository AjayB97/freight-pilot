from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import VerifyCarrierRequest, VerifyCarrierResponse
from app.core.security import require_api_key
from app.db.models import Carrier
from app.db.session import get_db
from app.services.fmcsa import lookup_mc

router = APIRouter(prefix="/carriers", tags=["carriers"])


@router.post("/verify", response_model=VerifyCarrierResponse, dependencies=[Depends(require_api_key)])
async def verify_carrier(payload: VerifyCarrierRequest, db: Session = Depends(get_db)):
    result = await lookup_mc(payload.mc_number)

    # Upsert cache entry for the dashboard.
    existing = db.get(Carrier, result.mc_number)
    now = datetime.now(timezone.utc)
    if existing is None:
        db.add(
            Carrier(
                mc_number=result.mc_number,
                legal_name=result.legal_name,
                dba_name=result.dba_name,
                dot_number=result.dot_number,
                status=result.status,
                allowed_to_operate=result.allowed_to_operate,
                raw=result.raw,
                last_checked_at=now,
            )
        )
    else:
        existing.legal_name = result.legal_name or existing.legal_name
        existing.dba_name = result.dba_name or existing.dba_name
        existing.dot_number = result.dot_number or existing.dot_number
        existing.status = result.status or existing.status
        existing.allowed_to_operate = (
            result.allowed_to_operate
            if result.allowed_to_operate is not None
            else existing.allowed_to_operate
        )
        existing.raw = result.raw or existing.raw
        existing.last_checked_at = now
    db.commit()

    return VerifyCarrierResponse(
        mc_number=result.mc_number,
        eligible=result.eligible,
        reason=result.reason,
        legal_name=result.legal_name,
        dba_name=result.dba_name,
        dot_number=result.dot_number,
        status=result.status,
        allowed_to_operate=result.allowed_to_operate,
    )
