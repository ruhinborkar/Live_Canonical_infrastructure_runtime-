import { useCallback, useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, RunMode } from "../api/client";
import {
  INITIAL_OPERATION_META,
  OperationMeta,
  parseLiveResult,
  pickRecoveryOutcome,
  pickReplayStatus,
  pickVerifyResults,
} from "../lib/parseRunResponse";
import { queryKeys } from "./queryKeys";
import { useToast } from "./useToast";

type ModeCallbacks = {
  onStart?: (mode: RunMode) => void;
  onComplete?: (mode: RunMode, data?: Record<string, unknown>) => void;
  onError?: (mode: RunMode) => void;
};

function emptyMeta(): Record<RunMode, OperationMeta> {
  return {
    live: { ...INITIAL_OPERATION_META },
    replay: { ...INITIAL_OPERATION_META },
    recover: { ...INITIAL_OPERATION_META },
    verify: { ...INITIAL_OPERATION_META },
  };
}

export function useRuntimeActions(callbacks: ModeCallbacks = {}) {
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const callbacksRef = useRef(callbacks);
  callbacksRef.current = callbacks;

  const [operationMeta, setOperationMeta] = useState(emptyMeta);

  const setModeState = useCallback((mode: RunMode, patch: Partial<OperationMeta>) => {
    setOperationMeta((prev) => ({
      ...prev,
      [mode]: { ...prev[mode], ...patch },
    }));
  }, []);

  const invalidateQueries = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: queryKeys.runs });
    queryClient.invalidateQueries({ queryKey: queryKeys.report });
    queryClient.invalidateQueries({ queryKey: ["events"] });
    queryClient.invalidateQueries({ queryKey: queryKeys.eventsSummary });
    queryClient.invalidateQueries({ queryKey: ["console"] });
    queryClient.invalidateQueries({ queryKey: queryKeys.health });
  }, [queryClient]);

  const handleSuccess = useCallback(
    (mode: RunMode, data: Record<string, unknown>) => {
      if (mode === "live") {
        const live = parseLiveResult(data);
        queryClient.setQueryData(queryKeys.lastLive, live);
        showToast(
          `Live — ${live.replay_status}`,
          live.replay_status.includes("VERIFIED") ? "success" : "error"
        );
      } else if (mode === "replay") {
        const status = pickReplayStatus(data);
        queryClient.setQueryData(queryKeys.lastReplay, { verification_result: status });
        showToast(`Replay — ${status}`, status.includes("VERIFIED") ? "success" : "error");
      } else if (mode === "recover") {
        const outcome = pickRecoveryOutcome(data);
        queryClient.setQueryData(queryKeys.lastRecover, { recovery_outcome: outcome });
        showToast(`Recovery — ${outcome}`, "info");
      } else if (mode === "verify") {
        const results = pickVerifyResults(data);
        queryClient.setQueryData(queryKeys.lastVerify, results);
        const detected = results.filter((r) => r.failure_detected).length;
        showToast(`Verify — ${detected}/${results.length} detected`, "info");
      }

      setModeState(mode, {
        state: "success",
        error: null,
        completedAt: new Date().toISOString(),
      });
      invalidateQueries();
      callbacksRef.current.onComplete?.(mode, data);
    },
    [invalidateQueries, queryClient, setModeState, showToast]
  );

  const handleError = useCallback(
    (mode: RunMode, error: Error) => {
      setModeState(mode, { state: "error", error: error.message });
      showToast(`${mode}: ${error.message}`, "error");
      callbacksRef.current.onError?.(mode);
      callbacksRef.current.onComplete?.(mode);
    },
    [setModeState, showToast]
  );

  const liveMutation = useMutation({
    mutationFn: () => api.runLive().then((d) => d as unknown as Record<string, unknown>),
  });
  const replayMutation = useMutation({
    mutationFn: () =>
      api.runReplay().then((d) => d as unknown as Record<string, unknown>),
  });
  const recoverMutation = useMutation({
    mutationFn: () =>
      api.runRecover().then((d) => d as unknown as Record<string, unknown>),
  });
  const verifyMutation = useMutation({
    mutationFn: () => api.runVerify().then((d) => d as unknown as Record<string, unknown>),
  });

  const mutationsRef = useRef({
    live: liveMutation,
    replay: replayMutation,
    recover: recoverMutation,
    verify: verifyMutation,
  });
  mutationsRef.current = { live: liveMutation, replay: replayMutation, recover: recoverMutation, verify: verifyMutation };

  const execute = useCallback(
    async (mode: RunMode) => {
      if (
        liveMutation.isPending ||
        replayMutation.isPending ||
        recoverMutation.isPending ||
        verifyMutation.isPending
      ) {
        return;
      }

      setModeState(mode, { state: "running", error: null });
      callbacksRef.current.onStart?.(mode);

      try {
        const data = await mutationsRef.current[mode].mutateAsync();
        handleSuccess(mode, data as Record<string, unknown>);
      } catch (error) {
        handleError(mode, error instanceof Error ? error : new Error("Operation failed"));
      }
    },
    [
      handleError,
      handleSuccess,
      setModeState,
      liveMutation.isPending,
      replayMutation.isPending,
      recoverMutation.isPending,
      verifyMutation.isPending,
    ]
  );

  const loadingMode: RunMode | null = liveMutation.isPending
    ? "live"
    : replayMutation.isPending
      ? "replay"
      : recoverMutation.isPending
        ? "recover"
        : verifyMutation.isPending
          ? "verify"
          : null;

  return {
    execute,
    loadingMode,
    loading: loadingMode !== null,
    operationMeta,
  };
}
