"""Command-center operational runtime API.

Exposes live runtime state, work intake, queue, situation awareness,
intelligence, topology, diagnostics, and readiness. All values are real
runtime state derived from the operational backbone (no mock data).
"""

from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from services.operational_runtime_service import OperationalRuntimeService

router = APIRouter(prefix="/operations", tags=["operational-runtime"])


@router.get("/status")
def operations_status():
    return OperationalRuntimeService.status()


@router.get("/situation")
def operations_situation():
    return OperationalRuntimeService.situation()


@router.post("/start")
def operations_start():
    return OperationalRuntimeService.start()


@router.post("/stop")
def operations_stop():
    return OperationalRuntimeService.shutdown()


@router.post("/submit")
def operations_submit(
    payload: dict[str, Any] = Body(..., embed=False),
    priority: int | None = Query(default=None, ge=1, le=9),
):
    result = OperationalRuntimeService.submit_work(payload, priority=priority)
    if not result.get("accepted"):
        raise HTTPException(status_code=429, detail=result.get("reason", "rejected"))
    return result


@router.get("/queue")
def operations_queue():
    return OperationalRuntimeService.queue()


@router.get("/timeline")
def operations_timeline(limit: int = Query(default=100, ge=1, le=500)):
    return OperationalRuntimeService.timeline(limit=limit)


@router.get("/operator-timeline")
def operations_operator_timeline(limit: int = Query(default=100, ge=1, le=500)):
    return OperationalRuntimeService.operator_timeline(limit=limit)


@router.get("/alerts")
def operations_alerts():
    return OperationalRuntimeService.alerts()


@router.post("/alerts/{alert_id}/acknowledge")
def operations_ack_alert(alert_id: str, operator: str = Query(default="operator")):
    return OperationalRuntimeService.acknowledge_alert(alert_id, operator=operator)


@router.get("/topology")
def operations_topology():
    return OperationalRuntimeService.topology()


@router.get("/dependency-graph")
def operations_dependency_graph():
    return OperationalRuntimeService.dependency_graph()


@router.get("/intelligence")
def operations_intelligence():
    return OperationalRuntimeService.intelligence()


@router.get("/resources")
def operations_resources():
    return OperationalRuntimeService.resources()


@router.get("/diagnostics")
def operations_diagnostics():
    return OperationalRuntimeService.diagnostics()


@router.get("/readiness")
def operations_readiness():
    return OperationalRuntimeService.readiness()


@router.get("/dependencies")
def operations_dependencies():
    return OperationalRuntimeService.dependencies()


@router.get("/contexts")
def operations_contexts():
    return OperationalRuntimeService.contexts()


@router.get("/capabilities")
def operations_capabilities():
    return OperationalRuntimeService.capabilities_catalog()
