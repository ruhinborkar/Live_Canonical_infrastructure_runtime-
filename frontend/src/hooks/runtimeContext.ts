import { createContext, useContext } from "react";
import { LiveResult, RunMode, VerifyResult } from "../api/client";
import { VerifyPayload } from "../lib/normalize";
import { OperationMeta } from "../lib/parseRunResponse";
import { usePipelineWebSocket } from "./usePipelineWebSocket";
import { useRuns } from "./queries";

export interface RuntimeContextValue {
  online: boolean;
  loading: boolean;
  loadingMode: RunMode | null;
  operationMeta: Record<RunMode, OperationMeta>;
  hasLiveData: boolean;
  liveResult: LiveResult | null;
  replayStatus: string | null;
  recoveryStatus: string | null;
  lastVerifyResults: VerifyResult[];
  lastVerifyPayload: VerifyPayload | null;
  stageLog: ReturnType<typeof usePipelineWebSocket>["stageLog"];
  currentStage: ReturnType<typeof usePipelineWebSocket>["currentStage"];
  completedStages: ReturnType<typeof usePipelineWebSocket>["completedStages"];
  currentIndex: number;
  progress: number;
  runs: NonNullable<ReturnType<typeof useRuns>["data"]>;
  runsLoading: boolean;
  execute: (mode: RunMode) => Promise<void>;
  refreshAll: () => Promise<void>;
}

export const RuntimeContext = createContext<RuntimeContextValue | null>(null);

export function useRuntime() {
  const ctx = useContext(RuntimeContext);
  if (!ctx) throw new Error("useRuntime must be used within RuntimeProvider");
  return ctx;
}
