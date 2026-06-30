"""Decision recommendation interface.

Turns current operational signals (alerts, queue depth, drift, anomalies) into
ranked, generic recommendations to support — never replace — operator
decisions. Output is advisory only; it takes no autonomous action.
"""

from datetime import datetime, timezone
from typing import Any

from capabilities.alert_pipeline import AlertPipeline
from capabilities.task_queue import TaskQueue


class DecisionRecommendation:
    @classmethod
    def recommend(cls, *, drift: dict[str, Any] | None = None, anomalies: int = 0) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        recommendations: list[dict[str, Any]] = []

        alert_summary = AlertPipeline.summary()
        if alert_summary["critical"] > 0:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "INVESTIGATE_CRITICAL_ALERTS",
                    "rationale": f"{alert_summary['critical']} critical alert(s) active",
                }
            )
        pending = TaskQueue.pending()
        if pending > 50:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "SCALE_WORKERS",
                    "rationale": f"Queue depth {pending} exceeds comfort threshold",
                }
            )
        if drift and drift.get("drift_detected"):
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "REVIEW_OPERATIONAL_DRIFT",
                    "rationale": drift.get("summary", "Operational drift detected"),
                }
            )
        if anomalies > 0:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "TRIAGE_ANOMALIES",
                    "rationale": f"{anomalies} runtime anomaly signal(s)",
                }
            )
        if not recommendations:
            recommendations.append(
                {
                    "priority": "LOW",
                    "action": "MAINTAIN",
                    "rationale": "Runtime nominal; continue normal operations",
                }
            )

        return {"generated_at": now, "recommendations": recommendations}
