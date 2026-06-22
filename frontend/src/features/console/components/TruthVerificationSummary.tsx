import { Link } from "react-router-dom";
import { formatDateTime } from "../../../lib/utils";
import { useRuntimeStatus } from "../hooks/useConsoleQueries";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";

export default function TruthVerificationSummary() {
  const { data, isLoading, isError, refetch } = useRuntimeStatus();

  if (isError) {
    return (
      <Panel title="Truth Verification" subtitle="Latest verify run · /api/runtime/status">
        <ErrorState message="Failed to load truth verification summary" onRetry={() => void refetch()} />
      </Panel>
    );
  }

  if (isLoading) {
    return (
      <Panel title="Truth Verification" subtitle="Latest verify run · /api/runtime/status">
        <div className="h-24 animate-pulse rounded-lg bg-elevated/40" aria-hidden="true" />
      </Panel>
    );
  }

  const hasVerifyData =
    Boolean(data?.validation_state_diff) ||
    Boolean(data?.recovery_state_diff) ||
    Boolean(data?.truth_checks && Object.keys(data.truth_checks).length > 0);

  if (!data || !hasVerifyData) {
    return (
      <Panel title="Truth Verification" subtitle="Latest verify run · /api/runtime/status">
        <EmptyState
          title="No verify snapshot"
          message="Run Verify to populate validation and recovery state diffs on the dashboard"
        />
        <div className="mt-4 text-center">
          <Link to="/verify" className="btn-primary btn-sm">
            Open Verify →
          </Link>
        </div>
      </Panel>
    );
  }

  const validation = data.validation_state_diff;
  const recovery = data.recovery_state_diff;
  const checks = data.truth_checks ?? {};

  return (
    <Panel
      title="Truth Verification"
      subtitle={
        data.truth_source === "verify_run"
          ? "Truth status from latest verify run"
          : "Diff fields from latest verify run · truth status from live report"
      }
      action={
        <Link to="/verify" className="btn-ghost btn-sm">
          Full details →
        </Link>
      }
    >
      <div className="flex flex-wrap items-center gap-3">
        <StatusPill value={data.truth_verification_status} />
        {data.last_verify_at && (
          <span className="font-mono text-xs text-slate-500">
            verify {formatDateTime(data.last_verify_at)}
          </span>
        )}
      </div>

      {Object.keys(checks).length > 0 && (
        <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(checks).map(([check, passed]) => (
            <div
              key={check}
              className="flex items-center justify-between rounded-lg border border-line/60 bg-elevated/30 px-3 py-2 text-xs"
            >
              <span className="font-mono text-slate-400">{check}</span>
              <span className={passed ? "text-emerald-400" : "text-red-400"}>
                {passed ? "PASS" : "FAIL"}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {validation && (
          <div className="rounded-lg border border-line/60 bg-elevated/20 p-3 text-xs">
            <p className="font-semibold text-slate-300">Validation state diff</p>
            <p className="mt-1 font-mono text-slate-400">
              stored {validation.stored_valid} valid / {validation.stored_invalid} invalid
            </p>
            <p className="font-mono text-slate-400">
              recomputed {validation.recomputed_valid} valid / {validation.recomputed_invalid}{" "}
              invalid
            </p>
            <p className="mt-1 text-slate-500">
              match: {validation.match ? "yes" : "no"} · mismatches: {validation.mismatch_count}
            </p>
          </div>
        )}
        {recovery && (
          <div className="rounded-lg border border-line/60 bg-elevated/20 p-3 text-xs">
            <p className="font-semibold text-slate-300">Recovery state diff</p>
            <p className="mt-1 font-mono text-slate-400">
              resume_point={String(recovery.derived?.resume_point ?? "—")} · interrupted=
              {String(recovery.derived?.interrupted_events ?? "—")}
            </p>
            <p className="mt-1 text-slate-500">
              independent match: {recovery.match ? "yes" : "no"}
            </p>
          </div>
        )}
      </div>

      {data.original_truth_hash && (
        <p className="mt-3 break-all font-mono text-[10px] text-slate-500">
          truth_hash: {data.original_truth_hash.slice(0, 24)}…
        </p>
      )}
    </Panel>
  );
}
