import unittest

from replay.runtime_truth_reconstructor import RuntimeTruthReconstructor
from validation.truth_verifier import TruthVerifier


class TestTruthVerification(unittest.TestCase):
    def test_verify_returns_verdict_string(self):
        reconstruction = {
            "original_runtime_truth": {
                "sequence_lineage": [1, 2],
                "trace_lineage": ["A", "B"],
                "execution_state": "OPERATIONAL",
            },
            "reconstructed_runtime_truth": {
                "sequence_lineage": [1, 2],
                "trace_lineage": ["A", "B"],
                "execution_state": "OPERATIONAL",
                "event_records": [
                    {"hash_verified": True},
                    {"hash_verified": True},
                ],
            },
            "verification_outcomes": {"replay_status": "REPLAY_VERIFIED"},
        }

        verdict = TruthVerifier.verify(reconstruction)
        self.assertIn(verdict, ("TRUTH_VERIFIED", "TRUTH_MISMATCH"))

    def test_reconstructor_interface(self):
        self.assertTrue(hasattr(RuntimeTruthReconstructor, "reconstruct"))


if __name__ == "__main__":
    unittest.main()
