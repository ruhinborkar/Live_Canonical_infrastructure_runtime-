"""Operational context graph.

Groups executed events by mission/operational context, producing a graph of
contexts -> events and aggregate health per context. Powers context-grouped
situation awareness.
"""

from typing import Any

from intelligence import live_events


class OperationalContextGraph:
    @classmethod
    def build(cls, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        events = events if events is not None else live_events()
        contexts: dict[str, dict[str, Any]] = {}
        for event in events:
            context_id = event.get("context_id") or "uncontextualised"
            bucket = contexts.setdefault(
                context_id,
                {"context_id": context_id, "events": 0, "valid": 0, "invalid": 0, "traces": set()},
            )
            bucket["events"] += 1
            if event.get("validation_status") == "VALID":
                bucket["valid"] += 1
            elif event.get("validation_status") == "INVALID":
                bucket["invalid"] += 1
            if event.get("trace_id"):
                bucket["traces"].add(event["trace_id"])

        nodes = []
        for bucket in contexts.values():
            total = bucket["events"] or 1
            nodes.append(
                {
                    "context_id": bucket["context_id"],
                    "events": bucket["events"],
                    "valid": bucket["valid"],
                    "invalid": bucket["invalid"],
                    "trace_count": len(bucket["traces"]),
                    "health_pct": round(100 * bucket["valid"] / total, 1),
                }
            )
        return {"context_count": len(nodes), "contexts": nodes}
