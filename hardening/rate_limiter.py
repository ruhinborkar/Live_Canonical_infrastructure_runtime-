"""Token-bucket rate limiter.

Generic per-key rate limiting to protect ingestion from floods. A limit of 0
means unlimited. Thread-safe; used by the ingestion API surface.
"""

import threading
import time
from typing import Any


class RateLimiter:
    _lock = threading.RLock()
    _buckets: dict[str, dict[str, float]] = {}

    @classmethod
    def allow(cls, key: str, *, limit_per_minute: int) -> bool:
        if limit_per_minute <= 0:
            return True
        now = time.time()
        with cls._lock:
            bucket = cls._buckets.setdefault(
                key, {"tokens": float(limit_per_minute), "updated": now, "limit": limit_per_minute}
            )
            elapsed = now - bucket["updated"]
            refill = elapsed * (limit_per_minute / 60.0)
            bucket["tokens"] = min(limit_per_minute, bucket["tokens"] + refill)
            bucket["updated"] = now
            bucket["limit"] = limit_per_minute
            if bucket["tokens"] >= 1.0:
                bucket["tokens"] -= 1.0
                return True
            return False

    @classmethod
    def status(cls) -> list[dict[str, Any]]:
        with cls._lock:
            return [
                {"key": key, "tokens": round(b["tokens"], 2), "limit": b.get("limit")}
                for key, b in cls._buckets.items()
            ]

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._buckets = {}
