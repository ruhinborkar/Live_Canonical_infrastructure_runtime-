import { useCallback, useEffect, useRef, useState } from "react";
import { connectWebSocket, PIPELINE_STAGES, RunMode, StageUpdate } from "../api/client";

const MODE_STAGE: Record<RunMode, (typeof PIPELINE_STAGES)[number]> = {
  live: "INPUT",
  replay: "REPLAY",
  recover: "RECOVERY",
  verify: "VERIFICATION",
};

export function usePipelineWebSocket() {
  const [stageLog, setStageLog] = useState<StageUpdate[]>([]);
  const [currentStage, setCurrentStage] = useState<string | null>(null);
  const [completedStages, setCompletedStages] = useState<Set<string>>(new Set());
  const [isRunning, setIsRunning] = useState(false);
  const [activeMode, setActiveMode] = useState<RunMode | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const handleMessage = useCallback((update: StageUpdate) => {
    setStageLog((prev) => {
      const last = prev[prev.length - 1];
      if (last?.stage === update.stage && last?.status === update.status) {
        return prev;
      }
      return [...prev.slice(-99), update];
    });
    setCurrentStage(update.stage);
    setCompletedStages((prev) => new Set(prev).add(update.stage));
  }, []);

  useEffect(() => {
    let cancelled = false;
    let reconnectTimer: ReturnType<typeof setTimeout>;

    function connect() {
      if (cancelled) return;
      const socket = connectWebSocket(handleMessage);
      socketRef.current = socket;

      socket.onclose = () => {
        if (!cancelled) {
          reconnectTimer = setTimeout(connect, 3000);
        }
      };

      socket.onerror = () => {
        socket.close();
      };
    }

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimer);
      socketRef.current?.close();
    };
  }, [handleMessage]);

  const resetPipeline = useCallback(() => {
    setActiveMode("live");
    setStageLog([]);
    setCurrentStage(null);
    setCompletedStages(new Set());
    setIsRunning(true);
  }, []);

  const completePipeline = useCallback(() => {
    setIsRunning(false);
    setActiveMode(null);
    setCurrentStage("OBSERVABILITY");
    setCompletedStages(new Set(PIPELINE_STAGES));
  }, []);

  const startMode = useCallback((mode: RunMode) => {
    const stage = MODE_STAGE[mode];
    setActiveMode(mode);
    setIsRunning(true);
    setCurrentStage(stage);
    setCompletedStages(new Set());
    setStageLog((prev) => {
      const entry = { type: "stage" as const, stage, status: "STARTED" };
      const last = prev[prev.length - 1];
      if (last?.stage === stage && last?.status === "STARTED") return prev;
      return [...prev.slice(-99), entry];
    });
  }, []);

  const completeMode = useCallback((mode: RunMode, status = "COMPLETED") => {
    const stage = MODE_STAGE[mode];
    setIsRunning(false);
    setActiveMode(null);
    setCurrentStage(stage);
    setCompletedStages(new Set([stage]));
    setStageLog((prev) => {
      const last = prev[prev.length - 1];
      if (last?.stage === stage && last?.status === status) return prev;
      return [...prev.slice(-99), { type: "stage", stage, status }];
    });
  }, []);

  const currentIndex = currentStage
    ? PIPELINE_STAGES.indexOf(currentStage as (typeof PIPELINE_STAGES)[number])
    : -1;

  const doneCount = isRunning
    ? PIPELINE_STAGES.filter((_, i) => (currentIndex >= 0 ? i <= currentIndex : false)).length
    : completedStages.size;

  const progress = Math.round((doneCount / PIPELINE_STAGES.length) * 100);

  return {
    stageLog,
    currentStage,
    completedStages,
    currentIndex,
    progress,
    isRunning,
    activeMode,
    resetPipeline,
    completePipeline,
    startMode,
    completeMode,
  };
}
