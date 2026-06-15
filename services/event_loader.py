import json

from pathlib import Path

from typing import Any



from persistence.append_only_store import AppendOnlyStore



LOG_PATHS = {

    "live": AppendOnlyStore.LIVE_LOG,

    "replay": AppendOnlyStore.REPLAY_LOG,

    "recovery": AppendOnlyStore.RECOVERY_LOG,

}



_SUMMARY_EVENT_TYPES = frozenset({"REPLAY_VALIDATION", "RECOVERY_VALIDATION"})



_CATEGORY_ALIASES = frozenset({"normal", "corrupted", "interrupted"})





def read_log_events(file_path: str) -> list[dict[str, Any]]:

    """Load all events from an append-only JSONL log."""

    return _read_log(file_path)





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

        if e.get("event_type") in _SUMMARY_EVENT_TYPES

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

            "validation_status",

        )

    ).lower()

    return q in haystack





def _normalize_category(

    category: str | None,

    event_type: str | None,

) -> str | None:

    if category in _CATEGORY_ALIASES:

        return category

    if event_type in _CATEGORY_ALIASES:

        return event_type

    return category





def _is_hash_mismatch(event: dict[str, Any]) -> bool:

    if event.get("replay_verified") is False:

        return True

    if event.get("validation_status") == "INVALID" and event.get("event_type") == "CORRUPTED_EVENT":

        return True

    return False





def _matches_category(event: dict[str, Any], category: str | None) -> bool:

    if not category or category == "all":

        return True



    event_type = str(event.get("event_type", ""))



    if event_type in _SUMMARY_EVENT_TYPES:

        return False



    if category == "normal":

        if event_type != "NORMAL_EVENT":

            return False

        if event.get("validation_status") == "INVALID":

            return False

        if event.get("replay_verified") is False:

            return False

        return True



    if category == "corrupted":

        if event_type == "CORRUPTED_EVENT":

            return True

        return _is_hash_mismatch(event)



    if category == "interrupted":

        return event_type in ("INTERRUPTED_EVENT", "RECOVERY_CANDIDATE")



    return event_type == category





def _normalize_log(log: str | None, mode: str | None = None) -> str:

    selected = (mode or log or "live").lower()

    return selected if selected in LOG_PATHS else "live"





def load_events(

    log: str = "live",

    limit: int = 50,

    offset: int = 0,

    status: str | None = None,

    search: str | None = None,

    event_type: str | None = None,

    category: str | None = None,

    mode: str | None = None,

) -> dict[str, Any]:

    log_key = _normalize_log(log, mode)

    file_path = LOG_PATHS[log_key]

    all_events = _read_log(file_path)

    stats = _event_stats(all_events)



    normalized_category = _normalize_category(category, event_type)



    filtered = all_events

    if status in ("VALID", "INVALID"):

        filtered = [e for e in filtered if e.get("validation_status") == status]

    if normalized_category:

        filtered = [

            e for e in filtered if _matches_category(e, normalized_category)

        ]

    elif event_type and event_type not in _CATEGORY_ALIASES:

        filtered = [e for e in filtered if e.get("event_type") == event_type]

    if search and search.strip():

        filtered = [e for e in filtered if _matches_search(e, search.strip())]



    page = filtered[offset : offset + limit]

    return {

        "log": log_key,

        "mode": log_key,

        "total": len(all_events),

        "filtered_total": len(filtered),

        "offset": offset,

        "limit": limit,

        "stats": stats,

        "events": page,

        "filters": {

            "status": status,

            "search": search.strip() if search else None,

            "category": normalized_category,

            "event_type": event_type,

        },

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


