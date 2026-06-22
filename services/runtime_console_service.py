from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.api.runtime_meta import RUNTIME_VERSION, runtime_environment_label
from observability.final_runtime_reporter import FinalRuntimeReporter
from observability.runtime_metrics import RuntimeMetricsCollector
from observability.startup_validator import StartupValidator
from services.event_loader import load_event_summary, load_events
from services.run_store import list_runs


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _duration_ms(start: str | None, end: str | None) -> int | None:
    s, e = _parse_ts(start), _parse_ts(end)
    if not s or not e:
        return None
    return max(0, int((e - s).total_seconds() * 1000))


def _short_id(run_id: str) -> str:
    return run_id.split("-")[0]


def _pick(d: dict | None, *keys: str, default: str = "—") -> str:
    if not d:
        return default
    for key in keys:
        val = d.get(key)
        if val is not None:
            return str(val)
    return default


def _load_report() -> tuple[dict[str, Any] | None, str | None]:
    import json

    path = Path(FinalRuntimeReporter.OUTPUT_FILE)
    if not path.exists():
        return None, None
    try:
        with open(path, encoding="utf-8") as f:
            report = json.load(f)
        modified = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
        return report, modified
    except Exception:
        return None, None


def _operational_status(replay: str, truth: str, recovery: str, processed: int) -> str:
    if processed == 0:
        return "IDLE"
    if "MISMATCH" in replay or "MISMATCH" in truth or "FAILED" in replay:
        return "FAILED"
    if "VERIFIED" in replay and "VERIFIED" in truth:
        return "OPERATIONAL"
    if "REQUIRED" in recovery or "REQUIRED" in replay:
        return "DEGRADED"
    return "IDLE"


def _latest_verify_run() -> dict[str, Any] | None:
    for run in list_runs(limit=50):
        if run.get("mode") != "verify" or run.get("status") != "completed":
            continue
        result = run.get("result") or {}
        if result.get("truth_verification"):
            return run
    return None


def _should_overlay_verify_truth(
    *,
    report_truth: str,
    report_updated: str | None,
    verify_completed_at: str | None,
) -> bool:
    if not verify_completed_at:
        return report_truth in ("NOT_RUN", "—", "")
    verify_dt = _parse_ts(verify_completed_at)
    report_dt = _parse_ts(report_updated)
    if report_truth in ("NOT_RUN", "—", ""):
        return True
    if verify_dt and report_dt:
        return verify_dt >= report_dt
    if verify_dt and not report_dt:
        return True
    return False


def get_runtime_status() -> dict[str, Any]:
    report, report_updated = _load_report()
    runs = list_runs(limit=1)
    last_run = runs[0] if runs else None
    runtime = (report or {}).get("runtime_execution", {})
    replay = (report or {}).get("replay", {})
    truth = (report or {}).get("truth_reconstruction", {})
    recovery = (report or {}).get("recovery", {})
    dataset = (report or {}).get("dataset", {})

    replay_status = _pick(replay, "verification_result", default="NOT_RUN")
    truth_status = _pick(truth, "truth_verification", default="NOT_RUN")
    recovery_status = _pick(recovery, "recovery_status", default="NOT_RUN")
    processed = runtime.get("processed_events", 0)

    last_ts = None
    if last_run:
        last_ts = last_run.get("completed_at") or last_run.get("created_at")

    last_updated = report_updated or last_ts
    truth_source = "report"
    truth_checks: dict[str, Any] | None = None
    validation_state_diff: dict[str, Any] | None = None
    recovery_state_diff: dict[str, Any] | None = None
    original_truth_hash: str | None = None
    reconstructed_truth_hash: str | None = None
    last_verify_run_id: str | None = None
    last_verify_at: str | None = None

    verify_run = _latest_verify_run()
    if verify_run:
        verify_result = verify_run.get("result") or {}
        verify_completed_at = verify_run.get("completed_at") or verify_run.get("created_at")
        last_verify_run_id = verify_run.get("id")
        last_verify_at = verify_completed_at

        truth_checks = verify_result.get("truth_checks")
        validation_state_diff = verify_result.get("validation_state_diff")
        recovery_state_diff = verify_result.get("recovery_state_diff")
        original_truth_hash = verify_result.get("original_truth_hash")
        reconstructed_truth_hash = verify_result.get("reconstructed_truth_hash")

        if _should_overlay_verify_truth(
            report_truth=truth_status,
            report_updated=report_updated,
            verify_completed_at=verify_completed_at,
        ):
            truth_status = _pick(verify_result, "truth_verification", default=truth_status)
            truth_source = "verify_run"
            last_updated = verify_completed_at or last_updated

    return {
        "runtime_status": _operational_status(
            replay_status, truth_status, recovery_status, processed
        ),
        "runtime_version": RUNTIME_VERSION,
        "environment": runtime_environment_label(),
        "last_updated": last_updated,
        "total_events_processed": processed,
        "valid_events": runtime.get("valid_events", 0),
        "invalid_events": runtime.get("invalid_events", 0),
        "events_replayed": replay.get("events_replayed", 0),
        "events_reconstructed": truth.get("events_reconstructed", 0),
        "recovery_points": recovery.get("interrupted_events", 0)
        or dataset.get("interrupted_events", 0),
        "replay_verification_status": replay_status,
        "truth_verification_status": truth_status,
        "recovery_status": recovery_status,
        "truth_source": truth_source,
        "truth_checks": truth_checks,
        "validation_state_diff": validation_state_diff,
        "recovery_state_diff": recovery_state_diff,
        "original_truth_hash": original_truth_hash,
        "reconstructed_truth_hash": reconstructed_truth_hash,
        "last_verify_run_id": last_verify_run_id,
        "last_verify_at": last_verify_at,
        "last_execution_timestamp": last_ts,
        "last_run_id": last_run.get("id") if last_run else None,
        "api_online": True,
        "dataset": dataset,
    }


