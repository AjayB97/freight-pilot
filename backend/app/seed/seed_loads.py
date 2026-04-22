import json
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from app.db.models import Load
from app.db.session import SessionLocal

log = logging.getLogger(__name__)

SEED_FILE = Path(__file__).parent / "loads.json"


def _parse_dt(s: str) -> datetime:
    # tolerate "Z" suffix
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def seed_if_empty() -> None:
    """Insert starter loads if the table is empty. Safe to call on every boot."""
    if not SEED_FILE.exists():
        log.warning("No seed file at %s, skipping.", SEED_FILE)
        return

    with SessionLocal() as db:
        existing = db.execute(select(Load).limit(1)).first()
        if existing:
            return

        rows = json.loads(SEED_FILE.read_text())
        for r in rows:
            db.add(
                Load(
                    load_id=r["load_id"],
                    origin=r["origin"],
                    destination=r["destination"],
                    pickup_datetime=_parse_dt(r["pickup_datetime"]),
                    delivery_datetime=_parse_dt(r["delivery_datetime"]),
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
        db.commit()
        log.info("Seeded %d loads.", len(rows))
