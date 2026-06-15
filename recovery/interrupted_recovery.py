from datetime import datetime, timezone
from typing import Any

from persistence.append_only_store import AppendOnlyStore
from recovery.recovery_proof import RecoveryProofExporter
from services.event_loader import read_log_events

_RUNTIME_EVENT_TYPES = frozenset(
    {"NORMAL_EVENT", "CORRUPTED_EVENT", "INTERRUPTED_EVENT"}
)


class InterruptedRecovery:
    @classmethod
    def analyze_interruption(cls) -> dict[str, Any]:
        live_events = read_log_events(AppendOnlyStore.LIVE_LOG)

        runtime_events = [
            event
            for event in live_events
            if event.get("event_type") in _RUNTIME_EVENT_TYPES
        ]

        sequence_ids = sorted(
            event["sequence_id"]
            for event in runtime_events
            if event.get("sequence_id") is not None
        )

        missing_sequences: list[int] = []
        if sequence_ids:
            expected = set(range(sequence_ids[0], sequence_ids[-1] + 1))
            actual = set(sequence_ids)
            missing_sequences = sorted(expected - actual)

        duplicate_sequences = _duplicate_sequences(sequence_ids)

        interrupted_events = [
            event
            for event in runtime_events
            if event.get("event_type") == "INTERRUPTED_EVENT"
        ]

        broken_sequence_continuity = len(missing_sequences) > 0
        execution_interrupted = (
            broken_sequence_continuity
            or len(duplicate_sequences) > 0
            or len(interrupted_events) > 0
        )

        resume_point = None
        if missing_sequences:
            resume_point = missing_sequences[0]
        elif interrupted_events:
            resume_point = interrupted_events[0].get("sequence_id")

        recovery_outcome = (
            "RECOVERY_REQUIRED" if execution_interrupted else "RECOVERY_NOT_REQUIRED"
        )

        result = {
            "execution_interrupted": execution_interrupted,
            "broken_sequence_continuity": broken_sequence_continuity,
            "missing_sequences": missing_sequences,
            "duplicate_sequences": duplicate_sequences,
            "interrupted_events": len(interrupted_events),
            "resume_point": resume_point,
            "recovery_outcome": recovery_outcome,
        }

        cls._persist_analysis(runtime_events, result)
        RecoveryProofExporter.export(result, live_events=runtime_events)

        return result

    @classmethod
    def _persist_analysis(
        cls,
        live_events: list[dict[str, Any]],
        result: dict[str, Any],
    ) -> None:
        AppendOnlyStore.clear_log(AppendOnlyStore.RECOVERY_LOG)

        interrupted = [
            event
            for event in live_events
            if event.get("event_type") == "INTERRUPTED_EVENT"
        ]

        for event in interrupted:
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
                    "validation_reason": "interrupted execution",
                    "recovery_status": "PENDING",
                },
            )

        integrity_state = (
            "COMPROMISED" if result["execution_interrupted"] else "INTACT"
        )

        AppendOnlyStore.append_event(
            AppendOnlyStore.RECOVERY_LOG,
            {
                "event_type": "RECOVERY_VALIDATION",
                "recovery_status": result["recovery_outcome"],
                "integrity_state": integrity_state,
                "missing_sequences": result["missing_sequences"],
                "duplicate_sequences": result["duplicate_sequences"],
                "interrupted_events": result["interrupted_events"],
                "resume_point": result["resume_point"],
                "validation_status": (
                    "INVALID" if result["execution_interrupted"] else "VALID"
                ),
                "validation_reason": result["recovery_outcome"],
            },
        )


def _duplicate_sequences(sequence_ids: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: list[int] = []
    for sequence_id in sequence_ids:
        if sequence_id in seen:
            duplicates.append(sequence_id)
        seen.add(sequence_id)
    return duplicates
