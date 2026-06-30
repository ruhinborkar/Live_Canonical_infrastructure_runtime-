"""Sensor abstraction layer.

A uniform interface over arbitrary data sources ("sensors"). A sensor is any
callable that yields reading dicts. Readings are funnelled into ingestion as
runtime events, decoupling sources from the engine.
Domain-agnostic: a sensor could be a file tailer, a queue poller, a synthetic
generator, etc.
"""

from datetime import datetime, timezone
from typing import Any, Callable

SensorReader = Callable[[], list[dict[str, Any]]]


class SensorAbstraction:
    _sensors: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, reader: SensorReader, *, sensor_type: str = "generic") -> dict[str, Any]:
        cls._sensors[name] = {
            "name": name,
            "type": sensor_type,
            "reader": reader,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "reads": 0,
        }
        return cls.describe(name)

    @classmethod
    def poll(cls, name: str) -> list[dict[str, Any]]:
        sensor = cls._sensors.get(name)
        if not sensor:
            return []
        readings = sensor["reader"]() or []
        sensor["reads"] += len(readings)
        return [
            {
                "event_type": "NORMAL_EVENT",
                "runtime_state": "OPERATIONAL",
                "payload": reading if isinstance(reading, dict) else {"value": reading},
                "sensor": name,
            }
            for reading in readings
        ]

    @classmethod
    def describe(cls, name: str) -> dict[str, Any]:
        sensor = cls._sensors.get(name, {})
        return {k: v for k, v in sensor.items() if k != "reader"}

    @classmethod
    def list_sensors(cls) -> list[dict[str, Any]]:
        return [cls.describe(name) for name in cls._sensors]

    @classmethod
    def reset(cls) -> None:
        cls._sensors = {}
