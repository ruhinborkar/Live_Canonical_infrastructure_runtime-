import json
import time
import tracemalloc
from typing import Any, Callable

from datasets.runtime_dataset_generator import RuntimeDatasetGenerator
from datasets.runtime_dataset_loader import RuntimeDatasetLoader
from hashing.runtime_hasher import RuntimeHasher
from observability.final_runtime_reporter import FinalRuntimeReporter
from observability.runtime_proof_manifest import RuntimeProofManifest
from observability.runtime_metrics import RuntimeMetricsCollector
from observability.runtime_observer import RuntimeObserver
from persistence.append_only_store import AppendOnlyStore
from ledger.runtime_truth_ledger import RuntimeTruthLedger
from ledger.truth_snapshot_store import TruthSnapshotStore
from recovery.interrupted_recovery import InterruptedRecovery
from recovery.runtime_recovery import RuntimeRecovery
from recovery.recovery_proof import RecoveryProofExporter
from replay.runtime_truth_reconstructor import RuntimeTruthReconstructor
from validation.truth_verifier import TruthVerifier
from replay.runtime_replayer import RuntimeReplayer
from serialization.canonical_serializer import CanonicalSerializer
from validation.failure_injection_framework import FailureInjectionFramework
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
        TruthSnapshotStore.clear()

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
            RuntimeTruthLedger.record_snapshot(
                runtime_event,
                validation_status=runtime_event["validation_status"],
                payload_hash=payload_hash,
            )
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

        reconstruction_start = time.perf_counter()
        tracemalloc.start()
        reconstruction = RuntimeTruthReconstructor.reconstruct()
        ledger_reconstruction = RuntimeTruthLedger.reconstruct_without_replay_logs()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        reconstruction_ms = round((time.perf_counter() - reconstruction_start) * 1000, 2)
        memory_mb = round(peak_memory / (1024 * 1024), 2)

        truth_verification = TruthVerifier.verify(reconstruction)
        reconstruction_result = {
            **reconstruction,
            "truth_verification": truth_verification,
        }
        cls._observe("VERIFICATION", truth_verification)
        RuntimeMetricsCollector.set_pipeline_timings(
            reconstruction_ms=reconstruction_ms,
            memory_mb=memory_mb,
        )
        cls._observe("TRUTH_LEDGER", ledger_reconstruction["truth_reconstruction"])

        recovery_start = time.perf_counter()
        recovery_result = RuntimeRecovery.analyze(events)
        RuntimeRecovery.persist_recovery_log(events, recovery_result, clear_log=False)
        RecoveryProofExporter.export(recovery_result)
        RuntimeMetricsCollector.set_pipeline_timings(
            recovery_ms=round((time.perf_counter() - recovery_start) * 1000, 2)
        )
        cls._observe(
            "RECOVERY",
            "RECOVERY_REQUIRED"
            if recovery_result["recovery_required"]
            else "RECOVERY_NOT_REQUIRED",
        )

        proof_manifest = RuntimeProofManifest.export()

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
                "truth_verification": truth_verification,
                "truth_hash_match": reconstruction_result.get("truth_hash_match"),
                "original_truth_hash": reconstruction_result["original_runtime_truth"].get(
                    "truth_hash"
                ),
                "reconstructed_truth_hash": reconstruction_result[
                    "reconstructed_runtime_truth"
                ].get("truth_hash"),
                "execution_state": reconstruction_result["execution_state"],
                "sequence_lineage": reconstruction_result["sequence_lineage"],
                "trace_lineage": reconstruction_result["trace_lineage"],
            },
            "recovery": recovery_result,
            "truth_ledger": ledger_reconstruction,
            "proof_manifest": proof_manifest,
        }

        report_path = FinalRuntimeReporter.export_report(final_report)
        cls._observe("OBSERVABILITY", "REPORT_GENERATED")
        RuntimeMetricsCollector.set_counts(
            processed_events, processed_events, events_failed=invalid_events
        )
        RuntimeMetricsCollector.finalize(
            (time.perf_counter() - pipeline_start) * 1000
        )

        return {
            **final_report,
            "report_path": report_path,
            "status": "completed",
            "replay_status": replay_result["verification_result"],
            "truth_status": truth_verification,
            "recovery_proof_path": "runtime_recovery_proof.json",
            "truth_ledger_proof_path": "truth_ledger_reconstruction_proof.json",
            "recovery_status": recovery_result["recovery_status"],
            "truth_ledger_status": ledger_reconstruction["truth_reconstruction"],
        }

    @classmethod
    def execute_ledger_reconstruct(cls) -> dict[str, Any]:
        cls._observe("TRUTH_LEDGER", "RECONSTRUCTION_STARTED")
        result = RuntimeTruthLedger.reconstruct_without_replay_logs()
        cls._observe("TRUTH_LEDGER", result["truth_reconstruction"])
        return result

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
    def execute_verify(cls) -> dict[str, Any]:
        cls._observe("VERIFICATION", "FAILURE_PATH_STARTED")
        failure_results = FailurePathExecutor.execute()
        injection_results = FailureInjectionFramework.execute()
        detected = sum(1 for r in failure_results if r.get("failure_detected"))
        injection_detected = sum(1 for r in injection_results if r.get("detected"))

        reconstruction = RuntimeTruthReconstructor.reconstruct()
        truth_result = TruthVerifier.verify_with_details(reconstruction)

        cls._observe("VERIFICATION", truth_result["truth_verification"])
        cls._observe(
            "VERIFICATION",
            f"CHECKS_COMPLETED_{detected}_DETECTED_INJECTION_{injection_detected}",
        )

        return {
            "truth_verification": truth_result["truth_verification"],
            "truth_checks": truth_result["checks"],
            "validation_state_diff": truth_result.get("validation_state_diff", {}),
            "recovery_state_diff": truth_result.get("recovery_state_diff", {}),
            "original_truth_hash": truth_result.get("original_truth_hash"),
            "reconstructed_truth_hash": truth_result.get("reconstructed_truth_hash"),
            "failure_path_results": failure_results,
            "injection_results": injection_results,
        }

    @classmethod
    def execute_injection(cls) -> dict[str, Any]:
        cls._observe("VERIFICATION", "INJECTION_STARTED")
        results = FailureInjectionFramework.execute()
        detected = sum(1 for row in results if row.get("detected"))
        cls._observe("VERIFICATION", f"INJECTION_COMPLETED_{detected}_DETECTED")
        return {
            "injection_results": results,
            "detected_count": detected,
            "proof_path": "failure_injection_proof.json",
        }

    @classmethod
    def execute_manifest(cls) -> dict[str, Any]:
        cls._observe("OBSERVABILITY", "MANIFEST_STARTED")
        manifest = RuntimeProofManifest.export()
        cls._observe("OBSERVABILITY", manifest.get("overall", "MANIFEST_EXPORTED"))
        return manifest

    @classmethod
    def execute_demo(cls) -> dict[str, Any]:
        cls._observe("INPUT", "DEMO_STARTED")

        live_result = cls.execute_live()

        cls._observe("REPLAY", "DEMO_REPLAY")
        replay_result = cls.execute_replay()

        cls._observe("VERIFICATION", "DEMO_RECONSTRUCTION")
        reconstruction = RuntimeTruthReconstructor.reconstruct()
        truth_verification = TruthVerifier.verify(reconstruction)

        cls._observe("RECOVERY", "DEMO_RECOVERY")
        recovery_result = cls.execute_recover()

        verify_result = cls.execute_verify()

        proof_manifest = RuntimeProofManifest.export()

        cls._observe("OBSERVABILITY", "DEMO_COMPLETE")

        return {
            "live": live_result,
            "replay": replay_result,
            "reconstruction": reconstruction,
            "truth_verification": truth_verification,
            "recovery": recovery_result,
            "verify": verify_result,
            "proof_manifest": proof_manifest,
            "recovery_proof_path": "runtime_recovery_proof.json",
            "recovery_execution_proof_path": "runtime_recovery_execution_proof.json",
            "proof_manifest_path": "runtime_proof_manifest.json",
            "report_path": live_result.get("report_path"),
        }

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
