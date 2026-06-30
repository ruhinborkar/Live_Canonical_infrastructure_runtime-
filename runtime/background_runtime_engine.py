"""Background runtime engine — the operational spine.

Lifecycle:
    start -> restart recovery -> STARTING -> heartbeat + workers -> RUNNING
    submit(work) -> task queue -> scheduler -> worker -> canonical pipeline
    stop -> STOPPING -> drain workers -> STOPPED (clean)

The engine continuously processes queued work, validating, serialising,
hashing, persisting, and ledger-recording each event using the EXISTING
canonical primitives (no duplication), while emitting timeline, audit-chain,
and alert signals through the capability layer. It runs until intentionally
stopped.

Extensibility: register_post_processor() lets capability/intelligence modules
attach per-task analysis without modifying this core.
"""

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from capabilities.alert_pipeline import AlertPipeline
from capabilities.execution_audit_chain import ExecutionAuditChain
from capabilities.mission_context import MissionContext
from capabilities.situation_timeline import SituationTimeline
from capabilities.task_queue import TaskQueue
from hashing.runtime_hasher import RuntimeHasher
from ledger.runtime_truth_ledger import RuntimeTruthLedger
from persistence.append_only_store import AppendOnlyStore
from runtime.execution_scheduler import ExecutionScheduler
from runtime.graceful_shutdown import GracefulShutdown
from runtime.operational_state_manager import OperationalStateManager
from runtime.restart_recovery import RestartRecovery
from runtime.runtime_heartbeat import RuntimeHeartbeat
from runtime.worker_lifecycle import WorkerLifecycle
from serialization.canonical_serializer import CanonicalSerializer
from validation.runtime_validator import RuntimeValidator

PostProcessor = Callable[[dict[str, Any], dict[str, Any]], None]


