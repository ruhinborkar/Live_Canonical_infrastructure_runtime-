import { ReactNode } from "react";
import { formatDateTime } from "../../../lib/utils";
import { useRuntime } from "../../../hooks/useRuntime";
import { useRuntimeStatus } from "../hooks/useConsoleQueries";
import ErrorState from "../ui/ErrorState";
import { cn } from "../../../lib/utils";
import { config } from "../../../lib/config";

function operationalTone(status: string): string {
  if (status === "OPERATIONAL") return "text-neon-green";
  if (status === "DEGRADED") return "text-neon-amber";
  if (status === "FAILED") return "text-red-400";
  return "text-slate-400";
}

function envTone(env: string): string {
  if (env === "Production") return "text-neon-green";
  if (env === "Staging") return "text-neon-amber";
  return "text-slate-300";
}

interface StatCellProps {
  label: string;
  loading: boolean;
  children: ReactNode;
}

function StatCell({ label, loading, children }: StatCellProps) {
  return (
    <div className="rounded-xl border border-white/[0.06] bg-canvas/40 px-4 py-3 backdrop-blur-sm">
      <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">{label}</p>
      {loading ? (
        <div className="mt-2 h-7 w-28 animate-pulse rounded bg-elevated" aria-hidden="true" />
      ) : (
        <div className="mt-1">{children}</div>
      )}
    </div>
  );
}

export default function HeroStatusHeader() {
  const { online } = useRuntime();
  const { data, isLoading, isError, refetch } = useRuntimeStatus();

  if (isError) {
    return (
      <div className="hero-panel" role="banner">
        <ErrorState message="Unable to load runtime status" onRetry={() => void refetch()} />
      </div>
    );
  }

  const runtimeStatus = data?.runtime_status ?? "IDLE";
  const version = data?.runtime_version ?? config.runtimeVersion;
  const environment = data?.environment ?? config.appEnvLabel;

  return (
    <header className="hero-panel" role="banner" aria-label="Executive runtime status">
      <div className="relative z-10 flex flex-wrap items-start justify-between gap-6">
        <div className="min-w-[16rem] flex-1">
          <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-neon-blue/80">
            Infrastructure Runtime Operations Center
          </p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-50 sm:text-3xl">
            Canonical Runtime Console
          </h1>
          <p className="mt-2 max-w-xl text-sm text-slate-400">
            Production observability for deterministic execution, replay verification, and recovery
            orchestration.
          </p>
        </div>
      </div>

      <div
        className="relative z-10 mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5"
        role="list"
        aria-label="Executive status indicators"
      >
        <StatCell label="Runtime Status" loading={isLoading}>
          <p
            className={cn("font-mono text-lg font-bold tracking-wide", operationalTone(runtimeStatus))}
            role="listitem"
          >
            {runtimeStatus}
          </p>
        </StatCell>

        <StatCell label="API Status" loading={isLoading}>
          <div className="flex items-center gap-2" role="listitem">
            <span
              className={cn(
                "h-2 w-2 rounded-full",
                online ? "bg-neon-green shadow-glow-success" : "bg-red-500"
              )}
              aria-hidden="true"
            />
            <span className="font-mono text-sm font-semibold text-slate-200">
              {online ? "Online" : "Offline"}
            </span>
          </div>
        </StatCell>

        <StatCell label="Last Execution" loading={isLoading}>
          <p className="font-mono text-sm text-slate-200" role="listitem">
            {data?.last_execution_timestamp
              ? formatDateTime(data.last_execution_timestamp)
              : "No executions"}
          </p>
        </StatCell>

        <StatCell label="Runtime Version" loading={isLoading}>
          <p className="font-mono text-sm font-semibold text-slate-200" role="listitem">
            v{version}
          </p>
        </StatCell>

        <StatCell label="Environment" loading={isLoading}>
          <p className={cn("font-mono text-sm font-semibold", envTone(environment))} role="listitem">
            {environment}
          </p>
        </StatCell>
      </div>
    </header>
  );
}
