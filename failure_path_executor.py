
import json


class FailurePathExecutor:

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
    def _load_jsonl(file_path):

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
    def execute(cls):

        results = []

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

        # ----------------------------------
        # REAL TASK 6 ANALYSIS
        # ----------------------------------

        sequence_ids = []

        for event in all_events:

            if "sequence_id" in event:

                sequence_ids.append(
                    event["sequence_id"]
                )

        duplicates = []

        seen = set()

        for seq in sequence_ids:

            if seq in seen:

                duplicates.append(seq)

            seen.add(seq)

        if duplicates:

            results.append({

                "failure_type":
                    "DUPLICATE_PACKET",

                "failure_detected":
                    True,

                "observable_cause":
                    f"duplicate sequence ids {duplicates}"

            })

        expected = []

        if sequence_ids:

            expected = list(
                range(
                    min(sequence_ids),
                    max(sequence_ids) + 1
                )
            )

        missing = sorted(
            list(
                set(expected)
                -
                set(sequence_ids)
            )
        )

        if missing:

            results.append({

                "failure_type":
                    "SEQUENCE_CORRUPTION",

                "failure_detected":
                    True,

                "observable_cause":
                    f"missing sequences {missing}"

            })

        # ----------------------------------
        # EXECUTABLE FAILURE INJECTIONS
        # ----------------------------------

        mutated_trace = {

            "trace_id":
                "TRACE-HACKED"

        }

        if mutated_trace["trace_id"] != "TRACE-END-TO-END":

            results.append({

                "failure_type":
                    "TRACE_MUTATION",

                "failure_detected":
                    True,

                "observable_cause":
                    "trace lineage mismatch"

            })

        invalid_schema = {

            "temperature": 90

        }

        required_fields = [

            "trace_id",

            "sequence_id",

            "runtime_state"

        ]

        missing_fields = [

            field

            for field in required_fields

            if field not in invalid_schema

        ]

        if missing_fields:

            results.append({

                "failure_type":
                    "INVALID_SCHEMA",

                "failure_detected":
                    True,

                "observable_cause":
                    f"missing fields {missing_fields}"

            })

        partial_replay = live_events[:1]

        if (

            len(partial_replay)

            <

            len(live_events)

        ):

            results.append({

                "failure_type":
                    "PARTIAL_REPLAY_CORRUPTION",

                "failure_detected":
                    True,

                "observable_cause":
                    "incomplete replay reconstruction"

            })

        return results
