from fastapi import APIRouter

from backend.api.runtime_meta import RUNTIME_VERSION, runtime_environment_label
from observability.health_monitor import HealthMonitor
from observability.startup_validator import StartupValidator

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "canonical-infrastructure-runtime",
        "runtime_version": RUNTIME_VERSION,
        "environment": runtime_environment_label(),
    }


@router.get("/health/monitor")
def health_monitor():
    return HealthMonitor.get_status()


@router.get("/startup/validation")
def startup_validation():
    return StartupValidator.validate()
