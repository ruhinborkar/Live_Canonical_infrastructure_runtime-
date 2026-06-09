
import json
import os


class FinalRuntimeReporter:

    OUTPUT_FILE = (
        "observability/final_runtime_report.json"
    )

    @classmethod
    def export_report(
        cls,
        report
    ):

        os.makedirs(
            os.path.dirname(
                cls.OUTPUT_FILE
            ),
            exist_ok=True
        )

        with open(
            cls.OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        print(
            f"REPORT GENERATED: {cls.OUTPUT_FILE}"
        )

        return cls.OUTPUT_FILE
