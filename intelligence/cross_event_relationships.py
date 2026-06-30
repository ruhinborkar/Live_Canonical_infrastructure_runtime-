"""Cross-event relationships.

Detects generic relationships between executed events: shared trace, adjacent
sequence, and shared payload signal keys. Feeds correlation views without any
domain-specific semantics.
"""

from typing import Any

from intelligence import live_events


class CrossEventRelationships:
    @classmethod
    def analyze(cls, events: list[dict[str, Any]] | None = None, *, window: int = 60) -> dict[str, Any]:
        events = (events if events is not None else live_events())[-window:]
        relationships: list[dict[str, Any]] = []
        for i in range(len(events)):
            a = events[i]
            for j in range(i + 1, len(events)):
                b = events[j]
                links = cls._links(a, b)
                if links:
                    relationships.append(
                        {
                            "from": a.get("sequence_id"),
                            "to": b.get("sequence_id"),
                            "relations": links,
                        }
                    )
        return {
            "analysed_events": len(events),
            "relationship_count": len(relationships),
            "relationships": relationships[:150],
        }

    @staticmethod
    def _links(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
        links: list[str] = []
        if a.get("trace_id") and a.get("trace_id") == b.get("trace_id"):
            links.append("SAME_TRACE")
        sa, sb = a.get("sequence_id"), b.get("sequence_id")
        if isinstance(sa, int) and isinstance(sb, int) and abs(sa - sb) == 1:
            links.append("ADJACENT_SEQUENCE")
        pa = set((a.get("payload") or {}).keys())
        pb = set((b.get("payload") or {}).keys())
        if pa and pa == pb:
            links.append("SHARED_PAYLOAD_SHAPE")
        return links
