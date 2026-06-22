# Dead Code Audit

Phase 1 convergence audit — unused modules, methods, and components.

## Removed in Phase 1

| Item | Path | Evidence | Action |
|------|------|----------|--------|
| Truth reconstructor facade | `replay/runtime_reconstructor.py` | Zero imports in codebase | **DELETED** |
| Dead recovery stub | `RuntimeRecovery.recover()` | Never called from service or API | **REMOVED** (method deleted with module refactor) |
| Legacy EventsTable | `frontend/src/components/EventsTable.tsx` | Not in `App.tsx` route tree | **DELETED** |
| Legacy PipelineMonitor | `frontend/src/components/PipelineMonitor.tsx` | Superseded by `PipelineFlowMonitor` | **DELETED** |
| Legacy StatusCards | `frontend/src/components/StatusCards.tsx` | Superseded by `RuntimeMetricsGrid` | **DELETED** |
| Legacy ActionBar | `frontend/src/components/ActionBar.tsx` | Superseded by `OperationBar` | **DELETED** |
| Legacy RuntimeCharts | `frontend/src/components/RuntimeCharts.tsx` | No imports | **DELETED** |
| Legacy RuntimeSummary | `frontend/src/features/console/components/RuntimeSummary.tsx` | No imports | **DELETED** |

## Still Present (Intentional / Deferred)

| Item | Path | Notes | Phase |
|------|------|-------|-------|
| Demo API route | — | `execute_demo()` exists in CLI only; no `POST /runs/demo` | Optional — add in Phase 8 if needed |
| `backend/static/index.html` | Static fallback | May lag behind `frontend/dist` | Verify in Phase 8 deployment |
| `useEvents` hook | `frontend/src/hooks/queries.ts` | Used only if referenced — grep in Phase 9 | Phase 9 |
| `GET /api/events` | `backend/api/routes/events.py` | Active API surface, not dead | Keep |

## Previously Removed

| Item | Path |
|------|------|
| `validation/runtime_corruption.py` | Orphan validator |
| `validation/sequence_manager.py` | Orphan sequence helper |
| Notebook duplicate runtime | `Live_Canonical_Replay_Infrastructure_Runtime (1).ipynb` |

## Import Graph Verification

Modules with **no inbound imports** (should be entry points only):

| Module | Role |
|--------|------|
| `run_system.py` | CLI entry |
| `backend/api/main.py` | API entry |
| `tests/*.py` | Test entry |

Modules that **must** have inbound imports:

| Module | Imported By |
|--------|-------------|
| `runtime_replayer.py` | `runtime_service` |
| `runtime_truth_reconstructor.py` | `runtime_service` |
| `truth_verifier.py` | `runtime_service` |
| `persistence_helpers.py` | `runtime_recovery`, `interrupted_recovery` |
| `failure_path_executor.py` | `runtime_service` |

## Dead Code Removal Summary

| Category | Count Removed |
|----------|---------------|
| Python modules deleted | 1 (`runtime_reconstructor.py`) |
| Python dead methods removed | 1 (`RuntimeRecovery.recover`) |
| Frontend components deleted | 6 |
| Orphan validators (prior) | 2 |

**STATUS:** No known orphan facades or unused dashboard components remain.