def get_runtime_runs(limit: int = 20) -> dict[str, Any]:
    rows = []
    for run in list_runs(limit=limit):
        result = run.get("result") or {}
        runtime = result.get("runtime_execution") or {}
        replay = result.get("replay") or result
        truth = result.get("truth_reconstruction") or result
        recover = result.get("recovery") or result

        truth_result = _pick(
            truth,
            "truth_verification",
            "truth_status",
            default="—",
        )
        if run["mode"] == "verify" and truth_result == "—":
            truth_result = _pick(result, "truth_verification", default="—")

        rows.append(
            {
                "run_id": run["id"],
                "short_id": _short_id(run["id"]),
                "mode": run["mode"],
                "status": run["status"],
                "events_processed": runtime.get("processed_events")
                or result.get("events_replayed")
                or None,
                "replay_result": _pick(
                    replay,
                    "verification_result",
                    "replay_status",
                    default="—",
                ),
                "truth_result": truth_result,
                "recovery_result": _pick(
                    recover,
                    "recovery_status",
                    "recovery_outcome",
                    default="—",
                ),
                "duration_ms": _duration_ms(
                    run.get("created_at"), run.get("completed_at")
                ),
                "timestamp": run.get("completed_at") or run.get("created_at"),
                "created_at": run.get("created_at"),
                "completed_at": run.get("completed_at"),
            }
        )
    return {"runs": rows, "total": len(rows)}


def get_runtime_events(
    log: str = "live",
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    search: str | None = None,
    category: str | None = None,
    event_type: str | None = None,
    mode: str | None = None,
) -> dict[str, Any]:
    page = load_events(
        log=log,
        mode=mode,
        limit=limit,
        offset=offset,
        status=status,
        search=search,
        category=category,
        event_type=event_type,
    )
    log_key = page.get("log", log)
    events = []
    for event in page.get("events", []):
        hash_status = "—"
        if event.get("replay_verified") is True or event.get("validation_status") == "VALID":
            hash_status = "VERIFIED"
        elif event.get("replay_verified") is False or event.get("validation_status") == "INVALID":
            hash_status = "MISMATCH"
        elif event.get("payload_hash"):
            hash_status = "COMPUTED"

        events.append(
            {
                "trace_id": event.get("trace_id"),
                "sequence_id": event.get("sequence_id"),
                "event_type": event.get("event_type"),
                "runtime_state": event.get("runtime_state"),
                "validation_state": event.get("validation_status"),
                "hash_status": hash_status,
                "payload_hash": event.get("payload_hash"),
                "validation_reason": event.get("validation_reason"),
                "event_timestamp": event.get("event_timestamp"),
                "raw": event,
            }
        )

    return {
        **page,
        "events": events,
        "summary": load_event_summary().get("logs", {}).get(log_key, {}),
    }


