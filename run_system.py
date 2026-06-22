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
        choices=["live", "replay", "recover", "verify", "demo", "ledger", "inject", "manifest"],
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
