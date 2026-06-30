"""Resource allocation capability.

Generic token-bucket style allocator for abstract resource pools (e.g. worker
slots, compute units, bandwidth units). Domain-agnostic; callers define pool
names. Tracks utilisation for the dashboard's resource surface.
"""

import threading
from typing import Any


class ResourceAllocation:
    _lock = threading.RLock()
    _pools: dict[str, dict[str, int]] = {}

    @classmethod
    def define_pool(cls, name: str, capacity: int) -> dict[str, Any]:
        with cls._lock:
            cls._pools[name] = {"capacity": capacity, "allocated": 0}
            return cls._pool_view(name)

    @classmethod
    def allocate(cls, name: str, amount: int = 1) -> bool:
        with cls._lock:
            pool = cls._pools.setdefault(name, {"capacity": amount, "allocated": 0})
            if pool["allocated"] + amount > pool["capacity"]:
                return False
            pool["allocated"] += amount
            return True

    @classmethod
    def release(cls, name: str, amount: int = 1) -> None:
        with cls._lock:
            pool = cls._pools.get(name)
            if pool:
                pool["allocated"] = max(0, pool["allocated"] - amount)

    @classmethod
    def _pool_view(cls, name: str) -> dict[str, Any]:
        pool = cls._pools[name]
        capacity = pool["capacity"] or 1
        return {
            "pool": name,
            "capacity": pool["capacity"],
            "allocated": pool["allocated"],
            "available": pool["capacity"] - pool["allocated"],
            "utilisation_pct": round(100 * pool["allocated"] / capacity, 1),
        }

    @classmethod
    def utilisation(cls) -> list[dict[str, Any]]:
        with cls._lock:
            return [cls._pool_view(name) for name in cls._pools]

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._pools = {}
