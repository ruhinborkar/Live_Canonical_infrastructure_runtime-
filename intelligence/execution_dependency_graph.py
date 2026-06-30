"""Execution dependency graph.

Builds a directed graph where each executed event depends on the prior event
in its trace (and, lacking a trace, on the prior sequence). Reveals execution
ordering and fan-in/fan-out for the dependency visualisation surface.
"""

from typing import Any

from intelligence import live_events


class ExecutionDependencyGraph:
    @classmethod
    def build(cls, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        events = events if events is not None else live_events()
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        last_by_trace: dict[str, Any] = {}
        previous_sequence: Any = None

        for event in events:
            sequence_id = event.get("sequence_id")
            if sequence_id is None:
                continue
            trace_id = event.get("trace_id") or "untraced"
            nodes.append(
                {
                    "id": sequence_id,
                    "trace_id": trace_id,
                    "event_type": event.get("event_type"),
                    "validation_status": event.get("validation_status"),
                }
            )
            parent = last_by_trace.get(trace_id)
            if parent is None and previous_sequence is not None:
                parent = previous_sequence
            if parent is not None and parent != sequence_id:
                edges.append({"from": parent, "to": sequence_id})
            last_by_trace[trace_id] = sequence_id
            previous_sequence = sequence_id

        targets = {e["to"] for e in edges}
        roots = [n["id"] for n in nodes if n["id"] not in targets]
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "roots": roots[:25],
            "nodes": nodes[-100:],
            "edges": edges[-100:],
        }
