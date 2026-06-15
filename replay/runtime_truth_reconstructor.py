"""Rebuild runtime truth solely from append-only persisted execution logs."""

from typing import Any

from hashing.runtime_hasher import RuntimeHasher
from persistence.append_only_store import AppendOnlyStore
from serialization.canonical_serializer import CanonicalSerializer
from services.event_loader import read_log_events
from validation.runtime_validator import RuntimeValidator

_RUNTIME_EVENT_TYPES = frozenset(
    {"NORMAL_EVENT", "CORRUPTED_EVENT", "INTERRUPTED_EVENT"}
)


class RuntimeTruthReconstructor:
    @classmethod
    def reconstruct(cls) -> dict[str, Any]:
        live_events = read_log_events(AppendOnlyStore.LIVE_LOG)
        replay_events = read_log_events(AppendOnlyStore.REPLAY_LOG)
        recovery_events = read_log_events(AppendOnlyStore.RECOVERY_LOG)

        runtime_events = [
            event
            for event in live_events
            if event.get("event_type") in _RUNTIME_EVENT_TYPES
        ]

        original_truth = cls._capture_original_truth(runtime_events)
        reconstructed_truth = cls._rebuild_runtime_state(runtime_events)
        replay_outcome = cls._replay_outcome(replay_events)
        recovery_outcome = cls._recovery_outcome(recovery_events)

        return {
            "events_reconstructed": len(runtime_events),
            "original_runtime_truth": original_truth,
            "reconstructed_runtime_truth": reconstructed_truth,
            "execution_state": reconstructed_truth["execution_state"],
            "sequence_lineage": reconstructed_truth["sequence_lineage"],
            "trace_lineage": reconstructed_truth["trace_lineage"],
            "verification_outcomes": {
                "replay_status": replay_outcome,
                "recovery_status": recovery_outcome.get("recovery_status"),
                "integrity_state": recovery_outcome.get("integrity_state"),
            },
            "recovery_outcomes": recovery_outcome,
        }

    @staticmethod
    def _capture_original_truth(events: list[dict[str, Any]]) -> dict[str, Any]:
        sequence_lineage: list[int] = []
        trace_lineage: list[str] = []
        payload_hashes: list[str | None] = []
        execution_state: str | None = None
        event_records: list[dict[str, Any]] = []

        for event in events:
            sequence_id = event.get("sequence_id")
            if sequence_id is not None:
                sequence_lineage.append(sequence_id)

            trace_id = event.get("trace_id")
            if trace_id:
                trace_lineage.append(trace_id)

            payload_hashes.append(event.get("payload_hash"))
            execution_state = event.get("runtime_state", execution_state)

            event_records.append(
                {
                    "sequence_id": sequence_id,
                    "trace_id": trace_id,
                    "runtime_state": event.get("runtime_state"),
                    "event_type": event.get("event_type"),
                    "payload_hash": event.get("payload_hash"),
                    "validation_status": event.get("validation_status"),
                }
            )

        return {
            "execution_state": execution_state,
            "sequence_lineage": sequence_lineage,
            "trace_lineage": trace_lineage,
            "payload_hashes": payload_hashes,
            "event_records": event_records,
        }

    @staticmethod
    def _rebuild_runtime_state(events: list[dict[str, Any]]) -> dict[str, Any]:
        sequence_lineage: list[int] = []
        trace_lineage: list[str] = []
        payload_hashes: list[str] = []
        execution_state: str | None = None
        event_records: list[dict[str, Any]] = []

        for event in events:
            payload = event.get("payload", {})
            validation = RuntimeValidator.validate(event)
            canonical_payload = CanonicalSerializer.serialize(payload)
            recomputed_hash = RuntimeHasher.generate_hash(canonical_payload)
            stored_hash = event.get("payload_hash")

            sequence_id = event.get("sequence_id")
            if sequence_id is not None:
                sequence_lineage.append(sequence_id)

            trace_id = event.get("trace_id")
            if trace_id:
                trace_lineage.append(trace_id)

            hash_verified = stored_hash == recomputed_hash if stored_hash else True
            payload_hashes.append(recomputed_hash)
            execution_state = event.get("runtime_state", execution_state)

            event_records.append(
                {
                    "sequence_id": sequence_id,
                    "trace_id": trace_id,
                    "runtime_state": event.get("runtime_state"),
                    "event_type": event.get("event_type"),
                    "payload_hash": recomputed_hash,
                    "stored_hash": stored_hash,
                    "hash_verified": hash_verified,
                    "validation_status": (
                        "VALID" if validation["valid"] else "INVALID"
                    ),
                }
            )

        return {
            "execution_state": execution_state,
            "sequence_lineage": sequence_lineage,
            "trace_lineage": trace_lineage,
            "payload_hashes": payload_hashes,
            "event_records": event_records,
        }

    @staticmethod
    def _replay_outcome(replay_events: list[dict[str, Any]]) -> str:
        for event in reversed(replay_events):
            if event.get("event_type") == "REPLAY_VALIDATION":
                return str(event.get("status", "NOT_RUN"))
        return "NOT_RUN"

    @staticmethod
    def _recovery_outcome(recovery_events: list[dict[str, Any]]) -> dict[str, Any]:
        for event in reversed(recovery_events):
            if event.get("event_type") == "RECOVERY_VALIDATION":
                return {
                    "recovery_status": event.get("recovery_status"),
                    "integrity_state": event.get("integrity_state"),
                    "resume_point": event.get("resume_point"),
                    "missing_sequences": event.get("missing_sequences", []),
                    "interrupted_events": event.get("interrupted_events"),
                }
        return {
            "recovery_status": "NOT_RUN",
            "integrity_state": "UNKNOWN",
            "resume_point": None,
            "missing_sequences": [],
            "interrupted_events": None,
        }
