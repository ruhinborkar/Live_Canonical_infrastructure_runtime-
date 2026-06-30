"""Operational runtime orchestration facade.

Single composition point that boots the operational backbone and exposes a
clean API surface for the command-center dashboard. It wires together the
runtime engine, capability layer, intelligence layer, and hardening layer
without duplicating any of them.
"""

from typing import Any

from capabilities.alert_pipeline import AlertPipeline
from capabilities.decision_recommendation import DecisionRecommendation
from capabilities.event_ingestion import EventIngestion
from capabilities.mission_context import MissionContext
from capabilities.operator_actions import OperatorActions
from capabilities.resource_allocation import ResourceAllocation
from capabilities.situation_timeline import SituationTimeline
from capabilities.task_queue import TaskQueue
from config.runtime_config import RuntimeConfig
from hardening.dependency_monitor import DependencyMonitor
from hardening.graceful_degradation import GracefulDegradation
from hardening.rate_limiter import RateLimiter
from hardening.readiness_score import ReadinessScore
from hardening.runtime_diagnostics import RuntimeDiagnostics
from hardening.service_discovery import ServiceDiscovery
from hardening.structured_logger import StructuredLogger
from intelligence.context_aware_recovery import ContextAwareRecovery
from intelligence.cross_event_relationships import CrossEventRelationships
from intelligence.execution_confidence import ExecutionConfidence
from intelligence.execution_dependency_graph import ExecutionDependencyGraph
from intelligence.execution_lineage import ExecutionLineage
from intelligence.operational_context_graph import OperationalContextGraph
from intelligence.operational_drift_detection import OperationalDriftDetection
from intelligence.priority_propagation import PriorityPropagation
from intelligence.runtime_anomaly_detection import RuntimeAnomalyDetection
from intelligence.runtime_intelligence_hooks import attach as attach_intelligence
from intelligence.state_transition_engine import StateTransitionEngine
from runtime.background_runtime_engine import get_engine


