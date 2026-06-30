"""Operational readiness scoring.

Computes a 0-10 production readiness score from weighted operational signals:
startup validation, engine liveness, heartbeat freshness, subsystem health,
dependency health, audit-chain integrity, degradation mode, and anomaly rate.
Each contributor is transparent so the score is explainable, not a black box.
"""

from typing import Any

from capabilities.execution_audit_chain import ExecutionAuditChain
from hardening.dependency_monitor import DependencyMonitor
from hardening.graceful_degradation import GracefulDegradation
from intelligence.runtime_anomaly_detection import RuntimeAnomalyDetection
from observability.health_monitor import HealthMonitor
from observability.startup_validator import StartupValidator
from runtime.operational_state_manager import OperationalStateManager
from runtime.runtime_heartbeat import RuntimeHeartbeat


class ReadinessScore:
    @classmethod
    def compute(cls) -> dict[str, Any]:
        contributors: list[dict[str, Any]] = []

        def add(name: str, passed: bool, weight: float, detail: str = "") -> None:
            contributors.append(
                {"signal": name, "passed": bool(passed), "weight": weight, "detail": detail}
            )

        startup = StartupValidator.validate()
        add("startup_validation", startup.get("ready", False), 1.5, startup.get("status", ""))

        state = OperationalStateManager.current_state()
        add("engine_running", state in {"RUNNING", "DEGRADED"}, 2.0, f"state={state}")

        hb = RuntimeHeartbeat.liveness()
        add("heartbeat_alive", hb.get("alive", False), 1.5, f"tick={hb.get('heartbeat_tick')}")

        health = HealthMonitor.get_status()
        add("subsystem_health", health.get("overall") in {"HEALTHY", "DEGRADED"}, 1.5,
            health.get("overall", ""))

        deps = DependencyMonitor.check()
        add("dependencies", deps.get("healthy", False), 1.5,
            f"{deps.get('healthy_count')}/{deps.get('total')}")

        audit = ExecutionAuditChain.verify()
        add("audit_chain_intact", audit.get("intact", True), 1.0, f"entries={audit.get('entries')}")

        mode = GracefulDegradation.mode()
        add("degradation_mode", mode != "CRITICAL", 0.5, f"mode={mode}")

        anomalies = RuntimeAnomalyDetection.scan()
        add("low_anomaly_rate", anomalies.get("anomaly_rate", 0.0) <= 0.3, 0.5,
            f"rate={anomalies.get('anomaly_rate')}")

        total_weight = sum(c["weight"] for c in contributors)
        earned = sum(c["weight"] for c in contributors if c["passed"])
        score10 = round(10 * earned / total_weight, 1) if total_weight else 0.0

        if score10 >= 9:
            grade = "PRODUCTION_READY"
        elif score10 >= 7:
            grade = "OPERATIONAL"
        elif score10 >= 5:
            grade = "DEGRADED"
        else:
            grade = "NOT_READY"

        return {
            "score": score10,
            "max": 10,
            "grade": grade,
            "earned_weight": round(earned, 2),
            "total_weight": round(total_weight, 2),
            "contributors": contributors,
        }
