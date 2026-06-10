from datetime import datetime, timezone

from persistence.append_only_store import AppendOnlyStore


class RuntimeRecovery:
    RECOVERY_LOG = AppendOnlyStore.RECOVERY_LOG

    @staticmethod
    def analyze(events):
        interrupted_events = [
            event
            for event in events
            if event.get("event_type") == "INTERRUPTED_EVENT"
        ]

        recovery_required = len(interrupted_events) > 0

        return {
            "recovery_required": recovery_required,
            "interrupted_events": len(interrupted_events),
            "recovery_status": (
                "RECOVERY_REQUIRED"
                if recovery_required
                else "RECOVERY_NOT_REQUIRED"
            ),
        }

    @classmethod
    def persist_recovery_log(cls, events, recovery_result, *, clear_log: bool = True):
        if clear_log:
            AppendOnlyStore.clear_log(cls.RECOVERY_LOG)

        interrupted_events = [
            event
            for event in events
            if event.get("event_type") == "INTERRUPTED_EVENT"
        ]

        for event in interrupted_events:
            AppendOnlyStore.append_event(
                cls.RECOVERY_LOG,
                {
                    "event_timestamp": event.get(
                        "event_timestamp",
                        datetime.now(timezone.utc).isoformat(),
                    ),
                    "event_type": "RECOVERY_CANDIDATE",
                    "sequence_id": event.get("sequence_id"),
                    "trace_id": event.get("trace_id"),
                    "runtime_state": event.get("runtime_state", "INTERRUPTED"),
                    "payload": event.get("payload", {}),
                    "validation_status": "INVALID",
                    "validation_reason": "execution interrupted",
                    "recovery_status": "PENDING",
                },
            )

        integrity_state = (
            "COMPROMISED" if recovery_result["recovery_required"] else "INTACT"
        )

        AppendOnlyStore.append_event(
            cls.RECOVERY_LOG,
            {
                "event_type": "RECOVERY_VALIDATION",
                "recovery_status": recovery_result["recovery_status"],
                "integrity_state": integrity_state,
                "interrupted_events": recovery_result["interrupted_events"],
                "validation_status": (
                    "INVALID" if recovery_result["recovery_required"] else "VALID"
                ),
                "validation_reason": recovery_result["recovery_status"],
            },
        )

    @staticmethod
    def recover():
        return {
            "recovery_status": "RECOVERY_REQUIRED",
            "integrity_state": "COMPROMISED",
        }