def get_runtime_metrics() -> dict[str, Any]:
    metrics = RuntimeMetricsCollector.get_metrics()
    report, _ = _load_report()
    processed = metrics.get("processed_events", 0)
    if not processed and report:
        processed = (report.get("runtime_execution") or {}).get("processed_events", 0)

    total_ms = metrics.get("total_pipeline_ms", 0) or 0
    throughput = metrics.get("persistence_throughput_eps", 0) or 0.0
    if not throughput and total_ms > 0 and processed:
        throughput = round(processed / (total_ms / 1000), 2)

    return {
        "validation_latency_ms": metrics.get("validation_latency_ms", 0),
        "serialization_time_ms": metrics.get("serialization_time_ms", 0),
        "hash_computation_time_ms": metrics.get("hash_computation_time_ms", 0),
        "persistence_writes": metrics.get("persistence_writes", 0),
        "execution_duration_ms": metrics.get("execution_duration_ms", 0),
        "replay_duration_ms": metrics.get("replay_duration_ms", 0),
        "recovery_duration_ms": metrics.get("recovery_duration_ms", 0),
        "reconstruction_duration_ms": metrics.get("reconstruction_duration_ms", 0),
        "memory_consumption_mb": metrics.get("memory_consumption_mb", 0),
        "total_pipeline_ms": total_ms,
        "processed_events": processed,
        "events_failed": metrics.get("events_failed", 0),
        "runtime_throughput_eps": throughput,
        "persistence_throughput_eps": throughput,
        "last_updated": metrics.get("last_updated"),
    }


def get_startup_validation() -> dict[str, Any]:
    return StartupValidator.validate()


def get_health_monitor() -> dict[str, Any]:
    from observability.health_monitor import HealthMonitor

    return HealthMonitor.get_status()


def get_truth_ledger_status() -> dict[str, Any]:
    import json

    path = Path("truth_ledger_reconstruction_proof.json")
    if not path.exists():
        return {
            "available": False,
            "truth_reconstruction": "NOT_RUN",
            "source": "TRUTH_LEDGER",
            "runtime_state": "UNKNOWN",
        }
    with open(path, encoding="utf-8") as file:
        proof = json.load(file)
    return {"available": True, **proof}


def get_injection_results() -> dict[str, Any]:
    import json

    path = Path("failure_injection_proof.json")
    if not path.exists():
        return {"available": False, "results": [], "detected_count": 0}
    with open(path, encoding="utf-8") as file:
        proof = json.load(file)
    return {"available": True, **proof}


def get_proof_manifest() -> dict[str, Any]:
    import json

    path = Path("runtime_proof_manifest.json")
    if not path.exists():
        return {"available": False, "overall": "NOT_RUN", "checks": {}}
    with open(path, encoding="utf-8") as file:
        manifest = json.load(file)
    return {"available": True, **manifest}


def get_runtime_logs(limit: int = 100) -> dict[str, Any]:
    logs = []
    for entry in RuntimeMetricsCollector.get_logs(limit=limit):
        logs.append(
            {
                **entry,
                "message": entry.get("message") or f"{entry.get('stage', '—')} → {entry.get('status', '—')}",
            }
        )
    return {"logs": logs, "total": len(logs)}


def _file_report(path: Path, label: str) -> dict[str, Any]:
    exists = path.exists()
    modified = None
    size = None
    if exists:
        stat = path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        size = stat.st_size
    return {
        "name": label,
        "path": str(path).replace("\\", "/"),
        "exists": exists,
        "available": exists,
        "modified_at": modified,
        "size_bytes": size,
    }


def get_report_content(name: str, *, line_limit: int = 150) -> dict[str, Any]:
    reports = get_runtime_reports()["reports"]
    match = next((r for r in reports if r["name"] == name), None)
    if not match or not match.get("exists"):
        raise FileNotFoundError(f"Report not found: {name}")

    path = Path(match["path"])
    truncated = False

    if name.endswith(".jsonl"):
        lines: list[str] = []
        with open(path, encoding="utf-8") as file:
            for index, line in enumerate(file):
                if index >= line_limit:
                    truncated = True
                    break
                stripped = line.rstrip()
                if stripped:
                    lines.append(stripped)
        content = "\n".join(lines)
        if truncated:
            content += f"\n\n… truncated after {line_limit} lines"
    else:
        content = path.read_text(encoding="utf-8")
        if len(content) > 120_000:
            content = content[:120_000] + "\n\n… truncated for preview"
            truncated = True

    return {
        "name": name,
        "path": match["path"],
        "content": content,
        "truncated": truncated,
        "size_bytes": match.get("size_bytes"),
        "modified_at": match.get("modified_at"),
    }


def get_runtime_reports() -> dict[str, Any]:
    root = Path(".")
    review_packets = sorted(root.glob("REVIEW_PACKET*.md"), reverse=True)
    review_path = review_packets[0] if review_packets else root / "REVIEW_PACKET.md"

    artifacts = [
        _file_report(Path("logging/logs/live_execution.jsonl"), "live_execution.jsonl"),
        _file_report(Path(FinalRuntimeReporter.OUTPUT_FILE), "final_runtime_report.json"),
        _file_report(review_path, "REVIEW_PACKET.md"),
        _file_report(root / "README.md", "README.md"),
    ]
    return {"reports": artifacts, "total": len(artifacts)}
