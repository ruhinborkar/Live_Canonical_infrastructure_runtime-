"""Structured runtime configuration.

Single typed access point for runtime settings, layering environment-variable
overrides on top of the active environment profile. No secrets live here —
those go through security.secrets_provider.
"""

import os
from typing import Any

from config.environment_profiles import resolve_profile


class RuntimeConfig:
    _cache: dict[str, Any] | None = None

    @classmethod
    def load(cls, *, refresh: bool = False) -> dict[str, Any]:
        if cls._cache is not None and not refresh:
            return cls._cache
        env = os.getenv("RUNTIME_ENV", "development")
        profile_name, profile = resolve_profile(env)

        config = {
            "environment": profile_name,
            "runtime_version": os.getenv("RUNTIME_VERSION", "2.0.0"),
            "worker_count": int(os.getenv("RUNTIME_WORKERS", profile["worker_count"])),
            "heartbeat_interval": float(
                os.getenv("RUNTIME_HEARTBEAT_INTERVAL", profile["heartbeat_interval"])
            ),
            "rate_limit_per_minute": int(
                os.getenv("RUNTIME_RATE_LIMIT", profile["rate_limit_per_minute"])
            ),
            "log_level": os.getenv("RUNTIME_LOG_LEVEL", profile["log_level"]).upper(),
            "degrade_on_invalid_rate": float(
                os.getenv("RUNTIME_DEGRADE_INVALID_RATE", profile["degrade_on_invalid_rate"])
            ),
            "autostart_engine": os.getenv("RUNTIME_AUTOSTART", "true").lower() == "true",
        }
        cls._cache = config
        return config

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        return cls.load().get(key, default)
