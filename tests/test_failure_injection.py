import unittest

from validation.failure_injection_framework import FailureInjectionFramework


class TestFailureInjectionFramework(unittest.TestCase):
    def test_execute_returns_all_scenarios(self):
        results = FailureInjectionFramework.execute()
        self.assertEqual(len(results), 6)
        failure_types = {row["failure_type"] for row in results}
        self.assertIn("CORRUPTED_HASH", failure_types)
        self.assertIn("INTERRUPTED_EXECUTION", failure_types)
        self.assertIn("TRACE_CORRUPTION", failure_types)

    def test_corrupted_hash_response_format(self):
        results = FailureInjectionFramework.execute()
        corrupted = next(r for r in results if r["failure_type"] == "CORRUPTED_HASH")
        self.assertTrue(corrupted["detected"])
        self.assertEqual(corrupted["system_response"], "REPLAY_REJECTED")
        self.assertIn("failure_type", corrupted)
        self.assertIn("detected", corrupted)
        self.assertIn("system_response", corrupted)

    def test_all_injected_failures_detected(self):
        results = FailureInjectionFramework.execute()
        self.assertTrue(all(row["detected"] for row in results))


if __name__ == "__main__":
    unittest.main()
