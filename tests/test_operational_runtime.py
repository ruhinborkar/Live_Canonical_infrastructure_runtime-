import json
import unittest
from pathlib import Path

from capabilities.task_queue import TaskQueue, QUEUE_FILE
from runtime.background_runtime_engine import BackgroundRuntimeEngine
from runtime.operational_state_manager import OperationalStateManager, STATE_FILE
from runtime.restart_recovery import RestartRecovery


class TestOperationalRuntime(unittest.TestCase):
    def test_engine_lifecycle_and_processing(self):
        engine = BackgroundRuntimeEngine()
        TaskQueue.clear()
        status = engine.start(worker_count=2, heartbeat_interval=0.3)
        try:
            self.assertEqual(status["state"], "RUNNING")
            TaskQueue.clear()
            for i in range(1, 16):
                engine.submit(
                    {
                        "sequence_id": i,
                        "trace_id": f"t{i}",
                        "event_type": "NORMAL_EVENT",
                        "runtime_state": "OPERATIONAL",
                        "payload": {"temperature": 20 + i, "signal": "OK"},
                    },
                    priority=4,
                )
            self.assertTrue(engine.drain_until_idle(timeout=10))
            final = engine.status()
            self.assertTrue(final["heartbeat"]["alive"])
            self.assertGreaterEqual(final["counters"]["tasks_completed"], 15)
        finally:
            stopped = engine.stop()
            self.assertEqual(stopped["state"], "STOPPED")

    def test_invalid_event_raises_alert_and_counts(self):
        engine = BackgroundRuntimeEngine()
        TaskQueue.clear()
        engine.start(worker_count=1, heartbeat_interval=0.3)
        try:
            TaskQueue.clear()
            engine.submit(
                {"sequence_id": 999, "trace_id": "tc", "event_type": "CORRUPTED_EVENT",
                 "runtime_state": "OPERATIONAL", "payload": {"temperature": None}},
                priority=1,
            )
            engine.drain_until_idle(timeout=10)
            final = engine.status()
            self.assertGreaterEqual(final["counters"]["tasks_invalid"], 1)
        finally:
            engine.stop()

    def test_restart_recovery_detects_unclean_shutdown(self):
        # Simulate an unclean prior shutdown with a pending task.
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(
                {
                    "state": "RUNNING",
                    "previous_state": "STARTING",
                    "started_at": "2026-01-01T00:00:00+00:00",
                    "last_transition_at": "2026-01-01T00:00:00+00:00",
                    "stopped_cleanly": False,
                    "heartbeat_tick": 42,
                    "last_heartbeat_at": "2026-01-01T00:00:00+00:00",
                    "counters": {"tasks_accepted": 5, "tasks_completed": 4, "tasks_failed": 0, "tasks_invalid": 1},
                }
            ),
            encoding="utf-8",
        )
        QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        QUEUE_FILE.write_text(
            json.dumps(
                {"tasks": [{"task_id": "x", "priority": 3, "payload": {}, "status": "PENDING",
                            "enqueued_at": "2026-01-01T00:00:00+00:00"}]}
            ),
            encoding="utf-8",
        )

        recovery = RestartRecovery.recover()
        self.assertTrue(recovery["unclean_shutdown_detected"])
        self.assertTrue(recovery["recovered"])
        self.assertGreaterEqual(recovery["restored_pending_tasks"], 1)
        self.assertEqual(recovery["prior_heartbeat_tick"], 42)
        TaskQueue.clear()


if __name__ == "__main__":
    unittest.main()
