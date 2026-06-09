import { Link } from "react-router-dom";
import { useState } from "react";
import { useRun, useRuns, useRefreshRuns } from "../hooks/queries";
import { badgeClass, downloadJson, formatDateTime, statusTone } from "../lib/utils";
import { cn } from "../lib/utils";
import { TableSkeleton } from "./ui/Skeleton";

interface RunHistoryProps {
  compact?: boolean;
}

export default function RunHistory({ compact = false }: RunHistoryProps) {
  const { data: runs = [], isLoading, isFetching } = useRuns();
  const refreshRuns = useRefreshRuns();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const { data: selected } = useRun(compact ? null : selectedId);

  const displayRuns = compact ? runs.slice(0, 8) : runs;
  const busy = isLoading || isFetching;

  return (
    <div className={cn(!compact && "grid gap-6 lg:grid-cols-2")}>
      <div className="panel">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-semibold">Run History</h2>
          <div className="flex gap-2">
            {compact && (
              <Link to="/runs" className="btn-ghost btn-sm">
                View all →
              </Link>
            )}
            <button
              type="button"
              className="btn-secondary btn-sm"
              disabled={busy}
              onClick={() => refreshRuns()}
            >
              {busy ? "Refreshing…" : "Refresh"}
            </button>
          </div>
        </div>
        {isLoading ? (
          <TableSkeleton rows={5} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-left text-xs uppercase text-slate-500">
                  <th className="pb-2 pr-3">Mode</th>
                  <th className="pb-2 pr-3">Status</th>
                  <th className="pb-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {displayRuns.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="py-6 text-center text-slate-500">
                      No runs yet — click Run Live
                    </td>
                  </tr>
                ) : (
                  displayRuns.map((run) => (
                    <tr
                      key={run.id}
                      className={cn(
                        "border-b border-line/50 font-mono text-xs",
                        !compact && "cursor-pointer hover:bg-blue-500/5",
                        selectedId === run.id && "bg-blue-500/10"
                      )}
                      onClick={() => !compact && setSelectedId(run.id)}
                    >
                      <td className="py-2 pr-3 uppercase text-blue-400">{run.mode}</td>
                      <td className="py-2 pr-3">
                        <span className={badgeClass(statusTone(run.status))}>{run.status}</span>
                      </td>
                      <td className="py-2">{formatDateTime(run.created_at)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {!compact && selected && (
        <div className="panel">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold">Run Detail</h2>
            <button
              type="button"
              className="btn-secondary btn-sm"
              onClick={() => downloadJson(`run-${selected.id}.json`, selected)}
            >
              Download
            </button>
          </div>
          <dl className="mb-4 grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-xs text-slate-500">Mode</dt>
              <dd className="font-mono">{selected.mode}</dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500">Status</dt>
              <dd>
                <span className={badgeClass(statusTone(selected.status))}>
                  {selected.status}
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500">Started</dt>
              <dd>{formatDateTime(selected.created_at)}</dd>
            </div>
            {selected.completed_at && (
              <div>
                <dt className="text-xs text-slate-500">Completed</dt>
                <dd>{formatDateTime(selected.completed_at)}</dd>
              </div>
            )}
          </dl>
          {selected.result && (
            <pre className="max-h-96 overflow-auto rounded-lg bg-black/30 p-3 font-mono text-xs text-slate-400">
              {JSON.stringify(selected.result, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
