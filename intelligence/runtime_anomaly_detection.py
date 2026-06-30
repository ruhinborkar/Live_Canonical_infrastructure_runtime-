"""Runtime anomaly detection.

Scans the recent execution stream for generic anomalies: validation failures,
sequence gaps, duplicate sequences, and missing payload hashes. Emits anomaly
records for the alert/decision surfaces.
"""

from typing import Any

from intelligence import live_events


class RuntimeAnomalyDetection:
    @classmethod
    def scan(cls, events: list[dict[str, Any]] | None = None, *, window: int = 100) -> dict[str, Any]:
        events = (events if events is not None else live_events())[-window:]
        anomalies: list[dict[str, Any]] = []

        seen_sequences: set[Any] = set()
        per_trace: dict[str, list[int]] = {}
        for event in events:
            seq = event.get("sequence_id")
            trace = event.get("trace_id") or "untraced"
            if event.get("validation_status") == "INVALID":
                anomalies.append({"type": "VALIDATION_FAILURE", "sequence_id": seq,
                                  "detail": event.get("validation_reason")})
            if not event.get("payload_hash"):
                anomalies.append({"type": "MISSING_HASH", "sequence_id": seq})
            key = (trace, seq)
            if key in seen_sequences:
                anomalies.append({"type": "DUPLICATE_SEQUENCE", "sequence_id": seq, "trace_id": trace})
            seen_sequences.add(key)
            if isinstance(seq, int):
                per_trace.setdefault(trace, []).append(seq)

        # Gaps are only meaningful within a single trace's own sequence.
        for trace, seqs in per_trace.items():
            if len(seqs) < 2:
                continue
            seqs.sort()
            for prev, nxt in zip(seqs, seqs[1:]):
                if nxt - prev > 1:
                    anomalies.append({"type": "SEQUENCE_GAP", "trace_id": trace, "from": prev, "to": nxt})

        return {
            "analysed_events": len(events),
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:100],
            "anomaly_rate": round(len(anomalies) / len(events), 3) if events else 0.0,
        }
