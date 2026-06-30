"""Generic mission/operational context store.

A "context" is a named, scoped key/value envelope that work can be attached to
(e.g. a campaign, batch, tenant, or operational window). Domain-agnostic.
Inputs: context create/update calls.
Outputs: active context state for tagging tasks and dashboard grouping.
Persistence: data/mission_context.json.
"""

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from persistence.atomic_json import write_json_atomic

CONTEXT_FILE = Path("data/mission_context.json")


class MissionContext:
    _lock = threading.RLock()
    _contexts: dict[str, dict[str, Any]] = {}
    _active_id: str | None = None
    _loaded = False

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._loaded:
            return
        if CONTEXT_FILE.exists():
            try:
                data = json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
                cls._contexts = data.get("contexts", {})
                cls._active_id = data.get("active_id")
            except (json.JSONDecodeError, OSError):
                cls._contexts = {}
        cls._loaded = True

    @classmethod
    def _persist(cls) -> None:
        write_json_atomic(
            CONTEXT_FILE,
            {"contexts": cls._contexts, "active_id": cls._active_id, "updated_at": cls._now()},
        )

    @classmethod
    def create(cls, name: str, attributes: dict[str, Any] | None = None, *, activate: bool = True) -> dict[str, Any]:
        cls._ensure_loaded()
        with cls._lock:
            context = {
                "context_id": str(uuid.uuid4()),
                "name": name,
                "attributes": attributes or {},
                "created_at": cls._now(),
                "status": "ACTIVE",
            }
            cls._contexts[context["context_id"]] = context
            if activate or cls._active_id is None:
                cls._active_id = context["context_id"]
            cls._persist()
            return context

    @classmethod
    def active(cls) -> dict[str, Any] | None:
        cls._ensure_loaded()
        with cls._lock:
            if cls._active_id is None:
                return None
            return cls._contexts.get(cls._active_id)

    @classmethod
    def ensure_default(cls) -> dict[str, Any]:
        cls._ensure_loaded()
        with cls._lock:
            current = cls._contexts.get(cls._active_id) if cls._active_id else None
        if current:
            return current
        return cls.create("default-operational-context", {"origin": "auto"})

    @classmethod
    def list_all(cls) -> list[dict[str, Any]]:
        cls._ensure_loaded()
        with cls._lock:
            return list(cls._contexts.values())
