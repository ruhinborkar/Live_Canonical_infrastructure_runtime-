import json
import os


class AppendOnlyStore:

    LIVE_LOG = "logging/logs/live_execution.jsonl"

    REPLAY_LOG = "logging/logs/replay_log.jsonl"

    RECOVERY_LOG = "logging/logs/recovery_log.jsonl"

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
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(payload) + "\n"
            )
