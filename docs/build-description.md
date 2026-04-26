# Freight Pilot — Inbound Carrier Sales (v1)

Prepared for Acme Logistics by the Freight Pilot team.

---

## TL;DR

Freight Pilot automates inbound carrier calls end-to-end: carrier vetting, load
matching, negotiation, and structured call logging. The same data powers an
operator dashboard focused on business decisions, including revenue, conversion,
margin, and lane performance.

The product is designed to answer:
**"What should we do next?"** rather than just **"What happened?"**.

---

## Primary users

- **Inbound sales desk**
  - captures after-hours and overflow call volume
  - receives booking-ready transfers with full context
- **Sales/operations lead**
  - monitors conversion, margin, and recoverable pipeline
  - acts on recommendation-driven lane and pricing insights

---

## Current scope (v1)

### 1) Carrier vetting
- captures MC number
- verifies authority via FMCSA QCMobile
- rejects ineligible carriers and logs the reason

### 2) Load matching
- captures current location and equipment type
- searches available loads and pitches best candidates
- retries once with broadened criteria when needed

### 3. Negotiate (up to 3 rounds)

Pricing is **deterministic and policy-driven (server-side)**:

- **Floor:** 92% of loadboard rate (configurable)
- **Ceiling:** 115% of loadboard rate (configurable)
- **Sweet spot:** within ±3% → instant accept

**Behavior:**
- Above sweet spot → meet-in-the-middle
- Above ceiling → counter at ceiling → reject final
- Below floor → push up toward loadboard rate
- Final round → forced resolution (accept or reject)

All negotiation rounds are logged with reasoning for auditability.


Each negotiation round is logged with reasoning and commercial values.

### 4) Close and handoff
- on agreement: confirms load/rate and executes mocked transfer message
- on no agreement: exits politely and logs outcome

### 5) Extraction and classification
Per-call logging includes:
- outcome classification
- sentiment classification
- extracted call context
- negotiation history and final commercial state

---

## Dashboard: decision layer

The dashboard is intended for daily operating decisions, not passive reporting.

### Headline metrics
- booked revenue
- conversion rate
- average margin vs loadboard
- lost pipeline value

### Action-oriented views
- recommendation feed ("what to do next")
- funnel stage drop-off
- outcome and sentiment distribution
- top lanes by volume, conversion, and margin
- recent call and negotiation drill-down

All views are sourced from live agent-generated data.

---

## Integration architecture

- HappyRobot tools call:
  - `/carriers/verify`
  - `/loads/search`
  - `/negotiate`
  - `/calls`
- API endpoints are HTTPS and API-key protected.
- One shared datastore: agent writes, dashboard reads.
- No ETL or delayed data reconciliation required.

---

## Deliberate v1 boundaries

- **Live transfer**: mocked due to web-call limitations.
- **ML pricing policy**: deferred; deterministic rules used for control and explainability.
- **Multi-region High availability**: single-region pilot architecture.
- **CRM write-back**: structured payloads are ready; connector deferred to v1.1.

---

## Inputs required from Acme

1. FMCSA API key
2. sales rep transfer endpoint/ring group
3. pricing policy approval (floor/ceiling)
4. calibration session for call handling preferences

---

## Pilot success criteria

- **North star**: after-hours booked revenue per week
- **Guardrails**:
  - margin within agreed operating band
  - negative/frustrated sentiment below threshold
  - zero bookings for ineligible carriers

---

## Why this is credible

- captures every inbound opportunity
- enforces consistent negotiation behavior
- produces immediate, operator-usable insight
- connects automation directly to measurable business outcomes