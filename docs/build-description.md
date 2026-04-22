# Freight Pilot — Inbound Carrier Sales, v1

*Prepared for Acme Logistics by the Freight Pilot team*

## TL;DR

Carriers call Acme's inbound line 24/7. Most of those calls come in after
hours or during overlap, when the sales desk is maxed out. Freight Pilot
picks up every call, runs the carrier through FMCSA, matches them to a live
load, negotiates within policy, and either transfers a booking-ready call to
a sales rep or logs why it didn't convert.

Every call produces structured data — outcome, sentiment, rate, and
negotiation history — which feeds a dashboard your sales lead uses to
decide *what to do tomorrow*, not just *what happened yesterday*.

## Who it's for

- **Acme's inbound sales desk** — fewer abandoned calls, no after-hours
  gaps, and reps only get live-transferred calls that are already priced
  and verified.
- **Acme's sales lead / ops manager** — a real-time view of inbound
  performance: revenue, margin vs loadboard, conversion by lane, and
  recommended next actions.

## What it does today (v1)

A single HappyRobot voice agent (*"Bree"*) handles every inbound call and
does four things, in order:

1. **Vet** the carrier. Grabs their MC number, verifies them against the
   FMCSA QCMobile API, and refuses to book anyone whose authority is not
   active. The reason is logged — no silent drops.
2. **Match** them to a load. Asks one open question about current location
   and equipment, then searches Acme's load board for the best fit (closest
   pickup, then highest rate). Widens the search once before giving up.
3. **Negotiate** — up to three rounds. Pricing is **deterministic and
   policy-driven** server-side:
   - **Floor:** 92% of loadboard rate (configurable). Never agree below.
   - **Ceiling:** 115% of loadboard rate (configurable). Never agree above.
   - **Sweet spot:** within 3% of loadboard → instant accept.
   - **Above sweet spot, below ceiling:** meet-in-the-middle, accept on
     final round.
   - **Above ceiling:** counter at the ceiling, then reject on final round.
   - **Below floor:** counter UP to the loadboard rate (don't leave money on
     the table, but don't haggle hard).

   Every round is logged with the reasoning — auditors / sales leads can
   review *why* the agent made each call.
4. **Close**. On agreement, Bree confirms the lane and rate, then says
   "transferring you to a rep now" (mocked per Acme's request for v1; real
   transfer is a one-line change). On no-agreement, Bree politely ends and
   logs the outcome.

Throughout the call, Bree extracts structured fields (current location,
desired pickup day, equipment preference, notes), classifies the outcome
into one of seven buckets, and classifies sentiment into positive / neutral
/ negative / frustrated.

## The dashboard — what your sales lead actually needs

The home page answers four questions in the top row:

- **How much revenue did the agent book?** (with the call count that produced it)
- **What's our conversion rate?** (booked / total calls)
- **Are we pricing correctly?** — average margin vs loadboard. Green if
  close to 0%, red if we're booking below, amber if we're over-pricing.
- **What did we leave on the table?** — sum of unbooked rates from
  no-agreement / declined / abandoned calls.

Below that:

- A "**What to do next**" panel of auto-generated recommendations (e.g.
  *"Avg booked margin is +12% — you're leaving rate on the table; lower
  the ceiling"*, *"Lane Dallas→Atlanta converts 67% — source more of
  these"*).
- A **conversion funnel** showing where calls drop off between ring and
  book.
- **Outcome distribution** and **carrier sentiment** bars.
- **Top lanes** by call volume with conversion and margin per lane.
- A feed of **recent calls**, each drillable into a page with the
  summary, rates, rounds, extracted fields, and a link to the transcript.

Every number on the dashboard traces back to a specific agent action.

## How it integrates

- The HappyRobot agent calls four HTTPS endpoints on the Freight Pilot
  API: `/carriers/verify`, `/loads/search`, `/negotiate`, `/calls`.
- All endpoints require an API key (header auth). HTTPS is handled at the
  platform edge.
- The same database the agent writes to is the one the dashboard reads
  from — no ETL, no drift.

## What's explicitly *not* in v1 (and why)

- **Real transfer to a rep.** Mocked per Acme's instructions; v1.1 is a
  one-line change once we have the rep's ring group.
- **Learned pricing policy.** v1 is rule-based on purpose — we need
  explainability for the first 90 days so sales leaders trust it. The
  dashboard captures the ground truth we'd later use to train a policy.
- **Multi-region / high availability.** v1 is one machine with a persistent
  volume. Inbound volume doesn't justify more yet; we can move to Postgres
  and multi-region at any time without code changes.
- **CRM write-back.** We're capturing the structured data (MC, carrier
  name, extracted lane prefs) but not pushing to a CRM yet. Integration
  target for v1.1.

## What we need from Acme to go live

1. An FMCSA web key (5 minutes at mobile.fmcsa.dot.gov).
2. Acme's ring group or phone number to transfer to.
3. Sign-off on the **floor (92%)** and **ceiling (115%)** — these are the
   two numbers that most directly affect revenue and margin.
4. An hour with the sales lead to watch three real calls and tune the
   pitch script.

## Success metrics for the pilot

- **North-star:** after-hours revenue booked per week.
- **Guardrails:** avg margin within ±5% of loadboard, negative sentiment
  rate below 15%, zero bookings with non-authorized carriers.

All four are on the dashboard from day one.
