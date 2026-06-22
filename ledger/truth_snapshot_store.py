"""Append-only immutable execution-state snapshot store."""

from typing import Any

from persistence.append_only_store import AppendOnlyStore
from services.event_loader import read_log_events

LEDGER_FILE = "logging/truth_ledger/truth_snapshots.jsonl"


class TruthSnapshotStore:
    @classmethod
    def append_snapshot(cls, snapshot: dict[str, Any]) -> None:
        AppendOnlyStore.append_event(LEDGER_FILE, snapshot)

    @classmethod
    def read_all(cls) -> list[dict[str, Any]]:
        return read_log_events(LEDGER_FILE)

    @classmethod
    def clear(cls) -> None:
        AppendOnlyStore.clear_log(LEDGER_FILE)

    @classmethod
    def count(cls) -> int:
        return len(cls.read_all())
