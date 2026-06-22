import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestEndToEndRuntime(unittest.TestCase):
    def test_live_runtime_end_to_end(self):
        result = subprocess.run(
            [sys.executable, "run_system.py", "--mode", "live"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("LIVE EXECUTION COMPLETE", result.stdout)
        self.assertIn("REPLAY_VERIFIED", result.stdout)
        self.assertIn("TRUTH_VERIFIED", result.stdout)

        live_log = ROOT / "logging" / "logs" / "live_execution.jsonl"
        report = ROOT / "observability" / "final_runtime_report.json"
        recovery_proof = ROOT / "runtime_recovery_proof.json"

        self.assertTrue(live_log.exists())
        self.assertTrue(report.exists())
        self.assertTrue(recovery_proof.exists())

        with open(live_log, encoding="utf-8") as file:
            events = [json.loads(line) for line in file if line.strip()]

        self.assertEqual(len(events), 100)

        with open(recovery_proof, encoding="utf-8") as file:
            proof = json.load(file)

        self.assertTrue(proof["resumed_from_persisted_truth"])
        self.assertFalse(proof["assumptions_used"])

    def test_demo_runtime_end_to_end(self):
        result = subprocess.run(
            [sys.executable, "run_system.py", "--mode", "demo"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("DEMO EXECUTION COMPLETE", result.stdout)
        self.assertIn("REPLAY_VERIFIED", result.stdout)
        self.assertIn("TRUTH_VERIFIED", result.stdout)
        self.assertTrue(
            "RECOVERY_EXECUTED" in result.stdout or "RECOVERY_REQUIRED" in result.stdout
        )


if __name__ == "__main__":
    unittest.main()
