"""Backward-compatible facade for runtime truth reconstruction and verification."""

from replay.runtime_truth_reconstructor import RuntimeTruthReconstructor
from validation.truth_verifier import TruthVerifier


class RuntimeReconstructor:
    @classmethod
    def reconstruct(cls):
        reconstruction = RuntimeTruthReconstructor.reconstruct()
        truth_verification = TruthVerifier.verify(reconstruction)

        return {
            "events_reconstructed": reconstruction["events_reconstructed"],
            "execution_state": reconstruction["execution_state"],
            "trace_lineage": reconstruction["trace_lineage"],
            "sequence_order": reconstruction["sequence_lineage"],
            "ordered_sequence": (
                reconstruction["sequence_lineage"]
                == sorted(reconstruction["sequence_lineage"])
            ),
            "duplicate_sequences": _duplicate_sequences(
                reconstruction["sequence_lineage"]
            ),
            "sequence_integrity": len(
                _duplicate_sequences(reconstruction["sequence_lineage"])
            )
            == 0,
            "runtime_outcome": reconstruction["verification_outcomes"][
                "replay_status"
            ],
            "verification_state": reconstruction["verification_outcomes"][
                "integrity_state"
            ],
            "recovery_status": reconstruction["verification_outcomes"][
                "recovery_status"
            ],
            "truth_verification": truth_verification,
            "original_runtime_truth": reconstruction["original_runtime_truth"],
            "reconstructed_runtime_truth": reconstruction[
                "reconstructed_runtime_truth"
            ],
        }


def _duplicate_sequences(sequence_lineage: list[int]) -> list[int]:
    seen: set[int] = set()
    duplicates: list[int] = []
    for sequence_id in sequence_lineage:
        if sequence_id in seen:
            duplicates.append(sequence_id)
        seen.add(sequence_id)
    return duplicates
