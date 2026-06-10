import { Fragment, useEffect, useState } from "react";
import { RuntimeEvent } from "../api/client";
import { useEvents, useEventsSummary } from "../hooks/queries";
import { formatEventRange, LOG_META, LogType } from "../lib/eventLog";
import { cn } from "../lib/utils";
import { TableSkeleton } from "./ui/Skeleton";

type StatusFilter = "all" | "VALID" | "INVALID";

interface EventsTableProps {
  compact?: boolean;
  pageSize?: number;
}

function statusBadge(status?: string) {
  if (!status) return "badge-neutral";
  if (status === "VALID") return "badge-success";
  if (status === "INVALID") return "badge-danger";
  return "badge-neutral";
}

function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);
  return debounced;
}

function EventDetails({ event, logType }: { event: RuntimeEvent; logType: LogType }) {
  return (
    <div className="space-y-2 font-sans text-xs">
      {event.event_timestamp && (
        <p>
          <strong>Timestamp:</strong> {event.event_timestamp}
        </p>
      )}
      <p>
        <strong>Reason:</strong> {event.validation_reason ?? "—"}
      </p>
      <p className="break-all">
        <strong>Hash:</strong> {event.payload_hash ?? "—"}
      </p>
      {logType === "replay" && (
        <>
          <p>
            <strong>Replay verified:</strong>{" "}
            {event.replay_verified === undefined ? "—" : event.replay_verified ? "yes" : "no"}
          </p>
          <p className="break-all">
            <strong>Stored hash:</strong> {event.stored_hash ?? "—"}
          </p>
        </>
      )}
      {logType === "recovery" && event.recovery_status && (
        <p>
          <strong>Recovery status:</strong> {event.recovery_status}
        </p>
      )}
      {event.integrity_state && (
        <p>
          <strong>Integrity:</strong> {event.integrity_state}
        </p>
      )}
      {event.payload && Object.keys(event.payload).length > 0 && (
        <pre className="mt-2 overflow-auto rounded bg-black/30 p-2 font-mono text-slate-400">
          {JSON.stringify(event.payload, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default function EventsTable({ compact = false, pageSize = 25 }: EventsTableProps) {
  const [offset, setOffset] = useState(0);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [search, setSearch] = useState("");
  const [logType, setLogType] = useState<LogType>("live");
  const [expanded, setExpanded] = useState<number | null>(null);

  const debouncedSearch = useDebouncedValue(search, 300);
  const limit = compact ? 15 : pageSize;
  const apiStatus = statusFilter === "all" ? undefined : statusFilter;

  const summary = useEventsSummary();
  const { data, isLoading, isError, refetch, isFetching } = useEvents(
    logType,
    limit,
    offset,
    apiStatus,
    debouncedSearch
  );

  const events = data?.events ?? [];
  const stats = data?.stats;
  const filteredTotal = data?.filtered_total ?? 0;
  const logTotal = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(filteredTotal / limit));
  const currentPage = Math.floor(offset / limit) + 1;
  const meta = LOG_META[logType];
  const summaryCounts = summary.data?.logs?.[logType];

  function selectLog(next: LogType) {
    setLogType(next);
    setOffset(0);
    setExpanded(null);
    setStatusFilter("all");
    setSearch("");
  }

  function handleStatusChange(next: StatusFilter) {
    setStatusFilter(next);
    setOffset(0);
    setExpanded(null);
  }

  const hasFilters = statusFilter !== "all" || debouncedSearch.length > 0;
  const emptyMessage =
    logTotal === 0
      ? meta.emptyHint
      : hasFilters
        ? "No events match the current filters"
        : meta.emptyHint;

  return (
    <div className="panel">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-semibold">Events</h2>
        <button
          type="button"
          className="btn-secondary btn-sm"
          disabled={isFetching}
          onClick={() => {
            void refetch();
            void summary.refetch();
          }}
        >
          {isFetching ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {(Object.keys(LOG_META) as LogType[]).map((log) => {
          const count = summary.data?.logs?.[log]?.total;
          const active = logType === log;
          return (
            <button
              key={log}
              type="button"
              onClick={() => selectLog(log)}
              className={cn(
                "rounded-lg border px-3 py-1.5 text-sm font-medium transition-colors",
                active
                  ? "border-blue-500/50 bg-blue-600/20 text-blue-300"
                  : "border-line bg-elevated text-slate-400 hover:text-slate-200"
              )}
            >
              {LOG_META[log].label}
              {count !== undefined && (
                <span className="ml-1.5 font-mono text-xs opacity-80">({count})</span>
              )}
            </button>
          );
        })}
      </div>

      <p className="mb-3 text-xs text-slate-500">{meta.description}</p>

      {stats && logTotal > 0 && (
        <div className="mb-4 grid gap-2 sm:grid-cols-4">
          <div className="rounded-lg border border-line bg-elevated/50 px-3 py-2 text-center">
            <p className="text-[10px] uppercase text-slate-500">Total</p>
            <p className="font-mono text-lg font-semibold">{stats.total}</p>
          </div>
          <div className="rounded-lg border border-line bg-elevated/50 px-3 py-2 text-center">
            <p className="text-[10px] uppercase text-slate-500">Valid</p>
            <p className="font-mono text-lg font-semibold text-emerald-400">{stats.valid}</p>
          </div>
          <div className="rounded-lg border border-line bg-elevated/50 px-3 py-2 text-center">
            <p className="text-[10px] uppercase text-slate-500">Invalid</p>
            <p className="font-mono text-lg font-semibold text-red-400">{stats.invalid}</p>
          </div>
          <div className="rounded-lg border border-line bg-elevated/50 px-3 py-2 text-center">
            <p className="text-[10px] uppercase text-slate-500">Validation rows</p>
            <p className="font-mono text-lg font-semibold text-blue-400">
              {stats.validation_rows}
            </p>
          </div>
        </div>
      )}

      {!compact && (
        <div className="mb-4 flex flex-wrap gap-2">
          <input
            className="input max-w-xs"
            placeholder="Search trace, seq, type…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setOffset(0);
              setExpanded(null);
            }}
          />
          <select
            className="input w-auto"
            value={statusFilter}
            onChange={(e) => handleStatusChange(e.target.value as StatusFilter)}
          >
            <option value="all">All statuses</option>
            <option value="VALID">Valid only</option>
            <option value="INVALID">Invalid only</option>
          </select>
        </div>
      )}

      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
        <span>
          {summaryCounts?.exists === false
            ? "Log file not found on server"
            : `Showing ${formatEventRange(offset, limit, filteredTotal)}`}
        </span>
        {hasFilters && (
          <button
            type="button"
            className="text-blue-400 hover:text-blue-300"
            onClick={() => {
              setStatusFilter("all");
              setSearch("");
              setOffset(0);
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {isError ? (
        <p className="text-sm text-red-400">Failed to load events — is the API running?</p>
      ) : isLoading ? (
        <TableSkeleton rows={compact ? 5 : 8} />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-left text-xs uppercase text-slate-500">
                  <th className="pb-2 pr-3">Seq</th>
                  <th className="pb-2 pr-3">Type</th>
                  <th className="pb-2 pr-3">Status</th>
                  <th className="pb-2 pr-3">Trace</th>
                  {!compact && <th className="pb-2">State</th>}
                </tr>
              </thead>
              <tbody>
                {events.length === 0 ? (
                  <tr>
                    <td colSpan={compact ? 4 : 5} className="py-8 text-center text-slate-500">
                      {emptyMessage}
                    </td>
                  </tr>
                ) : (
                  events.map((event, i) => (
                    <Fragment key={`${event.sequence_id}-${event.event_type}-${offset}-${i}`}>
                      <tr
                        className={cn(
                          "border-b border-line/50 font-mono text-xs",
                          !compact && "cursor-pointer hover:bg-blue-500/5"
                        )}
                        onClick={() => !compact && setExpanded(expanded === i ? null : i)}
                      >
                        <td className="py-2 pr-3">{event.sequence_id ?? "—"}</td>
                        <td className="py-2 pr-3">{event.event_type ?? "—"}</td>
                        <td className="py-2 pr-3">
                          <span className={statusBadge(event.validation_status)}>
                            {event.validation_status ?? "—"}
                          </span>
                        </td>
                        <td className="py-2 pr-3">{event.trace_id ?? "—"}</td>
                        {!compact && <td className="py-2">{event.runtime_state ?? "—"}</td>}
                      </tr>
                      {!compact && expanded === i && (
                        <tr className="bg-canvas/50">
                          <td colSpan={5} className="p-4">
                            <EventDetails event={event} logType={logType} />
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {!compact && filteredTotal > limit && (
            <div className="mt-4 flex items-center justify-center gap-4 text-sm text-slate-400">
              <button
                type="button"
                className="btn-secondary btn-sm"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - limit))}
              >
                Previous
              </button>
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <button
                type="button"
                className="btn-secondary btn-sm"
                disabled={offset + limit >= filteredTotal}
                onClick={() => setOffset(offset + limit)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
