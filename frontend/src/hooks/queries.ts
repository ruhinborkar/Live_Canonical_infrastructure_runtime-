import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, LiveResult, RunMode, VerifyResult } from "../api/client";
import { bootstrapRuntimeState } from "../lib/bootstrapState";
import { config } from "../lib/config";
import { queryKeys } from "./queryKeys";
import { useToast } from "./useToast";

export { queryKeys };

export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: api.health,
    refetchInterval: config.healthPollMs,
    retry: 1,
  });
}

export function useRuns() {
  return useQuery({
    queryKey: queryKeys.runs,
    queryFn: async () => (await api.listRuns()).runs,
    staleTime: 0,
  });
}

export function useRun(runId: string | null) {
  return useQuery({
    queryKey: queryKeys.run(runId ?? ""),
    queryFn: () => api.getRun(runId!),
    enabled: Boolean(runId),
  });
}

export function useEvents(log = "live", limit = 25, offset = 0) {
  return useQuery({
    queryKey: queryKeys.events(log, limit, offset),
    queryFn: () => api.listEvents(log, limit, offset),
  });
}

export function useLatestReport(enabled = true) {
  return useQuery({
    queryKey: queryKeys.report,
    queryFn: api.getLatestReport,
    enabled,
    retry: false,
  });
}

export function useLastLiveResult() {
  return useQuery<LiveResult | null>({
    queryKey: queryKeys.lastLive,
    queryFn: async () => null,
    initialData: null,
    staleTime: Infinity,
  });
}

export function useLastReplayResult() {
  return useQuery<{ verification_result: string } | null>({
    queryKey: queryKeys.lastReplay,
    queryFn: async () => null,
    initialData: null,
    staleTime: Infinity,
  });
}

export function useLastRecoverResult() {
  return useQuery<{ recovery_outcome: string } | null>({
    queryKey: queryKeys.lastRecover,
    queryFn: async () => null,
    initialData: null,
    staleTime: Infinity,
  });
}

export function useLastVerifyResult() {
  return useQuery<VerifyResult[] | null>({
    queryKey: queryKeys.lastVerify,
    queryFn: async () => null,
    initialData: null,
    staleTime: Infinity,
  });
}

function pickRecoveryOutcome(data: Record<string, unknown>): string | null {
  const value = data.recovery_outcome ?? data.recovery_status;
  return value != null ? String(value) : null;
}

export function useRuntimeMutations(onStart?: () => void, onComplete?: () => void) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.runs });
    queryClient.invalidateQueries({ queryKey: queryKeys.report });
    queryClient.invalidateQueries({ queryKey: ["events"] });
    queryClient.invalidateQueries({ queryKey: queryKeys.health });
  };

  return useMutation({
    mutationFn: async (mode: RunMode) => {
      onStart?.();
      if (mode === "live") return api.runLive();
      if (mode === "replay") return api.runReplay();
      if (mode === "recover") return api.runRecover();
      return api.runVerify();
    },
    onSuccess: (data, mode) => {
      try {
        if (mode === "live") {
          const live = data as LiveResult;
          queryClient.setQueryData(queryKeys.lastLive, live);
          const status = live.replay_status ?? "completed";
          showToast(
            `Live run — ${status}`,
            status.includes("VERIFIED") ? "success" : "error"
          );
        } else if (mode === "replay") {
          const status = String(
            (data as Record<string, unknown>).verification_result ?? "completed"
          );
          queryClient.setQueryData(queryKeys.lastReplay, { verification_result: status });
          showToast(`Replay — ${status}`, status.includes("VERIFIED") ? "success" : "error");
        } else if (mode === "recover") {
          const outcome =
            pickRecoveryOutcome(data as Record<string, unknown>) ?? "completed";
          queryClient.setQueryData(queryKeys.lastRecover, { recovery_outcome: outcome });
          showToast(`Recovery — ${outcome}`, "info");
        } else if (mode === "verify") {
          const results = (data as { results: VerifyResult[] }).results ?? [];
          queryClient.setQueryData(queryKeys.lastVerify, results);
          showToast(`Verify — ${results.length} checks`, "info");
        }
        invalidate();
      } finally {
        onComplete?.();
      }
    },
    onError: (error: Error) => {
      showToast(error.message, "error");
      onComplete?.();
    },
  });
}

export function useRefreshAll() {
  const queryClient = useQueryClient();
  return async () => {
    await bootstrapRuntimeState(queryClient);
    await queryClient.invalidateQueries({
      predicate: (query) =>
        !query.queryKey.includes("lastLive") &&
        !query.queryKey.includes("lastReplay") &&
        !query.queryKey.includes("lastRecover") &&
        !query.queryKey.includes("lastVerify"),
    });
  };
}

export function useRefreshRuns() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return async () => {
    try {
      await queryClient.invalidateQueries({ queryKey: queryKeys.runs });
      await queryClient.refetchQueries({ queryKey: queryKeys.runs });
      showToast("Run history updated", "success");
    } catch (error) {
      showToast(
        error instanceof Error ? error.message : "Failed to refresh runs",
        "error"
      );
    }
  };
}
