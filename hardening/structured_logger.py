"""Structured operational logger.

Writes structured JSON log lines to a persistent operational log so runtime
behaviour is durably recorded (not just in-memory). Respects the configured
log level. Persisted under logging/logs/operational_runtime.jsonl.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOG_FILE = Path("logging/logs/operational_runtime.jsonl")

_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


class StructuredLogger:
    _lock = threading.RLock()
    _min_level = 20

    @classmethod
    def configure(cls, level: str) -> None:
        cls._min_level = _LEVELS.get(level.upper(), 20)

    @classmethod
    def log(cls, level: str, event: str, **fields: Any) -> dict[str, Any] | None:
        rank = _LEVELS.get(level.upper(), 20)
        if rank < cls._min_level:
            return None
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "event": event,
            "fields": fields,
        }
        with cls._lock:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    @classmethod
    def info(cls, event: str, **fields: Any) -> dict[str, Any] | None:
        return cls.log("INFO", event, **fields)

    @classmethod
    def warning(cls, event: str, **fields: Any) -> dict[str, Any] | None:
        return cls.log("WARNING", event, **fields)

    @classmethod
    def error(cls, event: str, **fields: Any) -> dict[str, Any] | None:
        return cls.log("ERROR", event, **fields)

    @classmethod
    def tail(cls, limit: int = 100) -> list[dict[str, Any]]:
        if not LOG_FILE.exists():
            return []
        lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
        out = []
        for line in lines[-limit:]:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return list(reversed(out))
