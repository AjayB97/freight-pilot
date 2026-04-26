from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ---------- Carriers ----------

class VerifyCarrierRequest(BaseModel):
    mc_number: str = Field(..., description="Carrier MC number. Digits or 'MC 123456' both accepted.")


class VerifyCarrierResponse(BaseModel):
    mc_number: str
    eligible: bool
    reason: str
    legal_name: Optional[str] = None
    dba_name: Optional[str] = None
    dot_number: Optional[str] = None
    status: Optional[str] = None
    allowed_to_operate: Optional[bool] = None


# ---------- Loads ----------

class LoadOut(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


# ---------- Negotiation ----------

class NegotiateRequest(BaseModel):
    load_id: str
    carrier_offer: float = Field(..., gt=0)
    round_number: int = Field(1, ge=1)
    mc_number: Optional[str] = None
    call_id: Optional[str] = Field(None, description="HappyRobot call id, for traceability")
    broker_last_counter: Optional[float] = Field(
        None,
        ge=0,
        description=(
            "If the broker already named a counter in the previous round, pass it here "
            "so the engine never suggests a *lower* broker number when the carrier walks "
            "their ask down (split midpoint would otherwise drop)."
        ),
    )


class NegotiateResponse(BaseModel):
    decision: str  # accept | counter | reject
    counter_offer: Optional[float] = None
    final_rate: Optional[float] = None
    reasoning: str
    round_number: int
    max_rounds: int
    loadboard_rate: float
    max_authorized: float
    floor: float


# ---------- Calls ----------

class CallCreate(BaseModel):
    external_call_id: Optional[str] = None
    mc_number: Optional[str] = None
    carrier_name: Optional[str] = None
    load_id: Optional[str] = None
    outcome: str = Field(
        ...,
        description=(
            "One of: booked | no_agreement | not_eligible | no_matching_load | "
            "carrier_declined | escalated | abandoned"
        ),
    )
    sentiment: Optional[str] = Field(
        None, description="One of: positive | neutral | negative | frustrated"
    )
    loadboard_rate: Optional[float] = None
    initial_offer: Optional[float] = None
    final_rate: Optional[float] = None
    rounds: Optional[int] = None
    summary: Optional[str] = None
    transcript_url: Optional[str] = None
    extracted: Optional[dict[str, Any]] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    @field_validator("loadboard_rate", "initial_offer", "final_rate", "rounds", mode="before")
    @classmethod
    def empty_numeric_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value


class CallOut(BaseModel):
    id: int
    external_call_id: Optional[str]
    mc_number: Optional[str]
    carrier_name: Optional[str]
    load_id: Optional[str]
    outcome: str
    sentiment: Optional[str]
    loadboard_rate: Optional[float]
    initial_offer: Optional[float]
    final_rate: Optional[float]
    rounds: Optional[int]
    summary: Optional[str]
    transcript_url: Optional[str]
    extracted: Optional[dict[str, Any]]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Metrics (dashboard) ----------

class FunnelPoint(BaseModel):
    stage: str
    count: int


class OutcomeBreakdown(BaseModel):
    outcome: str
    count: int
    revenue: float


class SentimentBreakdown(BaseModel):
    sentiment: str
    count: int


class LanePerformance(BaseModel):
    origin: str
    destination: str
    equipment_type: str
    calls: int
    booked: int
    conversion: float
    avg_final_rate: Optional[float]
    avg_loadboard_rate: Optional[float]
    avg_margin_pct: Optional[float]


class MetricsSummary(BaseModel):
    window_days: int
    total_calls: int
    booked_calls: int
    conversion_rate: float
    booked_revenue: float
    avg_final_rate: Optional[float]
    avg_loadboard_rate: Optional[float]
    avg_margin_pct: Optional[float]
    avg_rounds_to_book: Optional[float]
    lost_pipeline_value: float
    negative_sentiment_rate: float
    funnel: list[FunnelPoint]
    outcomes: list[OutcomeBreakdown]
    sentiment: list[SentimentBreakdown]
    top_lanes: list[LanePerformance]
    stale_loads: int  # loads that have never been pitched or not in N days
    recommendations: list[str]
