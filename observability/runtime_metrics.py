import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

METRICS_FILE = Path("observability/runtime_metrics.json")


class RuntimeMetricsCollector:
    _stage_started: dict[str, float] = {}
    _metrics: dict[str, Any] = {}
    _logs: list[dict[str, str]] = []

    @classmethod
    def reset(cls) -> None:
        cls._stage_started = {}
        cls._metrics = {
            "validation_latency_ms": 0,
            "serialization_time_ms": 0,
            "hash_computation_time_ms": 0,
            "persistence_writes": 0,
            "replay_duration_ms": 0,
            "recovery_duration_ms": 0,
            "total_pipeline_ms": 0,
            "last_updated": None,
        }
        cls._logs = []

    @classmethod
    def on_stage(cls, stage: str, status: str) -> None:
        now = time.perf_counter()
        ts = datetime.now(timezone.utc).isoformat()

        cls._logs.append(
            {
                "timestamp": ts,
                "stage": stage,
                "status": status,
                "message": f"{stage} → {status}",
                "level": "ERROR" if "FAILED" in status or "MISMATCH" in status else "INFO",
            }
        )
        cls._logs = cls._logs[-500:]

        if status.endswith("_STARTED") or status == "STARTED":
            cls._stage_started[stage] = now
            return

        started = cls._stage_started.get(stage)
        if started is None:
            return

        duration_ms = round((now - started) * 1000, 2)
        cls._stage_started.pop(stage, None)

        mapping = {
            "VALIDATION": "validation_latency_ms",
            "SERIALIZATION": "serialization_time_ms",
            "HASHING": "hash_computation_time_ms",
            "PERSISTENCE": "persistence_writes",
            "REPLAY": "replay_duration_ms",
            "RECOVERY": "recovery_duration_ms",
        }

        key = mapping.get(stage)
        if key == "persistence_writes":
            cls._metrics[key] = cls._metrics.get(key, 0) + 1
        elif key:
            cls._metrics[key] = duration_ms

        cls._metrics["last_updated"] = ts

    @classmethod
    def set_pipeline_timings(
        cls,
        *,
        validation_ms: float | None = None,
        serialization_ms: float | None = None,
        hash_ms: float | None = None,
        persistence_writes: int | None = None,
        replay_ms: float | None = None,
        recovery_ms: float | None = None,
    ) -> None:
        if validation_ms is not None:
            cls._metrics["validation_latency_ms"] = validation_ms
        if serialization_ms is not None:
            cls._metrics["serialization_time_ms"] = serialization_ms
        if hash_ms is not None:
            cls._metrics["hash_computation_time_ms"] = hash_ms
        if persistence_writes is not None:
            cls._metrics["persistence_writes"] = persistence_writes
        if replay_ms is not None:
            cls._metrics["replay_duration_ms"] = replay_ms
        if recovery_ms is not None:
            cls._metrics["recovery_duration_ms"] = recovery_ms
        cls._metrics["last_updated"] = datetime.now(timezone.utc).isoformat()

    @classmethod
    def set_counts(cls, processed: int, writes: int | None = None) -> None:
        if writes is not None:
            cls._metrics["persistence_writes"] = writes
        cls._metrics["processed_events"] = processed
        cls._metrics["last_updated"] = datetime.now(timezone.utc).isoformat()

    @classmethod
    def finalize(cls, total_ms: float | None = None) -> None:
        if total_ms is not None:
            cls._metrics["total_pipeline_ms"] = round(total_ms, 2)
        cls._metrics["last_updated"] = datetime.now(timezone.utc).isoformat()
        cls._persist()

    @classmethod
    def _persist(cls) -> None:
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(METRICS_FILE, "w", encoding="utf-8") as file:
            json.dump({"metrics": cls._metrics, "logs": cls._logs[-200:]}, file, indent=2)

    @classmethod
    def _load_file(cls) -> None:
        if not METRICS_FILE.exists():
            return
        with open(METRICS_FILE, encoding="utf-8") as file:
            data = json.load(file)
            if data.get("metrics"):
                cls._metrics = data["metrics"]
            if data.get("logs"):
                cls._logs = data["logs"]

    @classmethod
    def get_metrics(cls) -> dict[str, Any]:
        if not cls._metrics and METRICS_FILE.exists():
            cls._load_file()
        return dict(cls._metrics) if cls._metrics else {
            "validation_latency_ms": 0,
            "serialization_time_ms": 0,
            "hash_computation_time_ms": 0,
            "persistence_writes": 0,
            "replay_duration_ms": 0,
            "recovery_duration_ms": 0,
            "total_pipeline_ms": 0,
            "last_updated": None,
        }

    @classmethod
    def get_logs(cls, limit: int = 100) -> list[dict[str, str]]:
        if not cls._logs and METRICS_FILE.exists():
            cls._load_file()
        return list(reversed(cls._logs[-limit:]))

    @classmethod
    def get_snapshot(cls) -> dict[str, Any]:
        return {"metrics": cls.get_metrics(), "logs": cls.get_logs(100)}
