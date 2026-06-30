import { useState } from "react";

import {
  useAcknowledgeAlert,
  useEngineStatus,
  useOpsAlerts,
  useOpsQueue,
  useOpsTopology,
  useOperatorTimeline,
  useReadiness,
  useSituation,
  useSubmitWork,
} from "../hooks/useOperationsQueries";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border border-white/[0.06] bg-elevated px-3 py-2">
      <p className="text-[10px] uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-mono text-sm text-slate-200">{value}</p>
    </div>
  );
}

function EngineControl() {
  const { data } = useEngineStatus();
  const submit = useSubmitWork();
  const counters = data?.counters ?? {};
  return (
    <Panel
      title="Runtime Engine"
      subtitle="Live operational state · /api/operations/status"
      action={
        <button
          type="button"
          className="btn-secondary btn-sm"
          disabled={submit.isPending || !data?.running}
          onClick={() =>
            submit.mutate({
              payload: { payload: { temperature: 21, signal: "OK" } },
              priority: 4,
            })
          }
        >
          {submit.isPending ? "Submitting…" : "Submit test work"}
        </button>
      }
    >
      {data ? (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <StatusPill value={data.state} />
            <span className="text-xs text-slate-500">
              heartbeat tick {data.heartbeat.heartbeat_tick} ·{" "}
              {data.heartbeat.alive ? "alive" : "stale"}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
            <Metric label="Workers" value={`${data.workers.alive}/${data.workers.configured}`} />
            <Metric label="Pending" value={data.queue.pending} />
            <Metric label="Accepted" value={counters.tasks_accepted ?? 0} />
            <Metric label="Completed" value={counters.tasks_completed ?? 0} />
            <Metric label="Invalid" value={counters.tasks_invalid ?? 0} />
            <Metric label="Dispatched" value={data.scheduler.dispatched} />
            <Metric label="Uptime (s)" value={data.uptime_seconds ?? "—"} />
            <Metric label="Active alerts" value={data.alerts.active_count} />
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-500">Connecting to runtime engine…</p>
      )}
    </Panel>
  );
}

