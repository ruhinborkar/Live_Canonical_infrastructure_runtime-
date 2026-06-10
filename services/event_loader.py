import json
from pathlib import Path
from typing import Any

from persistence.append_only_store import AppendOnlyStore

LOG_PATHS = {
    "live": AppendOnlyStore.LIVE_LOG,
    "replay": AppendOnlyStore.REPLAY_LOG,
    "recovery": AppendOnlyStore.RECOVERY_LOG,
}


def _read_log(file_path: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    try:
        with open(file_path, encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    except FileNotFoundError:
        pass
    return events


def _event_stats(events: list[dict[str, Any]]) -> dict[str, int]:
    valid = sum(1 for e in events if e.get("validation_status") == "VALID")
    invalid = sum(1 for e in events if e.get("validation_status") == "INVALID")
    validation_rows = sum(
        1
        for e in events
        if e.get("event_type") in ("REPLAY_VALIDATION", "RECOVERY_VALIDATION")
    )
    return {
        "total": len(events),
        "valid": valid,
        "invalid": invalid,
        "validation_rows": validation_rows,
    }


def _matches_search(event: dict[str, Any], query: str) -> bool:
    q = query.lower()
    haystack = " ".join(
        str(event.get(field, ""))
        for field in (
            "trace_id",
            "sequence_id",
            "event_type",
            "runtime_state",
            "validation_reason",
            "recovery_status",
        )
    ).lower()
    return q in haystack


_CATEGORY_MAP = {
    "normal": "NORMAL_EVENT",
    "corrupted": "CORRUPTED_EVENT",
    "interrupted": "INTERRUPTED_EVENT",
}


def load_events(
    log: str = "live",
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    search: str | None = None,
    event_type: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    file_path = LOG_PATHS.get(log, AppendOnlyStore.LIVE_LOG)
    all_events = _read_log(file_path)
    stats = _event_stats(all_events)

    filtered = all_events
    if status in ("VALID", "INVALID"):
        filtered = [e for e in filtered if e.get("validation_status") == status]
    if category and category in _CATEGORY_MAP:
        cat_type = _CATEGORY_MAP[category]
        filtered = [e for e in filtered if e.get("event_type") == cat_type]
    elif event_type:
        filtered = [e for e in filtered if e.get("event_type") == event_type]
    if search and search.strip():
        filtered = [e for e in filtered if _matches_search(e, search.strip())]

    page = filtered[offset : offset + limit]
    return {
        "log": log,
        "total": len(all_events),
        "filtered_total": len(filtered),
        "offset": offset,
        "limit": limit,
        "stats": stats,
        "events": page,
    }


def load_event_summary() -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for log_name, file_path in LOG_PATHS.items():
        events = _read_log(file_path)
        summary[log_name] = {
            **_event_stats(events),
            "file": file_path,
            "exists": Path(file_path).exists(),
        }
    return {"logs": summary}
