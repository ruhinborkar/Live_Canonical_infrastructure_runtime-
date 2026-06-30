"""Execution scheduler.

Decides which queued task runs next. Ordering authority only: it pulls the
highest-priority pending task from the task queue and hands it to a worker.
It never executes work itself and holds no business logic.
"""

import threading
from typing import Any

from capabilities.task_queue import TaskQueue


class ExecutionScheduler:
    _lock = threading.RLock()
    _dispatched = 0

    @classmethod
    def next_task(cls) -> dict[str, Any] | None:
        with cls._lock:
            task = TaskQueue.next_task()
            if task is not None:
                cls._dispatched += 1
            return task

    @classmethod
    def requeue(cls, task: dict[str, Any]) -> None:
        TaskQueue.requeue(task)

    @classmethod
    def stats(cls) -> dict[str, Any]:
        with cls._lock:
            return {
                "dispatched": cls._dispatched,
                "pending": TaskQueue.pending(),
            }

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._dispatched = 0
