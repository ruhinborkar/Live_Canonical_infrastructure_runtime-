"""Compare original runtime truth against reconstructed runtime truth."""

from typing import Any


class TruthVerifier:
    @classmethod
    def verify(cls, reconstruction: dict[str, Any]) -> str:
        if not cls._base_checks_pass(reconstruction):
            return "TRUTH_MISMATCH"

        original = reconstruction["original_runtime_truth"]
        rebuilt = reconstruction["reconstructed_runtime_truth"]

        if original["sequence_lineage"] != rebuilt["sequence_lineage"]:
            return "TRUTH_MISMATCH"

        if original["trace_lineage"] != rebuilt["trace_lineage"]:
            return "TRUTH_MISMATCH"

        if original["execution_state"] != rebuilt["execution_state"]:
            return "TRUTH_MISMATCH"

        for record in rebuilt["event_records"]:
            if not record.get("hash_verified", False):
                return "TRUTH_MISMATCH"

        sequence_lineage = rebuilt["sequence_lineage"]
        if len(sequence_lineage) != len(set(sequence_lineage)):
            return "TRUTH_MISMATCH"

        if sequence_lineage and sequence_lineage != sorted(sequence_lineage):
            return "TRUTH_MISMATCH"

        return "TRUTH_VERIFIED"

    @classmethod
    def verify_with_details(cls, reconstruction: dict[str, Any]) -> dict[str, Any]:
        original = reconstruction["original_runtime_truth"]
        rebuilt = reconstruction["reconstructed_runtime_truth"]
        replay_status = reconstruction["verification_outcomes"].get("replay_status")
        validation_state_diff = reconstruction.get("validation_state_diff", {})
        recovery_state_diff = reconstruction.get("recovery_state_diff", {})

        checks = {
            "replay_verified": reconstruction.get("replay_integrity_verified", False)
            and replay_status == "REPLAY_VERIFIED",
            "truth_hash_match": reconstruction.get("truth_hash_match", False),
            "validation_state_match": validation_state_diff.get("match", False),
            "recovery_state_match": recovery_state_diff.get("match", False),
            "sequence_lineage_match": (
                original["sequence_lineage"] == rebuilt["sequence_lineage"]
            ),
            "trace_lineage_match": (
                original["trace_lineage"] == rebuilt["trace_lineage"]
            ),
            "execution_state_match": (
                original["execution_state"] == rebuilt["execution_state"]
            ),
            "hash_integrity": all(
                record.get("hash_verified", False)
                for record in rebuilt["event_records"]
            ),
            "sequence_integrity": len(rebuilt["sequence_lineage"])
            == len(set(rebuilt["sequence_lineage"])),
            "sequence_ordered": (
                not rebuilt["sequence_lineage"]
                or rebuilt["sequence_lineage"] == sorted(rebuilt["sequence_lineage"])
            ),
        }

        truth_verification = (
            "TRUTH_VERIFIED" if all(checks.values()) else "TRUTH_MISMATCH"
        )

        return {
            "truth_verification": truth_verification,
            "checks": checks,
            "original_truth_hash": original.get("truth_hash"),
            "reconstructed_truth_hash": rebuilt.get("truth_hash"),
            "validation_state_diff": validation_state_diff,
            "recovery_state_diff": recovery_state_diff,
        }

    @staticmethod
    def _base_checks_pass(reconstruction: dict[str, Any]) -> bool:
        if not reconstruction.get("replay_integrity_verified", False):
            return False

        if not reconstruction.get("truth_hash_match", False):
            return False

        validation_state_diff = reconstruction.get("validation_state_diff", {})
        if not validation_state_diff.get("match", False):
            return False

        recovery_state_diff = reconstruction.get("recovery_state_diff", {})
        if not recovery_state_diff.get("match", False):
            return False

        return True
