import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import select

from app.db.models import Load
from app.db.session import SessionLocal

log = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent / "loads.json"


def _parse_dt(s: str) -> datetime:
    # tolerate "Z" suffix
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _today_utc_midnight() -> datetime:
    # DB stores naive datetimes; keep comparisons and writes in UTC-naive form.
    return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)


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
    """Upsert starter loads and refresh dates to keep them current."""
    if not SEED_FILE.exists():
        log.warning("No seed file at %s, skipping.", SEED_FILE)
        return

    with SessionLocal() as db:
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
                        status="available",
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
                # Reset demo loads to available on each boot/deploy.
                existing.status = "available"
            upserted += 1

        db.commit()
        log.info("Seeded/refreshed %d loads with rolling dates.", upserted)
