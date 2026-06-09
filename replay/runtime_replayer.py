
import json

from serialization.canonical_serializer import (
    CanonicalSerializer
)

from hashing.runtime_hasher import (
    RuntimeHasher
)


class RuntimeReplayer:

    LOG_FILE = (
        "logging/logs/live_execution.jsonl"
    )

    @classmethod
    def execute_replay(
        cls
    ):

        events_replayed = 0

        hashes_recomputed = 0

        runtime_states_rebuilt = 0

        replay_verified = True

        try:

            with open(
                cls.LOG_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                for line in file:

                    line = line.strip()

                    if not line:
                        continue

                    event = json.loads(
                        line
                    )

                    payload = event.get(
                        "payload",
                        {}
                    )

                    original_truth = {

                        "payload":
                            payload,

                        "runtime_state":
                            event.get(
                                "runtime_state"
                            ),

                        "sequence_id":
                            event.get(
                                "sequence_id"
                            )

                    }

                    canonical_payload = (

                        CanonicalSerializer.serialize(
                            payload
                        )

                    )

                    payload_hash = (

                        RuntimeHasher.generate_hash(
                            canonical_payload
                        )

                    )

                    stored_hash = event.get(
                        "payload_hash"
                    )

                    if (
                        stored_hash
                        and
                        stored_hash != payload_hash
                    ):

                        replay_verified = False

                    reconstructed_truth = {

                        "payload":
                            json.loads(
                                canonical_payload
                            ),

                        "runtime_state":
                            event.get(
                                "runtime_state"
                            ),

                        "sequence_id":
                            event.get(
                                "sequence_id"
                            )

                    }

                    if (
                        original_truth
                        !=
                        reconstructed_truth
                    ):

                        replay_verified = False

                    events_replayed += 1

                    hashes_recomputed += 1

                    runtime_states_rebuilt += 1

        except FileNotFoundError:

            replay_verified = False

        return {

            "events_replayed":
                events_replayed,

            "hashes_recomputed":
                hashes_recomputed,

            "runtime_states_rebuilt":
                runtime_states_rebuilt,

            "verification_result":

                (
                    "REPLAY_VERIFIED"
                    if replay_verified
                    else
                    "REPLAY_MISMATCH"
                )

        }
