import json
import subprocess
import sys
import unittest
from pathlib import Path

from ledger.runtime_truth_ledger import RuntimeTruthLedger
from ledger.truth_snapshot_store import TruthSnapshotStore
from persistence.append_only_store import AppendOnlyStore

ROOT = Path(__file__).resolve().parents[1]


class TestTruthLedger(unittest.TestCase):
    def setUp(self):
        TruthSnapshotStore.clear()
        AppendOnlyStore.clear_log(AppendOnlyStore.REPLAY_LOG)

    def test_snapshot_fields(self):
        RuntimeTruthLedger.record_snapshot(
            {
                "trace_id": "TRACE-1",
                "sequence_id": 1,
                "runtime_state": "OPERATIONAL",
                "event_type": "NORMAL_EVENT",
                "event_timestamp": "2026-01-01T00:00:00+00:00",
            },
            validation_status="VALID",
            payload_hash="abc123",
        )

        snapshots = TruthSnapshotStore.read_all()
        self.assertEqual(len(snapshots), 1)
        snapshot = snapshots[0]
        for field in (
            "trace_id",
            "sequence_id",
            "execution_state",
            "validation_state",
            "recovery_state",
            "timestamp",
        ):
            self.assertIn(field, snapshot)

    def test_reconstruct_from_ledger_without_replay_logs(self):
        for sequence_id in (1, 2, 3):
            RuntimeTruthLedger.record_snapshot(
                {
                    "trace_id": f"TRACE-{sequence_id}",
                    "sequence_id": sequence_id,
                    "runtime_state": "OPERATIONAL",
                    "event_type": "NORMAL_EVENT",
                    "event_timestamp": f"2026-01-01T00:00:0{sequence_id}+00:00",
                },
                validation_status="VALID",
                payload_hash=f"hash-{sequence_id}",
            )

        AppendOnlyStore.clear_log(AppendOnlyStore.REPLAY_LOG)
        result = RuntimeTruthLedger.reconstruct_without_replay_logs()

        self.assertEqual(result["truth_reconstruction"], "SUCCESS")
        self.assertEqual(result["source"], "TRUTH_LEDGER")
        self.assertEqual(result["runtime_state"], "OPERATIONAL")
        self.assertEqual(result["snapshots_reconstructed"], 3)

        proof_path = ROOT / "truth_ledger_reconstruction_proof.json"
        self.assertTrue(proof_path.exists())
        with open(proof_path, encoding="utf-8") as file:
            proof = json.load(file)
        self.assertEqual(proof["source"], "TRUTH_LEDGER")

    def test_live_pipeline_writes_ledger(self):
        result = subprocess.run(
            [sys.executable, "run_system.py", "--mode", "live"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("LIVE EXECUTION COMPLETE", result.stdout)

        ledger_path = ROOT / "logging" / "truth_ledger" / "truth_snapshots.jsonl"
        self.assertTrue(ledger_path.exists())
        with open(ledger_path, encoding="utf-8") as file:
            snapshots = [json.loads(line) for line in file if line.strip()]
        self.assertEqual(len(snapshots), 100)

        AppendOnlyStore.clear_log(AppendOnlyStore.REPLAY_LOG)
        reconstruction = RuntimeTruthLedger.reconstruct()
        self.assertEqual(reconstruction["truth_reconstruction"], "SUCCESS")
        self.assertEqual(reconstruction["source"], "TRUTH_LEDGER")


if __name__ == "__main__":
    unittest.main()
