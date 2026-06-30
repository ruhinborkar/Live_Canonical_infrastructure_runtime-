"""Worker lifecycle management.

Owns a pool of worker threads. Each worker continuously asks the scheduler
for the next task and processes it via the injected processor callback until
the pool is asked to drain. Tracks per-worker liveness for observability.
"""

import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable

from runtime.execution_scheduler import ExecutionScheduler

Processor = Callable[[dict[str, Any]], dict[str, Any]]

IDLE_SLEEP_SECONDS = 0.2


class WorkerLifecycle:
    def __init__(self, processor: Processor, worker_count: int = 2) -> None:
        self._processor = processor
        self._worker_count = max(1, worker_count)
        self._threads: list[threading.Thread] = []
        self._stop = threading.Event()
        self._drain = threading.Event()
        self._status: dict[str, dict[str, Any]] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _worker_loop(self, name: str) -> None:
        while not self._stop.is_set():
            task = ExecutionScheduler.next_task()
            if task is None:
                if self._drain.is_set():
                    break
                self._mark(name, "IDLE", None)
                time.sleep(IDLE_SLEEP_SECONDS)
                continue
            self._mark(name, "PROCESSING", task.get("task_id"))
            try:
                self._processor(task)
            except Exception as exc:  # noqa: BLE001 - workers must never crash the pool
                self._mark(name, "ERROR", task.get("task_id"), error=str(exc))
        self._mark(name, "STOPPED", None)

    def _mark(self, name: str, state: str, task_id: str | None, error: str | None = None) -> None:
        with self._lock:
            self._status[name] = {
                "worker": name,
                "state": state,
                "task_id": task_id,
                "error": error,
                "updated_at": self._now(),
            }

    def start(self) -> None:
        self._stop.clear()
        self._drain.clear()
        self._threads = []
        for index in range(self._worker_count):
            name = f"worker-{index + 1}"
            thread = threading.Thread(target=self._worker_loop, args=(name,), name=name, daemon=True)
            self._threads.append(thread)
            self._mark(name, "STARTING", None)
            thread.start()

    def drain_and_stop(self, timeout: float = 10.0) -> None:
        """Stop accepting new idle waits; let in-flight tasks finish."""
        self._drain.set()
        deadline = time.time() + timeout
        while time.time() < deadline and ExecutionScheduler.stats()["pending"] > 0:
            time.sleep(0.1)
        self._stop.set()
        for thread in self._threads:
            thread.join(timeout=2.0)

    def stop_now(self) -> None:
        self._stop.set()
        for thread in self._threads:
            thread.join(timeout=2.0)

    @property
    def worker_count(self) -> int:
        return self._worker_count

    def status(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._status.values())

    def alive(self) -> int:
        return sum(1 for t in self._threads if t.is_alive())
