import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, LiveResult } from "../api/client";
import { bootstrapRuntimeState } from "../lib/bootstrapState";
import { normalizeRuns, VerifyPayload } from "../lib/normalize";
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
    queryFn: async () => normalizeRuns(await api.listRuns()),
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

export function useEvents(
  log = "live",
  limit = 25,
  offset = 0,
  status?: "VALID" | "INVALID",
  search?: string,
  eventType?: string
) {
  return useQuery({
    queryKey: queryKeys.events(log, limit, offset, status, search, eventType),
    queryFn: () =>
      api.listEvents({ log, limit, offset, status, search, event_type: eventType }),
    staleTime: 0,
  });
}

export function useEventsSummary() {
  return useQuery({
    queryKey: queryKeys.eventsSummary,
    queryFn: api.getEventsSummary,
    staleTime: 0,
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
  return useQuery<VerifyPayload | null>({
    queryKey: queryKeys.lastVerify,
    queryFn: async () => null,
    initialData: null,
    staleTime: Infinity,
  });
}

export function useRefreshAll() {
  const queryClient = useQueryClient();
  return async () => {
    await bootstrapRuntimeState(queryClient);
    await queryClient.invalidateQueries({ queryKey: queryKeys.eventsSummary });
    await queryClient.invalidateQueries({ queryKey: ["console"] });
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
