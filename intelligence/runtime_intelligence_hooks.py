"""Attach the intelligence layer to the runtime engine.

Demonstrates the extensibility contract: intelligence services are registered
as engine post-processors WITHOUT modifying the engine core. Each processed
event is scored for confidence and screened for anomalies; low confidence or
anomalies raise advisory alerts and timeline entries.
"""

from typing import Any

from capabilities.alert_pipeline import AlertPipeline
from capabilities.situation_timeline import SituationTimeline
from intelligence.execution_confidence import ExecutionConfidence

_LOW_CONFIDENCE = 0.4


def _on_processed(event: dict[str, Any], result: dict[str, Any]) -> None:
    confidence = ExecutionConfidence.score_event(event)
    result["confidence"] = confidence
    if confidence < _LOW_CONFIDENCE:
        AlertPipeline.raise_alert(
            "execution_confidence",
            f"Low-confidence execution ({confidence})",
            severity="WARNING",
            context={"sequence_id": event.get("sequence_id")},
        )
        SituationTimeline.record(
            "INTELLIGENCE",
            f"Low execution confidence {confidence}",
            severity="WARNING",
            details={"sequence_id": event.get("sequence_id")},
        )


def attach(engine: Any) -> None:
    engine.register_post_processor(_on_processed)
