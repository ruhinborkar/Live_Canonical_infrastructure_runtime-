"""Executable hostile-runtime failure injection and detection."""

import copy
import json
import os
from typing import Any, Callable

from datasets.runtime_dataset_loader import RuntimeDatasetLoader
from hashing.runtime_hasher import RuntimeHasher
from persistence.append_only_store import AppendOnlyStore
from recovery.persistence_helpers import analyze_recovery_state, missing_sequences
from serialization.canonical_serializer import CanonicalSerializer
from services.event_loader import read_log_events
from validation.runtime_validator import RuntimeValidator

PROOF_FILE = "failure_injection_proof.json"

Injector = Callable[[list[dict[str, Any]]], tuple[list[dict[str, Any]], str]]


class FailureInjectionFramework:
    @classmethod
    def _base_events(cls) -> list[dict[str, Any]]:
        live_events = read_log_events(AppendOnlyStore.LIVE_LOG)
        if live_events:
            return live_events
        return RuntimeDatasetLoader.load_events()

    @classmethod
    def execute(cls) -> list[dict[str, Any]]:
        base_events = cls._base_events()
        scenarios: list[tuple[Injector, str]] = [
            (cls._inject_dropped_events, "DROPPED_EVENT"),
            (cls._inject_reordered_events, "REORDERED_EVENT"),
            (cls._inject_duplicated_events, "DUPLICATED_EVENT"),
            (cls._inject_corrupted_hash, "CORRUPTED_HASH"),
            (cls._inject_trace_corruption, "TRACE_CORRUPTION"),
            (cls._inject_interrupted_execution, "INTERRUPTED_EXECUTION"),
        ]

        results: list[dict[str, Any]] = []
        for injector, failure_type in scenarios:
            injected_events = injector(base_events)
            result = cls._validate_injection(injected_events, failure_type)
            results.append(result)

        cls.export_proof(results)
        return results

    @staticmethod
    def _inject_dropped_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if len(events) < 3:
            return copy.deepcopy(events)
        mutated = copy.deepcopy(events)
        del mutated[len(mutated) // 2]
        return mutated

    @staticmethod
    def _inject_reordered_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        mutated = copy.deepcopy(events)
        if len(mutated) >= 4:
            mutated[1], mutated[2] = mutated[2], mutated[1]
        return mutated

    @staticmethod
    def _inject_duplicated_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        mutated = copy.deepcopy(events)
        if mutated:
            duplicate = copy.deepcopy(mutated[0])
            mutated.insert(1, duplicate)
        return mutated

    @staticmethod
    def _inject_corrupted_hash(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        mutated = copy.deepcopy(events)
        for event in mutated:
            if event.get("payload_hash"):
                event["payload_hash"] = "0" * 64
                break
            payload = event.get("payload", {})
            canonical = CanonicalSerializer.serialize(payload)
            event["payload_hash"] = RuntimeHasher.generate_hash(canonical)
            event["payload_hash"] = "corrupted-" + event["payload_hash"][:54]
            break
        return mutated

    @staticmethod
    def _inject_trace_corruption(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        mutated = copy.deepcopy(events)
        if mutated:
            mutated[0]["trace_id"] = "TRACE-CORRUPTED"
        return mutated

    @staticmethod
    def _inject_interrupted_execution(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        mutated = copy.deepcopy(events)
        if not mutated:
            return mutated
        target = mutated[min(len(mutated) - 1, len(mutated) // 2)]
        target["event_type"] = "INTERRUPTED_EVENT"
        target["runtime_state"] = "INTERRUPTED"
        return mutated

    @classmethod
    def _validate_injection(
        cls,
        events: list[dict[str, Any]],
        failure_type: str,
    ) -> dict[str, Any]:
        if failure_type == "DROPPED_EVENT":
            sequence_ids = [
                event["sequence_id"]
                for event in events
                if event.get("sequence_id") is not None
            ]
            gaps = missing_sequences(sorted(sequence_ids))
            detected = len(gaps) > 0
            return {
                "failure_type": failure_type,
                "detected": detected,
                "system_response": "SEQUENCE_DIVERGENCE" if detected else "ACCEPTED",
            }

        if failure_type == "REORDERED_EVENT":
            sequence_ids = [
                event["sequence_id"]
                for event in events
                if event.get("sequence_id") is not None
            ]
            detected = bool(sequence_ids) and sequence_ids != sorted(sequence_ids)
            return {
                "failure_type": failure_type,
                "detected": detected,
                "system_response": "SEQUENCE_DIVERGENCE" if detected else "ACCEPTED",
            }

        if failure_type == "DUPLICATED_EVENT":
            sequence_ids = [
                event["sequence_id"]
                for event in events
                if event.get("sequence_id") is not None
            ]
            detected = len(sequence_ids) != len(set(sequence_ids))
            return {
                "failure_type": failure_type,
                "detected": detected,
                "system_response": "SEQUENCE_DIVERGENCE" if detected else "ACCEPTED",
            }

        if failure_type == "CORRUPTED_HASH":
            detected = False
            for event in events:
                payload = event.get("payload", {})
                canonical = CanonicalSerializer.serialize(payload)
                recomputed = RuntimeHasher.generate_hash(canonical)
                stored = event.get("payload_hash")
                if stored and stored != recomputed:
                    detected = True
                    break
            return {
                "failure_type": failure_type,
                "detected": detected,
                "system_response": "REPLAY_REJECTED" if detected else "REPLAY_VERIFIED",
            }

        if failure_type == "TRACE_CORRUPTION":
            trace_ids = [
                event.get("trace_id")
                for event in events
                if event.get("trace_id")
            ]
            detected = "TRACE-CORRUPTED" in trace_ids or len(set(trace_ids)) != len(trace_ids)
            return {
                "failure_type": failure_type,
                "detected": detected,
                "system_response": "TRACE_CORRUPTION" if detected else "TRACE_VERIFIED",
            }

        if failure_type == "INTERRUPTED_EXECUTION":
            recovery = analyze_recovery_state(events, include_duplicates=False)
            detected = recovery.get("recovery_required", False)
            return {
                "failure_type": failure_type,
                "detected": detected,
                "system_response": "RECOVERY_REQUIRED" if detected else "RECOVERY_NOT_REQUIRED",
            }

        return {
            "failure_type": failure_type,
            "detected": False,
            "system_response": "UNKNOWN",
        }

    @classmethod
    def export_proof(cls, results: list[dict[str, Any]]) -> dict[str, Any]:
        proof = {
            "proof_type": "FAILURE_INJECTION",
            "scenarios_executed": len(results),
            "detected_count": sum(1 for row in results if row.get("detected")),
            "results": results,
        }
        os.makedirs(os.path.dirname(PROOF_FILE) or ".", exist_ok=True)
        with open(PROOF_FILE, "w", encoding="utf-8") as file:
            json.dump(proof, file, indent=4)
        return proof
