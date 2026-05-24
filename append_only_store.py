
import json
import os


class AppendOnlyStore:

    LIVE_LOG = (

        "canonical_infrastructure_runtime/"
        "logging/logs/live_execution.jsonl"
    )

    REPLAY_LOG = (

        "canonical_infrastructure_runtime/"
        "logging/logs/replay_log.jsonl"
    )

    RECOVERY_LOG = (

        "canonical_infrastructure_runtime/"
        "logging/logs/recovery_log.jsonl"
    )

    @staticmethod
    def append_event(
        file_path,
        payload
    ):

        os.makedirs(

            os.path.dirname(file_path),

            exist_ok=True
        )

        with open(
            file_path,
            "a"
        ) as file:

            file.write(
                json.dumps(payload) + "\n"
            )
