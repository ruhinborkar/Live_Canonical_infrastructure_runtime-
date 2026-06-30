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
from hardening.low_anomaly_rate_check import evaluate_low_anomaly_rate
from observability.health_monitor import HealthMonitor
from observability.startup_validator import StartupValidator
from runtime.operational_state_manager import OperationalStateManager
from runtime.runtime_heartbeat import RuntimeHeartbeat


class ReadinessScore:
    @classmethod
    def compute(cls) -> dict[str, Any]:
        contributors: list[dict[str, Any]] = []

        def add(
            name: str,
            passed: bool,
            weight: float,
            detail: str = "",
            *,
            extra: dict[str, Any] | None = None,
        ) -> None:
            row: dict[str, Any] = {
                "signal": name,
                "passed": bool(passed),
                "weight": weight,
                "detail": detail,
            }
            if extra:
                row.update(extra)
            contributors.append(row)

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

        anomaly_check = evaluate_low_anomaly_rate()
        add(
            "low_anomaly_rate",
            anomaly_check["counts_for_score"],
            0.5,
            anomaly_check["message"],
            extra={
                "check": anomaly_check["check"],
                "status": anomaly_check["status"],
                "reason": anomaly_check["reason"],
                "intentional_anomalies": anomaly_check["intentional_anomalies"],
                "unexpected_anomalies": anomaly_check["unexpected_anomalies"],
                "production_impact": anomaly_check["production_impact"],
                "message": anomaly_check["message"],
                "failure_injection_active": anomaly_check["failure_injection_active"],
                "anomaly_rate": anomaly_check["anomaly_rate"],
                "threshold": anomaly_check["threshold"],
                "display_status": (
                    "TEST_FAIL"
                    if anomaly_check["status"] == "FAIL"
                    and not anomaly_check["production_impact"]
                    else anomaly_check["status"]
                ),
            },
        )

        total_weight = sum(c["weight"] for c in contributors)
        earned = sum(
            c["weight"]
            for c in contributors
            if c.get("counts_for_score", c["passed"])
        )
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
