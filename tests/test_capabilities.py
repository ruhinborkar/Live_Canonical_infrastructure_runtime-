import unittest

from capabilities.alert_pipeline import AlertPipeline
from capabilities.execution_audit_chain import ExecutionAuditChain
from capabilities.execution_priority import ExecutionPriority
from capabilities.operational_contracts import OperationalContracts
from capabilities.resource_allocation import ResourceAllocation
from capabilities.task_queue import TaskQueue


class TestCapabilities(unittest.TestCase):
    def test_task_queue_priority_order(self):
        TaskQueue.clear()
        TaskQueue.enqueue({"event_type": "A"}, priority=7)
        TaskQueue.enqueue({"event_type": "B"}, priority=1)
        first = TaskQueue.next_task()
        self.assertEqual(first["priority"], 1)
        TaskQueue.clear()

    def test_execution_priority_scoring(self):
        self.assertLess(
            ExecutionPriority.score({"event_type": "INTERRUPTED_EVENT", "payload": {}}),
            ExecutionPriority.score({"event_type": "NORMAL_EVENT", "payload": {}}),
        )

    def test_alert_pipeline_raise_and_ack(self):
        AlertPipeline.reset()
        alert = AlertPipeline.raise_alert("test", "boom", severity="CRITICAL")
        self.assertEqual(AlertPipeline.summary()["critical"], 1)
        AlertPipeline.acknowledge(alert["alert_id"])
        self.assertEqual(AlertPipeline.summary()["active_count"], 0)

    def test_audit_chain_integrity(self):
        ExecutionAuditChain.reset()
        for i in range(5):
            ExecutionAuditChain.append("TEST", {"i": i})
        result = ExecutionAuditChain.verify()
        self.assertTrue(result["intact"])
        self.assertGreaterEqual(result["entries"], 5)

    def test_operational_contracts(self):
        OperationalContracts.define("evt", {"sequence_id": "int", "payload": "dict"})
        ok = OperationalContracts.validate("evt", {"sequence_id": 1, "payload": {}})
        bad = OperationalContracts.validate("evt", {"sequence_id": "x"})
        self.assertTrue(ok["valid"])
        self.assertFalse(bad["valid"])

    def test_resource_allocation(self):
        ResourceAllocation.reset()
        ResourceAllocation.define_pool("cpu", 2)
        self.assertTrue(ResourceAllocation.allocate("cpu", 2))
        self.assertFalse(ResourceAllocation.allocate("cpu", 1))
        ResourceAllocation.release("cpu", 1)
        self.assertTrue(ResourceAllocation.allocate("cpu", 1))


if __name__ == "__main__":
    unittest.main()
