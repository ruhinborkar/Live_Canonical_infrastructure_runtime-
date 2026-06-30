"""Operational drift detection.

Compares a recent window of execution against an earlier baseline window to
detect drift in the invalid-event rate. Generic statistical comparison; no
domain thresholds beyond a configurable tolerance.
"""

from typing import Any

from intelligence import live_events


class OperationalDriftDetection:
    @classmethod
    def detect(
        cls,
        events: list[dict[str, Any]] | None = None,
        *,
        window: int = 50,
        tolerance: float = 0.15,
    ) -> dict[str, Any]:
        events = events if events is not None else live_events()
        if len(events) < window * 2:
            return {
                "drift_detected": False,
                "reason": "insufficient_history",
                "baseline_invalid_rate": None,
                "recent_invalid_rate": None,
            }

        baseline = events[-window * 2 : -window]
        recent = events[-window:]

        baseline_rate = cls._invalid_rate(baseline)
        recent_rate = cls._invalid_rate(recent)
        delta = round(recent_rate - baseline_rate, 3)
        drift = abs(delta) > tolerance

        return {
            "drift_detected": drift,
            "baseline_invalid_rate": baseline_rate,
            "recent_invalid_rate": recent_rate,
            "delta": delta,
            "tolerance": tolerance,
            "summary": (
                f"Invalid rate moved {delta:+.3f} (baseline {baseline_rate} -> recent {recent_rate})"
                if drift
                else "No significant drift"
            ),
        }

    @staticmethod
    def _invalid_rate(events: list[dict[str, Any]]) -> float:
        if not events:
            return 0.0
        invalid = sum(1 for e in events if e.get("validation_status") == "INVALID")
        return round(invalid / len(events), 3)
