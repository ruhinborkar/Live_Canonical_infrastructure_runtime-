"""Persist and reconstruct runtime truth from immutable ledger snapshots only."""

import json
import os
from datetime import datetime, timezone
from typing import Any

from hashing.runtime_hasher import RuntimeHasher
from ledger.truth_snapshot_store import TruthSnapshotStore
from serialization.canonical_serializer import CanonicalSerializer

PROOF_FILE = "truth_ledger_reconstruction_proof.json"


class RuntimeTruthLedger:
    @staticmethod
    def recovery_state_for_event(event: dict[str, Any], *, validation_valid: bool) -> str:
        if event.get("event_type") == "RECOVERED_EVENT":
            return "RECOVERED"
        if event.get("event_type") == "INTERRUPTED_EVENT":
            return "INTERRUPTED"
        if event.get("event_type") == "CORRUPTED_EVENT" or not validation_valid:
            return "COMPROMISED"
        return "INTACT"

    @classmethod
    def record_snapshot(
        cls,
        event: dict[str, Any],
        *,
        validation_status: str,
        payload_hash: str | None = None,
    ) -> dict[str, Any]:
        snapshot = {
            "snapshot_timestamp": event.get(
                "event_timestamp",
                datetime.now(timezone.utc).isoformat(),
            ),
            "trace_id": event.get("trace_id"),
            "sequence_id": event.get("sequence_id"),
            "execution_state": event.get("runtime_state"),
            "validation_state": validation_status,
            "recovery_state": cls.recovery_state_for_event(
                event,
                validation_valid=validation_status == "VALID",
            ),
            "timestamp": event.get(
                "event_timestamp",
                datetime.now(timezone.utc).isoformat(),
            ),
            "event_type": event.get("event_type"),
            "payload_hash": payload_hash,
        }
        TruthSnapshotStore.append_snapshot(snapshot)
        return snapshot

    @classmethod
    def reconstruct(cls) -> dict[str, Any]:
        snapshots = TruthSnapshotStore.read_all()

        if not snapshots:
            return {
                "truth_reconstruction": "FAILED",
                "source": "TRUTH_LEDGER",
                "runtime_state": "UNKNOWN",
                "snapshots_reconstructed": 0,
                "reason": "ledger empty",
            }

        sequence_lineage = [
            snapshot["sequence_id"]
            for snapshot in snapshots
            if snapshot.get("sequence_id") is not None
        ]
        trace_lineage = [
            snapshot["trace_id"]
            for snapshot in snapshots
            if snapshot.get("trace_id")
        ]
        execution_state = snapshots[-1].get("execution_state")
        payload_hashes = [
            snapshot.get("payload_hash")
            for snapshot in snapshots
            if snapshot.get("payload_hash")
        ]

        snapshot_truth = {
            "execution_state": execution_state,
            "sequence_lineage": sequence_lineage,
            "trace_lineage": trace_lineage,
            "payload_hashes": payload_hashes,
        }
        truth_hash = RuntimeHasher.generate_hash(
            CanonicalSerializer.serialize(snapshot_truth)
        )

        sequence_ordered = (
            not sequence_lineage or sequence_lineage == sorted(sequence_lineage)
        )
        sequence_unique = len(sequence_lineage) == len(set(sequence_lineage))

        success = sequence_ordered and sequence_unique and len(snapshots) > 0
        runtime_state = execution_state or "OPERATIONAL"

        return {
            "truth_reconstruction": "SUCCESS" if success else "FAILED",
            "source": "TRUTH_LEDGER",
            "runtime_state": runtime_state,
            "snapshots_reconstructed": len(snapshots),
            "sequence_lineage": sequence_lineage,
            "trace_lineage": trace_lineage,
            "execution_state": execution_state,
            "truth_hash": truth_hash,
            "validation_summary": {
                "valid": sum(
                    1 for s in snapshots if s.get("validation_state") == "VALID"
                ),
                "invalid": sum(
                    1 for s in snapshots if s.get("validation_state") == "INVALID"
                ),
            },
            "recovery_summary": {
                "intact": sum(
                    1 for s in snapshots if s.get("recovery_state") == "INTACT"
                ),
                "interrupted": sum(
                    1 for s in snapshots if s.get("recovery_state") == "INTERRUPTED"
                ),
                "compromised": sum(
                    1 for s in snapshots if s.get("recovery_state") == "COMPROMISED"
                ),
            },
        }

    @classmethod
    def export_proof(cls, reconstruction: dict[str, Any] | None = None) -> dict[str, Any]:
        proof = reconstruction or cls.reconstruct()
        os.makedirs(os.path.dirname(PROOF_FILE) or ".", exist_ok=True)
        with open(PROOF_FILE, "w", encoding="utf-8") as file:
            json.dump(proof, file, indent=4)
        return proof

    @classmethod
    def reconstruct_without_replay_logs(cls) -> dict[str, Any]:
        """Proof entry point: reconstruction uses ledger snapshots only."""
        return cls.export_proof(cls.reconstruct())
