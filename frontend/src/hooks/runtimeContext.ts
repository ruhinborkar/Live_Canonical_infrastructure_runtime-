import { createContext, useContext } from "react";
import { LiveResult, RunMode, VerifyResult } from "../api/client";
import { usePipelineWebSocket } from "./usePipelineWebSocket";
import { useRuns } from "./queries";

export interface RuntimeContextValue {
  online: boolean;
  loading: boolean;
  liveResult: LiveResult | null;
  replayStatus: string | null;
  recoveryStatus: string | null;
  lastVerifyResults: VerifyResult[] | null;
  stageLog: ReturnType<typeof usePipelineWebSocket>["stageLog"];
  currentStage: ReturnType<typeof usePipelineWebSocket>["currentStage"];
  completedStages: ReturnType<typeof usePipelineWebSocket>["completedStages"];
  currentIndex: number;
  progress: number;
  runs: NonNullable<ReturnType<typeof useRuns>["data"]>;
  runsLoading: boolean;
  run: (mode: RunMode) => void;
  refreshAll: () => Promise<void>;
}

export const RuntimeContext = createContext<RuntimeContextValue | null>(null);

export function useRuntime() {
  const ctx = useContext(RuntimeContext);
  if (!ctx) throw new Error("useRuntime must be used within RuntimeProvider");
  return ctx;
}
