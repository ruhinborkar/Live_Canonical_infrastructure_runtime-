# Deployment Guide

How to run the operational runtime backbone in development and production-style
deployments.

## 1. Configuration (Phase 6)

Configuration is layered: **environment profile → environment variables**.
Profiles live in `config/environment_profiles.py`; access is via
`config/runtime_config.py`. Secrets are never read directly — always through
`security/secrets_provider.py`.

| Variable | Default | Purpose |
|----------|---------|---------|
| `RUNTIME_ENV` | `development` | Selects profile (`development`/`staging`/`production`) |
| `RUNTIME_WORKERS` | profile | Worker pool size |
| `RUNTIME_HEARTBEAT_INTERVAL` | `1.0` | Heartbeat seconds |
| `RUNTIME_RATE_LIMIT` | profile | Ingestion rate limit / minute (0 = unlimited) |
| `RUNTIME_LOG_LEVEL` | profile | Structured log level |
| `RUNTIME_AUTOSTART` | `true` | Auto-start engine on API startup |

Profiles:

| Profile | Workers | Rate limit | Log level |
|---------|---------|-----------|-----------|
| development | 2 | unlimited | DEBUG |
| staging | 3 | 600/min | INFO |
| production | 4 | 1200/min | INFO |

## 2. Run modes (`run_system.py`)

| Mode | Behaviour |
|------|-----------|
| `operate` | Boot the backbone and run continuously until Ctrl+C (`--duration N` to time-box) |
| `smoke` | Automated continuous-runtime smoke test + readiness proof |
| `live` / `replay` / `recover` / `verify` / `ledger` / `inject` / `manifest` / `demo` | Canonical runtime-proof flows (unchanged) |

```bash
# Continuous operational runtime
python run_system.py --mode operate

# Time-boxed continuous run (CI-friendly)
python run_system.py --mode operate --duration 10

# Automated smoke + readiness
python run_system.py --mode smoke
```

## 3. API server

```bash
# Development
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002 --reload

# Production-style
$env:RUNTIME_ENV = "production"   # PowerShell
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8002 --workers 1
```

> Run uvicorn with a single OS worker process. The runtime engine itself is
> multi-threaded; multiple uvicorn workers would each start their own engine and
> contend over the shared state file.

The engine auto-starts on API startup (`RUNTIME_AUTOSTART=true`) and stops
gracefully on shutdown.

## 4. Frontend

```bash
cd frontend
npm install
npm run dev      # http://127.0.0.1:5173
npm run build    # production bundle in dist/
```

Set `VITE_API_URL` to the API base (defaults to `/api`).

## 5. Containers

`Dockerfile` and `docker-compose.yml` build the API + static dashboard. Health
checks hit `/api/health`. For production set `RUNTIME_ENV=production`.

```bash
docker compose up --build
```

## 6. Operational endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/operations/status` | Live engine state, workers, heartbeat, counters |
| `GET /api/operations/situation` | What's happening / attention / next |
| `GET /api/operations/readiness` | Operational readiness score (0–10) |
| `GET /api/operations/queue` | Pending execution queue |
| `GET /api/operations/alerts` | Active alerts |
| `POST /api/operations/submit` | Submit work |
| `POST /api/operations/stop` | Graceful stop |

## 7. Persistence & recovery

State and pending work persist to `data/operational_state.json` and
`data/runtime_queue.json`. On restart the engine detects an unclean prior
shutdown and restores pending work automatically — no manual intervention.
