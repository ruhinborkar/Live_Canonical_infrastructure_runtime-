
class RuntimeValidator:

    REQUIRED_FIELDS = [
        "trace_id",
        "sequence_id",
        "runtime_state",
        "event_type",
        "payload",
    ]

    @staticmethod
    def validate(event):
        for field in RuntimeValidator.REQUIRED_FIELDS:
            if field not in event:
                return {
                    "valid": False,
                    "reason": f"missing field: {field}",
                }

        if event.get("event_type") == "CORRUPTED_EVENT":
            return {
                "valid": False,
                "reason": "corrupted event type",
            }

        payload = event.get("payload", {})

        if payload.get("temperature") is None:
            return {
                "valid": False,
                "reason": "invalid payload: temperature is null",
            }

        if payload.get("signal") == "MUTATED":
            return {
                "valid": False,
                "reason": "mutated signal detected",
            }

        return {
            "valid": True,
            "reason": "ok",
        }
