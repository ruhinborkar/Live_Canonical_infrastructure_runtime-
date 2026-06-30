import argparse
import json

from services.runtime_service import RuntimeService


def execute_live_runtime():
    result = RuntimeService.execute_live()
    print("\nLIVE EXECUTION COMPLETE")
    print(result["replay_status"])
    print(result["truth_status"])
    print("OBSERVABILITY GENERATED")
    print(json.dumps(result, indent=4))
    print(f"\nREPORT PATH: {result['report_path']}")
    print(f"RECOVERY PROOF: {result.get('recovery_proof_path')}")


def run_replay():
    result = RuntimeService.execute_replay()
    print(json.dumps(result, indent=4))


def run_recover():
    result = RuntimeService.execute_recover()
    print(json.dumps(result, indent=4))


def run_verify():
    result = RuntimeService.execute_verify()
    print(result["truth_verification"])
    print(json.dumps(result, indent=4))


def run_ledger():
    result = RuntimeService.execute_ledger_reconstruct()
    print(result["truth_reconstruction"])
    print(result["source"])
    print(result["runtime_state"])
    print(json.dumps(result, indent=4))


def run_inject():
    result = RuntimeService.execute_injection()
    for row in result["injection_results"]:
        print(f"{row['failure_type']}: detected={row['detected']} response={row['system_response']}")
    print(json.dumps(result, indent=4))


def run_manifest():
    result = RuntimeService.execute_manifest()
    print(result.get("overall", "UNKNOWN"))
    print(json.dumps(result, indent=4))


def run_operate(duration: float = 0.0):
    """Boot the operational runtime backbone and keep it alive.

    Continuously feeds synthetic work and runs until interrupted (Ctrl+C) or,
    when --duration is given, for that many seconds. Proves the runtime stays
    alive and processes work continuously.
    """
    import time

    from services.operational_runtime_service import OperationalRuntimeService

    boot = OperationalRuntimeService.boot()
    print("OPERATIONAL RUNTIME STARTED:", boot["state"])
    counter = 0
    start = time.time()
    try:
        while True:
            counter += 1
            OperationalRuntimeService.submit_work(
                {"payload": {"temperature": 20 + (counter % 10), "signal": "OK"}},
                priority=5,
            )
            status = OperationalRuntimeService.status()
            print(
                f"tick={status['heartbeat']['heartbeat_tick']} "
                f"accepted={status['counters'].get('tasks_accepted')} "
                f"completed={status['counters'].get('tasks_completed')} "
                f"pending={status['queue']['pending']} state={status['state']}"
            )
            if duration and (time.time() - start) >= duration:
                break
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nInterrupt received — shutting down gracefully")
    finally:
        result = OperationalRuntimeService.shutdown()
        print("OPERATIONAL RUNTIME STOPPED:", result["state"])


def run_smoke():
    """Automated continuous-runtime smoke test with readiness proof."""
    import time

    from services.operational_runtime_service import OperationalRuntimeService

    boot = OperationalRuntimeService.boot()
    assert boot["state"] == "RUNNING", boot
    for i in range(1, 31):
        OperationalRuntimeService.submit_work(
            {"payload": {"temperature": 20 + (i % 10), "signal": "OK"}}, priority=4
        )
    OperationalRuntimeService.submit_work(
        {"event_type": "CORRUPTED_EVENT", "payload": {"temperature": None}}, priority=1
    )
    from runtime.background_runtime_engine import get_engine

    get_engine().drain_until_idle(timeout=15)
    time.sleep(1.5)
    status = OperationalRuntimeService.status()
    readiness = OperationalRuntimeService.readiness()
    OperationalRuntimeService.shutdown()
    print("SMOKE RESULT")
    print(json.dumps({
        "engine_state_after_work": status["state"],
        "heartbeat_alive": status["heartbeat"]["alive"],
        "tasks_accepted": status["counters"].get("tasks_accepted"),
        "tasks_completed": status["counters"].get("tasks_completed"),
        "tasks_invalid": status["counters"].get("tasks_invalid"),
        "readiness_score": readiness["score"],
        "readiness_grade": readiness["grade"],
    }, indent=4))


def run_demo():
    result = RuntimeService.execute_demo()

    print("\nDEMO EXECUTION COMPLETE")
    print(result["live"]["replay_status"])
    print(result["truth_verification"])
    print(result["recovery"]["recovery_outcome"])
    print(f"REPORT PATH: {result['report_path']}")
    print(f"RECOVERY PROOF: {result['recovery_proof_path']}")
    if result.get("live", {}).get("truth_ledger_proof_path"):
        print(f"TRUTH LEDGER PROOF: {result['live']['truth_ledger_proof_path']}")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Live Canonical Infrastructure Runtime"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="live",
        choices=[
            "live", "replay", "recover", "verify", "demo", "ledger", "inject",
            "manifest", "operate", "smoke",
        ],
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.0,
        help="For --mode operate: seconds to run before stopping (0 = until Ctrl+C)",
    )
    args = parser.parse_args()
    print(f"\nRUNNING MODE: {args.mode}\n")

    if args.mode == "live":
        execute_live_runtime()
    elif args.mode == "replay":
        run_replay()
    elif args.mode == "recover":
        run_recover()
    elif args.mode == "verify":
        run_verify()
    elif args.mode == "demo":
        run_demo()
    elif args.mode == "ledger":
        run_ledger()
    elif args.mode == "inject":
        run_inject()
    elif args.mode == "manifest":
        run_manifest()
    elif args.mode == "operate":
        run_operate(duration=args.duration)
    elif args.mode == "smoke":
        run_smoke()
