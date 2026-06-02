
import argparse

from canonical_infrastructure_runtime.observability.runtime_observer import RuntimeObserver


def execute_runtime():

    RuntimeObserver.observe(
        "INPUT",
        "EVENT_RECEIVED"
    )

    RuntimeObserver.observe(
        "VALIDATION",
        "PASSED"
    )

    RuntimeObserver.observe(
        "SERIALIZATION",
        "COMPLETED"
    )

    RuntimeObserver.observe(
        "PERSISTENCE",
        "APPEND_ONLY_WRITE"
    )

    RuntimeObserver.observe(
        "REPLAY",
        "COMPLETED"
    )

    RuntimeObserver.observe(
        "VERIFICATION",
        "True"
    )

    RuntimeObserver.observe(
        "RECOVERY",
        "RECOVERY_VALIDATED"
    )

    print(
        "\nRUNTIME EXECUTION COMPLETE"
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        type=str,
        default="live"
    )

    args = parser.parse_args()

    print(
        f"\nRUNTIME MODE: {args.mode}\n"
    )

    execute_runtime()
