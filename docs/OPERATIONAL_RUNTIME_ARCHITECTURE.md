# Operational Runtime Architecture

This document describes how the canonical runtime platform was evolved from a
**demo / runtime-proof system** into a **continuously operating operational
runtime backbone**. It is generic, reusable, and domain-agnostic — there is no
organisation-specific, classified, or military logic anywhere in the design.

## 1. From runtime-proof to runtime backbone

| Before (runtime-proof) | After (operational backbone) |
|------------------------|------------------------------|
| One-shot batch pipeline (`RuntimeService.execute_live`) processes N events then exits | Background engine starts, accepts work continuously, and runs until intentionally stopped |
| No scheduler / workers | Priority scheduler dispatches to a managed worker pool |
| No heartbeat / liveness | Monotonic heartbeat with liveness window |
| No persisted lifecycle state | Operational state manager persists state + counters |
| Process exit = data lost | Restart recovery restores state and pending work |
| Report-style dashboard | Live command-center surfaces (state, queue, alerts, topology) |

The canonical primitives — **validation, serialization, hashing, append-only
persistence, truth ledger, replay, recovery, observability** — are reused
unchanged. The new layers wrap and continuously drive them.

## 2. Layered architecture

```
            ┌─────────────────────────────────────────────┐
            │        Command Center Dashboard (React)       │
            │  live state · queue · alerts · topology · …   │
            └───────────────▲───────────────────────────────┘
                            │  /api/operations/*  (real values)
            ┌───────────────┴───────────────────────────────┐
            │     OperationalRuntimeService (facade)         │
            └───────┬───────────────┬───────────────┬────────┘
                    │               │               │
        ┌───────────▼──┐   ┌────────▼───────┐  ┌────▼────────────┐
        │  runtime/    │   │ capabilities/  │  │ intelligence/   │
        │  ENGINE      │   │ 13 generic     │  │ 10 analytical   │
        │  (spine)     │   │ capabilities   │  │ services        │
        └───────┬──────┘   └────────────────┘  └─────────────────┘
                │ reuses (no duplication)
        ┌───────▼───────────────────────────────────────────────┐
        │ validation · serialization · hashing · persistence ·   │
        │ truth ledger · replay · recovery · observability       │
        └────────────────────────────────────────────────────────┘
                │
        ┌───────▼───────────────────────────────────────────────┐
        │ hardening/ · config/ · security/  (cross-cutting)      │
        └────────────────────────────────────────────────────────┘
```

## 3. Phase 1 — Runtime engine components

All under `runtime/`:

| Component | File | Responsibility |
|-----------|------|----------------|
| Background runtime engine | `background_runtime_engine.py` | Composition + lifecycle; the operational spine |
| Execution scheduler | `execution_scheduler.py` | Ordering authority: pulls highest-priority pending task |
| Worker lifecycle | `worker_lifecycle.py` | Managed worker thread pool, per-worker liveness |
| Runtime heartbeat | `runtime_heartbeat.py` | Monotonic tick + liveness window |
| Operational state manager | `operational_state_manager.py` | Persisted single source of truth for state + counters |
| Graceful shutdown | `graceful_shutdown.py` | Signal-driven orderly drain |
| Restart recovery | `restart_recovery.py` | Detects unclean shutdown, restores pending work |

### Lifecycle and states

`STOPPED → STARTING → RUNNING ⇄ DEGRADED → STOPPING → STOPPED`

Transitions are guarded by `intelligence/state_transition_engine.py`
(a finite-state machine) and recorded for audit.

### Target behavior (achieved)

> Runtime starts → accepts work → schedules execution → continuously processes
> events → continuously validates → continuously observes → continuously
> recovers → runs until intentionally stopped.

Proven by `python run_system.py --mode operate` (continuous) and
`--mode smoke` (automated), and by `tests/test_operational_runtime.py`.

## 4. Phase 2 — Generic capability layer (`capabilities/`)

13 reusable modules with clean interfaces that attach to the engine without
modifying it: event ingestion, mission context, task queue, execution
priority, resource allocation, operator actions, situation timeline, alert
pipeline, decision recommendation, sensor abstraction, external adapter,
operational contracts, execution audit chain. See `CAPABILITY_ARCHITECTURE.md`.

## 5. Phase 3 — Runtime intelligence layer (`intelligence/`)

10 read-mostly analytical services derived from the live event stream:
execution dependency graph, operational context graph, execution lineage,
cross-event relationships, priority propagation, state-transition engine,
context-aware recovery, execution confidence, runtime anomaly detection,
operational drift detection. They attach as engine post-processors via
`runtime_intelligence_hooks.attach()` — demonstrating extension without core
change.

## 6. Phase 4 — Command center

`backend/api/routes/operations.py` exposes live runtime values (never mock).
The React `CommandCenter` answers the three command-center questions: **what is
happening**, **what requires attention**, **what happens next**.

## 7. Phase 6 — Operational hardening

`config/`, `security/`, `hardening/` provide structured configuration,
environment profiles, secrets abstraction, structured logs, rate limiting,
graceful degradation, service discovery, dependency monitoring, runtime
diagnostics, and an explainable operational readiness score (0–10).

> Note: the structured logger lives in `hardening/structured_logger.py`, not
> `logging/`, because a top-level `logging` package would shadow Python's
> standard-library `logging` module and break the application.

## 8. Extensibility contract

A capability or intelligence service attaches in one of two ways:

1. **Post-processor** — `engine.register_post_processor(fn)`; `fn(event, result)`
   runs after each task with no engine changes.
2. **Facade method** — add a read view on `OperationalRuntimeService` and an
   endpoint in `operations.py`.

Neither path requires editing `background_runtime_engine.py`, satisfying
"capability modules can attach without changing core architecture."
