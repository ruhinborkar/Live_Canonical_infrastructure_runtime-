import { useEffect, useMemo, useState } from "react";
import { TableSkeleton } from "../../../components/ui/Skeleton";
import SortableTh from "../../../components/ui/SortableTh";
import { LOG_META, LogType } from "../../../lib/eventLog";
import { nextSortDirection, sortRows, SortDirection } from "../../../lib/tableSort";
import { cn } from "../../../lib/utils";
import { useRuntimeEvents } from "../hooks/useConsoleQueries";
import { RuntimeEventRow } from "../api/types";
import EmptyState from "../ui/EmptyState";
import ErrorState from "../ui/ErrorState";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";

type CategoryFilter = "all" | "normal" | "corrupted" | "interrupted";

const CATEGORY_FILTERS: { id: CategoryFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "normal", label: "Normal" },
  { id: "corrupted", label: "Corrupted" },
  { id: "interrupted", label: "Interrupted" },
];

type SortKey = keyof Pick<
  RuntimeEventRow,
  "trace_id" | "sequence_id" | "event_type" | "runtime_state" | "validation_state" | "hash_status"
>;

function hashTone(status: string): string {
  if (status === "VERIFIED") return "text-neon-green";
  if (status === "MISMATCH") return "text-red-400";
  return "text-slate-400";
}

interface EventExplorerProps {
  pageSize?: number;
  initialLog?: LogType;
  initialCategory?: "normal" | "corrupted" | "interrupted";
}

export default function EventExplorer({
  pageSize = 20,
  initialLog,
  initialCategory,
}: EventExplorerProps) {
  const [log, setLog] = useState<LogType>(initialLog ?? "live");
  const [offset, setOffset] = useState(0);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<"all" | "VALID" | "INVALID">("all");
  const [category, setCategory] = useState<CategoryFilter>(
    initialCategory ?? "all"
  );
  const [sortKey, setSortKey] = useState<SortKey>("sequence_id");
  const [sortDir, setSortDir] = useState<SortDirection>("asc");

  useEffect(() => {
    if (initialLog) {
      setLog(initialLog);
      setOffset(0);
    }
  }, [initialLog]);

  useEffect(() => {
    if (initialCategory) {
      setCategory(initialCategory);
      setOffset(0);
    }
  }, [initialCategory]);

  const categoryFilter = category === "all" ? undefined : category;
  const statusFilter = status === "all" ? undefined : status;
  const searchFilter = search.trim() || undefined;

  const { data, isLoading, isError, refetch, isFetching } = useRuntimeEvents(
    log,
    pageSize,
    offset,
    statusFilter,
    searchFilter,
    categoryFilter
  );

  useEffect(() => {
    if (import.meta.env.DEV) {
      console.debug("[EventExplorer] filters", {
        log,
        category: categoryFilter,
        status: statusFilter,
        search: searchFilter,
        offset,
        filteredTotal: data?.filtered_total,
      });
    }
  }, [log, categoryFilter, statusFilter, searchFilter, offset, data?.filtered_total]);

  const events = data?.events ?? [];
  const sortedEvents = useMemo(
    () => sortRows(events, sortKey, sortDir),
    [events, sortKey, sortDir]
  );
  const filteredTotal = data?.filtered_total ?? 0;
  const totalPages = Math.max(1, Math.ceil(filteredTotal / pageSize));

  function handleSort(column: string) {
    const key = column as SortKey;
    setSortDir((dir) => nextSortDirection(sortKey, key, dir));
    setSortKey(key);
  }

  return (
    <Panel
      title="Event Explorer"
      subtitle="Canonical event stream · /api/runtime/events"
      action={
        <button
          type="button"
          className="btn-secondary btn-sm"
          disabled={isFetching}
          onClick={() => {
            void refetch({ cancelRefetch: false });
          }}
        >
          Refresh
        </button>
      }
      noPadding
    >
      <div className="border-b border-line/60 px-5 pb-4">
        <div className="mb-3 flex flex-wrap gap-2">
          {(Object.keys(LOG_META) as LogType[]).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => {
                setLog(key);
                setOffset(0);
              }}
              className={cn("filter-chip", log === key && "filter-chip--active")}
            >
              {LOG_META[key].label}
            </button>
          ))}
        </div>

        <div className="mb-3 flex flex-wrap gap-2">
          {CATEGORY_FILTERS.map((f) => (
            <button
              key={f.id}
              type="button"
              onClick={() => {
                setCategory(f.id);
                setOffset(0);
              }}
              className={cn("filter-chip", category === f.id && "filter-chip--active")}
            >
              {f.label}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          <input
            className="input max-w-xs"
            placeholder="Search trace, seq, type…"
            aria-label="Search events"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setOffset(0);
            }}
          />
          <select
            className="input w-auto"
            value={status}
            onChange={(e) => {
              setStatus(e.target.value as "all" | "VALID" | "INVALID");
              setOffset(0);
            }}
            aria-label="Filter by validation status"
          >
            <option value="all">All validation states</option>
            <option value="VALID">Valid</option>
            <option value="INVALID">Invalid</option>
          </select>
        </div>
      </div>

      {isError ? (
        <div className="p-5">
          <ErrorState message="Failed to load events" onRetry={() => void refetch()} />
        </div>
      ) : isLoading ? (
        <div className="p-5">
          <TableSkeleton rows={8} />
        </div>
      ) : events.length === 0 ? (
        <div className="p-5">
          <EmptyState
            title="No events"
            message={
              filteredTotal === 0 && (data?.total ?? 0) > 0
                ? "No events match the current filters. Try All or clear search."
                : LOG_META[log].emptyHint
            }
          />
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="ops-table w-full" aria-label="Runtime events">
              <thead>
                <tr className="border-b border-line">
                  <SortableTh label="Trace ID" column="trace_id" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                  <SortableTh label="Sequence ID" column="sequence_id" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                  <SortableTh label="Event Type" column="event_type" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                  <SortableTh label="Runtime State" column="runtime_state" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                  <SortableTh label="Validation Status" column="validation_state" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                  <SortableTh label="Hash Status" column="hash_status" sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
                </tr>
              </thead>
              <tbody>
                {sortedEvents.map((ev, i) => (
                  <tr key={`${ev.sequence_id}-${ev.trace_id}-${i}`}>
                    <td className="text-neon-blue/90">{ev.trace_id ?? "—"}</td>
                    <td>{ev.sequence_id ?? "—"}</td>
                    <td>{ev.event_type ?? "—"}</td>
                    <td className="text-slate-400">{ev.runtime_state ?? "—"}</td>
                    <td>
                      {ev.validation_state ? (
                        <StatusPill value={ev.validation_state} />
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className={cn("font-semibold", hashTone(ev.hash_status))}>
                      {ev.hash_status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {totalPages > 1 && (
            <div className="flex justify-center gap-4 border-t border-line/60 px-5 py-4 text-xs text-slate-500">
              <button
                type="button"
                className="btn-secondary btn-sm"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - pageSize))}
              >
                Previous
              </button>
              <span>
                Page {Math.floor(offset / pageSize) + 1} of {totalPages}
              </span>
              <button
                type="button"
                className="btn-secondary btn-sm"
                disabled={offset + pageSize >= filteredTotal}
                onClick={() => setOffset(offset + pageSize)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </Panel>
  );
}
