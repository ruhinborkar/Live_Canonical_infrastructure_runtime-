from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from services.runtime_console_service import (
    get_report_content,
    get_runtime_events,
    get_runtime_logs,
    get_runtime_metrics,
    get_runtime_reports,
    get_runtime_runs,
    get_runtime_status,
)

router = APIRouter(prefix="/runtime", tags=["runtime-console"])


@router.get("/status")
def runtime_status():
    return get_runtime_status()


@router.get("/runs")
def runtime_runs(limit: int = Query(default=20, ge=1, le=100)):
    return get_runtime_runs(limit=limit)


@router.get("/events")
def runtime_events(
    log: Literal["live", "replay", "recovery"] = Query(default="live"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    status: Literal["VALID", "INVALID"] | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
    category: Literal["normal", "corrupted", "interrupted"] | None = Query(default=None),
):
    return get_runtime_events(
        log=log,
        limit=limit,
        offset=offset,
        status=status,
        search=search,
        category=category,
    )


@router.get("/metrics")
def runtime_metrics():
    return get_runtime_metrics()


@router.get("/logs")
def runtime_logs(limit: int = Query(default=100, ge=1, le=500)):
    return get_runtime_logs(limit=limit)


@router.get("/reports")
def runtime_reports():
    return get_runtime_reports()


@router.get("/reports/{artifact_name}/content")
def runtime_report_content(
    artifact_name: str,
    line_limit: int = Query(default=150, ge=1, le=500),
):
    try:
        return get_report_content(artifact_name, line_limit=line_limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
