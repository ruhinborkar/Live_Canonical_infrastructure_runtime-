"""Operational state manager.

Single source of truth for the runtime's lifecycle state and operational
counters. Persisted so restart recovery can detect an unclean shutdown and
restore continuity.
"""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from persistence.atomic_json import write_json_atomic

STATE_FILE = Path("data/operational_state.json")

VALID_STATES = {"STARTING", "RUNNING", "DEGRADED", "STOPPING", "STOPPED"}


class OperationalStateManager:
    _lock = threading.RLock()
    _state: dict[str, Any] = {}

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _default(cls) -> dict[str, Any]:
        return {
            "state": "STOPPED",
            "previous_state": None,
            "started_at": None,
            "last_transition_at": cls._now(),
            "stopped_cleanly": True,
            "heartbeat_tick": 0,
            "last_heartbeat_at": None,
            "counters": {
                "tasks_accepted": 0,
                "tasks_completed": 0,
                "tasks_failed": 0,
                "tasks_invalid": 0,
            },
        }

    @classmethod
    def load(cls) -> dict[str, Any]:
        with cls._lock:
            if STATE_FILE.exists():
                try:
                    cls._state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    cls._state = cls._default()
            else:
                cls._state = cls._default()
            return dict(cls._state)

    @classmethod
    def _ensure(cls) -> None:
        if not cls._state:
            cls.load()

    @classmethod
    def _persist(cls) -> None:
        write_json_atomic(STATE_FILE, cls._state)

    @classmethod
    def transition(cls, new_state: str, *, stopped_cleanly: bool | None = None) -> dict[str, Any]:
        if new_state not in VALID_STATES:
            raise ValueError(f"invalid state: {new_state}")
        with cls._lock:
            cls._ensure()
            current = cls._state.get("state")
            try:
                from intelligence.state_transition_engine import StateTransitionEngine

                StateTransitionEngine.record(current, new_state)
            except Exception:  # noqa: BLE001 - transition audit must never block lifecycle
                pass
            cls._state["previous_state"] = current
            cls._state["state"] = new_state
            cls._state["last_transition_at"] = cls._now()
            if new_state == "STARTING":
                cls._state["started_at"] = cls._now()
                cls._state["stopped_cleanly"] = False
            if stopped_cleanly is not None:
                cls._state["stopped_cleanly"] = stopped_cleanly
            cls._persist()
            return dict(cls._state)

    @classmethod
    def mark_clean_stop(cls) -> None:
        with cls._lock:
            cls._ensure()
            cls._state["stopped_cleanly"] = True
            cls._persist()

    @classmethod
    def record_heartbeat(cls, tick: int) -> None:
        with cls._lock:
            cls._ensure()
            cls._state["heartbeat_tick"] = tick
            cls._state["last_heartbeat_at"] = cls._now()
            cls._persist()

    @classmethod
    def increment(cls, counter: str, amount: int = 1) -> None:
        with cls._lock:
            cls._ensure()
            counters = cls._state.setdefault("counters", {})
            counters[counter] = counters.get(counter, 0) + amount
            cls._persist()

    @classmethod
    def current_state(cls) -> str:
        with cls._lock:
            cls._ensure()
            return cls._state.get("state", "STOPPED")

    @classmethod
    def snapshot(cls) -> dict[str, Any]:
        with cls._lock:
            cls._ensure()
            snap = dict(cls._state)
            started = snap.get("started_at")
            uptime = None
            if started and snap.get("state") not in {"STOPPED"}:
                try:
                    delta = datetime.now(timezone.utc) - datetime.fromisoformat(started)
                    uptime = round(delta.total_seconds(), 1)
                except ValueError:
                    uptime = None
            snap["uptime_seconds"] = uptime
            return snap
