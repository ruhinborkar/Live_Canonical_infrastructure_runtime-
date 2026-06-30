# Capability Architecture

The platform is organised as an **ecosystem of reusable capabilities** that
attach to the operational runtime backbone. Each capability is generic (no
organisation-specific or classified logic) and defines a clear contract:
**Inputs, Outputs, Dependencies, Authority boundaries, Attachment rules, and
Future consumers.**

Detailed per-capability specifications live in `docs/capabilities/`.

## Capability catalogue

| # | Capability | Module / Source | Spec |
|---|------------|-----------------|------|
| 1 | Execution | `runtime/background_runtime_engine.py` + canonical pipeline | [execution.md](capabilities/execution.md) |
| 2 | Replay | `replay/` | [replay.md](capabilities/replay.md) |
| 3 | Recovery | `recovery/` + `intelligence/context_aware_recovery.py` | [recovery.md](capabilities/recovery.md) |
| 4 | Ledger | `ledger/runtime_truth_ledger.py` | [ledger.md](capabilities/ledger.md) |
| 5 | Observability | `observability/` | [observability.md](capabilities/observability.md) |
| 6 | Health | `observability/health_monitor.py` + `hardening/dependency_monitor.py` | [health.md](capabilities/health.md) |
| 7 | Scheduling | `runtime/execution_scheduler.py` + `capabilities/task_queue.py` | [scheduling.md](capabilities/scheduling.md) |
| 8 | Alert | `capabilities/alert_pipeline.py` | [alert.md](capabilities/alert.md) |
| 9 | Timeline | `capabilities/situation_timeline.py` + `operator_actions.py` | [timeline.md](capabilities/timeline.md) |
| 10 | Telemetry | `observability/runtime_metrics.py` + `hardening/runtime_diagnostics.py` | [telemetry.md](capabilities/telemetry.md) |

## Generic operational capability modules (Phase 2)

These thirteen modules under `capabilities/` are the building blocks the
capabilities above are assembled from:

| Module | Purpose | Authority boundary |
|--------|---------|--------------------|
| `event_ingestion` | Normalise + submit inbound work | Intake only; never executes |
| `mission_context` | Named scoped context envelopes | Tagging/grouping only |
| `task_queue` | Persisted priority queue | Ordering of pending work |
| `execution_priority` | Rule-based priority scoring | Advisory score only |
| `resource_allocation` | Abstract resource pools | Accounting only |
| `operator_actions` | Operator intervention log | Record only |
| `situation_timeline` | Time-ordered significant events | Record only |
| `alert_pipeline` | Raise/route/ack alerts | Classify + track; no remediation |
| `decision_recommendation` | Advisory recommendations | Advisory only; no autonomous action |
| `sensor_abstraction` | Uniform source interface | Read sources only |
| `external_adapter` | External system bridge | Translate; isolate failures |
| `operational_contracts` | Schema enforcement | Validate shape only |
| `execution_audit_chain` | Tamper-evident audit chain | Append + verify only |

## Attachment rules (apply to all capabilities)

1. A capability MUST NOT modify `background_runtime_engine.py` to attach.
2. Cross-task analytics attach as **post-processors** via
   `engine.register_post_processor`.
3. Read surfaces are exposed through `OperationalRuntimeService` + the
   `/api/operations/*` API, never by reaching into engine internals.
4. Capabilities MUST be domain-agnostic and side-effect-isolated (a failing
   capability cannot crash execution; the engine wraps post-processors in
   guarded try/except).
5. Persistence uses the canonical append-only / JSON conventions already in
   the repo — no new storage engines.
