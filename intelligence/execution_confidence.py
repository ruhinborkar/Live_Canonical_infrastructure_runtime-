"""Execution confidence scoring.

Assigns a 0-1 confidence score to an executed event and to the runtime as a
whole, from generic signals: validation outcome, payload-hash presence, and
recent invalid rate. Higher = more trustworthy execution.
"""

from typing import Any

from intelligence import live_events


class ExecutionConfidence:
    @classmethod
    def score_event(cls, event: dict[str, Any]) -> float:
        score = 1.0
        if event.get("validation_status") == "INVALID":
            score -= 0.6
        if not event.get("payload_hash"):
            score -= 0.2
        if event.get("event_type") in {"CORRUPTED_EVENT", "INTERRUPTED_EVENT"}:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 3)

    @classmethod
    def runtime_confidence(cls, events: list[dict[str, Any]] | None = None, *, window: int = 100) -> dict[str, Any]:
        events = (events if events is not None else live_events())[-window:]
        if not events:
            return {"confidence": 1.0, "sample": 0, "grade": "NOMINAL"}
        scores = [cls.score_event(e) for e in events]
        avg = sum(scores) / len(scores)
        grade = "NOMINAL" if avg >= 0.85 else "DEGRADED" if avg >= 0.6 else "LOW"
        return {
            "confidence": round(avg, 3),
            "sample": len(events),
            "min": round(min(scores), 3),
            "grade": grade,
        }
