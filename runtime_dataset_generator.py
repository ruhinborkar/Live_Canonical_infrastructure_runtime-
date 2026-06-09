import json
import os
from datetime import datetime, timezone


class RuntimeDatasetGenerator:
    OUTPUT_FILE = "datasets/runtime_dataset.jsonl"

    @classmethod
    def generate(cls):
        os.makedirs("datasets", exist_ok=True)

        events = []

        for sequence_id in range(1, 81):
            events.append({
                "trace_id": f"TRACE-{sequence_id % 5}",
                "event_timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "NORMAL_EVENT",
                "runtime_state": "OPERATIONAL",
                "sequence_id": sequence_id,
                "payload": {
                    "signal": "ACTIVE",
                    "temperature": 70 + (sequence_id % 20)
                }
            })

        for sequence_id in range(81, 91):
            events.append({
                "trace_id": f"TRACE-{sequence_id % 5}",
                "event_timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "CORRUPTED_EVENT",
                "runtime_state": "CORRUPTED",
                "sequence_id": sequence_id,
                "payload": {
                    "signal": "MUTATED",
                    "temperature": None
                }
            })

        for sequence_id in range(91, 101):
            events.append({
                "trace_id": f"TRACE-{sequence_id % 5}",
                "event_timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "INTERRUPTED_EVENT",
                "runtime_state": "INTERRUPTED",
                "sequence_id": sequence_id,
                "payload": {
                    "signal": "INTERRUPTED",
                    "temperature": 0
                }
            })

        with open(cls.OUTPUT_FILE, "w", encoding="utf-8") as file:
            for event in events:
                file.write(json.dumps(event, sort_keys=True) + "\n")

        return {
            "dataset_file": cls.OUTPUT_FILE,
            "total_events": len(events),
            "normal_events": 80,
            "corrupted_events": 10,
            "interrupted_events": 10,
            "trace_count": 5
        }
