"""Runtime heartbeat.

Periodically proves the engine is alive by incrementing a monotonically
increasing tick and persisting the timestamp via the state manager. A stale
heartbeat (no beat within the liveness window) indicates the runtime is hung.
"""

import threading
import time
from datetime import datetime, timezone
from typing import Any

from runtime.operational_state_manager import OperationalStateManager

DEFAULT_INTERVAL_SECONDS = 1.0
LIVENESS_WINDOW_SECONDS = 5.0


class RuntimeHeartbeat:
    def __init__(self, interval_seconds: float = DEFAULT_INTERVAL_SECONDS) -> None:
        self.interval = interval_seconds
        self._tick = OperationalStateManager.snapshot().get("heartbeat_tick", 0)
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._tick += 1
            OperationalStateManager.record_heartbeat(self._tick)
            self._stop.wait(self.interval)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="runtime-heartbeat", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval * 2)

    @property
    def tick(self) -> int:
        return self._tick

    @staticmethod
    def liveness() -> dict[str, Any]:
        snap = OperationalStateManager.snapshot()
        last = snap.get("last_heartbeat_at")
        alive = False
        age = None
        if last:
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(last)).total_seconds()
                alive = age <= LIVENESS_WINDOW_SECONDS
            except ValueError:
                alive = False
        return {
            "heartbeat_tick": snap.get("heartbeat_tick", 0),
            "last_heartbeat_at": last,
            "age_seconds": round(age, 2) if age is not None else None,
            "alive": alive,
            "liveness_window_seconds": LIVENESS_WINDOW_SECONDS,
        }
