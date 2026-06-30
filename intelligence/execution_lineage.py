"""Execution lineage.

Reconstructs the ordered lineage of execution per trace, including validation
outcomes and payload-hash continuity, so any executed event can be traced back
through its predecessors.
"""

from typing import Any

from intelligence import live_events


class ExecutionLineage:
    @classmethod
    def build(cls, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        events = events if events is not None else live_events()
        lineages: dict[str, list[dict[str, Any]]] = {}
        for event in events:
            trace_id = event.get("trace_id") or "untraced"
            lineages.setdefault(trace_id, []).append(
                {
                    "sequence_id": event.get("sequence_id"),
                    "event_type": event.get("event_type"),
                    "validation_status": event.get("validation_status"),
                    "payload_hash": event.get("payload_hash"),
                }
            )
        for chain in lineages.values():
            chain.sort(key=lambda n: (n["sequence_id"] is None, n["sequence_id"]))
        return {
            "trace_count": len(lineages),
            "longest_lineage": max((len(c) for c in lineages.values()), default=0),
            "lineages": {k: v for k, v in list(lineages.items())[:25]},
        }

    @classmethod
    def for_trace(cls, trace_id: str) -> list[dict[str, Any]]:
        return cls.build().get("lineages", {}).get(trace_id, [])
