"""Low anomaly rate readiness check with intentional vs unexpected classification.

Distinguishes anomalies from hostile validation / failure-injection testing
from anomalies that indicate real production-health issues. The check may
remain visibly FAIL during injection testing while production_impact stays false.
"""

import json
from pathlib import Path
from typing import Any

from intelligence import live_events
from intelligence.runtime_anomaly_detection import RuntimeAnomalyDetection

PROOF_FILE = Path("failure_injection_proof.json")
DEFAULT_THRESHOLD = 0.3

INTENTIONAL_EVENT_TYPES = frozenset({"CORRUPTED_EVENT", "INTERRUPTED_EVENT"})
INTENTIONAL_VALIDATION_FRAGMENTS = (
    "corrupted event type",
    "mutated signal detected",
    "invalid payload",
)


def _failure_injection_proof() -> dict[str, Any] | None:
    if not PROOF_FILE.exists():
        return None
    try:
        return json.loads(PROOF_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def failure_injection_active() -> bool:
    """True when hostile validation has been executed and detected scenarios."""
    proof = _failure_injection_proof()
    return bool(proof and proof.get("detected_count", 0) > 0)


def _event_index(events: list[dict[str, Any]]) -> dict[Any, dict[str, Any]]:
    index: dict[Any, dict[str, Any]] = {}
    for event in events:
        seq = event.get("sequence_id")
        if seq is not None:
            index[seq] = event
    return index


def _is_intentional_event(event: dict[str, Any] | None) -> bool:
    if not event:
        return False
    if event.get("event_type") in INTENTIONAL_EVENT_TYPES:
        return True
    reason = str(event.get("validation_reason", "")).lower()
    if any(fragment in reason for fragment in INTENTIONAL_VALIDATION_FRAGMENTS):
        return True
    # Canonical batch/demo pipeline events (no operational processed_at stamp).
    if event.get("processed_at") is None and event.get("task_id") is None:
        return True
    return False


def _classify_anomaly(anomaly: dict[str, Any], event_index: dict[Any, dict[str, Any]]) -> str:
    seq = anomaly.get("sequence_id")
    event = event_index.get(seq) if seq is not None else None
    trace = anomaly.get("trace_id") or (event or {}).get("trace_id")

    if _is_intentional_event(event):
        return "intentional"

    # Sequence gaps in canonical/demo traces (non-session) are expected after demo/inject.
    if anomaly.get("type") == "SEQUENCE_GAP" and trace and not str(trace).startswith("session-"):
        return "intentional"

    return "unexpected"


def evaluate_low_anomaly_rate(
    *,
    threshold: float = DEFAULT_THRESHOLD,
    window: int = 100,
) -> dict[str, Any]:
    events = live_events()[-window:]
    scan = RuntimeAnomalyDetection.scan(events, window=window)
    event_index = _event_index(events)

    intentional = 0
    unexpected = 0
    for anomaly in scan.get("anomalies", []):
        if _classify_anomaly(anomaly, event_index) == "intentional":
            intentional += 1
        else:
            unexpected += 1

    rate = scan.get("anomaly_rate", 0.0)
    injection_active = failure_injection_active() or intentional > 0
    under_threshold = rate <= threshold

    if under_threshold and unexpected == 0:
        status = "PASS"
        reason = "Anomaly rate within acceptable threshold"
        message = f"Anomaly rate {rate} is within threshold {threshold}."
        production_impact = False
        counts_for_score = True
    elif injection_active and unexpected == 0:
        status = "FAIL"
        reason = "Failure Injection Test Active"
        message = (
            f"{intentional} intentional anomal{'y' if intentional == 1 else 'ies'} detected. "
            "No unexpected production anomalies."
        )
        production_impact = False
        counts_for_score = True
    else:
        status = "FAIL"
        reason = "Unexpected runtime anomalies detected"
        if unexpected > 0:
            message = (
                f"{unexpected} unexpected production anomal{'y' if unexpected == 1 else 'ies'} detected. "
                "Production readiness impacted."
            )
        else:
            message = f"Anomaly rate {rate} exceeds threshold {threshold}. Production readiness impacted."
        production_impact = True
        counts_for_score = False

    return {
        "check": "low_anomaly_rate",
        "status": status,
        "passed": status == "PASS",
        "reason": reason,
        "intentional_anomalies": intentional,
        "unexpected_anomalies": unexpected,
        "production_impact": production_impact,
        "message": message,
        "failure_injection_active": injection_active,
        "anomaly_rate": rate,
        "threshold": threshold,
        "analysed_events": scan.get("analysed_events", 0),
        "counts_for_score": counts_for_score,
    }
