import { useState } from "react";
import { api, RunRecord, statusClass } from "../api/client";
import { useRuntime } from "../hooks/useRuntime";
import LoadingSpinner from "./LoadingSpinner";

interface RunHistoryProps {
  compact?: boolean;
}

export default function RunHistory({ compact = false }: RunHistoryProps) {
  const { runs } = useRuntime();
  const [selected, setSelected] = useState<RunRecord | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const displayRuns = compact ? runs.slice(0, 8) : runs;

  async function selectRun(run: RunRecord) {
    if (compact) return;
    setLoadingDetail(true);
    try {
      const detail = await api.getRun(run.id);
      setSelected(detail);
    } finally {
      setLoadingDetail(false);
    }
  }

  function downloadReport() {
    if (!selected?.result) return;
    const blob = new Blob([JSON.stringify(selected.result, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `run-${selected.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className={`run-history ${compact ? "" : "run-history-full"}`}>
      <div className="panel glass">
        <h2>Run History</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Mode</th>
                <th>Status</th>
                <th>Time</th>
                {!compact && <th>ID</th>}
              </tr>
            </thead>
            <tbody>
              {displayRuns.length === 0 ? (
                <tr>
                  <td colSpan={compact ? 3 : 4} className="loading">
                    No runs yet
                  </td>
                </tr>
              ) : (
                displayRuns.map((run) => (
                  <tr
                    key={run.id}
                    className={!compact ? "clickable" : ""}
                    onClick={() => selectRun(run)}
                  >
                    <td>
                      <span className="mode-badge">{run.mode}</span>
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          run.status === "completed" ? "valid" : "invalid"
                        }`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td>{new Date(run.created_at).toLocaleString()}</td>
                    {!compact && (
                      <td>
                        <code className="run-id">{run.id.slice(0, 8)}…</code>
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {!compact && selected && (
        <div className="panel glass run-detail">
          <div className="panel-header">
            <h2>Run Detail</h2>
            <button className="btn btn-secondary btn-sm" onClick={downloadReport}>
              Download JSON
            </button>
          </div>
          {loadingDetail ? (
            <LoadingSpinner />
          ) : (
            <>
              <div className="detail-grid">
                <div>
                  <span className="card-label">Mode</span>
                  <div>{selected.mode}</div>
                </div>
                <div>
                  <span className="card-label">Status</span>
                  <div className={`card-value ${statusClass(selected.status)}`}>
                    {selected.status}
                  </div>
                </div>
                <div>
                  <span className="card-label">Started</span>
                  <div>{new Date(selected.created_at).toLocaleString()}</div>
                </div>
                {selected.completed_at && (
                  <div>
                    <span className="card-label">Completed</span>
                    <div>{new Date(selected.completed_at).toLocaleString()}</div>
                  </div>
                )}
              </div>
              {selected.result && (
                <pre className="json-preview">
                  {JSON.stringify(selected.result, null, 2)}
                </pre>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
