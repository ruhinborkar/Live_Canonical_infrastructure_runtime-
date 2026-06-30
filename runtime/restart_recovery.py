"""Restart recovery.

On engine start, inspects persisted operational state to determine whether the
previous lifecycle ended cleanly. If not (process killed, crash, container
restart), it restores pending work from the persisted queue and reports a
recovered restart so the runtime resumes continuity instead of starting blind.
"""

from typing import Any

from capabilities.task_queue import TaskQueue
from runtime.operational_state_manager import OperationalStateManager

UNCLEAN_PRIOR_STATES = {"RUNNING", "DEGRADED", "STOPPING", "STARTING"}


class RestartRecovery:
    @classmethod
    def recover(cls) -> dict[str, Any]:
        prior = OperationalStateManager.load()
        prior_state = prior.get("state")
        stopped_cleanly = prior.get("stopped_cleanly", True)

        restored_pending = TaskQueue.restore()

        unclean = (not stopped_cleanly) and (prior_state in UNCLEAN_PRIOR_STATES)
        recovered = unclean or restored_pending > 0

        return {
            "prior_state": prior_state,
            "stopped_cleanly": stopped_cleanly,
            "unclean_shutdown_detected": unclean,
            "restored_pending_tasks": restored_pending,
            "recovered": recovered,
            "prior_counters": prior.get("counters", {}),
            "prior_heartbeat_tick": prior.get("heartbeat_tick", 0),
        }
