import time
from typing import Any, Callable

from datasets.runtime_dataset_generator import RuntimeDatasetGenerator
from datasets.runtime_dataset_loader import RuntimeDatasetLoader
from hashing.runtime_hasher import RuntimeHasher
from observability.final_runtime_reporter import FinalRuntimeReporter
from observability.runtime_metrics import RuntimeMetricsCollector
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
        pipeline_start = time.perf_counter()
        RuntimeMetricsCollector.reset()
        cls._observe("INPUT", "DATASET_GENERATION_STARTED")
        dataset_summary = RuntimeDatasetGenerator.generate()

        cls._observe("INPUT", "DATASET_LOADED")
        events = RuntimeDatasetLoader.load_events()

        AppendOnlyStore.clear_log(AppendOnlyStore.LIVE_LOG)
        AppendOnlyStore.clear_log(AppendOnlyStore.REPLAY_LOG)
        AppendOnlyStore.clear_log(AppendOnlyStore.RECOVERY_LOG)

        processed_events = 0
        valid_events = 0
        invalid_events = 0

        validation_start = time.perf_counter()
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

        loop_ms = round((time.perf_counter() - validation_start) * 1000, 2)
        per_event = round(loop_ms / max(processed_events, 1), 2)
        RuntimeMetricsCollector.set_pipeline_timings(
            validation_ms=per_event,
            serialization_ms=per_event,
            hash_ms=per_event,
            persistence_writes=processed_events,
        )

        cls._observe("VALIDATION", "COMPLETED")
        cls._observe("SERIALIZATION", "COMPLETED")
        cls._observe("HASHING", "COMPLETED")
        cls._observe("PERSISTENCE", "APPEND_ONLY_WRITE_COMPLETED")

        replay_start = time.perf_counter()
        replay_result = RuntimeReplayer.execute_replay(clear_log=False, persist=True)
        RuntimeMetricsCollector.set_pipeline_timings(
            replay_ms=round((time.perf_counter() - replay_start) * 1000, 2)
        )
        cls._observe("REPLAY", replay_result["verification_result"])

        reconstruction_result = RuntimeReconstructor.reconstruct()
        cls._observe("VERIFICATION", reconstruction_result["truth_verification"])

        recovery_start = time.perf_counter()
        recovery_result = RuntimeRecovery.analyze(events)
        RuntimeRecovery.persist_recovery_log(events, recovery_result, clear_log=False)
        RuntimeMetricsCollector.set_pipeline_timings(
            recovery_ms=round((time.perf_counter() - recovery_start) * 1000, 2)
        )
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
        RuntimeMetricsCollector.set_counts(processed_events, processed_events)
        RuntimeMetricsCollector.finalize(
            (time.perf_counter() - pipeline_start) * 1000
        )

        return {
            **final_report,
            "report_path": report_path,
            "status": "completed",
            "replay_status": replay_result["verification_result"],
            "truth_status": reconstruction_result["truth_verification"],
            "recovery_status": recovery_result["recovery_status"],
        }

    @classmethod
    def execute_replay(cls) -> dict[str, Any]:
        cls._observe("REPLAY", "STARTED")
        result = RuntimeReplayer.execute_replay(clear_log=True, persist=True)
        cls._observe("REPLAY", result["verification_result"])
        return result

    @classmethod
    def execute_recover(cls) -> dict[str, Any]:
        cls._observe("RECOVERY", "ANALYSIS_STARTED")
        result = InterruptedRecovery.analyze_interruption()
        outcome = result.get("recovery_outcome", result.get("recovery_status", "UNKNOWN"))
        cls._observe("RECOVERY", str(outcome))
        return result

    @classmethod
    def execute_verify(cls) -> list[dict[str, Any]]:
        cls._observe("VERIFICATION", "FAILURE_PATH_STARTED")
        results = FailurePathExecutor.execute()
        detected = sum(1 for r in results if r.get("failure_detected"))
        cls._observe("VERIFICATION", f"CHECKS_COMPLETED_{detected}_DETECTED")
        return results

    @staticmethod
    def load_events(
        log: str = "live",
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
        search: str | None = None,
        event_type: str | None = None,
    ) -> dict[str, Any]:
        from services.event_loader import load_events as _load_events

        return _load_events(
            log=log,
            limit=limit,
            offset=offset,
            status=status,
            search=search,
            event_type=event_type,
        )

    @staticmethod
    def get_latest_report() -> dict[str, Any] | None:
        import json
        from pathlib import Path

        report_path = Path(FinalRuntimeReporter.OUTPUT_FILE)
        if not report_path.exists():
            return None
        with open(report_path, encoding="utf-8") as file:
            return json.load(file)
