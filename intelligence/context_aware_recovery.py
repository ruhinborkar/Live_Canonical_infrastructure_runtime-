"""Context-aware recovery.

Recommends recovery actions using runtime intelligence rather than fixed rules:
it combines anomaly signals, execution confidence, and lineage to suggest which
traces/sequences need recovery and how confident that suggestion is.

Advisory layer over the canonical recovery system — it does not replace
recovery/interrupted_recovery; it enriches it with context.
"""

from typing import Any

from intelligence import live_events
from intelligence.execution_confidence import ExecutionConfidence
from intelligence.runtime_anomaly_detection import RuntimeAnomalyDetection


class ContextAwareRecovery:
    @classmethod
    def assess(cls, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        events = events if events is not None else live_events()
        anomalies = RuntimeAnomalyDetection.scan(events)
        confidence = ExecutionConfidence.runtime_confidence(events)

        suspect_sequences = sorted(
            {
                a.get("sequence_id")
                for a in anomalies["anomalies"]
                if a.get("sequence_id") is not None
                and a.get("type") in {"VALIDATION_FAILURE", "DUPLICATE_SEQUENCE", "MISSING_HASH"}
            }
        )

        if not suspect_sequences and not anomalies["anomalies"]:
            recommendation = "NO_RECOVERY_REQUIRED"
        elif confidence["grade"] == "LOW":
            recommendation = "FULL_CONTEXT_RECOVERY"
        else:
            recommendation = "TARGETED_RECOVERY"

        return {
            "recommendation": recommendation,
            "suspect_sequences": suspect_sequences[:50],
            "anomaly_count": anomalies["anomaly_count"],
            "runtime_confidence": confidence["confidence"],
            "confidence_grade": confidence["grade"],
        }
