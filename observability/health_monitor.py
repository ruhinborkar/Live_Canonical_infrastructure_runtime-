"""Runtime health monitoring across core subsystems."""

from pathlib import Path
from typing import Any

from persistence.append_only_store import AppendOnlyStore
from services.event_loader import read_log_events
from services.runtime_console_service import _load_report


def _status(ok: bool, *, healthy: str, unhealthy: str) -> str:
    return healthy if ok else unhealthy


class HealthMonitor:
    @classmethod
    def check_persistence_health(cls) -> str:
        log_dir = Path("logging/logs")
        writable = True
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            probe = log_dir / ".health_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
        except OSError:
            writable = False

        live_exists = Path(AppendOnlyStore.LIVE_LOG).exists()
        return _status(
            writable,
            healthy="PERSISTENCE_AVAILABLE" if live_exists else "PERSISTENCE_READY",
            unhealthy="PERSISTENCE_UNAVAILABLE",
        )

    @classmethod
    def check_replay_health(cls) -> str:
        report, _ = _load_report()
        replay = (report or {}).get("replay", {})
        status = str(replay.get("verification_result", "NOT_RUN"))
        if status == "REPLAY_VERIFIED":
            return "REPLAY_HEALTHY"
        if status == "NOT_RUN":
            return "REPLAY_IDLE"
        return "REPLAY_UNHEALTHY"

    @classmethod
    def check_recovery_health(cls) -> str:
        report, _ = _load_report()
        recovery = (report or {}).get("recovery", {})
        status = str(recovery.get("recovery_status", "NOT_RUN"))
        if status == "RECOVERY_NOT_REQUIRED":
            return "RECOVERY_HEALTHY"
        if status == "RECOVERY_REQUIRED":
            return "RECOVERY_ATTENTION"
        if status == "NOT_RUN":
            return "RECOVERY_IDLE"
        return "RECOVERY_UNHEALTHY"

    @classmethod
    def check_runtime_health(cls) -> str:
        report, _ = _load_report()
        runtime = (report or {}).get("runtime_execution", {})
        processed = runtime.get("processed_events", 0)
        if processed > 0:
            return "RUNTIME_OPERATIONAL"
        live_events = read_log_events(AppendOnlyStore.LIVE_LOG)
        if live_events:
            return "RUNTIME_OPERATIONAL"
        return "RUNTIME_IDLE"

    @classmethod
    def get_status(cls) -> dict[str, Any]:
        runtime_health = cls.check_runtime_health()
        replay_health = cls.check_replay_health()
        persistence_health = cls.check_persistence_health()
        recovery_health = cls.check_recovery_health()

        unhealthy = {
            "REPLAY_UNHEALTHY",
            "RECOVERY_UNHEALTHY",
            "PERSISTENCE_UNAVAILABLE",
        }
        attention = {"RECOVERY_ATTENTION"}

        values = [runtime_health, replay_health, persistence_health, recovery_health]
        if any(value in unhealthy for value in values):
            overall = "UNHEALTHY"
        elif any(value in attention for value in values):
            overall = "DEGRADED"
        else:
            overall = "HEALTHY"

        return {
            "overall": overall,
            "runtime_health": runtime_health,
            "replay_health": replay_health,
            "persistence_health": persistence_health,
            "recovery_health": recovery_health,
        }
