"""Hash-chained execution audit log.

Each entry is linked to the previous via a chained hash, giving a
tamper-evident record of every executed task.
Inputs: audit records from the engine processor.
Outputs: verifiable chain for compliance / forensics.
Dependencies: hashing.runtime_hasher, serialization.canonical_serializer.
"""

import threading
from datetime import datetime, timezone
from typing import Any

from hashing.runtime_hasher import RuntimeHasher
from persistence.append_only_store import AppendOnlyStore
from serialization.canonical_serializer import CanonicalSerializer
from services.event_loader import read_log_events

AUDIT_LOG = "logging/logs/execution_audit_chain.jsonl"
GENESIS_HASH = "0" * 64


class ExecutionAuditChain:
    _lock = threading.RLock()
    _last_hash: str | None = None

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _load_last_hash(cls) -> str:
        if cls._last_hash is not None:
            return cls._last_hash
        entries = read_log_events(AUDIT_LOG)
        cls._last_hash = entries[-1]["entry_hash"] if entries else GENESIS_HASH
        return cls._last_hash

    @classmethod
    def append(cls, action: str, record: dict[str, Any]) -> dict[str, Any]:
        with cls._lock:
            previous_hash = cls._load_last_hash()
            body = {
                "timestamp": cls._now(),
                "action": action,
                "record": record,
                "previous_hash": previous_hash,
            }
            entry_hash = RuntimeHasher.generate_hash(CanonicalSerializer.serialize(body))
            entry = {**body, "entry_hash": entry_hash}
            AppendOnlyStore.append_event(AUDIT_LOG, entry)
            cls._last_hash = entry_hash
            return entry

    @classmethod
    def verify(cls) -> dict[str, Any]:
        """Recompute the chain and confirm integrity."""
        entries = read_log_events(AUDIT_LOG)
        previous_hash = GENESIS_HASH
        broken_at = None
        for index, entry in enumerate(entries):
            body = {
                "timestamp": entry.get("timestamp"),
                "action": entry.get("action"),
                "record": entry.get("record"),
                "previous_hash": entry.get("previous_hash"),
            }
            expected = RuntimeHasher.generate_hash(CanonicalSerializer.serialize(body))
            if entry.get("previous_hash") != previous_hash or entry.get("entry_hash") != expected:
                broken_at = index
                break
            previous_hash = entry["entry_hash"]
        return {
            "entries": len(entries),
            "intact": broken_at is None,
            "broken_at": broken_at,
            "head_hash": previous_hash,
        }

    @classmethod
    def tail(cls, limit: int = 50) -> list[dict[str, Any]]:
        return list(reversed(read_log_events(AUDIT_LOG)[-limit:]))

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._last_hash = None
