import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { formatDateTime } from "../../../lib/utils";
import { TableSkeleton } from "../../../components/ui/Skeleton";
import SortableTh from "../../../components/ui/SortableTh";
import { nextSortDirection, sortRows, SortDirection } from "../../../lib/tableSort";
import { useRuntimeRuns } from "../hooks/useConsoleQueries";
import { RuntimeRunRow } from "../api/types";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";

type SortKey = keyof Pick<
  RuntimeRunRow,
  "short_id" | "status" | "events_processed" | "duration_ms" | "timestamp"
>;

function formatDuration(ms: number | null): string {
  if (ms == null) return "—";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export default function RecentRunsTable({ limit = 12 }: { limit?: number }) {
  const { data, isLoading, isError, refetch, isFetching } = useRuntimeRuns(limit);
  const [sortKey, setSortKey] = useState<SortKey>("timestamp");
  const [sortDir, setSortDir] = useState<SortDirection>("desc");

  const runs = useMemo(() => {
    const rows = data?.runs ?? [];
    return sortRows(rows, sortKey, sortDir);
  }, [data?.runs, sortKey, sortDir]);

  function handleSort(column: string) {
    const key = column as SortKey;
    setSortDir((dir) => nextSortDirection(sortKey, key, dir));
    setSortKey(key);
  }

  return (
    <Panel
      title="Recent Runs"
      subtitle="Execution history · /api/runtime/runs"
      action={
        <div className="flex gap-2">
          <button
            type="button"
            className="btn-secondary btn-sm"
            disabled={isFetching}
            onClick={() => void refetch()}
          >
            {isFetching ? "Refreshing…" : "Refresh"}
          </button>
          <Link to="/runs" className="btn-ghost btn-sm">
            View all →
          </Link>
        </div>
      }
      noPadding
    >
      {isError ? (
        <div className="p-5">
          <ErrorState message="Failed to load run history" onRetry={() => void refetch()} />
        </div>
      ) : isLoading ? (
        <div className="p-5">
          <TableSkeleton rows={6} />
        </div>
      ) : !data?.runs.length ? (
        <div className="p-5">
          <EmptyState
            title="No runs recorded"
            message="Execute Run Live to create the first run entry"
          />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="ops-table w-full" aria-label="Recent runtime runs">
            <thead>
              <tr className="border-b border-line">
                <SortableTh label="Run ID" column="short_id" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                <SortableTh label="Status" column="status" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                <SortableTh label="Events" column="events_processed" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                <th>Replay</th>
                <th>Truth</th>
                <th>Recovery</th>
                <SortableTh label="Duration" column="duration_ms" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                <SortableTh label="Timestamp" column="timestamp" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.run_id}>
                  <td className="text-neon-blue">{run.short_id}</td>
                  <td>
                    <StatusPill value={run.status} />
                  </td>
                  <td>{run.events_processed ?? "—"}</td>
                  <td>
                    <StatusPill value={run.replay_result} />
                  </td>
                  <td>
                    <StatusPill value={run.truth_result} />
                  </td>
                  <td>
                    <StatusPill value={run.recovery_result} />
                  </td>
                  <td className="text-slate-400">{formatDuration(run.duration_ms)}</td>
                  <td className="text-slate-500">
                    {run.timestamp ? formatDateTime(run.timestamp) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Panel>
  );
}
