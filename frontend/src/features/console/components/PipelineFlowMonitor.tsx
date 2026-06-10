import { useMemo, useState } from "react";
import { PIPELINE_STAGES } from "../../../api/client";
import { useRuntime } from "../../../hooks/useRuntime";
import { useRuntimeLogs, useRuntimeStatus } from "../hooks/useConsoleQueries";
import Panel from "../ui/Panel";
import { cn } from "../../../lib/utils";

const STAGE_LABELS: Record<string, string> = {
  INPUT: "Input",
  VALIDATION: "Validation",
  SERIALIZATION: "Serialization",
  HASHING: "Hashing",
  PERSISTENCE: "Persistence",
  REPLAY: "Replay",
  VERIFICATION: "Verification",
  RECOVERY: "Recovery",
  OBSERVABILITY: "Observability",
};

type NodeState = "completed" | "running" | "failed" | "warning" | "idle";

export default function PipelineFlowMonitor() {
  const { stageLog, completedStages, currentIndex, progress, loadingMode } = useRuntime();
  const { data: status } = useRuntimeStatus();
  const { data: logsData } = useRuntimeLogs(200);
  const [selectedStage, setSelectedStage] = useState<string | null>(null);
  const running = loadingMode !== null;
  const recoveryRequired = (status?.recovery_status ?? "").includes("REQUIRED");

  function stageFailed(stage: string): boolean {
    return stageLog.some(
      (e) =>
        e.stage === stage &&
        (e.status.includes("FAILED") || e.status.includes("MISMATCH"))
    );
  }

  function nodeState(stage: string, index: number): NodeState {
    if (stageFailed(stage)) return "failed";
    if (stage === "RECOVERY" && recoveryRequired && !running) return "warning";
    if (running && currentIndex >= 0) {
      if (index < currentIndex) return "completed";
      if (index === currentIndex) return "running";
      return "idle";
    }
    if (completedStages.has(stage)) return "completed";
    if (status && status.total_events_processed > 0) {
      if (stage === "RECOVERY" && recoveryRequired) return "warning";
      if (status.runtime_status === "FAILED" && (stage === "REPLAY" || stage === "VERIFICATION")) {
        return "failed";
      }
      return "completed";
    }
    return "idle";
  }

  const nodeClass: Record<NodeState, string> = {
    completed: "pipeline-node pipeline-node--completed",
    running: "pipeline-node pipeline-node--running",
    failed: "pipeline-node pipeline-node--failed",
    warning: "pipeline-node pipeline-node--warning",
    idle: "pipeline-node pipeline-node--idle",
  };

  const displayProgress = running
    ? Math.max(progress, 12)
    : progress || (status?.total_events_processed ? 100 : 0);

  const stageLogs = useMemo(() => {
    const api = logsData?.logs ?? [];
    const ws = stageLog.map((e) => ({
      timestamp: new Date().toISOString(),
      stage: e.stage,
      status: e.status,
      message: `${e.stage} → ${e.status}`,
    }));
    const merged = api.length > 0 ? api : ws;
    if (!selectedStage) return merged.slice(-5).reverse();
    return merged.filter((l) => l.stage === selectedStage).slice(-8).reverse();
  }, [logsData?.logs, stageLog, selectedStage]);

  const activeStage = selectedStage ?? stageLog[stageLog.length - 1]?.stage ?? null;
  const activeState = activeStage
    ? nodeState(activeStage, PIPELINE_STAGES.indexOf(activeStage as (typeof PIPELINE_STAGES)[number]))
    : "idle";

  return (
    <Panel
      title="Pipeline Flow Monitor"
      subtitle="Click a stage to inspect runtime status and logs"
    >
      <div className="mb-5 flex items-center justify-between gap-4">
        <p className="text-xs text-slate-500">
          {running && loadingMode
            ? `${loadingMode.toUpperCase()} operation in flight`
            : status?.runtime_status === "OPERATIONAL"
              ? "All stages nominal"
              : status?.runtime_status === "FAILED"
                ? "Pipeline failure detected"
                : "Awaiting or recovering"}
        </p>
        <span className="font-mono text-xs text-neon-blue" aria-live="polite">
          {displayProgress}%
        </span>
      </div>

      <div
        className="relative mb-6 h-1 overflow-hidden rounded-full bg-elevated/80"
        role="progressbar"
        aria-valuenow={displayProgress}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Pipeline completion"
      >
        <div
          className="h-full rounded-full bg-gradient-to-r from-neon-blue/80 to-neon-green/80 transition-all duration-500"
          style={{ width: `${displayProgress}%` }}
        />
      </div>

      <div className="overflow-x-auto pb-2" tabIndex={0} aria-label="Pipeline stages">
        <div className="flex min-w-max items-center gap-1">
          {PIPELINE_STAGES.map((stage, i) => {
            const state = nodeState(stage, i);
            const selected = selectedStage === stage;
            return (
              <span key={stage} className="flex items-center">
                {i > 0 && <span className="pipeline-connector mx-1" aria-hidden="true" />}
                <button
                  type="button"
                  className={cn(
                    nodeClass[state],
                    selected && "ring-2 ring-neon-blue/50",
                    "cursor-pointer"
                  )}
                  aria-label={`${STAGE_LABELS[stage]}: ${state}`}
                  aria-pressed={selected}
                  onClick={() => setSelectedStage(stage)}
                >
                  <span className="font-mono text-[9px] font-bold uppercase tracking-wider">
                    {stage}
                  </span>
                  <span className="mt-0.5 text-[10px] text-slate-500">
                    {STAGE_LABELS[stage]}
                  </span>
                </button>
              </span>
            );
          })}
        </div>
      </div>

      <div className="mt-4 rounded-lg border border-line/60 bg-canvas/50 p-3 font-mono text-[11px]">
        <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">
          {activeStage ? `${activeStage} · ${activeState}` : "Stage details"}
        </p>
        {stageLogs.length === 0 ? (
          <p className="text-slate-500">No log entries for this stage yet</p>
        ) : (
          stageLogs.map((entry, i) => (
            <div key={`${entry.stage}-${entry.status}-${i}`} className="text-slate-400">
              <span className="text-slate-600">{entry.timestamp?.slice(11, 19) ?? "--:--:--"}</span>{" "}
              <span className="text-neon-blue">[{entry.stage}]</span>{" "}
              <span className="text-slate-300">{entry.status}</span>
            </div>
          ))
        )}
      </div>
    </Panel>
  );
}
