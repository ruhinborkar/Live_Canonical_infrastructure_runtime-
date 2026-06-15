# Validation Guide

Reviewer validation path — under 10 minutes.

---

## Setup

```bash
pip install -r backend/requirements.txt
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `python run_system.py --mode live` | Full live pipeline |
| `python run_system.py --mode demo` | Live → Replay → Reconstruction → Truth → Recovery → Observability |
| `python run_system.py --mode replay` | Replay verification only |
| `python run_system.py --mode recover` | Interrupted recovery analysis |
| `python run_system.py --mode verify` | Truth verification + failure-path checks |
| `python -m unittest tests.test_end_to_end_runtime` | Automated end-to-end test |

---

## Expected Outputs (demo / live)

Stdout must include:

```
REPLAY_VERIFIED
TRUTH_VERIFIED
```

Recovery outcome for the standard dataset:

```
RECOVERY_REQUIRED
```

Generated artifacts:

| File | Proof |
|------|-------|
| `logging/logs/live_execution.jsonl` | 100 persisted events |
| `logging/logs/replay_log.jsonl` | Replay records + `REPLAY_VALIDATION` |
| `logging/logs/recovery_log.jsonl` | Recovery candidates + `RECOVERY_VALIDATION` |
| `observability/final_runtime_report.json` | Full execution report |
| `runtime_recovery_proof.json` | Recovery resumes from persisted truth (`assumptions_used: false`) |

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

### Recovery required

Standard dataset includes 10 `INTERRUPTED_EVENT` records (sequences 91–100).

```bash
python run_system.py --mode recover
```

Expected: `recovery_outcome: RECOVERY_REQUIRED`, `resume_point: 91`

---

## Quick Validation (5 steps)

1. `python run_system.py --mode demo`
2. Confirm stdout: `REPLAY_VERIFIED`, `TRUTH_VERIFIED`, `RECOVERY_REQUIRED`
3. Inspect `runtime_recovery_proof.json` — `resumed_from_persisted_truth: true`
4. Inspect `observability/final_runtime_report.json`
5. Run `python -m unittest tests.test_end_to_end_runtime`
