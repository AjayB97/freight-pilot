
---

```markdown
# Freight Pilot — Inbound Carrier Sales, v1

*Prepared for Acme Logistics by the Freight Pilot team*

---

## TL;DR

Carriers call Acme's inbound line 24/7. Many of these calls occur after
hours or during peak overlap, when the sales desk is saturated. Freight
Pilot answers every call, verifies the carrier via FMCSA, matches them to
a live load, negotiates within a defined pricing policy, and either
transfers a booking-ready call to a sales rep or logs precisely why the
call did not convert.

Every interaction produces structured data — outcome, sentiment, rate, and
negotiation history — which feeds a dashboard designed to answer:
**“What should we do next?”**, not just **“What happened?”**.

---

## Who it's for

- **Inbound Sales Desk**
  - Eliminates missed calls and after-hours gaps
  - Only receives pre-qualified, price-aligned transfers
- **Sales Lead / Ops Manager**
  - Real-time visibility into revenue, margin, and conversion
  - Clear recommendations on pricing and lane strategy

---

## What it does today (v1)

A single HappyRobot voice agent (*"Bree"*) handles inbound calls end-to-end:

### 1. Vet the carrier
- Collects MC number
- Verifies via FMCSA QCMobile API
- Rejects carriers without active authority
- Logs rejection reason explicitly

---

### 2. Match to a load
- Asks for:
  - current location
  - equipment type
- Searches load board:
  - prioritizes proximity and rate
- Expands search once before exiting

---

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

---

### 4. Close

- On agreement:
  - Confirms load + rate
  - Simulates transfer to rep (mocked in v1)
- On failure:
  - Ends call politely
  - Logs outcome

---

### 5. Extract & classify

Captured automatically:
- Carrier preferences
- Lane details
- Negotiation history

Classified into:
- **Outcome** (7 categories: booked, no agreement, invalid carrier, etc.)
- **Sentiment** (positive, neutral, negative, frustrated)

---

## The dashboard — decision layer

Designed for **daily operational decisions**, not reporting.

### Top-level metrics

- **Revenue booked**
- **Conversion rate**
- **Margin vs loadboard**
- **Missed revenue opportunity**

---

### Decision support

- **“What to do next” panel**
  - Dynamic recommendations:
    - pricing adjustments
    - lane prioritization
- **Conversion funnel**
  - identifies drop-off stages
- **Outcome + sentiment breakdown**
- **Top lanes**
  - volume, conversion, margin
- **Recent calls feed**
  - drill-down into:
    - negotiation rounds
    - extracted fields
    - transcript

Every metric ties directly to agent actions.

---

## How it integrates

- HappyRobot agent calls:
  - `/carriers/verify`
  - `/loads/search`
  - `/negotiate`
  - `/calls`
- All endpoints:
  - HTTPS
  - API key protected
- Single shared database:
  - agent writes
  - dashboard reads
  - no ETL, no drift

---

## What’s not in v1 (by design)

- **Live call transfer**
  - Mocked for now
  - trivial to enable (1-line change)

- **ML-based pricing**
  - Rule-based for explainability
  - groundwork captured for future training

- **High availability / multi-region**
  - Single instance sufficient for pilot
  - architecture is upgrade-ready (Postgres)

- **CRM integration**
  - structured data captured
  - write-back deferred to v1.1

---

## What we need from Acme

1. FMCSA API key
2. Sales rep transfer number / ring group
3. Approval on pricing policy:
   - Floor (92%)
   - Ceiling (115%)
4. 1-hour calibration session with sales lead

---

## Success metrics (pilot)

- **North star**
  - After-hours revenue booked per week

- **Guardrails**
  - Margin within ±5% of loadboard
  - <15% negative sentiment
  - 0 invalid carrier bookings

All tracked live in the dashboard.

---

## Why this works

- Captures **every inbound opportunity**
- Standardizes **negotiation quality**
- Produces **actionable data from day one**
- Bridges gap between **AI automation and real ops decisions**

Freight Pilot is not just handling calls —  
it is building a **repeatable, measurable inbound sales engine** for Acme Logistics.