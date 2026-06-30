"""External system adapter framework.

A registry of named adapters that translate between the runtime and external
systems (inbound or outbound). Adapters implement a simple contract: a
`handle(payload) -> dict` callable. The framework provides safe dispatch with
status tracking; it never assumes a specific protocol or vendor.
"""

from datetime import datetime, timezone
from typing import Any, Callable

AdapterHandler = Callable[[dict[str, Any]], dict[str, Any]]


class ExternalAdapterFramework:
    _adapters: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, handler: AdapterHandler, *, direction: str = "outbound") -> dict[str, Any]:
        cls._adapters[name] = {
            "name": name,
            "direction": direction,
            "handler": handler,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "invocations": 0,
            "failures": 0,
            "last_status": "READY",
        }
        return cls.describe(name)

    @classmethod
    def dispatch(cls, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        adapter = cls._adapters.get(name)
        if not adapter:
            return {"ok": False, "error": f"unknown adapter: {name}"}
        adapter["invocations"] += 1
        try:
            result = adapter["handler"](payload)
            adapter["last_status"] = "OK"
            return {"ok": True, "result": result}
        except Exception as exc:  # noqa: BLE001 - isolate adapter failures
            adapter["failures"] += 1
            adapter["last_status"] = "ERROR"
            return {"ok": False, "error": str(exc)}

    @classmethod
    def describe(cls, name: str) -> dict[str, Any]:
        adapter = cls._adapters.get(name, {})
        return {k: v for k, v in adapter.items() if k != "handler"}

    @classmethod
    def list_adapters(cls) -> list[dict[str, Any]]:
        return [cls.describe(name) for name in cls._adapters]

    @classmethod
    def reset(cls) -> None:
        cls._adapters = {}