class OperationalRuntimeService:
    _booted = False

    # ----- lifecycle -------------------------------------------------------
    @classmethod
    def boot(cls) -> dict[str, Any]:
        config = RuntimeConfig.load()
        StructuredLogger.configure(config["log_level"])
        engine = get_engine()
        attach_intelligence(engine)
        cls._register_services()

        result = engine.start(
            worker_count=config["worker_count"],
            heartbeat_interval=config["heartbeat_interval"],
        )
        cls._booted = True
        StructuredLogger.info("runtime_booted", state=result.get("state"),
                              workers=config["worker_count"])
        SituationTimeline.record("RUNTIME", "Operational runtime booted",
                                 details={"workers": config["worker_count"]})
        return result

    @classmethod
    def shutdown(cls) -> dict[str, Any]:
        StructuredLogger.info("runtime_shutdown_requested")
        return get_engine().stop(graceful=True)

    @classmethod
    def start(cls) -> dict[str, Any]:
        return cls.boot()

    @classmethod
    def _register_services(cls) -> None:
        ServiceDiscovery.register("runtime_engine", kind="core", endpoint="/api/operations/status")
        ServiceDiscovery.register("task_queue", kind="capability")
        ServiceDiscovery.register("situation_timeline", kind="capability")
        ServiceDiscovery.register("alert_pipeline", kind="capability")
        ServiceDiscovery.register("execution_audit_chain", kind="capability")
        ServiceDiscovery.register("intelligence_layer", kind="intelligence")
        ResourceAllocation.define_pool("worker_slots", RuntimeConfig.get("worker_count", 2))

    # ----- intake ----------------------------------------------------------
    @classmethod
    def submit_work(cls, payload: dict[str, Any], *, priority: int | None = None) -> dict[str, Any]:
        limit = RuntimeConfig.get("rate_limit_per_minute", 0)
        if not RateLimiter.allow("ingestion", limit_per_minute=limit):
            GracefulDegradation.degrade("ingestion", "rate limit exceeded", severity="DEGRADED")
            return {"accepted": False, "reason": "RATE_LIMITED"}
        GracefulDegradation.restore("ingestion")
        task = EventIngestion.ingest(payload, priority=priority, source="api")
        OperatorActions.record("SUBMIT_WORK", target=task["task_id"],
                               details={"priority": task["priority"]})
        return {"accepted": True, "task": task}

    @classmethod
    def acknowledge_alert(cls, alert_id: str, operator: str = "operator") -> dict[str, Any]:
        alert = AlertPipeline.acknowledge(alert_id, operator=operator)
        OperatorActions.record("ACK_ALERT", target=alert_id, operator=operator)
        return {"acknowledged": alert is not None, "alert": alert}

    # ----- views -----------------------------------------------------------
    @classmethod
    def status(cls) -> dict[str, Any]:
        return get_engine().status()

    @classmethod
    def situation(cls) -> dict[str, Any]:
        """Answers: what is happening / what requires attention / what's next."""
        anomalies = RuntimeAnomalyDetection.scan()
        drift = OperationalDriftDetection.detect()
        confidence = ExecutionConfidence.runtime_confidence()
        return {
            "what_is_happening": {
                "engine": get_engine().status()["state"],
                "queue_pending": TaskQueue.pending(),
                "recent_timeline": SituationTimeline.tail(limit=15),
                "runtime_confidence": confidence,
            },
            "what_requires_attention": {
                "alerts": AlertPipeline.summary(),
                "anomalies": anomalies,
                "drift": drift,
                "degradation": GracefulDegradation.status(),
            },
            "what_happens_next": DecisionRecommendation.recommend(
                drift=drift, anomalies=anomalies["anomaly_count"]
            ),
        }

    @classmethod
    def queue(cls) -> dict[str, Any]:
        return TaskQueue.snapshot(limit=50)

    @classmethod
    def timeline(cls, limit: int = 100) -> dict[str, Any]:
        return {"entries": SituationTimeline.tail(limit=limit)}

    @classmethod
    def alerts(cls) -> dict[str, Any]:
        return AlertPipeline.summary()

    @classmethod
    def operator_timeline(cls, limit: int = 100) -> dict[str, Any]:
        return {"actions": OperatorActions.tail(limit=limit)}

    @classmethod
    def topology(cls) -> dict[str, Any]:
        healthy, total = ServiceDiscovery.healthy_count()
        return {
            "services": ServiceDiscovery.registry(),
            "healthy": healthy,
            "total": total,
            "state_transitions": StateTransitionEngine.history(limit=20),
            "legal_transitions": StateTransitionEngine.legal_map(),
        }

    @classmethod
    def dependency_graph(cls) -> dict[str, Any]:
        return ExecutionDependencyGraph.build()

    @classmethod
    def intelligence(cls) -> dict[str, Any]:
        anomalies = RuntimeAnomalyDetection.scan()
        drift = OperationalDriftDetection.detect()
        return {
            "dependency_graph": ExecutionDependencyGraph.build(),
            "context_graph": OperationalContextGraph.build(),
            "lineage": ExecutionLineage.build(),
            "relationships": CrossEventRelationships.analyze(),
            "priority_propagation": PriorityPropagation.propagate(),
            "confidence": ExecutionConfidence.runtime_confidence(),
            "anomalies": anomalies,
            "drift": drift,
            "context_aware_recovery": ContextAwareRecovery.assess(),
        }

    @classmethod
    def resources(cls) -> dict[str, Any]:
        return {"pools": ResourceAllocation.utilisation()}

    @classmethod
    def diagnostics(cls) -> dict[str, Any]:
        return RuntimeDiagnostics.snapshot()

    @classmethod
    def readiness(cls) -> dict[str, Any]:
        return ReadinessScore.compute()

    @classmethod
    def dependencies(cls) -> dict[str, Any]:
        return DependencyMonitor.check()

    @classmethod
    def contexts(cls) -> dict[str, Any]:
        return {"active": MissionContext.active(), "all": MissionContext.list_all()}

    @classmethod
    def capabilities_catalog(cls) -> dict[str, Any]:
        return {
            "capabilities": [
                "event_ingestion", "mission_context", "task_queue", "execution_priority",
                "resource_allocation", "operator_actions", "situation_timeline",
                "alert_pipeline", "decision_recommendation", "sensor_abstraction",
                "external_adapter", "operational_contracts", "execution_audit_chain",
            ],
            "intelligence": [
                "execution_dependency_graph", "operational_context_graph", "execution_lineage",
                "cross_event_relationships", "priority_propagation", "state_transition_engine",
                "context_aware_recovery", "execution_confidence", "runtime_anomaly_detection",
                "operational_drift_detection",
            ],
            "hardening": [
                "runtime_config", "environment_profiles", "secrets_provider", "structured_logger",
                "rate_limiter", "graceful_degradation", "service_discovery", "dependency_monitor",
                "runtime_diagnostics", "readiness_score",
            ],
        }
