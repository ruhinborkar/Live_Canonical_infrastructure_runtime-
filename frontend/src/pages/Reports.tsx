import { useLatestReport } from "../hooks/queries";
import { useRuntime } from "../hooks/useRuntime";
import { downloadJson } from "../lib/utils";
import { CardSkeleton } from "../components/ui/Skeleton";

export default function Reports() {
  const { data: report, isLoading, isError, refetch } = useLatestReport();
  const { run, loading } = useRuntime();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold">Reports</h1>
          <p className="text-sm text-slate-400">Latest runtime execution report</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn-secondary btn-sm" onClick={() => refetch()} disabled={loading}>
            Refresh
          </button>
          <button
            className="btn-primary btn-sm"
            onClick={() => run("live")}
            disabled={loading}
          >
            {loading ? "Running…" : "Generate report"}
          </button>
          {report && (
            <button
              className="btn-secondary btn-sm"
              onClick={() => downloadJson("final_runtime_report.json", report)}
            >
              Download JSON
            </button>
          )}
        </div>
      </div>

      {isLoading ? (
        <CardSkeleton />
      ) : isError || !report ? (
        <div className="panel text-center text-sm text-slate-400">
          No report yet — click <strong>Generate report</strong> to run live mode
        </div>
      ) : (
        <pre className="panel max-h-[70vh] overflow-auto font-mono text-xs text-slate-400">
          {JSON.stringify(report, null, 2)}
        </pre>
      )}
    </div>
  );
}
