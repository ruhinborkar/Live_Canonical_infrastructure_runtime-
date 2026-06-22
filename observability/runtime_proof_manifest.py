"""Aggregate executable runtime proof artifacts into a single manifest."""

import json
import os
from pathlib import Path
from typing import Any

from observability.health_monitor import HealthMonitor
from observability.startup_validator import StartupValidator

MANIFEST_FILE = "runtime_proof_manifest.json"

PROOF_PATHS = {
    "truth_ledger": "truth_ledger_reconstruction_proof.json",
    "failure_injection": "failure_injection_proof.json",
    "recovery": "runtime_recovery_proof.json",
    "recovery_execution": "runtime_recovery_execution_proof.json",
    "runtime_report": "observability/final_runtime_report.json",
}


class RuntimeProofManifest:
    @classmethod
    def _load_json(cls, path: str) -> dict[str, Any] | None:
        file_path = Path(path)
        if not file_path.exists():
            return None
        with open(file_path, encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def export(cls) -> dict[str, Any]:
        artifacts: dict[str, Any] = {}
        for name, path in PROOF_PATHS.items():
            payload = cls._load_json(path)
            artifacts[name] = {
                "path": path,
                "available": payload is not None,
                "payload": payload,
            }

        health = HealthMonitor.get_status()
        startup = StartupValidator.validate()

        checks = {
            "truth_ledger_success": (
                artifacts["truth_ledger"]["payload"] or {}
            ).get("truth_reconstruction") == "SUCCESS",
            "failure_injection_detected": (
                (artifacts["failure_injection"]["payload"] or {}).get("detected_count", 0) > 0
            ),
            "recovery_executable": (
                (artifacts["recovery"]["payload"] or {}).get("recovery_executed", False)
                or (artifacts["recovery_execution"]["payload"] or {}).get(
                    "recovery_executed", False
                )
            ),
            "startup_ready": startup.get("ready", False),
            "health_available": health.get("overall") in {"HEALTHY", "DEGRADED"},
        }

        manifest = {
            "proof_type": "RUNTIME_PROOF_MANIFEST",
            "overall": "PASS" if all(checks.values()) else "PARTIAL",
            "checks": checks,
            "artifacts": {
                name: {
                    "path": data["path"],
                    "available": data["available"],
                }
                for name, data in artifacts.items()
            },
            "health": health,
            "startup": startup,
        }

        os.makedirs(os.path.dirname(MANIFEST_FILE) or ".", exist_ok=True)
        with open(MANIFEST_FILE, "w", encoding="utf-8") as file:
            json.dump(manifest, file, indent=4)

        return manifest
