from pathlib import Path
import json


class SequenceManager:

    SEQUENCE_FILE = Path(
        "logging/logs/sequence_state.json"
    )

    @classmethod
    def next_sequence(cls):

        cls.SEQUENCE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not cls.SEQUENCE_FILE.exists():

            with open(
                cls.SEQUENCE_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    {"last_sequence": 0},
                    file
                )

        with open(
            cls.SEQUENCE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            state = json.load(file)

        next_value = (
            state["last_sequence"] + 1
        )

        with open(
            cls.SEQUENCE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {
                    "last_sequence": next_value
                },
                file
            )

        return next_value
