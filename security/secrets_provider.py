"""Secrets provider abstraction.

A single indirection for retrieving secrets so the rest of the codebase never
reads environment variables or files directly. The default backend reads from
the process environment; alternative backends (vault, file, KMS) can be added
without changing callers. Secret values are never logged or echoed.
"""

import os
from typing import Any


class SecretsProvider:
    _backend = "env"

    @classmethod
    def get(cls, key: str, *, default: str | None = None) -> str | None:
        if cls._backend == "env":
            return os.getenv(key, default)
        return default

    @classmethod
    def require(cls, key: str) -> str:
        value = cls.get(key)
        if value is None:
            raise KeyError(f"required secret not configured: {key}")
        return value

    @classmethod
    def has(cls, key: str) -> bool:
        return cls.get(key) is not None

    @classmethod
    def describe(cls) -> dict[str, Any]:
        """Non-sensitive description of provider state for diagnostics."""
        return {"backend": cls._backend, "source": "process-environment"}
