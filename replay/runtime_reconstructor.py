
import json


class RuntimeReconstructor:

    LIVE_LOG = (
        "logging/logs/live_execution.jsonl"
    )

    REPLAY_LOG = (
        "logging/logs/replay_log.jsonl"
    )

    RECOVERY_LOG = (
        "logging/logs/recovery_log.jsonl"
    )

    @staticmethod
    def _load_jsonl(
        file_path
    ):

        events = []

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                for line in file:

                    line = line.strip()

                    if not line:
                        continue

                    events.append(
                        json.loads(line)
                    )

        except FileNotFoundError:

            pass

        return events

    @classmethod
    def reconstruct(
        cls
    ):

        live_events = cls._load_jsonl(
            cls.LIVE_LOG
        )

        replay_events = cls._load_jsonl(
            cls.REPLAY_LOG
        )

        recovery_events = cls._load_jsonl(
            cls.RECOVERY_LOG
        )

        all_events = (

            live_events
            +
            replay_events
            +
            recovery_events

        )

        trace_lineage = []

        sequence_order = []

        execution_state = None

        runtime_outcome = None

        verification_state = None

        recovery_status = None

        for event in all_events:

            if "trace_id" in event:

                trace_lineage.append(
                    event["trace_id"]
                )

            if "sequence_id" in event:

                sequence_order.append(
                    event["sequence_id"]
                )

            if "runtime_state" in event:

                execution_state = (
                    event["runtime_state"]
                )

            if (
                event.get(
                    "event_type"
                )
                ==
                "REPLAY_VALIDATION"
            ):

                runtime_outcome = (
                    event.get(
                        "status"
                    )
                )

            if (
                event.get(
                    "event_type"
                )
                ==
                "RECOVERY_VALIDATION"
            ):

                recovery_status = (
                    event.get(
                        "recovery_status"
                    )
                )

                verification_state = (
                    event.get(
                        "integrity_state"
                    )
                )

        duplicate_sequences = []

        seen = set()

        for sequence_id in sequence_order:

            if sequence_id in seen:

                duplicate_sequences.append(
                    sequence_id
                )

            seen.add(
                sequence_id
            )

        sequence_integrity = (

            len(
                duplicate_sequences
            )
            ==
            0

        )

        ordered_sequence = (

            sequence_order
            ==
            sorted(sequence_order)

        )

        if sequence_integrity and ordered_sequence:
            truth_verification = "TRUTH_VERIFIED"
        else:
            truth_verification = "TRUTH_MISMATCH"

        return {

            "events_reconstructed":
                len(all_events),

            "execution_state":
                execution_state,

            "trace_lineage":
                trace_lineage,

            "sequence_order":
                sequence_order,

            "ordered_sequence":
                ordered_sequence,

            "duplicate_sequences":
                duplicate_sequences,

            "sequence_integrity":
                sequence_integrity,

            "runtime_outcome":
                runtime_outcome,

            "verification_state":
                verification_state,

            "recovery_status":
                recovery_status,

            "truth_verification":
                truth_verification,

        }
