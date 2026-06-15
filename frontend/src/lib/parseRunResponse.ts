import { LiveResult, RunMode, VerifyResult } from "../api/client";
import { normalizeVerifyPayload, normalizeVerifyResults } from "./normalize";

export type OperationState = "idle" | "running" | "success" | "error";

export interface OperationMeta {
  state: OperationState;
  error: string | null;
  completedAt: string | null;
}

export const INITIAL_OPERATION_META: OperationMeta = {
  state: "idle",
  error: null,
  completedAt: null,
};

export function pickReplayStatus(data: Record<string, unknown>): string {
  return String(data.verification_result ?? data.replay_status ?? "UNKNOWN");
}

export function pickRecoveryOutcome(data: Record<string, unknown>): string {
  return String(data.recovery_outcome ?? data.recovery_status ?? "UNKNOWN");
}

export function pickVerifyResults(data: Record<string, unknown>): VerifyResult[] {
  return normalizeVerifyResults(data);
}

export { normalizeVerifyPayload };

export function parseLiveResult(data: Record<string, unknown>): LiveResult {
  const runtime = data.runtime_execution as LiveResult["runtime_execution"] | undefined;
  const dataset = data.dataset as LiveResult["dataset"] | undefined;

  return {
    run_id: String(data.run_id ?? ""),
    status: String(data.status ?? "completed"),
    replay_status: pickReplayStatus(data),
    truth_status: String(
      (data.truth_reconstruction as Record<string, unknown> | undefined)?.truth_verification ??
        data.truth_status ??
        "UNKNOWN"
    ),
    recovery_status: pickRecoveryOutcome(
      (data.recovery as Record<string, unknown> | undefined) ?? data
    ),
    runtime_execution: runtime ?? {
      processed_events: 0,
      valid_events: 0,
      invalid_events: 0,
    },
    dataset: dataset ?? {
      total_events: 0,
      normal_events: 0,
      corrupted_events: 0,
      interrupted_events: 0,
    },
  };
}

export function operationLabel(mode: RunMode): string {
  const labels: Record<RunMode, string> = {
    live: "Run Live",
    replay: "Replay",
    recover: "Recover",
    verify: "Verify",
  };
  return labels[mode];
}
