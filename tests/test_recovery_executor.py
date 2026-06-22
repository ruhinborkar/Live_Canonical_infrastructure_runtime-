import unittest

from services.runtime_service import RuntimeService


class TestRecoveryExecutor(unittest.TestCase):
    def test_executable_recovery_after_live(self):
        RuntimeService.execute_live()
        result = RuntimeService.execute_recover()

        self.assertTrue(result.get("recovery_executed"))
        self.assertGreater(result.get("events_recovered", 0), 0)
        self.assertEqual(result.get("recovery_outcome"), "RECOVERY_EXECUTED")

        proof_path = __import__("pathlib").Path("runtime_recovery_execution_proof.json")
        self.assertTrue(proof_path.exists())
        proof = __import__("json").loads(proof_path.read_text(encoding="utf-8"))
        self.assertEqual(proof.get("proof_type"), "EXECUTABLE_RECOVERY")
        self.assertFalse(proof.get("assumptions_used"))


if __name__ == "__main__":
    unittest.main()
