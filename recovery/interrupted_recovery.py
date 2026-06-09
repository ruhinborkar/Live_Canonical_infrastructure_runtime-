
import json


class InterruptedRecovery:

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
    def analyze_interruption(
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

        sequence_ids = []

        for event in all_events:

            if "sequence_id" in event:

                sequence_ids.append(
                    event["sequence_id"]
                )

        sequence_ids = sorted(
            sequence_ids
        )

        missing_sequences = []

        if sequence_ids:

            start = min(
                sequence_ids
            )

            end = max(
                sequence_ids
            )

            expected = set(
                range(
                    start,
                    end + 1
                )
            )

            actual = set(
                sequence_ids
            )

            missing_sequences = sorted(
                list(
                    expected - actual
                )
            )

        duplicate_sequences = []

        seen = set()

        for sequence_id in sequence_ids:

            if sequence_id in seen:

                duplicate_sequences.append(
                    sequence_id
                )

            seen.add(
                sequence_id
            )

        broken_sequence_continuity = (

            len(
                missing_sequences
            ) > 0

        )

        execution_interrupted = (

            broken_sequence_continuity

            or

            len(
                duplicate_sequences
            ) > 0

        )

        resume_point = None

        if missing_sequences:

            resume_point = (
                missing_sequences[0]
            )

        recovery_outcome = (

            "RECOVERY_REQUIRED"

            if execution_interrupted

            else

            "RECOVERY_NOT_REQUIRED"

        )

        return {

            "execution_interrupted":
                execution_interrupted,

            "broken_sequence_continuity":
                broken_sequence_continuity,

            "missing_sequences":
                missing_sequences,

            "duplicate_sequences":
                duplicate_sequences,

            "resume_point":
                resume_point,

            "recovery_outcome":
                recovery_outcome

        }
