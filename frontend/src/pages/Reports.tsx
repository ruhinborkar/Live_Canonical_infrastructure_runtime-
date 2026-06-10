import { useLatestReport } from "../hooks/queries";
import { useRuntime } from "../hooks/useRuntime";
import { downloadJson } from "../lib/utils";
import { CardSkeleton } from "../components/ui/Skeleton";
import ReportsPanel from "../features/console/components/ReportsPanel";

export default function Reports() {
  const { data: report, isLoading, isError, refetch } = useLatestReport();
  const { execute, loadingMode } = useRuntime();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold">Reports</h1>
          <p className="text-sm text-slate-400">Generated runtime artifacts and latest execution report</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-secondary btn-sm" onClick={() => void refetch()}>
            Refresh
          </button>
          <button
            type="button"
            className="btn-primary btn-sm"
            onClick={() => void execute("live")}
            disabled={loadingMode === "live"}
          >
            {loadingMode === "live" ? "Running…" : "Generate report"}
          </button>
          {report && (
            <button
              type="button"
              className="btn-secondary btn-sm"
              onClick={() => downloadJson("final_runtime_report.json", report)}
            >
              Download JSON
            </button>
          )}
        </div>
      </div>

      <ReportsPanel />

      <div className="panel">
        <h2 className="mb-3 font-semibold">final_runtime_report.json</h2>
        {isLoading ? (
          <CardSkeleton />
        ) : isError || !report ? (
          <p className="text-center text-sm text-slate-400">
            No report yet — click <strong>Generate report</strong> to run live mode
          </p>
        ) : (
          <pre className="max-h-[50vh] overflow-auto rounded-lg bg-black/30 p-4 font-mono text-xs text-slate-400">
            {JSON.stringify(report, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
