"""Environment profiles.

Named operational profiles (development / staging / production) that set safe
defaults for runtime behaviour. Selected via the RUNTIME_ENV variable.
"""

from typing import Any

PROFILES: dict[str, dict[str, Any]] = {
    "development": {
        "worker_count": 2,
        "heartbeat_interval": 1.0,
        "rate_limit_per_minute": 0,          # 0 = unlimited
        "log_level": "DEBUG",
        "degrade_on_invalid_rate": 0.5,
    },
    "staging": {
        "worker_count": 3,
        "heartbeat_interval": 1.0,
        "rate_limit_per_minute": 600,
        "log_level": "INFO",
        "degrade_on_invalid_rate": 0.35,
    },
    "production": {
        "worker_count": 4,
        "heartbeat_interval": 1.0,
        "rate_limit_per_minute": 1200,
        "log_level": "INFO",
        "degrade_on_invalid_rate": 0.25,
    },
}

_ALIASES = {"dev": "development", "stage": "staging", "prod": "production"}


def resolve_profile(env: str) -> tuple[str, dict[str, Any]]:
    key = _ALIASES.get(env.lower(), env.lower())
    if key not in PROFILES:
        key = "development"
    return key, dict(PROFILES[key])
