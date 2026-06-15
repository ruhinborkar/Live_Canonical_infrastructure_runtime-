import { useState } from "react";
import { formatDateTime } from "../../../lib/utils";
import { RuntimeReportArtifact } from "../api/types";
import { runtimeApi } from "../api/runtimeApi";
import { useRuntimeReports, useReportContent } from "../hooks/useConsoleQueries";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";
import { safeArray } from "../../../lib/normalize";
import { cn } from "../../../lib/utils";
import { KpiCardSkeleton } from "../ui/KpiCardSkeleton";

function formatSize(bytes: number | null): string {
  if (bytes == null) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileIcon(name: string): string {
  if (name.endsWith(".jsonl")) return "JSONL";
  if (name.endsWith(".json")) return "JSON";
  if (name.endsWith(".md")) return "MD";
  return "FILE";
}

export default function ReportsPanel() {
  const { data, isLoading, isError, refetch, isFetching } = useRuntimeReports();
  const [viewing, setViewing] = useState<string | null>(null);
  const contentQuery = useReportContent(viewing);

  return (
    <Panel
      title="Reports Center"
      subtitle="Generated runtime artifacts · /api/runtime/reports"
      action={
        <button
          type="button"
          className="btn-secondary btn-sm"
          disabled={isFetching}
          onClick={() => void refetch()}
          aria-label="Refresh reports"
        >
          Refresh
        </button>
      }
    >
      {isError ? (
        <ErrorState message="Failed to load report artifacts" onRetry={() => void refetch()} />
      ) : isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <KpiCardSkeleton key={i} />
          ))}
        </div>
      ) : safeArray<RuntimeReportArtifact>(data?.reports).length === 0 ? (
        <EmptyState title="No reports found" message="Run Live to generate runtime artifacts" />
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2" role="list" aria-label="Runtime reports">
            {safeArray<RuntimeReportArtifact>(data?.reports).map((report) => (
              <article key={report.name} className="report-card" role="listitem">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex min-w-0 items-center gap-2">
                    <span className="shrink-0 rounded border border-line/80 bg-canvas/60 px-1.5 py-0.5 font-mono text-[9px] text-slate-500">
                      {fileIcon(report.name)}
                    </span>
                    <p className="truncate font-mono text-sm text-slate-200">{report.name}</p>
                  </div>
                  <StatusPill value={report.available ? "AVAILABLE" : "MISSING"} />
                </div>
                <p className="mt-2 truncate text-xs text-slate-500" title={report.path}>
                  {report.path}
                </p>
                <div className="mt-3 flex flex-wrap gap-3 text-[10px] text-slate-500">
                  <span>
                    Generated:{" "}
                    <time className="font-mono text-slate-400">
                      {report.modified_at ? formatDateTime(report.modified_at) : "—"}
                    </time>
                  </span>
                  <span>Size: {formatSize(report.size_bytes)}</span>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <button
                    type="button"
                    className="btn-secondary btn-sm"
                    disabled={!report.available}
                    onClick={() => setViewing(report.name)}
                  >
                    View
                  </button>
                  {report.available && (
                    <button
                      type="button"
                      className="btn-ghost btn-sm"
                      onClick={() => {
                        void runtimeApi.reportContent(report.name).then((payload) => {
                          const blob = new Blob([payload.content], { type: "text/plain" });
                          const url = URL.createObjectURL(blob);
                          const anchor = document.createElement("a");
                          anchor.href = url;
                          anchor.download = report.name;
                          anchor.click();
                          URL.revokeObjectURL(url);
                        });
                      }}
                    >
                      Download
                    </button>
                  )}
                </div>
                <div
                  className={cn(
                    "mt-2 h-0.5 w-full rounded-full",
                    report.available
                      ? "bg-gradient-to-r from-neon-green/60 to-neon-blue/40"
                      : "bg-line"
                  )}
                  aria-hidden="true"
                />
              </article>
            ))}
          </div>

          {viewing && (
            <div className="mt-4 rounded-lg border border-line/80 bg-canvas/50 p-4">
              <div className="mb-3 flex items-center justify-between gap-2">
                <h3 className="font-mono text-sm text-slate-200">{viewing}</h3>
                <button
                  type="button"
                  className="btn-ghost btn-sm"
                  onClick={() => setViewing(null)}
                >
                  Close
                </button>
              </div>
              {contentQuery.isLoading ? (
                <p className="text-sm text-slate-500">Loading artifact…</p>
              ) : contentQuery.isError ? (
                <ErrorState
                  message="Failed to load artifact content"
                  onRetry={() => void contentQuery.refetch()}
                />
              ) : (
                <pre className="max-h-64 overflow-auto font-mono text-xs text-slate-400">
                  {contentQuery.data?.content ?? "No content"}
                </pre>
              )}
            </div>
          )}
        </>
      )}
    </Panel>
  );
}
