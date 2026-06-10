import { useEffect, useMemo, useRef } from "react";
import { useRuntime } from "../../../hooks/useRuntime";
import { useRuntimeLogs } from "../hooks/useConsoleQueries";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import Panel from "../ui/Panel";
import { cn } from "../../../lib/utils";

function lineTone(status: string): string {
  if (status.includes("FAILED") || status.includes("MISMATCH")) return "text-red-400";
  if (status.includes("REQUIRED")) return "text-neon-amber";
  if (status.includes("VERIFIED") || status.includes("COMPLETED")) return "text-neon-green/90";
  return "text-slate-300";
}

export default function RuntimeLogConsole() {
  const { stageLog } = useRuntime();
  const { data, isLoading, isError, refetch } = useRuntimeLogs(100);
  const scrollRef = useRef<HTMLDivElement>(null);

  const merged = useMemo(() => {
    const apiLogs = (data?.logs ?? []).map((l) => ({
      ...l,
      message: l.message || `${l.stage} → ${l.status}`,
    }));

    const liveWs = stageLog.map((e) => ({
      timestamp: new Date().toISOString(),
      stage: e.stage,
      status: e.status,
      message: `${e.stage} → ${e.status}`,
      level: e.status.includes("FAILED") || e.status.includes("MISMATCH") ? "ERROR" : "INFO",
    }));

    const source = apiLogs.length > 0 ? apiLogs : liveWs;

    return [...source]
      .sort((a, b) => a.timestamp.localeCompare(b.timestamp))
      .slice(-120);
  }, [data?.logs, stageLog]);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [merged.length, merged[merged.length - 1]?.timestamp]);

  return (
    <Panel
      title="Runtime Log Console"
      subtitle="Live execution stream · /api/runtime/logs"
      action={
        <button
          type="button"
          className="btn-secondary btn-sm"
          onClick={() => void refetch()}
          aria-label="Refresh log console"
        >
          Refresh
        </button>
      }
      noPadding
    >
      {isError ? (
        <div className="p-4">
          <ErrorState message="Failed to load runtime logs" onRetry={() => void refetch()} />
        </div>
      ) : isLoading && merged.length === 0 ? (
        <div className="console-terminal p-4 font-mono text-xs text-slate-500" aria-busy="true">
          Initializing log stream…
        </div>
      ) : merged.length === 0 ? (
        <div className="p-4">
          <EmptyState
            title="Log console empty"
            message="Pipeline stage events will appear here during execution"
          />
        </div>
      ) : (
        <div
          ref={scrollRef}
          className="console-terminal max-h-80 overflow-y-auto p-4 font-mono text-xs leading-relaxed"
          role="log"
          aria-live="polite"
          aria-label="Runtime execution logs"
          tabIndex={0}
        >
          <div className="mb-3 flex items-center gap-2 border-b border-line/40 pb-2 text-[10px] uppercase tracking-widest text-slate-600">
            <span className="h-2 w-2 rounded-full bg-neon-green shadow-glow-success" />
            runtime.log · {merged.length} entries
          </div>
          <table className="w-full border-collapse">
            <thead>
              <tr className="text-left text-[10px] uppercase tracking-wider text-slate-600">
                <th className="pb-2 pr-3 font-semibold">Time</th>
                <th className="pb-2 pr-3 font-semibold">Stage</th>
                <th className="pb-2 pr-3 font-semibold">Status</th>
                <th className="pb-2 font-semibold">Message</th>
              </tr>
            </thead>
            <tbody>
              {merged.map((line, i) => (
                <tr
                  key={`${line.timestamp}-${line.stage}-${i}`}
                  className="console-line border-b border-line/20"
                >
                  <td className="py-1 pr-3 text-slate-600">
                    {line.timestamp?.slice(11, 19) ?? "--:--:--"}
                  </td>
                  <td className={cn("py-1 pr-3 font-semibold", lineTone(line.status))}>
                    {line.stage}
                  </td>
                  <td className={cn("py-1 pr-3", lineTone(line.status))}>{line.status}</td>
                  <td className={cn("py-1 text-slate-400")}>{line.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Panel>
  );
}
