import VerifyResults from "../components/VerifyResults";
import { useRuntimeStatus } from "../features/console/hooks/useConsoleQueries";
import StatusPill from "../features/console/ui/StatusPill";
import { formatDateTime } from "../lib/utils";

export default function VerifyPage() {
  const { data: status, isLoading } = useRuntimeStatus();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold">Verification</h1>
        <p className="text-sm text-slate-400">Replay, truth reconstruction, and failure-path validation</p>
      </div>

      <div className="panel">
        <h2 className="mb-4 font-semibold">Runtime Verification State</h2>
        {isLoading ? (
          <p className="text-sm text-slate-500">Loading verification status…</p>
        ) : !status || status.total_events_processed === 0 ? (
          <p className="text-sm text-slate-500">Run Live to populate verification results</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-line/80 bg-elevated/40 p-4">
              <p className="text-[10px] uppercase tracking-widest text-slate-500">Replay</p>
              <div className="mt-2">
                <StatusPill value={status.replay_verification_status} />
              </div>
              <p className="mt-2 font-mono text-sm text-slate-300">{status.events_replayed} events</p>
            </div>
            <div className="rounded-lg border border-line/80 bg-elevated/40 p-4">
              <p className="text-[10px] uppercase tracking-widest text-slate-500">Truth</p>
              <div className="mt-2">
                <StatusPill value={status.truth_verification_status} />
              </div>
              <p className="mt-2 font-mono text-sm text-slate-300">
                {status.events_reconstructed} reconstructed
              </p>
            </div>
            <div className="rounded-lg border border-line/80 bg-elevated/40 p-4">
              <p className="text-[10px] uppercase tracking-widest text-slate-500">Recovery</p>
              <div className="mt-2">
                <StatusPill value={status.recovery_status} />
              </div>
              <p className="mt-2 font-mono text-sm text-slate-300">
                {status.recovery_points} recovery points
              </p>
            </div>
          </div>
        )}
        {status?.last_updated && (
          <p className="mt-4 text-xs text-slate-500">
            Last updated {formatDateTime(status.last_updated)}
          </p>
        )}
      </div>

      <VerifyResults />
    </div>
  );
}
