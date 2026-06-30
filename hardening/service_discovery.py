"""Service discovery registry.

A lightweight in-process registry of operational services/capabilities and
their endpoints so the runtime (and dashboard) can enumerate what is attached
and reachable. Generic — no external coordination service required.
"""

import threading
from datetime import datetime, timezone
from typing import Any


class ServiceDiscovery:
    _lock = threading.RLock()
    _services: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, *, kind: str, endpoint: str | None = None, healthy: bool = True) -> dict[str, Any]:
        with cls._lock:
            cls._services[name] = {
                "name": name,
                "kind": kind,
                "endpoint": endpoint,
                "healthy": healthy,
                "registered_at": datetime.now(timezone.utc).isoformat(),
            }
            return cls._services[name]

    @classmethod
    def set_health(cls, name: str, healthy: bool) -> None:
        with cls._lock:
            if name in cls._services:
                cls._services[name]["healthy"] = healthy

    @classmethod
    def registry(cls) -> list[dict[str, Any]]:
        with cls._lock:
            return list(cls._services.values())

    @classmethod
    def healthy_count(cls) -> tuple[int, int]:
        with cls._lock:
            total = len(cls._services)
            healthy = sum(1 for s in cls._services.values() if s["healthy"])
            return healthy, total

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._services = {}
