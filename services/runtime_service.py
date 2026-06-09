from typing import Any, Callable

from datasets.runtime_dataset_generator import RuntimeDatasetGenerator
from datasets.runtime_dataset_loader import RuntimeDatasetLoader
from hashing.runtime_hasher import RuntimeHasher
from observability.final_runtime_reporter import FinalRuntimeReporter
from observability.runtime_observer import RuntimeObserver
from persistence.append_only_store import AppendOnlyStore
from recovery.interrupted_recovery import InterruptedRecovery
from recovery.runtime_recovery import RuntimeRecovery
from replay.runtime_reconstructor import RuntimeReconstructor
from replay.runtime_replayer import RuntimeReplayer
from serialization.canonical_serializer import CanonicalSerializer
from validation.failure_path_executor import FailurePathExecutor
from validation.runtime_validator import RuntimeValidator

StageCallback = Callable[[str, str], None]


class RuntimeService:
    @staticmethod
    def _observe(stage: str, status: str) -> None:
        RuntimeObserver.observe(stage, status)

    @classmethod
    def execute_live(cls) -> dict[str, Any]:
        cls._observe("INPUT", "DATASET_GENERATION_STARTED")
        dataset_summary = RuntimeDatasetGenerator.generate()

        cls._observe("INPUT", "DATASET_LOADED")
        events = RuntimeDatasetLoader.load_events()

        AppendOnlyStore.clear_log(AppendOnlyStore.LIVE_LOG)

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
            payload_hash = RuntimeHasher.generate_hash(serialized_payload)

            runtime_event = dict(event)
            runtime_event["payload_hash"] = payload_hash
            runtime_event["validation_status"] = (
                "VALID" if validation_result["valid"] else "INVALID"
            )
            runtime_event["validation_reason"] = validation_result["reason"]

            AppendOnlyStore.append_event(AppendOnlyStore.LIVE_LOG, runtime_event)
            processed_events += 1

        cls._observe("VALIDATION", "COMPLETED")
        cls._observe("SERIALIZATION", "COMPLETED")
        cls._observe("HASHING", "COMPLETED")
        cls._observe("PERSISTENCE", "APPEND_ONLY_WRITE_COMPLETED")

        replay_result = RuntimeReplayer.execute_replay()
        cls._observe("REPLAY", replay_result["verification_result"])

        reconstruction_result = RuntimeReconstructor.reconstruct()
        cls._observe("VERIFICATION", reconstruction_result["truth_verification"])

        recovery_result = RuntimeRecovery.analyze(events)
        cls._observe(
            "RECOVERY",
            "RECOVERY_REQUIRED"
            if recovery_result["recovery_required"]
            else "RECOVERY_NOT_REQUIRED",
        )

        final_report = {
            "dataset": dataset_summary,
            "runtime_execution": {
                "processed_events": processed_events,
                "valid_events": valid_events,
                "invalid_events": invalid_events,
            },
            "replay": replay_result,
            "truth_reconstruction": {
                "events_reconstructed": reconstruction_result["events_reconstructed"],
                "truth_verification": reconstruction_result["truth_verification"],
            },
            "recovery": recovery_result,
        }

        report_path = FinalRuntimeReporter.export_report(final_report)
        cls._observe("OBSERVABILITY", "REPORT_GENERATED")

        return {
            **final_report,
            "report_path": report_path,
            "status": "completed",
            "replay_status": replay_result["verification_result"],
            "truth_status": reconstruction_result["truth_verification"],
            "recovery_status": recovery_result["recovery_status"],
        }

    @staticmethod
    def execute_replay() -> dict[str, Any]:
        return RuntimeReplayer.execute_replay()

    @staticmethod
    def execute_recover() -> dict[str, Any]:
        return InterruptedRecovery.analyze_interruption()

    @staticmethod
    def execute_verify() -> list[dict[str, Any]]:
        return FailurePathExecutor.execute()

    @staticmethod
    def load_events(
        log: str = "live",
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        paths = {
            "live": AppendOnlyStore.LIVE_LOG,
            "replay": AppendOnlyStore.REPLAY_LOG,
            "recovery": AppendOnlyStore.RECOVERY_LOG,
        }
        file_path = paths.get(log, AppendOnlyStore.LIVE_LOG)

        import json

        events = []
        try:
            with open(file_path, encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except FileNotFoundError:
            pass

        total = len(events)
        page = events[offset : offset + limit]
        return {"total": total, "offset": offset, "limit": limit, "events": page}

    @staticmethod
    def get_latest_report() -> dict[str, Any] | None:
        import json
        from pathlib import Path

        report_path = Path(FinalRuntimeReporter.OUTPUT_FILE)
        if not report_path.exists():
            return None
        with open(report_path, encoding="utf-8") as file:
            return json.load(file)
