import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import {
  api,
  connectWebSocket,
  LiveResult,
  RunMode,
  RunRecord,
  StageUpdate,
  VerifyResult,
} from "../api/client";
import { useToast } from "./useToast";

interface RuntimeContextValue {
  online: boolean;
  loading: boolean;
  liveResult: LiveResult | null;
  runs: RunRecord[];
  stageLog: StageUpdate[];
  currentStage: string | null;
  completedStages: Set<string>;
  lastVerifyResults: VerifyResult[] | null;
  refresh: () => Promise<void>;
  run: (mode: RunMode) => Promise<void>;
  resetPipeline: () => void;
}

const RuntimeContext = createContext<RuntimeContextValue | null>(null);

export function RuntimeProvider({ children }: { children: ReactNode }) {
  const { showToast } = useToast();
  const [online, setOnline] = useState(false);
  const [loading, setLoading] = useState(false);
  const [liveResult, setLiveResult] = useState<LiveResult | null>(null);
  const [runs, setRuns] = useState<RunRecord[]>([]);
  const [stageLog, setStageLog] = useState<StageUpdate[]>([]);
  const [currentStage, setCurrentStage] = useState<string | null>(null);
  const [completedStages, setCompletedStages] = useState<Set<string>>(new Set());
  const [lastVerifyResults, setLastVerifyResults] = useState<VerifyResult[] | null>(null);

  const refresh = useCallback(async () => {
    try {
      await api.health();
      setOnline(true);
      const runsData = await api.listRuns();
      setRuns(runsData.runs);
    } catch {
      setOnline(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const socket = connectWebSocket((update) => {
      setStageLog((prev) => [...prev.slice(-99), update]);
      setCurrentStage(update.stage);
      setCompletedStages((prev) => new Set(prev).add(update.stage));
    });
    return () => socket.close();
  }, [refresh]);

  const resetPipeline = useCallback(() => {
    setStageLog([]);
    setCurrentStage(null);
    setCompletedStages(new Set());
  }, []);

  const run = useCallback(
    async (mode: RunMode) => {
      setLoading(true);
      resetPipeline();

      try {
        if (mode === "live") {
          const result = await api.runLive();
          setLiveResult(result);
          showToast(
            `Live run complete — ${result.replay_status}`,
            result.replay_status.includes("VERIFIED") ? "success" : "error"
          );
        } else if (mode === "replay") {
          const result = await api.runReplay();
          const status = String(result.verification_result ?? "done");
          showToast(`Replay: ${status}`, status.includes("VERIFIED") ? "success" : "error");
        } else if (mode === "recover") {
          const result = await api.runRecover();
          const outcome = String(result.recovery_outcome ?? "done");
          showToast(`Recovery: ${outcome}`, "info");
        } else {
          const result = await api.runVerify();
          setLastVerifyResults(result.results);
          showToast(`Verify complete — ${result.results.length} checks`, "info");
        }
        await refresh();
      } catch (err) {
        showToast(err instanceof Error ? err.message : "Run failed", "error");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [refresh, resetPipeline, showToast]
  );

  return (
    <RuntimeContext.Provider
      value={{
        online,
        loading,
        liveResult,
        runs,
        stageLog,
        currentStage,
        completedStages,
        lastVerifyResults,
        refresh,
        run,
        resetPipeline,
      }}
    >
      {children}
    </RuntimeContext.Provider>
  );
}

export function useRuntime() {
  const ctx = useContext(RuntimeContext);
  if (!ctx) throw new Error("useRuntime must be used within RuntimeProvider");
  return ctx;
}
