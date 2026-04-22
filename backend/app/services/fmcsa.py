"""Thin client around the FMCSA QCMobile API.

Docs: https://mobile.fmcsa.dot.gov/QCDevsite/docs/getCarriersByMC
Endpoint used: GET /carriers/docket-number/{docket}?webKey=...

The FMCSA API is flaky and slow. We cache results in the `carriers` table and
apply a clear eligibility rule the agent can rely on.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Temporary test allowlist for end-to-end HappyRobot demos.
# Remove before production handoff.
TEST_ELIGIBLE_MCS = {"12345", "3456"}


@dataclass
class CarrierLookupResult:
    mc_number: str
    eligible: bool
    reason: str
    legal_name: str | None = None
    dba_name: str | None = None
    dot_number: str | None = None
    status: str | None = None
    allowed_to_operate: bool | None = None
    raw: dict[str, Any] | None = None


def _normalize_mc(mc: str) -> str:
    """Carriers often say 'MC 123456' or 'MC-123456'. Keep digits only."""
    return "".join(c for c in mc if c.isdigit())


async def lookup_mc(mc_number: str) -> CarrierLookupResult:
    settings = get_settings()
    digits = _normalize_mc(mc_number)

    if not digits:
        return CarrierLookupResult(
            mc_number=mc_number,
            eligible=False,
            reason="Invalid MC number format.",
        )

    if digits in TEST_ELIGIBLE_MCS:
        return CarrierLookupResult(
            mc_number=digits,
            eligible=True,
            reason="Carrier is authorized to operate.",
            legal_name=f"Test Carrier MC {digits}",
            dba_name=f"Test Carrier {digits}",
            dot_number=f"TST{digits}",
            status="A",
            allowed_to_operate=True,
            raw={"source": "test-allowlist"},
        )

    if not settings.fmcsa_api_key:
        # Don't silently "approve" carriers. Fail closed so the agent asks
        # the carrier to try again or escalates to a rep.
        return CarrierLookupResult(
            mc_number=digits,
            eligible=False,
            reason="FMCSA lookup not configured on the server.",
        )

    url = f"{settings.fmcsa_base_url}/carriers/docket-number/{digits}"
    params = {"webKey": settings.fmcsa_api_key}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
    except httpx.HTTPError as exc:
        logger.warning("FMCSA request failed for MC %s: %s", digits, exc)
        return CarrierLookupResult(
            mc_number=digits,
            eligible=False,
            reason="FMCSA service is currently unreachable.",
        )

    if resp.status_code != 200:
        return CarrierLookupResult(
            mc_number=digits,
            eligible=False,
            reason=f"FMCSA returned {resp.status_code}.",
            raw={"status_code": resp.status_code, "body": resp.text[:500]},
        )

    payload = resp.json()
    content = payload.get("content") or []
    if not content:
        return CarrierLookupResult(
            mc_number=digits,
            eligible=False,
            reason="No carrier found with this MC number.",
            raw=payload,
        )

    first = content[0] if isinstance(content, list) else content
    carrier = first.get("carrier") if isinstance(first, dict) else None
    if not carrier:
        return CarrierLookupResult(
            mc_number=digits,
            eligible=False,
            reason="Unexpected response from FMCSA.",
            raw=payload,
        )

    allowed_raw = carrier.get("allowedToOperate")
    allowed = None
    if isinstance(allowed_raw, str):
        allowed = allowed_raw.strip().upper() == "Y"
    elif isinstance(allowed_raw, bool):
        allowed = allowed_raw

    status_code = carrier.get("statusCode") or carrier.get("status")
    legal_name = carrier.get("legalName")
    dba_name = carrier.get("dbaName")
    dot_number = str(carrier.get("dotNumber")) if carrier.get("dotNumber") else None

    eligible = bool(allowed) and (status_code in (None, "A"))
    if eligible:
        reason = "Carrier is authorized to operate."
    elif allowed is False:
        reason = "Carrier is not authorized to operate per FMCSA."
    elif status_code and status_code != "A":
        reason = f"Carrier status is '{status_code}' per FMCSA."
    else:
        reason = "Carrier eligibility could not be confirmed."

    return CarrierLookupResult(
        mc_number=digits,
        eligible=eligible,
        reason=reason,
        legal_name=legal_name,
        dba_name=dba_name,
        dot_number=dot_number,
        status=status_code,
        allowed_to_operate=allowed,
        raw=payload,
    )
