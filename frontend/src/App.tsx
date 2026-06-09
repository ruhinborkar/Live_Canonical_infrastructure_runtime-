import { useCallback, useEffect, useState } from "react";
import {
  api,
  connectWebSocket,
  LiveResult,
  RunRecord,
  StageUpdate,
} from "./api/client";
import "./App.css";

const PIPELINE_STAGES = [
  "INPUT",
  "VALIDATION",
  "SERIALIZATION",
  "HASHING",
  "PERSISTENCE",
  "REPLAY",
  "VERIFICATION",
  "RECOVERY",
  "OBSERVABILITY",
];

function statusClass(value: string): string {
  if (value.includes("VERIFIED") || value.includes("NOT_REQUIRED") || value === "ok") {
    return "success";
  }
  if (value.includes("REQUIRED") || value.includes("MISMATCH") || value.includes("FAILED")) {
    return "warning";
  }
  return "";
}

export default function App() {
  const [online, setOnline] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveResult, setLiveResult] = useState<LiveResult | null>(null);
  const [runs, setRuns] = useState<RunRecord[]>([]);
  const [events, setEvents] = useState<Array<Record<string, unknown>>>([]);
  const [eventTotal, setEventTotal] = useState(0);
  const [stageLog, setStageLog] = useState<StageUpdate[]>([]);
  const [activeStages, setActiveStages] = useState<Set<string>>(new Set());
  const [doneStages, setDoneStages] = useState<Set<string>>(new Set());
  const [lastOutput, setLastOutput] = useState<string>("");

  const refresh = useCallback(async () => {
    try {
      await api.health();
      setOnline(true);
      const [runsData, eventsData] = await Promise.all([
        api.listRuns(),
        api.listEvents("live", 20),
      ]);
      setRuns(runsData.runs);
      setEvents(eventsData.events);
      setEventTotal(eventsData.total);
    } catch {
      setOnline(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const socket = connectWebSocket((update) => {
      setStageLog((prev) => [...prev.slice(-49), update]);
      setActiveStages((prev) => new Set(prev).add(update.stage));
      setDoneStages((prev) => new Set(prev).add(update.stage));
    });
    return () => socket.close();
  }, [refresh]);

  const resetPipeline = () => {
    setStageLog([]);
    setActiveStages(new Set());
    setDoneStages(new Set());
  };

  const run = async (mode: "live" | "replay" | "recover" | "verify") => {
    setLoading(true);
    setError(null);
    resetPipeline();

    try {
      let output: unknown;
      if (mode === "live") {
        const result = await api.runLive();
        setLiveResult(result);
        output = result;
      } else if (mode === "replay") {
        output = await api.runReplay();
      } else if (mode === "recover") {
        output = await api.runRecover();
      } else {
        output = await api.runVerify();
      }
      setLastOutput(JSON.stringify(output, null, 2));
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Run failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Canonical Infrastructure Runtime</h1>
          <p>Deterministic execution, replay verification &amp; recovery dashboard</p>
        </div>
        <div className="health-badge">
          <span className={`health-dot ${online ? "" : "offline"}`} />
          API {online ? "online" : "offline"}
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid">
        <div className="card">
          <div className="card-label">Replay</div>
          <div className={`card-value ${statusClass(liveResult?.replay_status ?? "")}`}>
            {liveResult?.replay_status ?? "—"}
          </div>
        </div>
        <div className="card">
          <div className="card-label">Truth</div>
          <div className={`card-value ${statusClass(liveResult?.truth_status ?? "")}`}>
            {liveResult?.truth_status ?? "—"}
          </div>
        </div>
        <div className="card">
          <div className="card-label">Recovery</div>
          <div className={`card-value ${statusClass(liveResult?.recovery_status ?? "")}`}>
            {liveResult?.recovery_status ?? "—"}
          </div>
        </div>
        <div className="card">
          <div className="card-label">Events Processed</div>
          <div className="card-value">
            {liveResult?.runtime_execution?.processed_events ?? eventTotal || "—"}
          </div>
        </div>
      </div>

      <div className="actions">
        <button
          className="btn btn-primary"
          disabled={loading}
          onClick={() => run("live")}
        >
          {loading ? "Running…" : "Run Live"}
        </button>
        <button className="btn btn-secondary" disabled={loading} onClick={() => run("replay")}>
          Replay
        </button>
        <button className="btn btn-secondary" disabled={loading} onClick={() => run("recover")}>
          Recover
        </button>
        <button className="btn btn-secondary" disabled={loading} onClick={() => run("verify")}>
          Verify
        </button>
      </div>

      <div className="panel">
        <h2>Pipeline Monitor</h2>
        <div className="pipeline">
          {PIPELINE_STAGES.map((stage, i) => (
            <span key={stage} style={{ display: "contents" }}>
              {i > 0 && <span className="pipeline-arrow">→</span>}
              <span
                className={`pipeline-step ${
                  activeStages.has(stage) ? (doneStages.has(stage) ? "done" : "active") : ""
                }`}
              >
                {stage}
              </span>
            </span>
          ))}
        </div>
        <div className="stage-log" style={{ marginTop: "1rem" }}>
          {stageLog.length === 0 ? (
            <div className="loading">Waiting for pipeline events…</div>
          ) : (
            stageLog.map((entry, i) => (
              <div key={i}>
                <span className="stage-name">{entry.stage}</span> → {entry.status}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="two-col">
        <div className="panel">
          <h2>Recent Events ({eventTotal} total)</h2>
          <table>
            <thead>
              <tr>
                <th>Seq</th>
                <th>Type</th>
                <th>Status</th>
                <th>Trace</th>
              </tr>
            </thead>
            <tbody>
              {events.length === 0 ? (
                <tr>
                  <td colSpan={4} className="loading">
                    No events yet — run live mode
                  </td>
                </tr>
              ) : (
                events.slice(0, 15).map((event, i) => (
                  <tr key={i}>
                    <td>{String(event.sequence_id)}</td>
                    <td>{String(event.event_type)}</td>
                    <td>
                      <span
                        className={`badge ${
                          event.validation_status === "VALID" ? "valid" : "invalid"
                        }`}
                      >
                        {String(event.validation_status ?? "—")}
                      </span>
                    </td>
                    <td>{String(event.trace_id)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="panel">
          <h2>Run History</h2>
          <table>
            <thead>
              <tr>
                <th>Mode</th>
                <th>Status</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {runs.length === 0 ? (
                <tr>
                  <td colSpan={3} className="loading">
                    No runs yet
                  </td>
                </tr>
              ) : (
                runs.slice(0, 8).map((run) => (
                  <tr key={run.id}>
                    <td>{run.mode}</td>
                    <td>
                      <span className={`badge ${run.status === "completed" ? "valid" : "invalid"}`}>
                        {run.status}
                      </span>
                    </td>
                    <td>{new Date(run.created_at).toLocaleTimeString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {lastOutput && (
        <div className="panel">
          <h2>Last Run Output</h2>
          <pre className="json-preview">{lastOutput}</pre>
        </div>
      )}
    </div>
  );
}
