"""Priority propagation.

Propagates urgency along the execution dependency graph: if a node is urgent,
its descendants inherit elevated urgency. Generic graph propagation used to
re-rank pending/related work.
"""

from typing import Any

from intelligence.execution_dependency_graph import ExecutionDependencyGraph


class PriorityPropagation:
    @classmethod
    def propagate(cls, seeds: dict[Any, int] | None = None) -> dict[str, Any]:
        graph = ExecutionDependencyGraph.build()
        adjacency: dict[Any, list[Any]] = {}
        for edge in graph["edges"]:
            adjacency.setdefault(edge["from"], []).append(edge["to"])

        # Seed urgency: explicit seeds, else invalid nodes get elevated urgency.
        urgency: dict[Any, int] = dict(seeds or {})
        if not urgency:
            for node in graph["nodes"]:
                if node.get("validation_status") == "INVALID":
                    urgency[node["id"]] = 1

        propagated: dict[Any, int] = dict(urgency)
        frontier = list(urgency.items())
        while frontier:
            node_id, level = frontier.pop()
            for child in adjacency.get(node_id, []):
                inherited = min(9, level + 1)
                if child not in propagated or inherited < propagated[child]:
                    propagated[child] = inherited
                    frontier.append((child, inherited))

        return {
            "seeded_nodes": len(urgency),
            "propagated_nodes": len(propagated),
            "priority_map": {str(k): v for k, v in list(propagated.items())[:100]},
        }
