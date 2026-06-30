import unittest

from intelligence.cross_event_relationships import CrossEventRelationships
from intelligence.execution_confidence import ExecutionConfidence
from intelligence.execution_dependency_graph import ExecutionDependencyGraph
from intelligence.execution_lineage import ExecutionLineage
from intelligence.operational_drift_detection import OperationalDriftDetection
from intelligence.runtime_anomaly_detection import RuntimeAnomalyDetection
from intelligence.state_transition_engine import StateTransitionEngine

SAMPLE = [
    {"sequence_id": 1, "trace_id": "t1", "event_type": "NORMAL_EVENT",
     "validation_status": "VALID", "payload_hash": "a", "payload": {"temperature": 20}},
    {"sequence_id": 2, "trace_id": "t1", "event_type": "NORMAL_EVENT",
     "validation_status": "VALID", "payload_hash": "b", "payload": {"temperature": 21}},
    {"sequence_id": 3, "trace_id": "t1", "event_type": "CORRUPTED_EVENT",
     "validation_status": "INVALID", "payload_hash": "c", "payload": {"temperature": None}},
]


class TestIntelligence(unittest.TestCase):
    def test_dependency_graph(self):
        graph = ExecutionDependencyGraph.build(SAMPLE)
        self.assertEqual(graph["node_count"], 3)
        self.assertGreaterEqual(graph["edge_count"], 2)

    def test_lineage(self):
        lineage = ExecutionLineage.build(SAMPLE)
        self.assertEqual(lineage["trace_count"], 1)
        self.assertEqual(lineage["longest_lineage"], 3)

    def test_relationships(self):
        rel = CrossEventRelationships.analyze(SAMPLE)
        self.assertGreater(rel["relationship_count"], 0)

    def test_confidence(self):
        conf = ExecutionConfidence.runtime_confidence(SAMPLE)
        self.assertLess(conf["confidence"], 1.0)

    def test_anomaly_detection(self):
        result = RuntimeAnomalyDetection.scan(SAMPLE)
        types = {a["type"] for a in result["anomalies"]}
        self.assertIn("VALIDATION_FAILURE", types)

    def test_drift_insufficient_history(self):
        result = OperationalDriftDetection.detect(SAMPLE, window=50)
        self.assertFalse(result["drift_detected"])

    def test_state_transition_legality(self):
        self.assertTrue(StateTransitionEngine.is_legal("RUNNING", "STOPPING"))
        self.assertFalse(StateTransitionEngine.is_legal("STOPPED", "RUNNING"))


if __name__ == "__main__":
    unittest.main()
