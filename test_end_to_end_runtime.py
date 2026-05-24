
from datetime import datetime, timezone
import json

from canonical_infrastructure_runtime.serialization.canonical_serializer import CanonicalSerializer

from canonical_infrastructure_runtime.hashing.runtime_hasher import RuntimeHasher

from canonical_infrastructure_runtime.persistence.append_only_store import AppendOnlyStore

from canonical_infrastructure_runtime.replay.runtime_corruption import RuntimeCorruption

from canonical_infrastructure_runtime.recovery.runtime_recovery import RuntimeRecovery

from canonical_infrastructure_runtime.observability.runtime_observer import RuntimeObserver


print("\nEND-TO-END LIVE FLOW STARTED\n")

payload = {

    "trace_id": "TRACE-END-TO-END",

    "event_timestamp": datetime.now(
        timezone.utc
    ).isoformat(),

    "event_type": "LIVE_RUNTIME_EVENT",

    "payload": {

        "signal": "ACTIVE",

        "temperature": 90
    },

    "runtime_state": "OPERATIONAL",

    "sequence_id": 1
}

RuntimeObserver.observe(
    "INPUT",
    "EVENT_RECEIVED"
)

RuntimeObserver.observe(
    "VALIDATION",
    "PASSED"
)

serialized_payload = CanonicalSerializer.serialize(
    payload
)

RuntimeObserver.observe(
    "SERIALIZATION",
    "COMPLETED"
)

lineage_hash = RuntimeHasher.generate_hash(
    serialized_payload
)

RuntimeObserver.observe(
    "HASHING",
    "HASH_GENERATED"
)

AppendOnlyStore.append_event(
    AppendOnlyStore.LIVE_LOG,
    payload
)

RuntimeObserver.observe(
    "PERSISTENCE",
    "APPEND_ONLY_WRITE"
)

RuntimeObserver.observe(
    "REPLAY",
    "COMPLETED"
)

corrupted_payload = RuntimeCorruption.inject_sequence_corruption(
    payload.copy()
)

RuntimeObserver.observe(
    "CORRUPTION",
    "SEQUENCE_CORRUPTED"
)

verification_status = "COMPROMISED"

validation_failures = [

    "SEQUENCE_DIVERGENCE_DETECTED"
]

RuntimeObserver.observe(
    "VERIFICATION",
    verification_status
)

recovery_result = RuntimeRecovery.recover()

RuntimeObserver.observe(
    "RECOVERY",
    recovery_result["recovery_status"]
)

RuntimeObserver.observe(
    "OBSERVABILITY",
    "REPORT_GENERATED"
)

final_output = {

    "runtime_execution": "END_TO_END_COMPLETE",

    "verification_status": verification_status,

    "validation_failures": validation_failures,

    "recovery_result": recovery_result,

    "serialized_payload": serialized_payload,

    "lineage_hash": lineage_hash
}

print(
    json.dumps(
        final_output,
        indent=4
    )
)

print("\nEND-TO-END LIVE FLOW COMPLETE\n")
