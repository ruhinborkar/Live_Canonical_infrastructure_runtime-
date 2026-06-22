"""Execute recovery by resuming from persisted truth and appending recovered events."""

from datetime import datetime, timezone
from typing import Any

from datasets.runtime_dataset_loader import RuntimeDatasetLoader
from hashing.runtime_hasher import RuntimeHasher
from ledger.runtime_truth_ledger import RuntimeTruthLedger
from persistence.append_only_store import AppendOnlyStore
from recovery.persistence_helpers import analyze_recovery_state, filter_runtime_events
from serialization.canonical_serializer import CanonicalSerializer
from services.event_loader import read_log_events
from validation.runtime_validator import RuntimeValidator

PROOF_FILE = "runtime_recovery_execution_proof.json"


class RuntimeRecoveryExecutor:
    @classmethod
    def execute(cls, recovery_analysis: dict[str, Any] | None = None) -> dict[str, Any]:
        live_events = read_log_events(AppendOnlyStore.LIVE_LOG)
        runtime_events = filter_runtime_events(live_events)
        analysis = recovery_analysis or analyze_recovery_state(
            runtime_events, include_duplicates=False
        )

        resume_point = analysis.get("resume_point")
        if not analysis.get("recovery_required") or resume_point is None:
            return {
                "recovery_executed": False,
                "events_recovered": 0,
                "recovery_outcome": analysis.get("recovery_outcome", "RECOVERY_NOT_REQUIRED"),
                "reason": "recovery not required",
            }

        dataset_by_sequence = {
            event["sequence_id"]: event
            for event in RuntimeDatasetLoader.load_events()
            if event.get("sequence_id") is not None
        }

        events_recovered = 0
        recovered_sequences: list[int] = []

        for event in runtime_events:
            sequence_id = event.get("sequence_id")
            if sequence_id is None or sequence_id < resume_point:
                continue
            if event.get("event_type") != "INTERRUPTED_EVENT":
                continue

            source = dataset_by_sequence.get(sequence_id, event)
            recovered_event = {
                **source,
                "event_type": "RECOVERED_EVENT",
                "runtime_state": "OPERATIONAL",
                "event_timestamp": datetime.now(timezone.utc).isoformat(),
                "recovered_from": "INTERRUPTED_EVENT",
                "resume_point": resume_point,
            }

            validation = RuntimeValidator.validate(
                {
                    **recovered_event,
                    "event_type": "NORMAL_EVENT",
                }
            )
            canonical = CanonicalSerializer.serialize(recovered_event.get("payload", {}))
            payload_hash = RuntimeHasher.generate_hash(canonical)

            recovered_event["payload_hash"] = payload_hash
            recovered_event["validation_status"] = (
                "VALID" if validation["valid"] else "INVALID"
            )
            recovered_event["validation_reason"] = (
                validation["reason"] if validation["valid"] else "recovery validation failed"
            )

            AppendOnlyStore.append_event(AppendOnlyStore.LIVE_LOG, recovered_event)
            RuntimeTruthLedger.record_snapshot(
                recovered_event,
                validation_status=recovered_event["validation_status"],
                payload_hash=payload_hash,
            )
            events_recovered += 1
            recovered_sequences.append(sequence_id)

        result = {
            "recovery_executed": events_recovered > 0,
            "events_recovered": events_recovered,
            "recovered_sequences": recovered_sequences,
            "resume_point": resume_point,
            "recovery_outcome": "RECOVERY_EXECUTED" if events_recovered else "RECOVERY_FAILED",
            "execution_state": "OPERATIONAL" if events_recovered else "INTERRUPTED",
        }

        proof = {
            **result,
            "proof_type": "EXECUTABLE_RECOVERY",
            "source_log": AppendOnlyStore.LIVE_LOG,
            "ledger_updated": events_recovered > 0,
            "assumptions_used": False,
        }
        cls._export_execution_proof(proof)
        return result

    @staticmethod
    def _export_execution_proof(proof: dict[str, Any]) -> None:
        import json
        import os

        os.makedirs(os.path.dirname(PROOF_FILE) or ".", exist_ok=True)
        with open(PROOF_FILE, "w", encoding="utf-8") as file:
            json.dump(proof, file, indent=4)
