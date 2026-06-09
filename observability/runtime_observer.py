from typing import Callable


class RuntimeObserver:
    _listeners: list[Callable[[str, str], None]] = []

    @classmethod
    def add_listener(cls, callback: Callable[[str, str], None]) -> None:
        cls._listeners.append(callback)

    @classmethod
    def remove_listener(cls, callback: Callable[[str, str], None]) -> None:
        if callback in cls._listeners:
            cls._listeners.remove(callback)

    @classmethod
    def clear_listeners(cls) -> None:
        cls._listeners.clear()

    @staticmethod
    def observe(stage, status):
        print(f"[OBSERVABILITY] STAGE={stage} | STATUS={status}")
        for listener in RuntimeObserver._listeners:
            listener(stage, status)