import { useRuntime } from "../hooks/useRuntime";
import ActionBar from "./ActionBar";

export default function VerifyResults() {
  const { lastVerifyResults, loading } = useRuntime();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold">Failure-Path Verification</h1>
        <p className="text-sm text-slate-400">
          Hostile validation: duplicates, sequence corruption, trace mutation, schema errors
        </p>
      </div>

      <ActionBar />

      {loading ? (
        <div className="panel text-center text-sm text-slate-400">Running verification…</div>
      ) : !lastVerifyResults ? (
        <div className="panel text-center text-sm text-slate-400">
          Click <strong>Verify</strong> to run failure-path tests
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {lastVerifyResults.map((result) => (
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
      )}
    </div>
  );
}
