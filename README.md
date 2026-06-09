# Live Canonical Infrastructure Runtime

Deterministic execution platform with a **FastAPI backend** and **React dashboard** for live runtime execution, replay verification, recovery analysis, and observability.

## Architecture

```
React Dashboard (port 5173)
        ↓ REST + WebSocket
FastAPI Backend (port 8000)
        ↓
Runtime Service Layer
        ↓
datasets → validation → serialization → hashing → persistence
  → replay → reconstruction → recovery → observability
```

## Quick Start (Development)

### 1. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Start API server

```bash
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8001
```

API docs: http://127.0.0.1:8001/docs

### 3. Start React frontend (new terminal — requires Node.js)

```bash
cd frontend
npm install
npm run dev
```

Dashboard: http://127.0.0.1:5173

The React app (v2 production UI) includes:
- **Login** (demo: `admin` / `runtime` — configure via `VITE_AUTH_*`)
- Sidebar layout with Dashboard, Events, Runs, Verify, Reports, Settings
- **Tailwind CSS** design system
- **TanStack React Query** for API caching and mutations
- Error boundaries, skeleton loaders, toast notifications
- Live pipeline monitor with progress bar
- Charts (validation split, dataset composition)
- Paginated event explorer with search and filters
- Run history with detail view and JSON download

```bash
cd frontend
npm install
npm run dev        # development
npm run build      # production static build → frontend/dist/
npm test           # vitest unit tests
```

### One command (Windows — starts both API + frontend)

```powershell
cd "c:\Users\Ruhin\OneDrive\Desktop\BlackHole Intelligence"
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Or double-click `start.bat`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/runs/live` | Full live pipeline |
| POST | `/api/runs/replay` | Replay verification |
| POST | `/api/runs/recover` | Recovery analysis |
| POST | `/api/runs/verify` | Failure-path tests |
| GET | `/api/runs` | Run history |
| GET | `/api/runs/report/latest` | Latest report |
| GET | `/api/events` | Paginated event log |
| WS | `/ws` | Live pipeline stage updates |

## CLI (still available)

```bash
python run_system.py --mode live
python run_system.py --mode replay
python run_system.py --mode recover
python run_system.py --mode verify
```

## Docker

```bash
docker compose up --build
```

- API: http://localhost:8000
- Dashboard: http://localhost:5173

## Testing

```bash
python -m unittest tests.test_end_to_end_runtime -v
```

## Project Structure

```
run_system.py              # CLI entry point
services/                  # Runtime service + run store (SQLite)
backend/api/               # FastAPI REST + WebSocket
frontend/                  # React + Vite dashboard
datasets/                  # Dataset generation and loading
validation/                # Event validation and failure-path testing
serialization/             # Canonical JSON serialization
hashing/                   # SHA-256 payload hashing
persistence/               # Append-only log storage
replay/                    # Replay and truth reconstruction
recovery/                  # Interrupted execution recovery
observability/             # Runtime observer and final report
tests/                     # End-to-end integration test
```
