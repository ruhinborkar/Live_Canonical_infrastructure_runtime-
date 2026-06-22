# Validation Guide

Reviewer validation path — under 10 minutes.

---

## Setup

```bash
pip install -r backend/requirements.txt
```

Optional Docker:

```bash
docker compose up --build
```

API: http://127.0.0.1:8000 (Docker) or http://127.0.0.1:8002 (local dev)  
Dashboard: http://127.0.0.1:5173/ (login: `admin` / `runtime`)

---

## Commands

| Command | Purpose |
|---------|---------|
| `python run_system.py --mode live` | Full live pipeline + truth ledger snapshots |
| `python run_system.py --mode demo` | Live → Replay → Truth → Recovery → Observability |
| `python run_system.py --mode ledger` | Truth ledger reconstruction proof (no replay logs) |
| `python run_system.py --mode inject` | Failure injection framework (6 scenarios) |
| `python run_system.py --mode manifest` | Aggregate proof manifest |
| `python run_system.py --mode recover` | Executable recovery from persisted truth |
| `python run_system.py --mode verify` | Truth verification + failure-path checks |
| `python -m unittest discover -s tests -p "test_*.py"` | Automated test suite |

---

## Truth Ledger Validation

```bash
python run_system.py --mode live
python run_system.py --mode ledger
```

Expected stdout:

```
SUCCESS
TRUTH_LEDGER
```

Expected proof file `truth_ledger_reconstruction_proof.json`:

```json
{
  "truth_reconstruction": "SUCCESS",
  "source": "TRUTH_LEDGER",
  "runtime_state": "OPERATIONAL"
}
```

Note: `runtime_state` reflects the final execution state in the dataset (may be `INTERRUPTED` when interrupted events are last).

API: `GET /api/runtime/ledger`

---

## Failure Injection Validation

```bash
python run_system.py --mode inject
```

Expected: 6 scenarios detected, including:

```json
{
  "failure_type": "CORRUPTED_HASH",
  "detected": true,
  "system_response": "REPLAY_REJECTED"
}
```

Proof file: `failure_injection_proof.json`  
API: `GET /api/runtime/injection`

---

## Deployment Validation

```bash
docker compose up --build -d
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/health/monitor
curl http://127.0.0.1:8000/api/startup/validation
```

Expected health monitor keys:

- `runtime_health`
- `replay_health`
- `persistence_health`
- `recovery_health`

Expected startup validation:

```json
{
  "ready": true,
  "status": "READY",
  "checks": {
    "persistence_available": true,
    "dataset_available": true,
    "configuration_valid": true,
    "runtime_ready": true
  }
}
```

---

## Demo / Live Expected Outputs

Stdout must include:

```
REPLAY_VERIFIED
TRUTH_VERIFIED
RECOVERY_REQUIRED or RECOVERY_EXECUTED
```

Generated artifacts:

| File | Proof |
|------|-------|
| `logging/truth_ledger/truth_snapshots.jsonl` | Immutable truth snapshots |
| `truth_ledger_reconstruction_proof.json` | Ledger-only reconstruction |
| `failure_injection_proof.json` | Hostile failure injection proof (6 scenarios) |
| `logging/logs/live_execution.jsonl` | 100 persisted events |
| `observability/final_runtime_report.json` | Full execution report |
| `runtime_recovery_proof.json` | Recovery analysis from persisted truth |
| `runtime_recovery_execution_proof.json` | Executable recovery (`RECOVERED_EVENT` appended) |
| `runtime_proof_manifest.json` | Aggregated proof manifest |

---

## Executable Recovery Validation

```bash
python run_system.py --mode live
python run_system.py --mode recover
```

Expected: `recovery_executed: true`, `events_recovered > 0`, `recovery_outcome: RECOVERY_EXECUTED`

Proof: `runtime_recovery_execution_proof.json` with `proof_type: EXECUTABLE_RECOVERY`

---

## Proof Manifest Validation

```bash
python run_system.py --mode manifest
```

Expected: `overall: PASS` or `PARTIAL` with `checks` for ledger, injection, recovery, startup, health.

API: `GET /api/runtime/manifest`

Metrics API (`GET /api/runtime/metrics`) includes `reconstruction_duration_ms`, `memory_consumption_mb`, `persistence_throughput_eps`.

---

## Quick Validation (10 minutes)

1. `pip install -r backend/requirements.txt`
2. `python run_system.py --mode demo`
3. `python run_system.py --mode ledger`
4. `python run_system.py --mode inject`
5. `python -m unittest discover -s tests -p "test_*.py"`
6. Start API + dashboard; confirm health, startup, ledger, and injection panels on Dashboard
7. Optional: `docker compose up --build`

---

## Failure Examples

### Replay mismatch

Tamper with a `payload_hash` in `logging/logs/live_execution.jsonl`, then:

```bash
python run_system.py --mode replay
```

Expected: `REPLAY_MISMATCH`

### Truth mismatch

Delete a line from `logging/logs/live_execution.jsonl`, then:

```bash
python run_system.py --mode verify
```

Expected: `TRUTH_MISMATCH`
