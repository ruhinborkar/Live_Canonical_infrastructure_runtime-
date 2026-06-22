from typing import Any

from persistence.append_only_store import AppendOnlyStore
from recovery.persistence_helpers import (
    analyze_recovery_state,
    filter_runtime_events,
    persist_recovery_log,
)
from recovery.recovery_proof import RecoveryProofExporter
from recovery.runtime_recovery_executor import RuntimeRecoveryExecutor
from services.event_loader import read_log_events


class InterruptedRecovery:
    @classmethod
    def analyze_interruption(cls) -> dict[str, Any]:
        live_events = read_log_events(AppendOnlyStore.LIVE_LOG)
        runtime_events = filter_runtime_events(live_events)

        analysis = analyze_recovery_state(runtime_events, include_duplicates=True)
        result = {
            "execution_interrupted": analysis["recovery_required"],
            "broken_sequence_continuity": len(analysis["missing_sequences"]) > 0,
            "missing_sequences": analysis["missing_sequences"],
            "duplicate_sequences": analysis["duplicate_sequences"],
            "interrupted_events": analysis["interrupted_events"],
            "resume_point": analysis["resume_point"],
            "recovery_outcome": analysis["recovery_outcome"],
        }

        persist_recovery_log(
            runtime_events,
            {
                **analysis,
                "recovery_outcome": analysis["recovery_outcome"],
            },
            clear_log=True,
            validation_reason="interrupted execution",
        )

        execution = RuntimeRecoveryExecutor.execute(analysis)
        result = {**result, **execution}
        RecoveryProofExporter.export(result, live_events=read_log_events(AppendOnlyStore.LIVE_LOG))

        return result
