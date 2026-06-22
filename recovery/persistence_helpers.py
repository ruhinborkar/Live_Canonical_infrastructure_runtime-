"""Shared recovery analysis and recovery-log persistence."""

from datetime import datetime, timezone
from typing import Any

from persistence.append_only_store import AppendOnlyStore

RUNTIME_EVENT_TYPES = frozenset(
    {"NORMAL_EVENT", "CORRUPTED_EVENT", "INTERRUPTED_EVENT"}
)


def filter_runtime_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if event.get("event_type") in RUNTIME_EVENT_TYPES
    ]


def duplicate_sequences(sequence_ids: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: list[int] = []
    for sequence_id in sequence_ids:
        if sequence_id in seen:
            duplicates.append(sequence_id)
        seen.add(sequence_id)
    return duplicates


def missing_sequences(sequence_ids: list[int]) -> list[int]:
    if not sequence_ids:
        return []
    expected = set(range(sequence_ids[0], sequence_ids[-1] + 1))
    actual = set(sequence_ids)
    return sorted(expected - actual)


def interrupted_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event for event in events if event.get("event_type") == "INTERRUPTED_EVENT"
    ]


def compute_resume_point(
    missing: list[int],
    interrupted: list[dict[str, Any]],
) -> int | None:
    if missing:
        return missing[0]
    if interrupted:
        return interrupted[0].get("sequence_id")
    return None


def analyze_recovery_state(
    events: list[dict[str, Any]],
    *,
    include_duplicates: bool = False,
) -> dict[str, Any]:
    runtime_events = filter_runtime_events(events)
    sequence_ids = sorted(
        event["sequence_id"]
        for event in runtime_events
        if event.get("sequence_id") is not None
    )

    gaps = missing_sequences(sequence_ids)
    duplicates = duplicate_sequences(sequence_ids) if include_duplicates else []
    interrupted = interrupted_events(runtime_events)

    recovery_required = (
        len(interrupted) > 0
        or len(gaps) > 0
        or (include_duplicates and len(duplicates) > 0)
    )

    resume_point = compute_resume_point(gaps, interrupted)
    recovery_status = (
        "RECOVERY_REQUIRED" if recovery_required else "RECOVERY_NOT_REQUIRED"
    )

    return {
        "recovery_required": recovery_required,
        "interrupted_events": len(interrupted),
        "missing_sequences": gaps,
        "duplicate_sequences": duplicates,
        "resume_point": resume_point,
        "recovery_outcome": recovery_status,
        "recovery_status": recovery_status,
    }


def persist_recovery_log(
    events: list[dict[str, Any]],
    recovery_result: dict[str, Any],
    *,
    clear_log: bool = True,
    validation_reason: str = "execution interrupted",
) -> None:
    if clear_log:
        AppendOnlyStore.clear_log(AppendOnlyStore.RECOVERY_LOG)

    for event in interrupted_events(events):
        AppendOnlyStore.append_event(
            AppendOnlyStore.RECOVERY_LOG,
            {
                "event_timestamp": event.get(
                    "event_timestamp",
                    datetime.now(timezone.utc).isoformat(),
                ),
                "event_type": "RECOVERY_CANDIDATE",
                "sequence_id": event.get("sequence_id"),
                "trace_id": event.get("trace_id"),
                "runtime_state": event.get("runtime_state", "INTERRUPTED"),
                "payload": event.get("payload", {}),
                "validation_status": "INVALID",
                "validation_reason": validation_reason,
                "recovery_status": "PENDING",
            },
        )

    integrity_state = (
        "COMPROMISED" if recovery_result.get("recovery_required") else "INTACT"
    )
    recovery_status = recovery_result.get(
        "recovery_status",
        recovery_result.get("recovery_outcome", "UNKNOWN"),
    )

    validation_row: dict[str, Any] = {
        "event_type": "RECOVERY_VALIDATION",
        "recovery_status": recovery_status,
        "integrity_state": integrity_state,
        "interrupted_events": recovery_result.get("interrupted_events"),
        "missing_sequences": recovery_result.get("missing_sequences", []),
        "resume_point": recovery_result.get("resume_point"),
        "validation_status": (
            "INVALID" if recovery_result.get("recovery_required") else "VALID"
        ),
        "validation_reason": recovery_result.get(
            "recovery_outcome", recovery_status
        ),
    }

    if recovery_result.get("duplicate_sequences") is not None:
        validation_row["duplicate_sequences"] = recovery_result["duplicate_sequences"]

    AppendOnlyStore.append_event(AppendOnlyStore.RECOVERY_LOG, validation_row)
