import json
from datetime import datetime, timezone

from hashing.runtime_hasher import RuntimeHasher
from persistence.append_only_store import AppendOnlyStore
from serialization.canonical_serializer import CanonicalSerializer


class RuntimeReplayer:
    LOG_FILE = AppendOnlyStore.LIVE_LOG
    REPLAY_LOG = AppendOnlyStore.REPLAY_LOG

    @classmethod
    def execute_replay(cls, *, clear_log: bool = True, persist: bool = True):
        if clear_log and persist:
            AppendOnlyStore.clear_log(cls.REPLAY_LOG)

        events_replayed = 0
        hashes_recomputed = 0
        runtime_states_rebuilt = 0
        replay_verified = True
        last_sequence_id = 0

        try:
            with open(cls.LOG_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue

                    event = json.loads(line)
                    payload = event.get("payload", {})

                    original_truth = {
                        "payload": payload,
                        "runtime_state": event.get("runtime_state"),
                        "sequence_id": event.get("sequence_id"),
                    }

                    canonical_payload = CanonicalSerializer.serialize(payload)
                    payload_hash = RuntimeHasher.generate_hash(canonical_payload)
                    stored_hash = event.get("payload_hash")
                    event_verified = not stored_hash or stored_hash == payload_hash

                    reconstructed_truth = {
                        "payload": json.loads(canonical_payload),
                        "runtime_state": event.get("runtime_state"),
                        "sequence_id": event.get("sequence_id"),
                    }

                    if original_truth != reconstructed_truth:
                        event_verified = False

                    if not event_verified:
                        replay_verified = False

                    sequence_id = event.get("sequence_id", 0)
                    last_sequence_id = sequence_id

                    if persist:
                        replay_record = {
                            "event_timestamp": event.get(
                                "event_timestamp",
                                datetime.now(timezone.utc).isoformat(),
                            ),
                            "event_type": event.get("event_type", "REPLAY_EVENT"),
                            "sequence_id": sequence_id,
                            "trace_id": event.get("trace_id"),
                            "runtime_state": event.get("runtime_state"),
                            "payload": payload,
                            "payload_hash": payload_hash,
                            "stored_hash": stored_hash,
                            "replay_verified": event_verified,
                            "validation_status": "VALID" if event_verified else "INVALID",
                            "validation_reason": (
                                "replay hash verified"
                                if event_verified
                                else "replay hash mismatch"
                            ),
                            "replay_source": "live_execution",
                        }
                        AppendOnlyStore.append_event(cls.REPLAY_LOG, replay_record)

                    events_replayed += 1
                    hashes_recomputed += 1
                    runtime_states_rebuilt += 1

        except FileNotFoundError:
            replay_verified = False

        verification_result = (
            "REPLAY_VERIFIED" if replay_verified else "REPLAY_MISMATCH"
        )

        if persist:
            AppendOnlyStore.append_event(
                cls.REPLAY_LOG,
                {
                    "event_type": "REPLAY_VALIDATION",
                    "status": verification_result,
                    "sequence_id": last_sequence_id,
                    "events_replayed": events_replayed,
                    "validation_status": "VALID" if replay_verified else "INVALID",
                    "validation_reason": verification_result,
                },
            )

        return {
            "events_replayed": events_replayed,
            "hashes_recomputed": hashes_recomputed,
            "runtime_states_rebuilt": runtime_states_rebuilt,
            "verification_result": verification_result,
        }
