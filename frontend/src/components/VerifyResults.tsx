import { VerifyResult } from "../api/client";
import { useRuntime } from "../hooks/useRuntime";
import { safeArray } from "../lib/normalize";
import { formatDateTime } from "../lib/utils";
import StatusPill from "../features/console/ui/StatusPill";
import OperationBar from "./OperationBar";

export default function VerifyResults() {
  const { lastVerifyResults, lastVerifyPayload, loadingMode, operationMeta, online } =
    useRuntime();
  const verifying = loadingMode === "verify";
  const meta = operationMeta.verify;

  const results = safeArray<VerifyResult>(lastVerifyResults);
  const detected = results.filter((r) => r.failure_detected).length;
  const total = results.length;
  const hasPayload = Boolean(lastVerifyPayload);
  const truthChecks = lastVerifyPayload?.truth_checks ?? {};

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold">Failure-Path Verification</h1>
          <p className="text-sm text-slate-400">
            Hostile validation: duplicates, sequence corruption, trace mutation, schema errors
          </p>
        </div>
        {meta.completedAt && (
          <p className="font-mono text-xs text-slate-500">
            Last run: {formatDateTime(meta.completedAt)}
          </p>
        )}
      </div>

      <OperationBar modes={["verify"]} />

      {verifying && (
        <div className="panel flex items-center justify-center gap-3 py-8 text-sm text-slate-400">
          <span className="h-5 w-5 animate-spin rounded-full border-2 border-blue-500/30 border-t-blue-400" />
          Executing failure-path verification suite…
        </div>
      )}

      {meta.error && !verifying && (
        <div className="panel border border-red-500/30 bg-red-500/5 text-sm text-red-300">
          <p className="font-semibold">Verification failed</p>
          <p className="mt-1">{meta.error}</p>
          {!online && (
            <p className="mt-2 text-xs text-red-400/80">
              Ensure the API is running on port 8002.
            </p>
          )}
        </div>
      )}

      {!hasPayload && !verifying && !meta.error ? (
        <div className="panel py-10 text-center text-sm text-slate-400">
          Click <strong>Verify</strong> to run failure-path tests
        </div>
      ) : null}

      {hasPayload && lastVerifyPayload && (
        <div className="panel space-y-4">
          <h2 className="font-semibold">Truth Verification</h2>
          <div className="flex flex-wrap items-center gap-3">
            <StatusPill value={lastVerifyPayload.truth_verification} />
            <span className="text-sm text-slate-400">Reconstruction proof from persisted logs</span>
          </div>
          {Object.keys(truthChecks).length > 0 && (
            <div className="grid gap-2 sm:grid-cols-2">
              {Object.entries(truthChecks).map(([check, passed]) => (
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
          {lastVerifyPayload.validation_state_diff && (
            <div className="rounded-lg border border-line/60 bg-elevated/20 p-3 text-xs">
              <p className="font-semibold text-slate-300">Validation state diff</p>
              <p className="mt-1 font-mono text-slate-400">
                stored {lastVerifyPayload.validation_state_diff.stored_valid} valid /{" "}
                {lastVerifyPayload.validation_state_diff.stored_invalid} invalid → recomputed{" "}
                {lastVerifyPayload.validation_state_diff.recomputed_valid} valid /{" "}
                {lastVerifyPayload.validation_state_diff.recomputed_invalid} invalid
              </p>
              <p className="mt-1 text-slate-500">
                mismatches: {lastVerifyPayload.validation_state_diff.mismatch_count}
              </p>
            </div>
          )}
          {lastVerifyPayload.recovery_state_diff && (
            <div className="rounded-lg border border-line/60 bg-elevated/20 p-3 text-xs">
              <p className="font-semibold text-slate-300">Recovery state diff</p>
              <p className="mt-1 font-mono text-slate-400">
                resume_point={String(lastVerifyPayload.recovery_state_diff.derived?.resume_point ?? "—")}{" "}
                · interrupted=
                {String(lastVerifyPayload.recovery_state_diff.derived?.interrupted_events ?? "—")}
              </p>
              <p className="mt-1 text-slate-500">
                independent match:{" "}
                {lastVerifyPayload.recovery_state_diff.match ? "yes" : "no"}
              </p>
            </div>
          )}
          {lastVerifyPayload.original_truth_hash && (
            <p className="break-all font-mono text-[10px] text-slate-500">
              truth_hash: {lastVerifyPayload.original_truth_hash.slice(0, 16)}…
            </p>
          )}
        </div>
      )}

      {total > 0 && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="panel text-center">
              <p className="text-xs uppercase text-slate-500">Total checks</p>
              <p className="mt-1 font-mono text-2xl font-bold">{total}</p>
            </div>
            <div className="panel text-center">
              <p className="text-xs uppercase text-slate-500">Detected</p>
              <p className="mt-1 font-mono text-2xl font-bold text-red-400">{detected}</p>
            </div>
            <div className="panel text-center">
              <p className="text-xs uppercase text-slate-500">Clear</p>
              <p className="mt-1 font-mono text-2xl font-bold text-emerald-400">
                {total - detected}
              </p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {results.map((result) => (
              <div
                key={result.failure_type}
                className={`panel border ${
                  result.failure_detected
                    ? "border-red-500/30 bg-red-500/5"
                    : "border-emerald-500/20"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-sm font-semibold">{result.failure_type}</span>
                  <span
                    className={result.failure_detected ? "badge-danger" : "badge-success"}
                  >
                    {result.failure_detected ? "DETECTED" : "CLEAR"}
                  </span>
                </div>
                <p className="mt-2 text-sm text-slate-400">{result.observable_cause}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
