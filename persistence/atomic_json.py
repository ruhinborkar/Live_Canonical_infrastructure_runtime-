"""Atomic, lock-tolerant JSON persistence helper.

Writes to a temporary file then atomically replaces the target, so readers
never observe a partially-written file. Tolerates transient Windows file locks
(another process momentarily holding the file) with a short bounded retry; on
persistent contention it degrades to best-effort rather than crashing the
caller, because the operational state is rewritten frequently.
"""

import json
import os
import time
from pathlib import Path
from typing import Any

_RETRIES = 5
_RETRY_DELAY = 0.05


def write_json_atomic(path: Path, data: Any, *, indent: int | None = 2) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    payload = json.dumps(data, indent=indent)
    for attempt in range(_RETRIES):
        try:
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, path)
            return True
        except (PermissionError, OSError):
            if attempt == _RETRIES - 1:
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
                return False
            time.sleep(_RETRY_DELAY)
    return False
