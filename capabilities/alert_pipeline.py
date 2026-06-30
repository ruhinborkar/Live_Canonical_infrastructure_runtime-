"""Generic alert pipeline.

Raises, routes, and tracks acknowledgement of operational alerts.
Inputs: alert signals (severity + reason) from engine/intelligence/capabilities.
Outputs: active + historical alerts for escalation surfaces.
Authority: classifies and tracks alerts; does not take corrective action.
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from persistence.append_only_store import AppendOnlyStore
from services.event_loader import read_log_events

ALERT_LOG = "logging/logs/alerts.jsonl"

SEVERITY_RANK = {"INFO": 0, "WARNING": 1, "CRITICAL": 2}


class AlertPipeline:
    _lock = threading.RLock()
    _active: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def raise_alert(
        cls,
        source: str,
        reason: str,
        *,
        severity: str = "WARNING",
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with cls._lock:
            alert = {
                "alert_id": str(uuid.uuid4()),
                "source": source,
                "reason": reason,
                "severity": severity if severity in SEVERITY_RANK else "WARNING",
                "context": context or {},
                "raised_at": cls._now(),
                "acknowledged": False,
                "acknowledged_at": None,
            }
            cls._active[alert["alert_id"]] = alert
            AppendOnlyStore.append_event(ALERT_LOG, {**alert, "event": "RAISED"})
            return alert

    @classmethod
    def acknowledge(cls, alert_id: str, operator: str = "operator") -> dict[str, Any] | None:
        with cls._lock:
            alert = cls._active.get(alert_id)
            if not alert:
                return None
            alert["acknowledged"] = True
            alert["acknowledged_at"] = cls._now()
            alert["acknowledged_by"] = operator
            AppendOnlyStore.append_event(ALERT_LOG, {**alert, "event": "ACKNOWLEDGED"})
            cls._active.pop(alert_id, None)
            return alert

    @classmethod
    def active(cls) -> list[dict[str, Any]]:
        with cls._lock:
            return sorted(
                cls._active.values(),
                key=lambda a: (-SEVERITY_RANK.get(a["severity"], 1), a["raised_at"]),
            )

    @classmethod
    def summary(cls) -> dict[str, Any]:
        with cls._lock:
            active = list(cls._active.values())
            return {
                "active_count": len(active),
                "critical": sum(1 for a in active if a["severity"] == "CRITICAL"),
                "warning": sum(1 for a in active if a["severity"] == "WARNING"),
                "info": sum(1 for a in active if a["severity"] == "INFO"),
                "alerts": cls.active(),
            }

    @classmethod
    def history(cls, limit: int = 100) -> list[dict[str, Any]]:
        return list(reversed(read_log_events(ALERT_LOG)[-limit:]))

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._active = {}