class BackgroundRuntimeEngine:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._heartbeat: RuntimeHeartbeat | None = None
        self._workers: WorkerLifecycle | None = None
        self._post_processors: list[PostProcessor] = []
        self._last_recovery: dict[str, Any] = {}
        self._sequence_counter = 0
        self._session_trace = f"session-{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def register_post_processor(self, processor: PostProcessor) -> None:
        with self._lock:
            if processor not in self._post_processors:
                self._post_processors.append(processor)

    # ----- lifecycle -------------------------------------------------------
    def start(self, *, worker_count: int = 2, heartbeat_interval: float = 1.0) -> dict[str, Any]:
        with self._lock:
            # Instance-scoped guard: only skip if THIS engine instance already
            # has live workers. A fresh process whose persisted state still says
            # RUNNING is precisely the unclean-restart case and must recover.
            if self._workers is not None and self._workers.alive() > 0:
                return self.status()

            self._last_recovery = RestartRecovery.recover()
            self._session_trace = f"session-{uuid.uuid4().hex[:8]}"
            self._sequence_counter = 0
            OperationalStateManager.transition("STARTING")
            SituationTimeline.record(
                "RUNTIME",
                "Runtime engine starting",
                details={"recovery": self._last_recovery},
            )

            MissionContext.ensure_default()

            self._heartbeat = RuntimeHeartbeat(heartbeat_interval)
            self._heartbeat.start()

            self._workers = WorkerLifecycle(self._process_task, worker_count=worker_count)
            self._workers.start()

            GracefulShutdown.register(self._on_signal_stop)

            OperationalStateManager.transition("RUNNING")
            SituationTimeline.record("RUNTIME", "Runtime engine operational", severity="INFO")
            return self.status()

    def _on_signal_stop(self) -> None:
        try:
            self.stop(graceful=True)
        except Exception:  # noqa: BLE001
            pass

    def stop(self, *, graceful: bool = True) -> dict[str, Any]:
        with self._lock:
            if OperationalStateManager.current_state() in {"STOPPED"}:
                return self.status()
            OperationalStateManager.transition("STOPPING")
            SituationTimeline.record("RUNTIME", "Runtime engine stopping", severity="WARNING")
            if self._workers:
                if graceful:
                    self._workers.drain_and_stop()
                else:
                    self._workers.stop_now()
            if self._heartbeat:
                self._heartbeat.stop()
            OperationalStateManager.transition("STOPPED", stopped_cleanly=True)
            SituationTimeline.record("RUNTIME", "Runtime engine stopped", severity="INFO")
            return self.status()

    def is_running(self) -> bool:
        return OperationalStateManager.current_state() in {"RUNNING", "DEGRADED"}

    # ----- work intake -----------------------------------------------------
    def submit(self, event: dict[str, Any], *, priority: int = 5, source: str = "api") -> dict[str, Any]:
        context = MissionContext.ensure_default()
        enriched = dict(event)
        enriched.setdefault("event_type", "NORMAL_EVENT")
        enriched.setdefault("runtime_state", "OPERATIONAL")
        enriched["context_id"] = context["context_id"]
        # Assign a contiguous monotonic sequence within a stable per-session
        # trace when the caller did not supply its own. This keeps lineage
        # coherent and avoids spurious per-trace sequence-gap anomalies.
        with self._lock:
            if enriched.get("sequence_id") is None:
                self._sequence_counter += 1
                enriched["sequence_id"] = self._sequence_counter
                enriched.setdefault("trace_id", self._session_trace)
            else:
                enriched.setdefault("trace_id", f"trace-{enriched['sequence_id']}")
        task = TaskQueue.enqueue(enriched, priority=priority, source=source)
        OperationalStateManager.increment("tasks_accepted")
        SituationTimeline.record(
            "INGESTION",
            f"Work accepted (priority {priority})",
            details={"task_id": task["task_id"], "event_type": enriched.get("event_type")},
        )
        return task

    # ----- processing ------------------------------------------------------
    def _process_task(self, task: dict[str, Any]) -> dict[str, Any]:
        event = dict(task.get("payload", {}))
        validation = RuntimeValidator.validate(event)
        serialized = CanonicalSerializer.serialize(event.get("payload", {}))
        payload_hash = RuntimeHasher.generate_hash(serialized)

        runtime_event = dict(event)
        runtime_event["payload_hash"] = payload_hash
        runtime_event["validation_status"] = "VALID" if validation["valid"] else "INVALID"
        runtime_event["validation_reason"] = validation["reason"]
        runtime_event["processed_at"] = self._now()
        runtime_event["task_id"] = task.get("task_id")

        AppendOnlyStore.append_event(AppendOnlyStore.LIVE_LOG, runtime_event)
        RuntimeTruthLedger.record_snapshot(
            runtime_event,
            validation_status=runtime_event["validation_status"],
            payload_hash=payload_hash,
        )
        ExecutionAuditChain.append(
            "TASK_EXECUTED",
            {
                "task_id": task.get("task_id"),
                "sequence_id": runtime_event.get("sequence_id"),
                "validation_status": runtime_event["validation_status"],
                "payload_hash": payload_hash,
            },
        )

        if validation["valid"]:
            OperationalStateManager.increment("tasks_completed")
        else:
            OperationalStateManager.increment("tasks_invalid")
            AlertPipeline.raise_alert(
                "runtime_engine",
                f"Invalid event rejected: {validation['reason']}",
                severity="WARNING",
                context={"task_id": task.get("task_id"), "sequence_id": runtime_event.get("sequence_id")},
            )
            SituationTimeline.record(
                "VALIDATION",
                f"Invalid event ({validation['reason']})",
                severity="WARNING",
                details={"task_id": task.get("task_id")},
            )

        result = {"task": task, "event": runtime_event, "validation": validation}
        for post in list(self._post_processors):
            try:
                post(runtime_event, result)
            except Exception:  # noqa: BLE001 - analytics must not break execution
                continue
        return result

    # ----- observability ---------------------------------------------------
    def status(self) -> dict[str, Any]:
        snap = OperationalStateManager.snapshot()
        return {
            "state": snap.get("state"),
            "previous_state": snap.get("previous_state"),
            "started_at": snap.get("started_at"),
            "uptime_seconds": snap.get("uptime_seconds"),
            "stopped_cleanly": snap.get("stopped_cleanly"),
            "counters": snap.get("counters", {}),
            "heartbeat": RuntimeHeartbeat.liveness(),
            "scheduler": ExecutionScheduler.stats(),
            "queue": TaskQueue.snapshot(limit=25),
            "workers": {
                "configured": self._workers.worker_count if self._workers else 0,
                "alive": self._workers.alive() if self._workers else 0,
                "detail": self._workers.status() if self._workers else [],
            },
            "alerts": AlertPipeline.summary(),
            "active_context": MissionContext.active(),
            "last_recovery": self._last_recovery,
            "running": self.is_running(),
        }

    def drain_until_idle(self, timeout: float = 10.0) -> bool:
        """Block until the queue is empty or timeout (useful for smoke tests)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if TaskQueue.pending() == 0:
                return True
            time.sleep(0.1)
        return TaskQueue.pending() == 0


_engine: BackgroundRuntimeEngine | None = None
_engine_lock = threading.Lock()


def get_engine() -> BackgroundRuntimeEngine:
    global _engine
    with _engine_lock:
        if _engine is None:
            _engine = BackgroundRuntimeEngine()
        return _engine
