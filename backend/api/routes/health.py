from fastapi import APIRouter

from backend.api.runtime_meta import RUNTIME_VERSION, runtime_environment_label

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "canonical-infrastructure-runtime",
        "runtime_version": RUNTIME_VERSION,
        "environment": runtime_environment_label(),
    }
