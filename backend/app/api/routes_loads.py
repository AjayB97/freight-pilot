from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.schemas import LoadOut
from app.core.security import require_api_key
from app.db.models import Load
from app.db.session import get_db

router = APIRouter(prefix="/loads", tags=["loads"])


def _today_utc_midnight() -> datetime:
    # DB stores naive datetimes; keep filtering UTC-naive.
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)


def _ilike(column, needle: str):
    # Force case-insensitive matching regardless of DB defaults/collation.
    # Also normalize extra whitespace in user input.
    normalized = " ".join(needle.split()).lower()
    return func.lower(column).like(f"%{normalized}%")


def _parse_limit(raw: Optional[str], default: int, minimum: int, maximum: int) -> int:
    if raw is None:
        return default
    value = raw.strip()
    if value == "":
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(minimum, min(maximum, parsed))


def _normalize_utc_naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


@router.get("/search", response_model=list[LoadOut], dependencies=[Depends(require_api_key)])
def search_loads(
    origin: Optional[str] = Query(None, description="City, state, or substring"),
    destination: Optional[str] = Query(None),
    equipment_type: Optional[str] = Query(None, description="e.g. 'Dry Van', 'Reefer', 'Flatbed'"),
    pickup_after: Optional[datetime] = Query(None),
    pickup_before: Optional[datetime] = Query(None),
    min_rate: Optional[float] = Query(None, ge=0),
    limit: Optional[str] = Query(None, description="Optional max rows (1-20); empty falls back to default."),
    db: Session = Depends(get_db),
):
    """Carrier-style search. Designed to be called by the HappyRobot agent
    as a tool. All params are optional so the agent can progressively filter.
    Returns up to `limit` available loads, best-matching first (by pickup time).
    """
    stmt = select(Load).where(Load.status == "available")

    if origin:
        stmt = stmt.where(_ilike(Load.origin, origin))
    if destination:
        stmt = stmt.where(_ilike(Load.destination, destination))
    if equipment_type:
        stmt = stmt.where(_ilike(Load.equipment_type, equipment_type))
    today = _today_utc_midnight()
    requested_pickup_after = _normalize_utc_naive(pickup_after)
    effective_pickup_after = requested_pickup_after if requested_pickup_after and requested_pickup_after >= today else today
    stmt = stmt.where(Load.pickup_datetime >= effective_pickup_after)
    requested_pickup_before = _normalize_utc_naive(pickup_before)
    if requested_pickup_before:
        stmt = stmt.where(Load.pickup_datetime <= requested_pickup_before)
    if min_rate is not None:
        stmt = stmt.where(Load.loadboard_rate >= min_rate)

    parsed_limit = _parse_limit(limit, default=5, minimum=1, maximum=20)
    stmt = stmt.order_by(Load.pickup_datetime.asc()).limit(parsed_limit)
    rows = db.execute(stmt).scalars().all()
    return rows


@router.get("/{load_id}", response_model=LoadOut, dependencies=[Depends(require_api_key)])
def get_load(load_id: str, db: Session = Depends(get_db)):
    load = db.get(Load, load_id)
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return load


@router.get("", response_model=list[LoadOut], dependencies=[Depends(require_api_key)])
def list_loads(
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search origin/destination/equipment"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Used by the dashboard (not the agent)."""
    stmt = select(Load).where(Load.pickup_datetime >= _today_utc_midnight())
    if status:
        stmt = stmt.where(Load.status == status)
    if q:
        stmt = stmt.where(
            or_(
                _ilike(Load.origin, q),
                _ilike(Load.destination, q),
                _ilike(Load.equipment_type, q),
                _ilike(Load.load_id, q),
            )
        )
    stmt = stmt.order_by(Load.pickup_datetime.asc()).limit(limit)
    return db.execute(stmt).scalars().all()
