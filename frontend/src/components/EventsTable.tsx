import { Fragment, useCallback, useEffect, useState } from "react";
import { api, RuntimeEvent } from "../api/client";
import LoadingSpinner from "./LoadingSpinner";

type Filter = "all" | "VALID" | "INVALID";

interface EventsTableProps {
  compact?: boolean;
  pageSize?: number;
}

export default function EventsTable({ compact = false, pageSize = 20 }: EventsTableProps) {
  const [events, setEvents] = useState<RuntimeEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [filter, setFilter] = useState<Filter>("all");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listEvents("live", compact ? 15 : pageSize, offset);
      setEvents(data.events);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, [compact, pageSize, offset]);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = events.filter((event) => {
    if (filter !== "all" && event.validation_status !== filter) return false;
    if (search) {
      const q = search.toLowerCase();
      const trace = String(event.trace_id ?? "").toLowerCase();
      const seq = String(event.sequence_id ?? "");
      return trace.includes(q) || seq.includes(q);
    }
    return true;
  });

  const totalPages = Math.ceil(total / pageSize);
  const currentPage = Math.floor(offset / pageSize) + 1;

  return (
    <div className="panel glass">
      <div className="panel-header">
        <h2>Events {compact ? "" : `(${total} total)`}</h2>
        {!compact && (
          <div className="toolbar">
            <input
              className="search-input"
              placeholder="Search trace or seq…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select
              className="select-input"
              value={filter}
              onChange={(e) => setFilter(e.target.value as Filter)}
            >
              <option value="all">All</option>
              <option value="VALID">Valid</option>
              <option value="INVALID">Invalid</option>
            </select>
          </div>
        )}
      </div>

      {loading ? (
        <LoadingSpinner label="Loading events…" />
      ) : (
        <>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Seq</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Trace</th>
                  {!compact && <th>State</th>}
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={compact ? 4 : 5} className="loading">
                      No events — run live mode first
                    </td>
                  </tr>
                ) : (
                  filtered.map((event, i) => (
                    <Fragment key={event.sequence_id ?? i}>
                      <tr
                        className={expanded === i ? "expanded-row" : "clickable"}
                        onClick={() => !compact && setExpanded(expanded === i ? null : i)}
                      >
                        <td>{event.sequence_id}</td>
                        <td>{event.event_type}</td>
                        <td>
                          <span
                            className={`badge ${
                              event.validation_status === "VALID" ? "valid" : "invalid"
                            }`}
                          >
                            {event.validation_status ?? "—"}
                          </span>
                        </td>
                        <td>{event.trace_id}</td>
                        {!compact && <td>{event.runtime_state}</td>}
                      </tr>
                      {!compact && expanded === i && (
                        <tr className="detail-row">
                          <td colSpan={5}>
                            <div className="event-detail">
                              <div>
                                <strong>Reason:</strong> {event.validation_reason ?? "—"}
                              </div>
                              <div>
                                <strong>Hash:</strong>{" "}
                                <code>{event.payload_hash ?? "—"}</code>
                              </div>
                              <div>
                                <strong>Payload:</strong>
                                <pre>{JSON.stringify(event.payload, null, 2)}</pre>
                              </div>
                            </div>
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
            <div className="pagination">
              <button
                className="btn btn-secondary btn-sm"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - pageSize))}
              >
                Previous
              </button>
              <span>
                Page {currentPage} of {totalPages}
              </span>
              <button
                className="btn btn-secondary btn-sm"
                disabled={offset + pageSize >= total}
                onClick={() => setOffset(offset + pageSize)}
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
