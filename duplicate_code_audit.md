# Duplicate Code Audit

Phase 1 convergence audit — duplicate logic identified and resolution status.

## Backend Duplicates

| ID | Duplicate | Locations | Resolution | Status |
|----|-----------|-----------|------------|--------|
| D-01 | Recovery log persistence | `runtime_recovery.py`, `interrupted_recovery.py` | Extracted to `recovery/persistence_helpers.py` | **RESOLVED** |
| D-02 | Sequence gap analysis | `runtime_recovery.analyze`, `interrupted_recovery`, `failure_path_executor` | Shared `analyze_recovery_state()` + `missing_sequences()` in persistence_helpers; failure_path uses event_loader only | **PARTIAL** — failure_path keeps hostile synthetic checks (Phase 5 will unify) |
| D-03 | JSONL file loading | `failure_path_executor._load_jsonl`, scattered hardcoded paths | `failure_path_executor` now uses `read_log_events` + `AppendOnlyStore` | **RESOLVED** |
| D-04 | Truth reconstruction facade | `runtime_reconstructor.py` wrapping reconstructor + verifier | File removed; pipeline uses canonical modules directly | **RESOLVED** |
| D-05 | Event query API | `/api/events` vs `/api/runtime/events` | Both delegate to `event_loader.load_events` — intentional dual surface (raw API vs dashboard) | **ACCEPTED** |
| D-06 | Recovery analysis (live vs recover) | `RuntimeRecovery.analyze` vs `InterruptedRecovery` | Both call `analyze_recovery_state()` with `include_duplicates` flag | **RESOLVED** |

## Frontend Duplicates

| ID | Duplicate | Locations | Resolution | Status |
|----|-----------|-----------|------------|--------|
| F-01 | Event table / explorer | `EventsTable.tsx` vs `EventExplorer.tsx` | Deleted `EventsTable.tsx` | **RESOLVED** |
| F-02 | Pipeline monitor | `PipelineMonitor.tsx` vs `PipelineFlowMonitor.tsx` | Deleted `PipelineMonitor.tsx` | **RESOLVED** |
| F-03 | Status KPI cards | `StatusCards.tsx` vs `RuntimeMetricsGrid.tsx` | Deleted `StatusCards.tsx` | **RESOLVED** |
| F-04 | Operation bar | `ActionBar.tsx` vs `OperationBar.tsx` | Deleted `ActionBar.tsx` | **RESOLVED** |
| F-05 | Runtime summary panel | `RuntimeSummary.tsx` vs `HeroStatusHeader` + metrics grid | Deleted `RuntimeSummary.tsx` | **RESOLVED** |
| F-06 | Charts component | `RuntimeCharts.tsx` (unused) | Deleted | **RESOLVED** |
| F-07 | Events query hooks | `useEvents` in `queries.ts` vs `useRuntimeEvents` in console | Both used — Events page could unify on console API in Phase 9 | **DEFERRED** |

## Previously Removed (Prior Convergence)

| Item | Reason |
|------|--------|
| `Live_Canonical_Replay_Infrastructure_Runtime (1).ipynb` | Full duplicate runtime in notebook |
| `validation/runtime_corruption.py` | Orphan, never wired |
| `validation/sequence_manager.py` | Orphan, duplicated sequence logic |
| `README (4).md`, `README (10).md` | Duplicate docs |
| `REVIEW_PACKET (6).md`, `REPO_CONVERGENCE (1).md` | Superseded copies |

## Remaining Overlap (Accepted / Phase 5+)

1. **Failure-path vs recovery sequence checks** — Different purposes (hostile validation vs operational recovery). Phase 5 `failure_injection_framework.py` will provide single injection source.
2. **Dual event API routes** — Same loader, different response shaping for dashboard vs raw clients.
3. **`useEvents` vs `useRuntimeEvents`** — Frontend hook duplication; low risk, fix in Phase 9.

## Verification

```bash
# No second replay engine
ls replay/*.py
# Expected: runtime_replayer.py, runtime_truth_reconstructor.py only

# No duplicate recovery persist logic in module files
rg "RECOVERY_CANDIDATE" recovery/
# Expected: persistence_helpers.py only (plus tests)
```

**Audit date:** Phase 1 completion  
**Duplicate systems remaining:** 0 parallel runtime stacks
