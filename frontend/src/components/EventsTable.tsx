import { Fragment, useState } from "react";
import { RuntimeEvent } from "../api/client";
import { useEvents, useRefreshAll } from "../hooks/queries";
import { cn } from "../lib/utils";
import { TableSkeleton } from "./ui/Skeleton";

type Filter = "all" | "VALID" | "INVALID";
type LogType = "live" | "replay" | "recovery";

interface EventsTableProps {
  compact?: boolean;
  pageSize?: number;
}

export default function EventsTable({ compact = false, pageSize = 20 }: EventsTableProps) {
  const [offset, setOffset] = useState(0);
  const [filter, setFilter] = useState<Filter>("all");
  const [search, setSearch] = useState("");
  const [logType, setLogType] = useState<LogType>("live");
  const [expanded, setExpanded] = useState<number | null>(null);
  const refreshAll = useRefreshAll();

  const limit = compact ? 15 : pageSize;
  const { data, isLoading, isError, refetch } = useEvents(logType, limit, offset);

  const events = data?.events ?? [];
  const total = data?.total ?? 0;

  const filtered = events.filter((event: RuntimeEvent) => {
    if (filter !== "all" && event.validation_status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        String(event.trace_id ?? "").toLowerCase().includes(q) ||
        String(event.sequence_id ?? "").includes(q)
      );
    }
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(total / limit));
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="panel">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-semibold">Events {!compact && `(${total})`}</h2>
        <div className="flex flex-wrap gap-2">
          {!compact && (
            <>
              <select
                className="input w-auto"
                value={logType}
                onChange={(e) => {
                  setLogType(e.target.value as LogType);
                  setOffset(0);
                }}
              >
                <option value="live">Live log</option>
                <option value="replay">Replay log</option>
                <option value="recovery">Recovery log</option>
              </select>
              <input
                className="input max-w-xs"
                placeholder="Search trace or seq…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <select
                className="input w-auto"
                value={filter}
                onChange={(e) => setFilter(e.target.value as Filter)}
              >
                <option value="all">All</option>
                <option value="VALID">Valid</option>
                <option value="INVALID">Invalid</option>
              </select>
            </>
          )}
          <button
            className="btn-secondary btn-sm"
            onClick={() => {
              refetch();
              if (compact) refreshAll();
            }}
          >
            Refresh
          </button>
        </div>
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
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={compact ? 4 : 5} className="py-6 text-center text-slate-500">
                      No events — run live mode first
                    </td>
                  </tr>
                ) : (
                  filtered.map((event, i) => (
                    <Fragment key={`${event.sequence_id}-${i}`}>
                      <tr
                        className={cn(
                          "border-b border-line/50 font-mono text-xs",
                          !compact && "cursor-pointer hover:bg-blue-500/5"
                        )}
                        onClick={() => !compact && setExpanded(expanded === i ? null : i)}
                      >
                        <td className="py-2 pr-3">{event.sequence_id}</td>
                        <td className="py-2 pr-3">{event.event_type}</td>
                        <td className="py-2 pr-3">
                          <span
                            className={
                              event.validation_status === "VALID"
                                ? "badge-success"
                                : "badge-danger"
                            }
                          >
                            {event.validation_status ?? "—"}
                          </span>
                        </td>
                        <td className="py-2 pr-3">{event.trace_id}</td>
                        {!compact && <td className="py-2">{event.runtime_state}</td>}
                      </tr>
                      {!compact && expanded === i && (
                        <tr className="bg-canvas/50">
                          <td colSpan={5} className="p-4 font-sans text-xs">
                            <p>
                              <strong>Reason:</strong> {event.validation_reason ?? "—"}
                            </p>
                            <p className="mt-1 break-all">
                              <strong>Hash:</strong> {event.payload_hash ?? "—"}
                            </p>
                            <pre className="mt-2 overflow-auto rounded bg-black/30 p-2 font-mono text-slate-400">
                              {JSON.stringify(event.payload, null, 2)}
                            </pre>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {!compact && totalPages > 1 && (
            <div className="mt-4 flex items-center justify-center gap-4 text-sm text-slate-400">
              <button
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
                className="btn-secondary btn-sm"
                disabled={offset + limit >= total}
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
