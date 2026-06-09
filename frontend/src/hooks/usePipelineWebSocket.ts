import { useCallback, useEffect, useRef, useState } from "react";
import { connectWebSocket, PIPELINE_STAGES, StageUpdate } from "../api/client";

export function usePipelineWebSocket() {
  const [stageLog, setStageLog] = useState<StageUpdate[]>([]);
  const [currentStage, setCurrentStage] = useState<string | null>(null);
  const [completedStages, setCompletedStages] = useState<Set<string>>(new Set());
  const [isRunning, setIsRunning] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  const handleMessage = useCallback((update: StageUpdate) => {
    setStageLog((prev) => [...prev.slice(-99), update]);
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
    setStageLog([]);
    setCurrentStage(null);
    setCompletedStages(new Set());
    setIsRunning(true);
  }, []);

  const completePipeline = useCallback(() => {
    setIsRunning(false);
    setCurrentStage("OBSERVABILITY");
    setCompletedStages(new Set(PIPELINE_STAGES));
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
    resetPipeline,
    completePipeline,
  };
}
