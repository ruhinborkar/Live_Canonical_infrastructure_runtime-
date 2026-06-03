
import argparse
import json

from observability.runtime_observer import (
    RuntimeObserver
)

from replay.runtime_replayer import (
    RuntimeReplayer
)

from recovery.interrupted_recovery import (
    InterruptedRecovery
)

from validation.failure_path_executor import (
    FailurePathExecutor
)


def run_live():

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
        "TRUE"
    )

    RuntimeObserver.observe(
        "RECOVERY",
        "RECOVERY_VALIDATED"
    )

    print(
        "\nLIVE EXECUTION COMPLETE"
    )


def run_replay():

    result = (
        RuntimeReplayer.execute_replay()
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )


def run_recover():

    result = (
        InterruptedRecovery.analyze_interruption()
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )


def run_verify():

    result = (
        FailurePathExecutor.execute()
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        type=str,
        default="live"
    )

    args, unknown = parser.parse_known_args()

    print(
        f"\nRUNNING MODE: {args.mode}\n"
    )

    if args.mode == "live":

        run_live()

    elif args.mode == "replay":

        run_replay()

    elif args.mode == "recover":

        run_recover()

    elif args.mode == "verify":

        run_verify()

    else:

        raise ValueError(
            f"Unsupported mode: {args.mode}"
        )
