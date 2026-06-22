"""Startup validation for deployable runtime readiness."""

import os
from pathlib import Path
from typing import Any

from backend.api.runtime_meta import RUNTIME_VERSION


class StartupValidator:
    @classmethod
    def validate(cls) -> dict[str, Any]:
        checks = {
            "persistence_available": cls._check_persistence(),
            "dataset_available": cls._check_dataset(),
            "configuration_valid": cls._check_configuration(),
            "runtime_ready": cls._check_runtime_ready(),
        }
        ready = all(checks.values())
        return {
            "ready": ready,
            "runtime_version": RUNTIME_VERSION,
            "checks": checks,
            "status": "READY" if ready else "NOT_READY",
        }

    @staticmethod
    def _check_persistence() -> bool:
        for directory in ("logging/logs", "logging/truth_ledger", "observability", "data"):
            path = Path(directory)
            try:
                path.mkdir(parents=True, exist_ok=True)
                probe = path / ".startup_probe"
                probe.write_text("ok", encoding="utf-8")
                probe.unlink(missing_ok=True)
            except OSError:
                return False
        return True

    @staticmethod
    def _check_dataset() -> bool:
        dataset = Path("datasets/runtime_dataset.jsonl")
        if dataset.exists() and dataset.stat().st_size > 0:
            return True
        generator = Path("datasets/runtime_dataset_generator.py")
        return generator.exists()

    @staticmethod
    def _check_configuration() -> bool:
        required_paths = ("backend/api/main.py", "services/runtime_service.py", "run_system.py")
        if not all(Path(path).exists() for path in required_paths):
            return False
        runtime_env = os.getenv("RUNTIME_ENV", "development")
        return runtime_env in {"development", "production", "staging"}

    @staticmethod
    def _check_runtime_ready() -> bool:
        from observability.health_monitor import HealthMonitor

        persistence = HealthMonitor.check_persistence_health()
        return persistence != "PERSISTENCE_UNAVAILABLE"
