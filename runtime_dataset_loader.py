import json


class RuntimeDatasetLoader:
    DATASET_FILE = "datasets/runtime_dataset.jsonl"

    @classmethod
    def load_events(cls):
        events = []

        with open(cls.DATASET_FILE, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    events.append(json.loads(line))

        return events
