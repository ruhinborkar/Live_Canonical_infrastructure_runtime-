import { formatDateTime } from "../../../lib/utils";
import { useRuntimeMetrics } from "../hooks/useConsoleQueries";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import MetricTile from "../ui/MetricTile";
import Panel from "../ui/Panel";
import { KpiCardSkeleton } from "../ui/KpiCardSkeleton";

export default function ObservabilityMetrics() {
  const { data, isLoading, isError, refetch } = useRuntimeMetrics();

  const metrics = [
    { label: "Validation Latency", value: data?.validation_latency_ms, unit: "ms" },
    { label: "Replay Duration", value: data?.replay_duration_ms, unit: "ms" },
    { label: "Recovery Duration", value: data?.recovery_duration_ms, unit: "ms" },
    { label: "Persistence Writes", value: data?.persistence_writes, unit: "" },
    {
      label: "Runtime Throughput",
      value: data?.runtime_throughput_eps,
      unit: "evt/s",
    },
  ];

  return (
    <Panel
      title="Observability Metrics"
      subtitle="Pipeline performance · /api/runtime/metrics"
      action={
        <button
          type="button"
          className="btn-secondary btn-sm"
          onClick={() => void refetch()}
          aria-label="Refresh observability metrics"
        >
          Refresh
        </button>
      }
    >
      {isError ? (
        <ErrorState message="Failed to load metrics" onRetry={() => void refetch()} />
      ) : isLoading ? (
        <div className="grid gap-3 grid-cols-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <KpiCardSkeleton key={i} />
          ))}
        </div>
      ) : !data?.last_updated ? (
        <EmptyState
          title="No metrics yet"
          message="Run Live to capture validation, replay, and recovery timings"
        />
      ) : (
        <>
          <div className="grid gap-3 grid-cols-2">
            {metrics.map((m) => (
              <MetricTile
                key={m.label}
                label={m.label}
                value={
                  m.value != null
                    ? `${m.value}${m.unit ? ` ${m.unit}` : ""}`
                    : "—"
                }
                sub={
                  m.label === "Runtime Throughput" && data.processed_events
                    ? `${data.processed_events} events / ${data.total_pipeline_ms}ms`
                    : undefined
                }
                tone="info"
              />
            ))}
          </div>
          <p className="mt-4 text-xs text-slate-500">
            Pipeline total:{" "}
            <span className="font-mono text-slate-300">{data.total_pipeline_ms ?? 0} ms</span>
            {data.last_updated && (
              <>
                {" "}
                · Last updated{" "}
                <time className="font-mono text-slate-400">
                  {formatDateTime(data.last_updated)}
                </time>
              </>
            )}
          </p>
        </>
      )}
    </Panel>
  );
}
