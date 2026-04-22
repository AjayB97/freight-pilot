# Email to Carlos Becker (c.becker@happyrobot.ai) — ahead of the meeting

> Recruiter on CC.

---

**Subject:** Freight Pilot — progress ahead of our call

Hi Carlos,

Looking forward to our chat. A quick preview of what I'll walk you through —
I wanted you to have the links before the meeting so you can poke around if
you've got five minutes.

**The build**
I've wrapped v1 of Freight Pilot, an inbound carrier sales POC framed as a
real product for a broker ("Acme Logistics"). It's one system end-to-end:

- A HappyRobot inbound agent ("Riley") that vets the carrier with FMCSA,
  matches them to a load, negotiates up to three rounds inside a clear
  pricing policy, and transfers on agreement.
- A Python/FastAPI backend that exposes the agent's tools
  (`/carriers/verify`, `/loads/search`, `/negotiate`, `/calls`) with API-key
  auth and a deterministic negotiation engine — every decision is auditable.
- A Next.js dashboard an ops lead actually uses: booked revenue, conversion
  funnel, margin vs loadboard, lost pipeline, sentiment, top lanes, and an
  auto-generated "what to do next" panel. Every number traces back to an
  agent action.

Both services are containerised; the API runs on Fly.io (Docker + persistent
volume for SQLite), the dashboard is on Vercel.

**Links**
- Dashboard: https://<your-vercel-url>
- API (health): https://<your-fly-url>/health
- API docs: https://<your-fly-url>/docs
- Repo: https://github.com/<you>/freight-pilot
- HappyRobot workflow: <paste the platform link>

**What I'll cover in the 5-min demo**
1. The setup — HappyRobot agent wiring, tool definitions, prompting choices.
2. A live web call: MC verification → load pitch → 3-round negotiation →
   booked transfer.
3. Dashboard walk-through with the call I just made visible on screen, and
   the recommendation it produced.

Happy to dig into any of the design decisions on the call — particularly the
rule-based negotiation and why v1 is explainable-first rather than LLM-priced.

Thanks,
Ajay
