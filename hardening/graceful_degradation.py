"""Graceful degradation manager.

Lets the runtime continue operating with reduced guarantees when a subsystem
is impaired, instead of failing hard. Tracks degraded subsystems and computes
an overall operational mode (NORMAL / DEGRADED / CRITICAL).
"""

import threading
from datetime import datetime, timezone
from typing import Any


class GracefulDegradation:
    _lock = threading.RLock()
    _degraded: dict[str, dict[str, Any]] = {}

    @classmethod
    def degrade(cls, subsystem: str, reason: str, *, severity: str = "DEGRADED") -> None:
        with cls._lock:
            cls._degraded[subsystem] = {
                "subsystem": subsystem,
                "reason": reason,
                "severity": severity,
                "since": datetime.now(timezone.utc).isoformat(),
            }

    @classmethod
    def restore(cls, subsystem: str) -> None:
        with cls._lock:
            cls._degraded.pop(subsystem, None)

    @classmethod
    def mode(cls) -> str:
        with cls._lock:
            if any(d["severity"] == "CRITICAL" for d in cls._degraded.values()):
                return "CRITICAL"
            if cls._degraded:
                return "DEGRADED"
            return "NORMAL"

    @classmethod
    def status(cls) -> dict[str, Any]:
        with cls._lock:
            return {
                "mode": cls.mode(),
                "degraded_subsystems": list(cls._degraded.values()),
            }

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._degraded = {}
