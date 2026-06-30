"""Generic, persisted priority task queue.

Inputs: tasks (payload + priority) submitted by any producer.
Outputs: ordered tasks for the execution scheduler.
Authority: owns pending-work ordering only; never executes work itself.
Persistence: data/runtime_queue.json so pending work survives restarts.
"""

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from persistence.atomic_json import write_json_atomic

QUEUE_FILE = Path("data/runtime_queue.json")


class TaskQueue:
    _lock = threading.RLock()
    _tasks: list[dict[str, Any]] = []
    _loaded = False

    @classmethod
    def _now(cls) -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._loaded:
            return
        cls.restore()

    @classmethod
    def restore(cls) -> int:
        """Reload pending tasks from disk (used by restart recovery)."""
        with cls._lock:
            cls._tasks = []
            if QUEUE_FILE.exists():
                try:
                    data = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
                    cls._tasks = [t for t in data.get("tasks", []) if t.get("status") == "PENDING"]
                except (json.JSONDecodeError, OSError):
                    cls._tasks = []
            cls._loaded = True
            return len(cls._tasks)

    @classmethod
    def _persist(cls) -> None:
        write_json_atomic(QUEUE_FILE, {"tasks": cls._tasks, "updated_at": cls._now()})

    @classmethod
    def enqueue(cls, payload: dict[str, Any], *, priority: int = 5, source: str = "api") -> dict[str, Any]:
        """Add a task. Lower priority value = higher urgency (1 highest)."""
        cls._ensure_loaded()
        with cls._lock:
            task = {
                "task_id": str(uuid.uuid4()),
                "priority": int(priority),
                "payload": payload,
                "source": source,
                "status": "PENDING",
                "enqueued_at": cls._now(),
            }
            cls._tasks.append(task)
            cls._persist()
            return task

    @classmethod
    def next_task(cls) -> dict[str, Any] | None:
        """Pop the highest-priority, earliest-enqueued pending task."""
        cls._ensure_loaded()
        with cls._lock:
            if not cls._tasks:
                return None
            cls._tasks.sort(key=lambda t: (t["priority"], t["enqueued_at"]))
            task = cls._tasks.pop(0)
            cls._persist()
            return task

    @classmethod
    def requeue(cls, task: dict[str, Any]) -> None:
        cls._ensure_loaded()
        with cls._lock:
            task["status"] = "PENDING"
            cls._tasks.append(task)
            cls._persist()

    @classmethod
    def pending(cls) -> int:
        cls._ensure_loaded()
        with cls._lock:
            return len(cls._tasks)

    @classmethod
    def snapshot(cls, limit: int = 50) -> dict[str, Any]:
        cls._ensure_loaded()
        with cls._lock:
            ordered = sorted(cls._tasks, key=lambda t: (t["priority"], t["enqueued_at"]))
            return {
                "pending": len(cls._tasks),
                "tasks": [
                    {
                        "task_id": t["task_id"],
                        "priority": t["priority"],
                        "source": t.get("source"),
                        "enqueued_at": t["enqueued_at"],
                        "event_type": (t.get("payload") or {}).get("event_type"),
                    }
                    for t in ordered[:limit]
                ],
            }

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._tasks = []
            cls._loaded = True
            cls._persist()
