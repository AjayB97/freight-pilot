from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Load(Base):
    __tablename__ = "loads"

    load_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    origin: Mapped[str] = mapped_column(String(128), index=True)
    destination: Mapped[str] = mapped_column(String(128), index=True)
    pickup_datetime: Mapped[datetime] = mapped_column(DateTime)
    delivery_datetime: Mapped[datetime] = mapped_column(DateTime)
    equipment_type: Mapped[str] = mapped_column(String(64), index=True)
    loadboard_rate: Mapped[float] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    commodity_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    num_of_pieces: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    miles: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dimensions: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="available", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Carrier(Base):
    """Cache of FMCSA lookups so repeat calls don't hammer the API and we can
    enrich the dashboard even when the FMCSA service is flaky."""

    __tablename__ = "carriers"

    mc_number: Mapped[str] = mapped_column(String(32), primary_key=True)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dba_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dot_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    allowed_to_operate: Mapped[Optional[bool]] = mapped_column(default=None, nullable=True)
    raw: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Call(Base):
    """One row per carrier call. Written by the HappyRobot agent at the
    end of a call via POST /calls."""

    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_call_id: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    mc_number: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)
    carrier_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    load_id: Mapped[Optional[str]] = mapped_column(ForeignKey("loads.load_id"), nullable=True, index=True)

    # Outcome classification (see docs for allowed values)
    outcome: Mapped[str] = mapped_column(String(64), index=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)

    # Commercials
    loadboard_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    initial_offer: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rounds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Free-form summary / transcript highlights from the agent
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Anything extra the agent extracted (equipment asked for, pickup pref, etc.)
    extracted: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=_utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    load: Mapped[Optional[Load]] = relationship(lazy="joined")


class NegotiationEvent(Base):
    """Every round of a negotiation — useful for training/QA and analytics."""

    __tablename__ = "negotiation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    call_external_id: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    load_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    mc_number: Mapped[Optional[str]] = mapped_column(String(32), index=True, nullable=True)
    round_number: Mapped[int] = mapped_column(Integer)
    loadboard_rate: Mapped[float] = mapped_column(Float)
    carrier_offer: Mapped[float] = mapped_column(Float)
    broker_response: Mapped[str] = mapped_column(String(16))  # accept | counter | reject
    broker_counter: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
