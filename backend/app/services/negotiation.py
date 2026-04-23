"""Rule-based negotiation engine.

We keep this deterministic so the agent is consistent across calls and the
business can explain every decision to an auditor. The agent calls us once per
round with the load_id, the carrier's offer, and which round we're on.

Policy (defaults, configurable via env):
  * loadboard_rate  = listed rate.
  * max_authorized  = loadboard_rate * (1 + negotiation_max_markup_pct)   [e.g. +15%]
  * floor           = loadboard_rate * negotiation_min_floor_pct          [e.g. 92%]
  * max_rounds      = 3

Optional **broker_last_counter** (passed from the agent after each `counter`):
  When the carrier lowers their ask across rounds, the naive midpoint
  (loadboard + carrier_offer) / 2 **moves down** with them — which sounds
  like the broker is backing off their own last number. If `broker_last_counter`
  is set, any new `counter_offer` is floored at that value so the broker's
  position is **weakly monotone** (never lower than what we already said).

Decision rules per round:
  * If offer <= max_authorized and offer <= loadboard_rate * 1.03  -> accept.
  * If offer > max_authorized                                      -> counter
      toward max_authorized (round 1/2) or reject (round 3).
  * If offer in (loadboard_rate * 1.03, max_authorized]            -> counter
      by splitting the difference to speed convergence; accept on round 3.
  * If offer < floor                                               -> counter up
      to loadboard_rate (obvious gift); accept silently otherwise.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.core.config import get_settings

Decision = Literal["accept", "counter", "reject"]


@dataclass
class NegotiationResult:
    decision: Decision
    counter_offer: float | None
    final_rate: float | None
    reasoning: str
    round_number: int
    max_rounds: int
    loadboard_rate: float
    max_authorized: float
    floor: float


def _round_money(x: float) -> float:
    return round(x / 25) * 25  # Round to nearest $25 like real brokers do.


def _floor_broker_counter(
    computed: float,
    broker_last_counter: float | None,
) -> float:
    """Never let a new broker counter sit below what we already said aloud."""
    if broker_last_counter is None:
        return computed
    return max(computed, broker_last_counter)


def evaluate_offer(
    loadboard_rate: float,
    carrier_offer: float,
    round_number: int,
    broker_last_counter: float | None = None,
) -> NegotiationResult:
    s = get_settings()
    max_rounds = s.negotiation_max_rounds
    max_authorized = loadboard_rate * (1 + s.negotiation_max_markup_pct)
    floor = loadboard_rate * s.negotiation_min_floor_pct

    round_number = max(1, int(round_number))

    # 1. Offer at or below sweet spot: accept.
    sweet_spot = loadboard_rate * 1.03
    if carrier_offer <= sweet_spot and carrier_offer >= floor:
        return NegotiationResult(
            decision="accept",
            counter_offer=None,
            final_rate=_round_money(carrier_offer),
            reasoning=(
                f"Offer ${carrier_offer:,.0f} is within 3% of loadboard "
                f"${loadboard_rate:,.0f}. Accepting."
            ),
            round_number=round_number,
            max_rounds=max_rounds,
            loadboard_rate=loadboard_rate,
            max_authorized=max_authorized,
            floor=floor,
        )

    # 2. Way below our floor — the carrier is underbidding. Counter UP to
    #    the loadboard rate (we don't leave money on the table but we also
    #    don't need to haggle hard).
    if carrier_offer < floor:
        counter = _floor_broker_counter(_round_money(loadboard_rate), broker_last_counter)
        if round_number >= max_rounds:
            return NegotiationResult(
                decision="accept",
                counter_offer=None,
                final_rate=_round_money(carrier_offer),
                reasoning=(
                    f"Final round. Offer ${carrier_offer:,.0f} is below our floor "
                    f"${floor:,.0f} but still profitable — accepting rather than losing the load."
                ),
                round_number=round_number,
                max_rounds=max_rounds,
                loadboard_rate=loadboard_rate,
                max_authorized=max_authorized,
                floor=floor,
            )
        return NegotiationResult(
            decision="counter",
            counter_offer=counter,
            final_rate=None,
            reasoning=(
                f"Offer ${carrier_offer:,.0f} is below floor ${floor:,.0f}. "
                f"Countering at loadboard rate ${counter:,.0f}."
            ),
            round_number=round_number,
            max_rounds=max_rounds,
            loadboard_rate=loadboard_rate,
            max_authorized=max_authorized,
            floor=floor,
        )

    # 3. Above sweet spot but within max authorized: meet in the middle, or
    #    accept on the final round.
    if sweet_spot < carrier_offer <= max_authorized:
        if round_number >= max_rounds:
            return NegotiationResult(
                decision="accept",
                counter_offer=None,
                final_rate=_round_money(carrier_offer),
                reasoning=(
                    f"Final round. Offer ${carrier_offer:,.0f} is within authorized ceiling "
                    f"${max_authorized:,.0f}. Accepting to close."
                ),
                round_number=round_number,
                max_rounds=max_rounds,
                loadboard_rate=loadboard_rate,
                max_authorized=max_authorized,
                floor=floor,
            )
        # Meet in the middle, biased toward loadboard — but never walk our own
        # counter *down* if the carrier simply lowered their ask vs last round.
        counter = _floor_broker_counter(
            _round_money((loadboard_rate + carrier_offer) / 2),
            broker_last_counter,
        )
        return NegotiationResult(
            decision="counter",
            counter_offer=counter,
            final_rate=None,
            reasoning=(
                f"Offer ${carrier_offer:,.0f} is above loadboard ${loadboard_rate:,.0f} "
                f"but within ceiling ${max_authorized:,.0f}. Splitting the difference at ${counter:,.0f}."
            ),
            round_number=round_number,
            max_rounds=max_rounds,
            loadboard_rate=loadboard_rate,
            max_authorized=max_authorized,
            floor=floor,
        )

    # 4. Above max authorized.
    if round_number >= max_rounds:
        return NegotiationResult(
            decision="reject",
            counter_offer=None,
            final_rate=None,
            reasoning=(
                f"Offer ${carrier_offer:,.0f} exceeds our authorized ceiling "
                f"${max_authorized:,.0f} and we're out of rounds. Politely decline."
            ),
            round_number=round_number,
            max_rounds=max_rounds,
            loadboard_rate=loadboard_rate,
            max_authorized=max_authorized,
            floor=floor,
        )

    counter = _floor_broker_counter(_round_money(max_authorized), broker_last_counter)
    return NegotiationResult(
        decision="counter",
        counter_offer=counter,
        final_rate=None,
        reasoning=(
            f"Offer ${carrier_offer:,.0f} exceeds our ceiling ${max_authorized:,.0f}. "
            f"Countering at max authorized ${counter:,.0f}."
        ),
        round_number=round_number,
        max_rounds=max_rounds,
        loadboard_rate=loadboard_rate,
        max_authorized=max_authorized,
        floor=floor,
    )
