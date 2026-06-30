"""Runtime diagnostics.

Aggregates a point-in-time diagnostic snapshot across the operational stack:
process info, configuration, dependency health, degradation mode, heartbeat
liveness, and audit-chain integrity. Used for support/triage and the readiness
score.
"""

import os
import platform
from datetime import datetime, timezone
from typing import Any

from capabilities.execution_audit_chain import ExecutionAuditChain
from config.runtime_config import RuntimeConfig
from hardening.dependency_monitor import DependencyMonitor
from hardening.graceful_degradation import GracefulDegradation
from hardening.service_discovery import ServiceDiscovery
from runtime.operational_state_manager import OperationalStateManager
from runtime.runtime_heartbeat import RuntimeHeartbeat


class RuntimeDiagnostics:
    @classmethod
    def snapshot(cls) -> dict[str, Any]:
        healthy, total = ServiceDiscovery.healthy_count()
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "process": {
                "pid": os.getpid(),
                "python": platform.python_version(),
                "platform": platform.system(),
            },
            "config": RuntimeConfig.load(),
            "operational_state": OperationalStateManager.snapshot(),
            "heartbeat": RuntimeHeartbeat.liveness(),
            "dependencies": DependencyMonitor.check(),
            "degradation": GracefulDegradation.status(),
            "audit_chain": ExecutionAuditChain.verify(),
            "service_registry": {"healthy": healthy, "total": total},
        }
