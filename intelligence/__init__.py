"""Runtime intelligence layer.

Generic analytical services that derive structure and insight from the live
runtime event stream: dependency/context graphs, lineage, relationships,
priority propagation, state transitions, context-aware recovery, confidence
scoring, anomaly detection, and operational drift detection.

These services are read-mostly: they observe the canonical live log / ledger
and emit derived views. None of them duplicate the execution pipeline.
"""

from typing import Any

from persistence.append_only_store import AppendOnlyStore
from services.event_loader import read_log_events


def live_events() -> list[dict[str, Any]]:
    """Shared helper: load the canonical live execution stream."""
    return read_log_events(AppendOnlyStore.LIVE_LOG)
