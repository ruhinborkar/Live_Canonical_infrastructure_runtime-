"""Rebuild runtime truth solely from append-only persisted execution logs."""

from typing import Any

from hashing.runtime_hasher import RuntimeHasher
from persistence.append_only_store import AppendOnlyStore
from recovery.persistence_helpers import analyze_recovery_state
from serialization.canonical_serializer import CanonicalSerializer
from services.event_loader import read_log_events
from validation.runtime_validator import RuntimeValidator

_RUNTIME_EVENT_TYPES = frozenset(
    {"NORMAL_EVENT", "CORRUPTED_EVENT", "INTERRUPTED_EVENT"}
)


_RECOVERY_COMPARE_KEYS = (
    "recovery_required",
    "recovery_status",
    "recovery_outcome",
    "interrupted_events",
    "missing_sequences",
    "resume_point",
    "integrity_state",
)


class RuntimeTruthReconstructor:
    @classmethod
    def reconstruct(cls) -> dict[str, Any]:
        live_events = read_log_events(AppendOnlyStore.LIVE_LOG)

        runtime_events = [
            event
            for event in live_events
            if event.get("event_type") in _RUNTIME_EVENT_TYPES
        ]

        original_truth = cls._capture_original_truth(runtime_events)
        reconstructed_truth = cls._rebuild_runtime_state(runtime_events)
        replay_integrity = cls._verify_replay_integrity(runtime_events)
        recovery_outcome = cls._derive_recovery_outcome(runtime_events)
        independent_recovery = cls._derive_recovery_outcome(runtime_events)
        validation_state_diff = cls._build_validation_state_diff(
            original_truth, reconstructed_truth
        )
        recovery_state_diff = cls._build_recovery_state_diff(
            recovery_outcome, independent_recovery
        )

        replay_status = (
            "REPLAY_VERIFIED" if replay_integrity else "REPLAY_MISMATCH"
        )

        return {
            "events_reconstructed": len(runtime_events),
            "original_runtime_truth": original_truth,
            "reconstructed_runtime_truth": reconstructed_truth,
            "truth_hash_match": (
                original_truth["truth_hash"] == reconstructed_truth["truth_hash"]
            ),
            "replay_integrity_verified": replay_integrity,
            "validation_state_diff": validation_state_diff,
            "recovery_state_diff": recovery_state_diff,
            "execution_state": reconstructed_truth["execution_state"],
            "sequence_lineage": reconstructed_truth["sequence_lineage"],
            "trace_lineage": reconstructed_truth["trace_lineage"],
            "verification_outcomes": {
                "replay_status": replay_status,
                "recovery_status": recovery_outcome.get("recovery_status"),
                "integrity_state": recovery_outcome.get("integrity_state"),
            },
            "recovery_outcomes": recovery_outcome,
        }

    @staticmethod
    def _truth_snapshot(
        *,
        execution_state: str | None,
        sequence_lineage: list[int],
        trace_lineage: list[str],
        payload_hashes: list[str | None],
    ) -> dict[str, Any]:
        return {
            "execution_state": execution_state,
            "sequence_lineage": sequence_lineage,
            "trace_lineage": trace_lineage,
            "payload_hashes": payload_hashes,
        }

    @classmethod
    def _compute_truth_hash(cls, snapshot: dict[str, Any]) -> str:
        canonical = CanonicalSerializer.serialize(snapshot)
        return RuntimeHasher.generate_hash(canonical)

    @classmethod
    def _capture_original_truth(cls, events: list[dict[str, Any]]) -> dict[str, Any]:
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
                    "validation_reason": event.get("validation_reason"),
                }
            )

        snapshot = cls._truth_snapshot(
            execution_state=execution_state,
            sequence_lineage=sequence_lineage,
            trace_lineage=trace_lineage,
            payload_hashes=payload_hashes,
        )

        return {
            **snapshot,
            "truth_hash": cls._compute_truth_hash(snapshot),
            "event_records": event_records,
        }

    @classmethod
    def _rebuild_runtime_state(cls, events: list[dict[str, Any]]) -> dict[str, Any]:
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
                    "validation_reason": validation["reason"],
                }
            )

        snapshot = cls._truth_snapshot(
            execution_state=execution_state,
            sequence_lineage=sequence_lineage,
            trace_lineage=trace_lineage,
            payload_hashes=payload_hashes,
        )

        return {
            **snapshot,
            "truth_hash": cls._compute_truth_hash(snapshot),
            "event_records": event_records,
        }

    @staticmethod
    def _verify_replay_integrity(events: list[dict[str, Any]]) -> bool:
        if not events:
            return False

        for event in events:
            payload = event.get("payload", {})
            canonical_payload = CanonicalSerializer.serialize(payload)
            recomputed_hash = RuntimeHasher.generate_hash(canonical_payload)
            stored_hash = event.get("payload_hash")
            if stored_hash and stored_hash != recomputed_hash:
                return False

        return True

    @staticmethod
    def _derive_recovery_outcome(events: list[dict[str, Any]]) -> dict[str, Any]:
        recovery_result = analyze_recovery_state(events, include_duplicates=False)
        integrity_state = (
            "COMPROMISED" if recovery_result.get("recovery_required") else "INTACT"
        )
        return {
            **recovery_result,
            "integrity_state": integrity_state,
            "interrupted_events": recovery_result.get("interrupted_events"),
        }

    @staticmethod
    def _build_validation_state_diff(
        original: dict[str, Any],
        rebuilt: dict[str, Any],
    ) -> dict[str, Any]:
        orig_records = {
            record.get("sequence_id"): record
            for record in original.get("event_records", [])
            if record.get("sequence_id") is not None
        }
        mismatches: list[dict[str, Any]] = []

        for record in rebuilt.get("event_records", []):
            sequence_id = record.get("sequence_id")
            stored = orig_records.get(sequence_id, {})
            stored_status = stored.get("validation_status")
            recomputed_status = record.get("validation_status")
            if stored_status != recomputed_status:
                mismatches.append(
                    {
                        "sequence_id": sequence_id,
                        "stored_status": stored_status,
                        "recomputed_status": recomputed_status,
                        "stored_reason": stored.get("validation_reason"),
                        "recomputed_reason": record.get("validation_reason"),
                    }
                )

        stored_records = original.get("event_records", [])
        rebuilt_records = rebuilt.get("event_records", [])

        return {
            "match": len(mismatches) == 0,
            "stored_valid": sum(
                1 for record in stored_records if record.get("validation_status") == "VALID"
            ),
            "stored_invalid": sum(
                1 for record in stored_records if record.get("validation_status") == "INVALID"
            ),
            "recomputed_valid": sum(
                1 for record in rebuilt_records if record.get("validation_status") == "VALID"
            ),
            "recomputed_invalid": sum(
                1 for record in rebuilt_records if record.get("validation_status") == "INVALID"
            ),
            "mismatch_count": len(mismatches),
            "mismatched_events": mismatches[:20],
        }

    @staticmethod
    def _build_recovery_state_diff(
        derived: dict[str, Any],
        independent: dict[str, Any],
    ) -> dict[str, Any]:
        field_diffs: dict[str, dict[str, Any]] = {}
        for key in _RECOVERY_COMPARE_KEYS:
            derived_value = derived.get(key)
            independent_value = independent.get(key)
            if derived_value != independent_value:
                field_diffs[key] = {
                    "derived": derived_value,
                    "independent": independent_value,
                }

        return {
            "match": len(field_diffs) == 0,
            "derived": {
                key: derived.get(key)
                for key in _RECOVERY_COMPARE_KEYS
            },
            "independent": {
                key: independent.get(key)
                for key in _RECOVERY_COMPARE_KEYS
            },
            "field_diffs": field_diffs,
        }
