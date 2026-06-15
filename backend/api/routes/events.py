from typing import Literal

from fastapi import APIRouter, Query

from services.event_loader import load_event_summary, load_events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/summary")
def get_events_summary():
    return load_event_summary()


@router.get("")
def list_events(
    log: Literal["live", "replay", "recovery"] = Query(default="live"),
    mode: Literal["live", "replay", "recovery"] | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    status: Literal["VALID", "INVALID"] | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
    event_type: Literal["normal", "corrupted", "interrupted"] | None = Query(default=None),
    category: Literal["normal", "corrupted", "interrupted"] | None = Query(default=None),
):
    return load_events(
        log=log,
        mode=mode,
        limit=limit,
        offset=offset,
        status=status,
        search=search,
        event_type=event_type,
        category=category,
    )
