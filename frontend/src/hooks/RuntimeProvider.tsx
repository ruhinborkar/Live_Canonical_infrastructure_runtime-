import { ReactNode, useCallback, useMemo } from "react";
import { RunMode } from "../api/client";
import { useBootstrap } from "./useBootstrap";
import {
  useEventsSummary,
  useHealth,
  useLastLiveResult,
  useLastRecoverResult,
  useLastReplayResult,
  useLastVerifyResult,
  useRefreshAll,
  useRuns,
} from "./queries";
import { usePipelineWebSocket } from "./usePipelineWebSocket";
import { useRuntimeActions } from "./useRuntimeActions";
import { RuntimeContext } from "./runtimeContext";

export function RuntimeProvider({ children }: { children: ReactNode }) {
  useBootstrap();
  const health = useHealth();
  const runs = useRuns();
  const eventsSummary = useEventsSummary();
  const pipeline = usePipelineWebSocket();

  const { execute, loading, loadingMode, operationMeta } = useRuntimeActions({
    onStart: (mode) => {
      if (mode === "live") pipeline.resetPipeline();
      else pipeline.startMode(mode);
    },
    onComplete: (mode, data) => {
      if (mode === "live") {
        pipeline.completePipeline();
        return;
      }
      const record = data ?? {};
      if (mode === "replay") {
        pipeline.completeMode("replay", String(record.verification_result ?? "COMPLETED"));
      } else if (mode === "recover") {
        pipeline.completeMode(
          "recover",
          String(record.recovery_outcome ?? record.recovery_status ?? "COMPLETED")
        );
      } else if (mode === "verify") {
        pipeline.completeMode("verify", "CHECKS_COMPLETED");
      }
    },
    onError: (mode) => {
      if (mode === "live") pipeline.completePipeline();
      else pipeline.completeMode(mode, "FAILED");
    },
  });

  const lastLive = useLastLiveResult();
  const lastReplay = useLastReplayResult();
  const lastRecover = useLastRecoverResult();
  const lastVerify = useLastVerifyResult();
  const refreshAll = useRefreshAll();

  const liveResult = lastLive.data ?? null;
  const replayStatus =
    lastReplay.data?.verification_result ?? liveResult?.replay_status ?? null;
  const recoveryStatus =
    lastRecover.data?.recovery_outcome ?? liveResult?.recovery_status ?? null;

  const hasLiveData = Boolean(
    (liveResult?.runtime_execution?.processed_events ?? 0) > 0 ||
      (eventsSummary.data?.logs?.live?.total ?? 0) > 0 ||
      (runs.data ?? []).some((run) => run.mode === "live" && run.status === "completed")
  );

  const online = health.data?.status === "ok";

  const stableExecute = useCallback((mode: RunMode) => execute(mode), [execute]);

  const value = useMemo(
    () => ({
      online,
      loading,
      loadingMode,
      operationMeta,
      hasLiveData,
      liveResult,
      replayStatus,
      recoveryStatus,
      lastVerifyResults: lastVerify.data ?? null,
      stageLog: pipeline.stageLog,
      currentStage: pipeline.currentStage,
      completedStages: pipeline.completedStages,
      currentIndex: pipeline.currentIndex,
      progress: pipeline.progress,
      runs: runs.data ?? [],
      runsLoading: runs.isLoading,
      execute: stableExecute,
      refreshAll,
    }),
    [
      online,
      loading,
      loadingMode,
      operationMeta,
      hasLiveData,
      liveResult,
      replayStatus,
      recoveryStatus,
      lastVerify.data,
      pipeline.stageLog,
      pipeline.currentStage,
      pipeline.completedStages,
      pipeline.currentIndex,
      pipeline.progress,
      runs.data,
      runs.isLoading,
      stableExecute,
      refreshAll,
    ]
  );

  return <RuntimeContext.Provider value={value}>{children}</RuntimeContext.Provider>;
}
