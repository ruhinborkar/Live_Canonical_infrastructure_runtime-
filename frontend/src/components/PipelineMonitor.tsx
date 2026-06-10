import { PIPELINE_STAGES } from "../api/client";
import { useRuntime } from "../hooks/useRuntime";
import { cn } from "../lib/utils";

const MODE_LABELS = {
  live: "Live pipeline",
  replay: "Replay",
  recover: "Recovery",
  verify: "Verification",
} as const;

export default function PipelineMonitor() {
  const { stageLog, completedStages, currentIndex, progress, loadingMode } = useRuntime();
  const running = loadingMode !== null;

  function stepClass(stage: string, index: number): string {
    if (running && currentIndex >= 0) {
      if (index < currentIndex) return "border-emerald-500/50 bg-emerald-500/10 text-emerald-400";
      if (index === currentIndex) return "border-blue-500 bg-blue-500/15 text-blue-400 shadow-glow";
      return "border-line text-slate-600 opacity-50";
    }
    if (completedStages.has(stage)) {
      return "border-emerald-500/50 bg-emerald-500/10 text-emerald-400";
    }
    return "border-line text-slate-500";
  }

  return (
    <div className="panel">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold">Pipeline Monitor</h2>
        <span className="font-mono text-xs text-slate-500">
          {running && loadingMode
            ? `${MODE_LABELS[loadingMode]}…`
            : `${progress}%`}
        </span>
      </div>

      <div className="mb-4 h-1.5 overflow-hidden rounded-full bg-elevated">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-600 to-emerald-500 transition-all duration-300"
          style={{
            width: `${running ? Math.max(progress, 15) : progress || (completedStages.size ? 100 : 0)}%`,
          }}
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {PIPELINE_STAGES.map((stage, i) => (
          <span key={stage} className="contents">
            {i > 0 && <span className="text-slate-600">→</span>}
            <span
              className={cn(
                "rounded-md border px-2 py-1 font-mono text-[10px] font-medium transition-all",
                stepClass(stage, i)
              )}
            >
              {stage}
            </span>
          </span>
        ))}
      </div>

      <div className="mt-4 max-h-48 overflow-y-auto font-mono text-xs">
        {stageLog.length === 0 ? (
          <p className="text-slate-500">
            {running
              ? "Operation in progress…"
              : "Click Run Live, Replay, Recover, or Verify"}
          </p>
        ) : (
          [...stageLog].reverse().map((entry, i) => (
            <div
              key={`${entry.stage}-${entry.status}-${stageLog.length - 1 - i}`}
              className="border-b border-line/50 py-1.5"
            >
              <span className="text-blue-400">{entry.stage}</span>
              <span className="text-slate-600"> → </span>
              <span className="text-slate-400">{entry.status}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
