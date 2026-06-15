import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from fastapi import APIRouter, HTTPException

from services.run_store import complete_run, create_run, get_run, list_runs
from services.runtime_service import RuntimeService

router = APIRouter(prefix="/runs", tags=["runs"])
_executor = ThreadPoolExecutor(max_workers=4)


def _run_in_thread(fn, *args) -> Any:
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(_executor, fn, *args)


@router.get("")
async def get_runs(limit: int = 20):
    return {"runs": list_runs(limit=limit)}


@router.get("/report/latest")
async def get_latest_report():
    report = RuntimeService.get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No report available")
    return report


@router.get("/{run_id}")
async def get_run_by_id(run_id: str):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("/live")
async def run_live():
    run_id = create_run("live")
    try:
        result = await _run_in_thread(RuntimeService.execute_live)
        complete_run(run_id, "completed", result)
        return {"run_id": run_id, "status": "completed", **result}
    except Exception as exc:
        complete_run(run_id, "failed", {"error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/replay")
async def run_replay():
    run_id = create_run("replay")
    try:
        result = await _run_in_thread(RuntimeService.execute_replay)
        complete_run(run_id, "completed", result)
        return {"run_id": run_id, "status": "completed", **result}
    except Exception as exc:
        complete_run(run_id, "failed", {"error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/recover")
async def run_recover():
    run_id = create_run("recover")
    try:
        result = await _run_in_thread(RuntimeService.execute_recover)
        complete_run(run_id, "completed", result)
        return {"run_id": run_id, "status": "completed", **result}
    except Exception as exc:
        complete_run(run_id, "failed", {"error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/verify")
async def run_verify():
    run_id = create_run("verify")
    try:
        result = await _run_in_thread(RuntimeService.execute_verify)
        failure_path_results = result.get("failure_path_results", [])
        stored = {**result, "failure_path_results": failure_path_results}
        complete_run(run_id, "completed", stored)
        return {
            "run_id": run_id,
            "status": "completed",
            "truth_verification": result.get("truth_verification"),
            "truth_checks": result.get("truth_checks"),
            "failure_path_results": failure_path_results,
            "results": failure_path_results,
            "verify": result,
        }
    except Exception as exc:
        complete_run(run_id, "failed", {"error": str(exc)})
        raise HTTPException(status_code=500, detail=str(exc)) from exc
