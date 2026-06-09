import json


class CanonicalSerializer:
    @staticmethod
    def serialize(payload):
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":")
        )
