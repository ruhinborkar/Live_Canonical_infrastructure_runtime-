import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hardening.low_anomaly_rate_check import (
    evaluate_low_anomaly_rate,
    failure_injection_active,
)
from hardening.readiness_score import ReadinessScore


def _clean_events() -> list[dict]:
    return [
        {
            "sequence_id": i,
            "trace_id": "session-test",
            "event_type": "NORMAL_EVENT",
            "runtime_state": "OPERATIONAL",
            "validation_status": "VALID",
            "payload_hash": f"hash-{i}",
            "processed_at": "2026-01-01T00:00:00+00:00",
            "task_id": f"task-{i}",
            "payload": {"temperature": 20 + i, "signal": "OK"},
        }
        for i in range(1, 11)
    ]


def _intentional_hostile_events() -> list[dict]:
    events = _clean_events()
    events.extend(
        [
            {
                "sequence_id": 20,
                "trace_id": "trace-demo",
                "event_type": "CORRUPTED_EVENT",
                "runtime_state": "OPERATIONAL",
                "validation_status": "INVALID",
                "validation_reason": "corrupted event type",
                "payload_hash": "hash-20",
                "payload": {"temperature": None},
            },
            {
                "sequence_id": 21,
                "trace_id": "trace-demo",
                "event_type": "INTERRUPTED_EVENT",
                "runtime_state": "INTERRUPTED",
                "validation_status": "INVALID",
                "validation_reason": "corrupted event type",
                "payload_hash": "hash-21",
                "payload": {"temperature": 10},
            },
        ]
    )
    return events


def _unexpected_anomaly_events() -> list[dict]:
    events = _clean_events()
    events.append(
        {
            "sequence_id": 5,
            "trace_id": "session-test",
            "event_type": "NORMAL_EVENT",
            "runtime_state": "OPERATIONAL",
            "validation_status": "INVALID",
            "validation_reason": "unexpected runtime fault",
            "payload_hash": "hash-5-dup",
            "processed_at": "2026-01-01T00:00:01+00:00",
            "task_id": "task-5-dup",
            "payload": {"temperature": 25, "signal": "OK"},
        }
    )
    return events


class TestLowAnomalyRateCheck(unittest.TestCase):
    def test_pass_when_rate_under_threshold(self):
        with patch("hardening.low_anomaly_rate_check.live_events", return_value=_clean_events()):
            result = evaluate_low_anomaly_rate(threshold=0.3)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["reason"], "Anomaly rate within acceptable threshold")
        self.assertEqual(result["unexpected_anomalies"], 0)
        self.assertFalse(result["production_impact"])
        self.assertTrue(result["counts_for_score"])

    def test_fail_with_injection_context_when_only_intentional(self):
        with tempfile.TemporaryDirectory() as tmp:
            proof_path = Path(tmp) / "failure_injection_proof.json"
            proof_path.write_text(
                json.dumps({"detected_count": 6, "scenarios_executed": 6, "results": []}),
                encoding="utf-8",
            )
            with patch("hardening.low_anomaly_rate_check.PROOF_FILE", proof_path):
                with patch(
                    "hardening.low_anomaly_rate_check.live_events",
                    return_value=_intentional_hostile_events(),
                ):
                    self.assertTrue(failure_injection_active())
                    result = evaluate_low_anomaly_rate(threshold=0.01)

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["reason"], "Failure Injection Test Active")
        self.assertGreater(result["intentional_anomalies"], 0)
        self.assertEqual(result["unexpected_anomalies"], 0)
        self.assertFalse(result["production_impact"])
        self.assertTrue(result["counts_for_score"])
        self.assertIn("No unexpected production anomalies", result["message"])

    def test_fail_with_production_impact_when_unexpected(self):
        with patch("hardening.low_anomaly_rate_check.live_events", return_value=_unexpected_anomaly_events()):
            result = evaluate_low_anomaly_rate(threshold=0.3)

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["reason"], "Unexpected runtime anomalies detected")
        self.assertGreater(result["unexpected_anomalies"], 0)
        self.assertTrue(result["production_impact"])
        self.assertFalse(result["counts_for_score"])
        self.assertIn("Production readiness impacted", result["message"])

    def test_readiness_includes_structured_anomaly_fields(self):
        with patch("hardening.low_anomaly_rate_check.live_events", return_value=_intentional_hostile_events()):
            with patch("hardening.readiness_score.evaluate_low_anomaly_rate") as mock_eval:
                mock_eval.return_value = {
                    "check": "low_anomaly_rate",
                    "status": "FAIL",
                    "passed": False,
                    "reason": "Failure Injection Test Active",
                    "intentional_anomalies": 12,
                    "unexpected_anomalies": 0,
                    "production_impact": False,
                    "message": "12 intentional anomalies detected. No unexpected production anomalies.",
                    "failure_injection_active": True,
                    "anomaly_rate": 0.6,
                    "threshold": 0.3,
                    "analysed_events": 20,
                    "counts_for_score": True,
                }
                readiness = ReadinessScore.compute()

        anomaly = next(c for c in readiness["contributors"] if c["signal"] == "low_anomaly_rate")
        self.assertEqual(anomaly["check"], "low_anomaly_rate")
        self.assertEqual(anomaly["reason"], "Failure Injection Test Active")
        self.assertEqual(anomaly["intentional_anomalies"], 12)
        self.assertEqual(anomaly["unexpected_anomalies"], 0)
        self.assertFalse(anomaly["production_impact"])
        self.assertEqual(anomaly["display_status"], "TEST_FAIL")


if __name__ == "__main__":
    unittest.main()
