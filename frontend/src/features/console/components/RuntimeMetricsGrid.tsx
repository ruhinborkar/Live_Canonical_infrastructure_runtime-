import { useNavigate } from "react-router-dom";
import { formatDateTime } from "../../../lib/utils";
import { cn } from "../../../lib/utils";
import { useRuntimeStatus } from "../hooks/useConsoleQueries";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";
import { KpiCardSkeleton } from "../ui/KpiCardSkeleton";

interface MetricDef {
  label: string;
  key: keyof Pick<
    import("../api/types").RuntimeStatus,
    | "total_events_processed"
    | "valid_events"
    | "invalid_events"
    | "events_replayed"
    | "events_reconstructed"
    | "recovery_points"
  >;
  status: (data: import("../api/types").RuntimeStatus) => string;
  tone: (
    data: import("../api/types").RuntimeStatus
  ) => "default" | "success" | "warning" | "info";
  href: string;
  detail: string;
}

const METRICS: MetricDef[] = [
  {
    label: "Processed Events",
    key: "total_events_processed",
    status: () => "INGESTED",
    tone: () => "info",
    href: "/events",
    detail: "View live event stream",
  },
  {
    label: "Valid Events",
    key: "valid_events",
    status: () => "VALIDATED",
    tone: () => "success",
    href: "/events?category=normal",
    detail: "Filter normal events",
  },
  {
    label: "Invalid Events",
    key: "invalid_events",
    status: (d) => (d.invalid_events > 0 ? "FLAGGED" : "CLEAN"),
    tone: (d) => (d.invalid_events > 0 ? "warning" : "default"),
    href: "/events?category=corrupted",
    detail: "Filter corrupted events",
  },
  {
    label: "Events Replayed",
    key: "events_replayed",
    status: (d) => d.replay_verification_status,
    tone: () => "success",
    href: "/events?log=replay",
    detail: "Open replay log",
  },
  {
    label: "Events Reconstructed",
    key: "events_reconstructed",
    status: (d) => d.truth_verification_status,
    tone: () => "success",
    href: "/verify",
    detail: "View truth verification",
  },
  {
    label: "Recovery Points",
    key: "recovery_points",
    status: (d) => d.recovery_status,
    tone: () => "warning",
    href: "/events?log=recovery",
    detail: "Open recovery log",
  },
];

const valueTone = {
  default: "text-slate-100",
  success: "text-neon-green",
  warning: "text-neon-amber",
  info: "text-neon-blue",
};

export default function RuntimeMetricsGrid() {
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = useRuntimeStatus();
  const lastUpdated = data?.last_updated;

  return (
    <Panel
      title="Runtime KPIs"
      subtitle="Sourced from final_runtime_report.json · click a card for details"
    >
      {isError ? (
        <ErrorState message="Failed to load runtime KPIs" onRetry={() => void refetch()} />
      ) : isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <KpiCardSkeleton key={i} />
          ))}
        </div>
      ) : !data || data.total_events_processed === 0 ? (
        <EmptyState
          title="No KPI data"
          message="Execute Run Live to populate runtime key performance indicators"
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {METRICS.map((m) => (
            <button
              key={m.key}
              type="button"
              className="metric-card w-full text-left"
              aria-label={`${m.label}: ${m.detail}`}
              onClick={() => navigate(m.href)}
            >
              <div className="flex items-start justify-between gap-2">
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
                  {m.label}
                </p>
                <StatusPill value={m.status(data)} />
              </div>
              <p
                className={cn(
                  "mt-2 font-mono text-2xl font-bold tabular-nums",
                  valueTone[m.tone(data)]
                )}
              >
                {data[m.key]}
              </p>
              <p className="mt-1 text-xs text-neon-blue/80">{m.detail} →</p>
              <p className="mt-2 text-[10px] text-slate-500">
                Last updated{" "}
                <time className="font-mono text-slate-400">
                  {lastUpdated ? formatDateTime(lastUpdated) : "—"}
                </time>
              </p>
            </button>
          ))}
        </div>
      )}
    </Panel>
  );
}
