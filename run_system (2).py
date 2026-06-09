import json

from datasets.runtime_dataset_generator import RuntimeDatasetGenerator
from datasets.runtime_dataset_loader import RuntimeDatasetLoader

from validation.runtime_validator import RuntimeValidator

from serialization.canonical_serializer import CanonicalSerializer
from hashing.runtime_hasher import RuntimeHasher
from persistence.append_only_store import AppendOnlyStore

from replay.runtime_replayer import RuntimeReplayer
from replay.runtime_reconstructor import RuntimeReconstructor

from recovery.runtime_recovery import RuntimeRecovery

from observability.runtime_observer import RuntimeObserver
from observability.final_runtime_reporter import FinalRuntimeReporter


def execute_runtime():
    RuntimeObserver.observe(
        "INPUT",
        "DATASET_GENERATION_STARTED"
    )

    dataset_summary = RuntimeDatasetGenerator.generate()

    RuntimeObserver.observe(
        "INPUT",
        "DATASET_LOADED"
    )

    events = RuntimeDatasetLoader.load_events()

    AppendOnlyStore.clear_log(
        AppendOnlyStore.LIVE_LOG
    )

    processed_events = 0
    valid_events = 0
    invalid_events = 0

    for event in events:
        validation_result = RuntimeValidator.validate(event)

        if validation_result["valid"]:
            valid_events += 1
        else:
            invalid_events += 1

        serialized_payload = CanonicalSerializer.serialize(
            event.get("payload", {})
        )

        payload_hash = RuntimeHasher.generate_hash(
            serialized_payload
        )

        runtime_event = dict(event)

        runtime_event["payload_hash"] = payload_hash
        runtime_event["validation_status"] = (
            "VALID"
            if validation_result["valid"]
            else "INVALID"
        )
        runtime_event["validation_reason"] = validation_result["reason"]

        AppendOnlyStore.append_event(
            AppendOnlyStore.LIVE_LOG,
            runtime_event
        )

        processed_events += 1

    RuntimeObserver.observe(
        "VALIDATION",
        "COMPLETED"
    )

    RuntimeObserver.observe(
        "SERIALIZATION",
        "COMPLETED"
    )

    RuntimeObserver.observe(
        "HASHING",
        "COMPLETED"
    )

    RuntimeObserver.observe(
        "PERSISTENCE",
        "APPEND_ONLY_WRITE_COMPLETED"
    )

    replay_result = RuntimeReplayer.execute_replay()

    RuntimeObserver.observe(
        "REPLAY",
        replay_result["verification_result"]
    )

    reconstruction_result = RuntimeReconstructor.reconstruct()

    RuntimeObserver.observe(
        "VERIFICATION",
        reconstruction_result["truth_verification"]
    )

    recovery_result = RuntimeRecovery.analyze(events)

    RuntimeObserver.observe(
        "RECOVERY",
        (
            "RECOVERY_REQUIRED"
            if recovery_result["recovery_required"]
            else "RECOVERY_NOT_REQUIRED"
        )
    )

    final_report = {
        "dataset": dataset_summary,
        "runtime_execution": {
            "processed_events": processed_events,
            "valid_events": valid_events,
            "invalid_events": invalid_events
        },
        "replay": replay_result,
        "truth_reconstruction": {
            "events_reconstructed": reconstruction_result[
                "events_reconstructed"
            ],
            "truth_verification": reconstruction_result[
                "truth_verification"
            ]
        },
        "recovery": recovery_result
    }

    report_path = FinalRuntimeReporter.export_report(
        final_report
    )

    RuntimeObserver.observe(
        "OBSERVABILITY",
        "REPORT_GENERATED"
    )

    print("\nLIVE EXECUTION COMPLETE")
    print("REPLAY VERIFIED")
    print(reconstruction_result["truth_verification"])
    print("OBSERVABILITY GENERATED")

    print(
        json.dumps(
            final_report,
            indent=4
        )
    )

    print(
        f"\nREPORT PATH: {report_path}"
    )


if __name__ == "__main__":
    execute_runtime()