function Readiness() {
  const { data } = useReadiness();
  return (
    <Panel title="Operational Readiness" subtitle="/api/operations/readiness">
      {data ? (
        <div className="space-y-3">
          <div className="flex items-baseline gap-3">
            <span className="font-mono text-3xl text-slate-100">{data.score}</span>
            <span className="text-slate-500">/ {data.max}</span>
            <StatusPill value={data.grade} />
          </div>
          <div className="space-y-1">
            {data.contributors.map((c) => (
              <div key={c.signal} className="flex items-center justify-between text-xs">
                <span className="font-mono text-slate-400">{c.signal}</span>
                <span className={c.passed ? "text-emerald-400" : "text-red-400"}>
                  {c.passed ? "PASS" : "FAIL"}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-500">Scoring…</p>
      )}
    </Panel>
  );
}

function Situation() {
  const { data } = useSituation();
  if (!data) {
    return (
      <Panel title="Situation Awareness" subtitle="/api/operations/situation">
        <p className="text-sm text-slate-500">Assessing situation…</p>
      </Panel>
    );
  }
  const next = data.what_happens_next.recommendations ?? [];
  return (
    <Panel title="Situation Awareness" subtitle="What is happening · requires attention · what's next">
      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <p className="mb-2 text-[10px] uppercase tracking-wide text-slate-500">What is happening</p>
          <p className="text-xs text-slate-300">Engine: {data.what_is_happening.engine}</p>
          <p className="text-xs text-slate-300">Queue: {data.what_is_happening.queue_pending}</p>
          <p className="text-xs text-slate-300">
            Confidence: {data.what_is_happening.runtime_confidence.confidence} (
            {data.what_is_happening.runtime_confidence.grade})
          </p>
        </div>
        <div>
          <p className="mb-2 text-[10px] uppercase tracking-wide text-slate-500">Requires attention</p>
          <p className="text-xs text-slate-300">
            Alerts: {data.what_requires_attention.alerts.active_count} (
            {data.what_requires_attention.alerts.critical} critical)
          </p>
          <p className="text-xs text-slate-300">
            Anomalies: {data.what_requires_attention.anomalies.anomaly_count}
          </p>
          <p className="text-xs text-slate-300">
            Drift: {data.what_requires_attention.drift.drift_detected ? "DETECTED" : "none"}
          </p>
          <p className="text-xs text-slate-300">
            Mode: {data.what_requires_attention.degradation.mode}
          </p>
        </div>
        <div>
          <p className="mb-2 text-[10px] uppercase tracking-wide text-slate-500">What happens next</p>
          {next.map((r, i) => (
            <div key={i} className="mb-1 text-xs">
              <span className="font-mono text-amber-300">{r.priority}</span>{" "}
              <span className="text-slate-300">{r.action}</span>
              <p className="text-[11px] text-slate-500">{r.rationale}</p>
            </div>
          ))}
        </div>
      </div>
    </Panel>
  );
}

function ExecutionQueue() {
  const { data } = useOpsQueue();
  return (
    <Panel title="Execution Queue" subtitle="/api/operations/queue">
      {data && data.tasks.length ? (
        <div className="space-y-1">
          <p className="text-xs text-slate-500">{data.pending} pending</p>
          {data.tasks.slice(0, 12).map((t) => (
            <div
              key={t.task_id}
              className="flex items-center justify-between rounded border border-white/[0.06] px-2 py-1 text-xs"
            >
              <span className="font-mono text-slate-400">P{t.priority}</span>
              <span className="text-slate-400">{t.event_type ?? "event"}</span>
              <span className="font-mono text-slate-600">{t.task_id.slice(0, 8)}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-500">Queue empty — workers keeping up</p>
      )}
    </Panel>
  );
}

function AlertEscalation() {
  const { data } = useOpsAlerts();
  const ack = useAcknowledgeAlert();
  return (
    <Panel title="Alert Escalation" subtitle="/api/operations/alerts">
      {data && data.alerts.length ? (
        <div className="space-y-2">
          {data.alerts.map((a) => (
            <div key={a.alert_id} className="rounded border border-white/[0.06] px-2 py-1 text-xs">
              <div className="flex items-center justify-between">
                <StatusPill value={a.severity} />
                <button
                  type="button"
                  className="btn-secondary btn-sm"
                  disabled={ack.isPending}
                  onClick={() => ack.mutate(a.alert_id)}
                >
                  Ack
                </button>
              </div>
              <p className="mt-1 text-slate-300">{a.reason}</p>
              <p className="text-[11px] text-slate-600">{a.source}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-500">No active alerts</p>
      )}
    </Panel>
  );
}

function Topology() {
  const { data } = useOpsTopology();
  return (
    <Panel title="Runtime Topology" subtitle="/api/operations/topology">
      {data ? (
        <div className="space-y-2">
          <p className="text-xs text-slate-500">
            {data.healthy}/{data.total} services healthy
          </p>
          <div className="grid grid-cols-2 gap-1">
            {data.services.map((s) => (
              <div key={s.name} className="flex items-center justify-between text-xs">
                <span className="font-mono text-slate-400">{s.name}</span>
                <span className={s.healthy ? "text-emerald-400" : "text-red-400"}>
                  {s.kind}
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-500">Loading topology…</p>
      )}
    </Panel>
  );
}

function OperatorTimeline() {
  const { data } = useOperatorTimeline();
  const actions = (data?.actions ?? []) as Array<Record<string, string>>;
  return (
    <Panel title="Operator Timeline" subtitle="/api/operations/operator-timeline">
      {actions.length ? (
        <div className="space-y-1">
          {actions.slice(0, 12).map((a, i) => (
            <div key={i} className="flex items-center justify-between text-xs">
              <span className="font-mono text-slate-400">{a.action}</span>
              <span className="text-slate-600">{a.operator}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-500">No operator actions yet</p>
      )}
    </Panel>
  );
}

export default function CommandCenter() {
  const [open, setOpen] = useState(true);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
          Operational Command Center
        </h2>
        <button type="button" className="btn-secondary btn-sm" onClick={() => setOpen((v) => !v)}>
          {open ? "Collapse" : "Expand"}
        </button>
      </div>
      {open && (
        <>
          <EngineControl />
          <Situation />
          <div className="grid gap-4 lg:grid-cols-3">
            <Readiness />
            <ExecutionQueue />
            <AlertEscalation />
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <Topology />
            <OperatorTimeline />
          </div>
        </>
      )}
    </div>
  );
}
