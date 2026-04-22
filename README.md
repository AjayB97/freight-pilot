# Freight Pilot — Inbound Carrier Sales

A working proof-of-concept of an inbound carrier sales system built on the
**HappyRobot** platform, with a custom API and an operator dashboard.

- **Agent** (on HappyRobot): vets the carrier with FMCSA, searches loads,
  pitches, negotiates up to 3 rounds against a deterministic pricing policy,
  transfers to a rep on agreement, and logs everything.
- **API** (`/backend`, FastAPI + SQLite): the agent's tools. Endpoints for
  carrier verification, load search, negotiation, and call logging. API-key
  auth, containerised with Docker.
- **Dashboard** (`/frontend`, Next.js): **business-outcome** metrics for an
  ops lead — booked revenue, conversion funnel, margin vs loadboard, lost
  pipeline, sentiment, top lanes, and auto-generated recommendations. Drill
  into any call or negotiation round.

Everything here is connected: the agent's tool calls flow into the same DB
the dashboard reads from. Every number on the dashboard traces back to an
agent action.

## Repo layout

```
.
├── backend/                  FastAPI service (API + business logic)
│   ├── app/
│   │   ├── api/              Route modules (carriers, loads, negotiate, calls, metrics)
│   │   ├── core/             Config + API-key auth
│   │   ├── db/               SQLAlchemy models + session
│   │   ├── services/         FMCSA client + negotiation engine
│   │   └── seed/             Sample load data, idempotent seeding
│   ├── Dockerfile
│   ├── fly.toml              Fly.io deploy config
│   └── requirements.txt
├── frontend/                 Next.js 15 dashboard (App Router, Tailwind)
│   ├── src/app/              Pages: overview, calls, call detail, loads, negotiations
│   ├── src/components/       UI primitives + charts
│   ├── src/lib/              Typed API client (server-only)
│   └── Dockerfile
├── docs/
│   ├── agent/
│   │   └── happyrobot-workflow.md   ← Paste into HappyRobot
│   ├── build-description.md         ← For the broker ("Acme Logistics")
│   └── deploy.md                    ← Fly.io + Vercel reproducible steps
├── docker-compose.yml
└── README.md
```

## Quick start (local)

Prereqs: Docker, Docker Compose, an FMCSA web key
(https://mobile.fmcsa.dot.gov/QCDevsite/home), Node 20+ only if you want to
run the frontend without Docker.

```bash
# 1. Set up env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# put your real FMCSA_API_KEY in backend/.env

# 2. Run both services
docker compose up --build

# 3. Open things
# API     → http://localhost:8080/docs
# Health  → http://localhost:8080/health
# Dashboard → http://localhost:3000
```

The DB auto-creates on first boot and seeds 12 realistic loads across common
U.S. lanes (dry van, reefer, flatbed).

## Calling the API manually

```bash
API=http://localhost:8080
KEY=dev-local-key   # default; change in production

curl -s "$API/loads/search?origin=Dallas&equipment_type=Dry%20Van" -H "X-API-Key: $KEY" | jq

curl -s -X POST "$API/carriers/verify" -H "X-API-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{"mc_number":"MC 1234567"}' | jq

curl -s -X POST "$API/negotiate" -H "X-API-Key: $KEY" \
  -H 'Content-Type: application/json' \
  -d '{"load_id":"LD-1001","carrier_offer":2400,"round_number":1}' | jq

curl -s -X POST "$API/calls" -H "X-API-Key: $KEY" \
  -H 'Content-Type: application/json' \
  -d '{"load_id":"LD-1001","outcome":"booked","sentiment":"positive","loadboard_rate":2150,"final_rate":2250,"rounds":2,"summary":"Demo booking."}' | jq
```

## HappyRobot agent

See [`docs/agent/happyrobot-workflow.md`](./docs/agent/happyrobot-workflow.md)
— that file is the complete spec: system prompt, call flow, tool definitions,
and classification rules.

## Deploy

See [`docs/deploy.md`](./docs/deploy.md) for reproducible Fly.io (API) +
Vercel (dashboard) steps.

## Design decisions

- **Deterministic negotiation.** The LLM is great at conversation but bad at
  disciplined pricing. The `negotiate` endpoint is pure rule-based: floor,
  ceiling, sweet-spot, meet-in-the-middle, final-round rules. The agent only
  *says* the numbers the server decides.
- **One system, one DB.** Every tool call the agent makes writes to the same
  SQLite file the dashboard reads. No ETL, no duplication.
- **Business metrics over activity metrics.** The dashboard intentionally
  leads with *booked revenue*, *conversion*, *margin*, *lost pipeline*, and
  *auto-generated recommendations* — not "number of API calls".
- **API-key auth everywhere.** Every endpoint except `/health` requires
  `X-API-Key`. HTTPS comes free with Fly.io's edge.
- **Containerised.** Both services ship as Docker images; a single
  `docker-compose up` reproduces the whole stack.

## Known limitations (honest list)

- SQLite single-writer. Fine for one region / one machine. Swap to Postgres
  if we ever need multi-region.
- FMCSA is slow and occasionally flaky — results are cached in a `carriers`
  table, but the first hit for a new MC number can take a few seconds.
- Negotiation policy is deterministic rules, not learned. That's *intentional*
  for v1 (explainability, audit), but the dashboard gives us the data to
  train a policy later.
