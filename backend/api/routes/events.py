from fastapi import APIRouter, Query

from services.runtime_service import RuntimeService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events(
    log: str = Query(default="live", pattern="^(live|replay|recovery)$"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return RuntimeService.load_events(log=log, limit=limit, offset=offset)
