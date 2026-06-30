"""Dependency monitor.

Checks the runtime's critical local dependencies (filesystem persistence
paths, dataset availability, ledger directory) and reports their health.
Generic and offline-safe; no network calls.
"""

from pathlib import Path
from typing import Any


class DependencyMonitor:
    DEPENDENCIES = {
        "live_log_dir": "logging/logs",
        "truth_ledger_dir": "logging/truth_ledger",
        "data_dir": "data",
        "dataset": "datasets/runtime_dataset.jsonl",
    }

    @classmethod
    def check(cls) -> dict[str, Any]:
        results = {}
        for name, path in cls.DEPENDENCIES.items():
            p = Path(path)
            if name == "dataset":
                ok = p.exists() and p.stat().st_size > 0 if p.exists() else False
                # dataset is regenerable; treat generator presence as acceptable
                if not ok and Path("datasets/runtime_dataset_generator.py").exists():
                    ok = True
            else:
                ok = cls._writable(p)
            results[name] = {"path": path, "healthy": ok}
        healthy = sum(1 for r in results.values() if r["healthy"])
        total = len(results)
        return {
            "healthy": healthy == total,
            "healthy_count": healthy,
            "total": total,
            "dependencies": results,
        }

    @staticmethod
    def _writable(path: Path) -> bool:
        try:
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".dep_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return True
        except OSError:
            return False
