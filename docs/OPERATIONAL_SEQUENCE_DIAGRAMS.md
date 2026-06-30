# Operational Sequence Diagrams

Mermaid sequence diagrams for the core operational flows. They render on
GitHub and in any Mermaid-aware viewer.

## 1. Runtime startup + restart recovery

```mermaid
sequenceDiagram
    participant Host as Process / Container
    participant API as FastAPI startup
    participant SVC as OperationalRuntimeService
    participant ENG as BackgroundRuntimeEngine
    participant RR as RestartRecovery
    participant SM as OperationalStateManager
    participant HB as Heartbeat
    participant WL as WorkerLifecycle

    Host->>API: start uvicorn
    API->>SVC: boot()
    SVC->>ENG: start(workers, interval)
    ENG->>RR: recover()
    RR->>SM: load() prior state
    RR->>RR: detect unclean shutdown + restore queue
    ENG->>SM: transition(STARTING)
    ENG->>HB: start()
    ENG->>WL: start() (N workers)
    ENG->>SM: transition(RUNNING)
    ENG-->>SVC: status(RUNNING)
```

## 2. Continuous work execution

```mermaid
sequenceDiagram
    participant OP as Operator / Sensor / API
    participant SVC as OperationalRuntimeService
    participant Q as TaskQueue
    participant SCH as ExecutionScheduler
    participant W as Worker
    participant PIPE as Canonical Pipeline
    participant CAP as Capabilities + Intelligence

    OP->>SVC: submit_work(payload)
    SVC->>Q: enqueue(priority)
    loop until stopped
        W->>SCH: next_task()
        SCH->>Q: pop highest priority
        SCH-->>W: task
        W->>PIPE: validate→serialize→hash→persist→ledger
        W->>CAP: timeline, audit chain, alerts, confidence
    end
```

## 3. Heartbeat + readiness

```mermaid
sequenceDiagram
    participant HB as Heartbeat thread
    participant SM as State Manager
    participant RS as ReadinessScore
    participant DASH as Dashboard

    loop every interval
        HB->>SM: record_heartbeat(tick++)
    end
    DASH->>RS: GET /api/operations/readiness
    RS->>SM: liveness + state
    RS-->>DASH: score/10 + contributors
```

## 4. Graceful shutdown

```mermaid
sequenceDiagram
    participant OS as Signal / API
    participant GS as GracefulShutdown
    participant ENG as Engine
    participant WL as Workers
    participant SM as State Manager

    OS->>GS: SIGINT / SIGTERM / stop()
    GS->>ENG: stop(graceful=True)
    ENG->>SM: transition(STOPPING)
    ENG->>WL: drain_and_stop() (finish in-flight)
    ENG->>SM: transition(STOPPED, clean=True)
```
