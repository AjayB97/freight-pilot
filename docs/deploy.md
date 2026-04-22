# Deploy guide

Target: **API → Fly.io** (Docker, 1 VM, persistent volume for SQLite),
**Dashboard → Vercel** (Next.js). HTTPS is automatic on both.

If you ever want everything on one platform, both services ship as Docker
images, so deploying both to Fly.io or both to Railway is a swap of two
commands.

---

## 1. Deploy the API to Fly.io

### Prereqs

- `fly` CLI installed (`brew install flyctl`).
- A Fly account (`fly auth signup` or `fly auth login`).
- Your FMCSA web key.

### Steps

From the repo root:

```bash
cd backend

# First-time only: create the app (pick a unique name).
# Use --no-deploy — we need to attach a volume first.
fly launch --no-deploy --copy-config --name freight-pilot-api

# Create a 1 GB volume in the same region as your app (ord here).
fly volumes create freight_pilot_data --size 1 --region ord

# Set secrets (never commit these).
fly secrets set \
  API_KEYS=$(openssl rand -hex 24) \
  FMCSA_API_KEY=<your-fmcsa-web-key> \
  CORS_ORIGINS=https://<your-vercel-app>.vercel.app

# Deploy.
fly deploy

# Confirm it's up.
fly status
curl https://freight-pilot-api.fly.dev/health
```

Note the API key you set in `API_KEYS` — you'll paste it into Vercel and
into the HappyRobot agent as a secret.

### Reproducing later

Everything is in `backend/fly.toml` and `backend/Dockerfile`. A fresh
`fly deploy` from the repo reproduces the current machine. The volume
persists the SQLite DB across deploys.

---

## 2. Deploy the dashboard to Vercel

### Prereqs

- A Vercel account + the `vercel` CLI (`npm i -g vercel`) **or** just connect
  the GitHub repo from the Vercel dashboard.

### Steps

From the repo root:

```bash
cd frontend

# First-time only: link the directory to a Vercel project.
vercel link

# Set the two env vars (server-side only).
vercel env add API_BASE_URL production    # https://freight-pilot-api.fly.dev
vercel env add API_KEY production         # the API key you set on Fly

# Ship it.
vercel --prod
```

If you prefer the Git integration:
- Import the repo in Vercel, set **Root directory** = `frontend`.
- Framework preset = Next.js. Build command + output dir default.
- Add `API_BASE_URL` and `API_KEY` under Project Settings → Environment Variables.

### Verifying the end-to-end flow

```bash
curl -H "X-API-Key: <YOUR_KEY>" https://freight-pilot-api.fly.dev/metrics/summary
```

Then open `https://<your-project>.vercel.app` — the dashboard should load with
the seeded data and zero calls.

---

## 3. Point the HappyRobot agent at it

In the HappyRobot UI, set the tool base URL to `https://freight-pilot-api.fly.dev`
and add `X-API-Key: <YOUR_KEY>` as a header on every tool. See
`docs/agent/happyrobot-workflow.md` for tool definitions.

---

## 4. Local = production parity

`docker compose up --build` at the repo root starts the exact same containers
that ship to Fly/Vercel, on the same ports, backed by a host-mounted
`backend/data/` directory for the SQLite file. If something breaks in prod
you can almost always reproduce it locally by copying the Fly secrets into
`backend/.env`.
