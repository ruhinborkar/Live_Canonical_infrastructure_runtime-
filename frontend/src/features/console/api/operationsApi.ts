import { config } from "../../../lib/config";

const BASE = config.apiUrl;

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}/operations${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : "Request failed");
  }
  return res.json();
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}/operations${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : "Request failed");
  }
  return res.json();
}

export interface EngineStatus {
  state: string;
  running: boolean;
  uptime_seconds: number | null;
  counters: Record<string, number>;
  heartbeat: { heartbeat_tick: number; alive: boolean; age_seconds: number | null };
  scheduler: { dispatched: number; pending: number };
  queue: { pending: number; tasks: Array<Record<string, unknown>> };
  workers: { configured: number; alive: number; detail: Array<Record<string, unknown>> };
  alerts: { active_count: number; critical: number; warning: number };
  active_context: { context_id: string; name: string } | null;
  last_recovery: Record<string, unknown>;
}

export interface SituationView {
  what_is_happening: {
    engine: string;
    queue_pending: number;
    recent_timeline: Array<Record<string, unknown>>;
    runtime_confidence: { confidence: number; grade: string };
  };
  what_requires_attention: {
    alerts: { active_count: number; critical: number; warning: number; alerts: Array<Record<string, unknown>> };
    anomalies: { anomaly_count: number; anomaly_rate: number };
    drift: { drift_detected: boolean; summary?: string };
    degradation: { mode: string; degraded_subsystems: Array<Record<string, unknown>> };
  };
  what_happens_next: { recommendations: Array<{ priority: string; action: string; rationale: string }> };
}

export interface ReadinessView {
  score: number;
  max: number;
  grade: string;
  contributors: Array<{ signal: string; passed: boolean; weight: number; detail: string }>;
}

export interface QueueView {
  pending: number;
  tasks: Array<{ task_id: string; priority: number; source?: string; enqueued_at: string; event_type?: string }>;
}

export interface AlertsView {
  active_count: number;
  critical: number;
  warning: number;
  info: number;
  alerts: Array<{ alert_id: string; source: string; reason: string; severity: string; raised_at: string }>;
}

export interface TopologyView {
  services: Array<{ name: string; kind: string; healthy: boolean }>;
  healthy: number;
  total: number;
  state_transitions: Array<{ from: string; to: string; legal: boolean; timestamp: string }>;
}

export const operationsApi = {
  status: () => get<EngineStatus>("/status"),
  situation: () => get<SituationView>("/situation"),
  readiness: () => get<ReadinessView>("/readiness"),
  queue: () => get<QueueView>("/queue"),
  alerts: () => get<AlertsView>("/alerts"),
  topology: () => get<TopologyView>("/topology"),
  timeline: (limit = 60) => get<{ entries: Array<Record<string, unknown>> }>(`/timeline?limit=${limit}`),
  operatorTimeline: (limit = 60) =>
    get<{ actions: Array<Record<string, unknown>> }>(`/operator-timeline?limit=${limit}`),
  intelligence: () => get<Record<string, unknown>>("/intelligence"),
  resources: () => get<{ pools: Array<Record<string, unknown>> }>("/resources"),
  dependencies: () => get<Record<string, unknown>>("/dependencies"),
  submit: (payload: Record<string, unknown>, priority?: number) =>
    post<{ accepted: boolean; task?: Record<string, unknown> }>(
      `/submit${priority ? `?priority=${priority}` : ""}`,
      payload
    ),
  acknowledge: (alertId: string) => post(`/alerts/${alertId}/acknowledge`),
  start: () => post<EngineStatus>("/start"),
  stop: () => post<EngineStatus>("/stop"),
};
