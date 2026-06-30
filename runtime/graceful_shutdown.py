"""Graceful shutdown coordination.

Registers OS signal handlers (where supported) so an interrupt triggers an
orderly drain instead of an abrupt kill. Safe to use under uvicorn or a bare
CLI process; signal registration is skipped when not on the main thread.
"""

import signal
import threading
from typing import Any, Callable

ShutdownHook = Callable[[], None]


class GracefulShutdown:
    _hooks: list[ShutdownHook] = []
    _registered = False
    _lock = threading.RLock()

    @classmethod
    def register(cls, hook: ShutdownHook) -> None:
        with cls._lock:
            cls._hooks.append(hook)
            cls._install_signal_handlers()

    @classmethod
    def _install_signal_handlers(cls) -> None:
        if cls._registered:
            return
        if threading.current_thread() is not threading.main_thread():
            # Signal handlers can only be installed from the main thread.
            return
        for sig_name in ("SIGINT", "SIGTERM"):
            sig = getattr(signal, sig_name, None)
            if sig is None:
                continue
            try:
                signal.signal(sig, cls._handle)
            except (ValueError, OSError, RuntimeError):
                continue
        cls._registered = True

    @classmethod
    def _handle(cls, signum: int, frame: Any) -> None:  # noqa: ANN401
        cls.trigger()

    @classmethod
    def trigger(cls) -> None:
        with cls._lock:
            hooks = list(cls._hooks)
        for hook in hooks:
            try:
                hook()
            except Exception:  # noqa: BLE001 - shutdown must be best-effort
                continue

    @classmethod
    def reset(cls) -> None:
        with cls._lock:
            cls._hooks = []
