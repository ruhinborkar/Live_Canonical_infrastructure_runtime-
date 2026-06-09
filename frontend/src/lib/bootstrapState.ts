import { QueryClient } from "@tanstack/react-query";
import { api, LiveResult, VerifyResult } from "../api/client";
import { queryKeys } from "../hooks/queryKeys";

function reportToLiveResult(report: Record<string, unknown>): LiveResult | null {
  const replay = report.replay as Record<string, unknown> | undefined;
  const truth = report.truth_reconstruction as Record<string, unknown> | undefined;
  const recovery = report.recovery as Record<string, unknown> | undefined;
  const runtime = report.runtime_execution as LiveResult["runtime_execution"] | undefined;
  const dataset = report.dataset as LiveResult["dataset"] | undefined;

  if (!replay && !runtime) return null;

  return {
    run_id: "",
    status: "completed",
    replay_status: String(replay?.verification_result ?? "—"),
    truth_status: String(truth?.truth_verification ?? "—"),
    recovery_status: String(recovery?.recovery_status ?? "—"),
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

export async function bootstrapRuntimeState(queryClient: QueryClient): Promise<void> {
  try {
    const report = await api.getLatestReport();
    const live = reportToLiveResult(report);
    if (live) {
      queryClient.setQueryData(queryKeys.lastLive, live);
    }
  } catch {
    // No report yet
  }

  try {
    const { runs } = await api.listRuns(50);

    const lastVerify = runs.find((r) => r.mode === "verify" && r.result?.results);
    if (lastVerify?.result?.results) {
      queryClient.setQueryData(
        queryKeys.lastVerify,
        lastVerify.result.results as VerifyResult[]
      );
    }

    const lastReplay = runs.find((r) => r.mode === "replay" && r.result);
    if (lastReplay?.result?.verification_result) {
      queryClient.setQueryData(queryKeys.lastReplay, {
        verification_result: String(lastReplay.result.verification_result),
      });
    }

    const lastRecover = runs.find((r) => r.mode === "recover" && r.result);
    const recoverOutcome =
      lastRecover?.result?.recovery_outcome ?? lastRecover?.result?.recovery_status;
    if (recoverOutcome) {
      queryClient.setQueryData(queryKeys.lastRecover, {
        recovery_outcome: String(recoverOutcome),
      });
    }
  } catch {
    // API offline
  }
}
