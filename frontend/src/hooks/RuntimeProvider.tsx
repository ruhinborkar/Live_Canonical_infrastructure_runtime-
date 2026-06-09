import { ReactNode, useCallback, useMemo } from "react";
import { RunMode } from "../api/client";
import { useBootstrap } from "./useBootstrap";
import {
  useHealth,
  useLastLiveResult,
  useLastRecoverResult,
  useLastReplayResult,
  useLastVerifyResult,
  useRefreshAll,
  useRuns,
  useRuntimeMutations,
} from "./queries";
import { usePipelineWebSocket } from "./usePipelineWebSocket";
import { RuntimeContext } from "./runtimeContext";

export function RuntimeProvider({ children }: { children: ReactNode }) {
  useBootstrap();
  const health = useHealth();
  const runs = useRuns();
  const pipeline = usePipelineWebSocket();
  const mutation = useRuntimeMutations(pipeline.resetPipeline, pipeline.completePipeline);
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

  const run = useCallback(
    (mode: RunMode) => {
      mutation.mutate(mode);
    },
    [mutation]
  );

  const value = useMemo(
    () => ({
      online: health.isSuccess,
      loading: mutation.isPending,
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
      run,
      refreshAll,
    }),
    [
      health.isSuccess,
      mutation.isPending,
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
      run,
      refreshAll,
    ]
  );

  return <RuntimeContext.Provider value={value}>{children}</RuntimeContext.Provider>;
}
