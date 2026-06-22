import unittest

from replay.runtime_truth_reconstructor import RuntimeTruthReconstructor
from validation.truth_verifier import TruthVerifier


def _matching_diffs() -> dict:
    return {
        "match": True,
        "stored_valid": 2,
        "stored_invalid": 0,
        "recomputed_valid": 2,
        "recomputed_invalid": 0,
        "mismatch_count": 0,
        "mismatched_events": [],
    }


def _matching_recovery_diff() -> dict:
    recovery = {
        "recovery_required": False,
        "recovery_status": "RECOVERY_NOT_REQUIRED",
        "recovery_outcome": "RECOVERY_NOT_REQUIRED",
        "interrupted_events": 0,
        "missing_sequences": [],
        "resume_point": None,
        "integrity_state": "INTACT",
    }
    return {
        "match": True,
        "derived": recovery,
        "independent": recovery,
        "field_diffs": {},
    }


class TestTruthVerification(unittest.TestCase):
    def test_verify_returns_verdict_string(self):
        reconstruction = {
            "original_runtime_truth": {
                "sequence_lineage": [1, 2],
                "trace_lineage": ["A", "B"],
                "execution_state": "OPERATIONAL",
                "truth_hash": "abc123",
            },
            "reconstructed_runtime_truth": {
                "sequence_lineage": [1, 2],
                "trace_lineage": ["A", "B"],
                "execution_state": "OPERATIONAL",
                "truth_hash": "abc123",
                "event_records": [
                    {"hash_verified": True},
                    {"hash_verified": True},
                ],
            },
            "truth_hash_match": True,
            "replay_integrity_verified": True,
            "validation_state_diff": _matching_diffs(),
            "recovery_state_diff": _matching_recovery_diff(),
            "verification_outcomes": {"replay_status": "REPLAY_VERIFIED"},
        }

        verdict = TruthVerifier.verify(reconstruction)
        self.assertEqual(verdict, "TRUTH_VERIFIED")

    def test_validation_state_mismatch_fails(self):
        reconstruction = {
            "original_runtime_truth": {
                "sequence_lineage": [1],
                "trace_lineage": ["A"],
                "execution_state": "OPERATIONAL",
                "truth_hash": "abc123",
            },
            "reconstructed_runtime_truth": {
                "sequence_lineage": [1],
                "trace_lineage": ["A"],
                "execution_state": "OPERATIONAL",
                "truth_hash": "abc123",
                "event_records": [{"hash_verified": True}],
            },
            "truth_hash_match": True,
            "replay_integrity_verified": True,
            "validation_state_diff": {
                "match": False,
                "mismatch_count": 1,
                "mismatched_events": [{"sequence_id": 1}],
            },
            "recovery_state_diff": _matching_recovery_diff(),
            "verification_outcomes": {"replay_status": "REPLAY_VERIFIED"},
        }

        self.assertEqual(TruthVerifier.verify(reconstruction), "TRUTH_MISMATCH")

    def test_verify_with_details_includes_state_diffs(self):
        reconstruction = {
            "original_runtime_truth": {
                "sequence_lineage": [1],
                "trace_lineage": ["A"],
                "execution_state": "OPERATIONAL",
                "truth_hash": "abc123",
            },
            "reconstructed_runtime_truth": {
                "sequence_lineage": [1],
                "trace_lineage": ["A"],
                "execution_state": "OPERATIONAL",
                "truth_hash": "abc123",
                "event_records": [{"hash_verified": True}],
            },
            "truth_hash_match": True,
            "replay_integrity_verified": True,
            "validation_state_diff": _matching_diffs(),
            "recovery_state_diff": _matching_recovery_diff(),
            "verification_outcomes": {"replay_status": "REPLAY_VERIFIED"},
        }

        result = TruthVerifier.verify_with_details(reconstruction)
        self.assertIn("validation_state_diff", result)
        self.assertIn("recovery_state_diff", result)
        self.assertTrue(result["checks"]["validation_state_match"])
        self.assertTrue(result["checks"]["recovery_state_match"])

    def test_reconstructor_interface(self):
        self.assertTrue(hasattr(RuntimeTruthReconstructor, "reconstruct"))


if __name__ == "__main__":
    unittest.main()
