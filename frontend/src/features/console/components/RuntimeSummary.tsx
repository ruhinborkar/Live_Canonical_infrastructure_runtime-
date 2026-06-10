import { formatDateTime } from "../../../lib/utils";
import { useRuntimeStatus } from "../hooks/useConsoleQueries";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import MetricTile from "../ui/MetricTile";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";
export default function RuntimeSummary() {
  const { data, isLoading, isError, refetch } = useRuntimeStatus();

  return (
    <Panel
      title="Runtime Summary"
      subtitle="Live operational status from /api/runtime/status"
    >
      {isError ? (
        <ErrorState message="Failed to load runtime status" onRetry={() => void refetch()} />
      ) : isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-lg bg-elevated" />
          ))}
        </div>
      ) : !data ? (
        <EmptyState title="No status data" message="Run Live to populate runtime summary" />
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <MetricTile label="Total Events Processed" value={data.total_events_processed} />
            <MetricTile
              label="Valid Events"
              value={data.valid_events}
              tone="success"
            />
            <MetricTile
              label="Invalid Events"
              value={data.invalid_events}
              tone={data.invalid_events > 0 ? "warning" : "default"}
            />
            <MetricTile
              label="Last Execution"
              value={
                data.last_execution_timestamp
                  ? formatDateTime(data.last_execution_timestamp)
                  : "—"
              }
              sub={data.last_run_id ? `Run ${data.last_run_id.slice(0, 8)}` : undefined}
            />
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg border border-line/80 bg-elevated/30 px-4 py-3">
              <p className="text-[10px] uppercase tracking-widest text-slate-500">
                Replay Verification
              </p>
              <div className="mt-2">
                <StatusPill value={data.replay_verification_status} />
              </div>
            </div>
            <div className="rounded-lg border border-line/80 bg-elevated/30 px-4 py-3">
              <p className="text-[10px] uppercase tracking-widest text-slate-500">
                Truth Verification
              </p>
              <div className="mt-2">
                <StatusPill value={data.truth_verification_status} />
              </div>
            </div>
            <div className="rounded-lg border border-line/80 bg-elevated/30 px-4 py-3">
              <p className="text-[10px] uppercase tracking-widest text-slate-500">
                Recovery Status
              </p>
              <div className="mt-2">
                <StatusPill value={data.recovery_status} />
              </div>
            </div>
          </div>
        </>
      )}
    </Panel>
  );
}
