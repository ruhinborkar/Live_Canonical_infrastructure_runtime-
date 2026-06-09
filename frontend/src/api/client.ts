import { config } from "../lib/config";

const API_BASE = config.apiUrl;

const DEFAULT_TIMEOUT_MS = 120_000;

async function request<T>(
  path: string,
  options?: RequestInit & { timeoutMs?: number }
): Promise<T> {
  const timeoutMs = options?.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
      signal: controller.signal,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(
        typeof error.detail === "string" ? error.detail : `Request failed (${response.status})`
      );
    }

    return response.json();
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(`Request timed out after ${timeoutMs / 1000}s — is the API running?`);
    }
    if (error instanceof TypeError) {
      throw new Error("Cannot reach API — start backend with .\\start.ps1 or .\\run-api.ps1");
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export type RunMode = "live" | "replay" | "recover" | "verify";

export interface StageUpdate {
  type: "stage";
  stage: string;
  status: string;
}

export interface RuntimeEvent {
  sequence_id?: number;
  trace_id?: string;
  event_type?: string;
  runtime_state?: string;
  validation_status?: string;
  validation_reason?: string;
  payload?: Record<string, unknown>;
  payload_hash?: string;
}

export interface RunRecord {
  id: string;
  mode: string;
  status: string;
  created_at: string;
  completed_at?: string;
  result?: Record<string, unknown>;
}

export interface LiveResult {
  run_id: string;
  status: string;
  replay_status: string;
  truth_status: string;
  recovery_status: string;
  runtime_execution: {
    processed_events: number;
    valid_events: number;
    invalid_events: number;
  };
  dataset: {
    total_events: number;
    normal_events: number;
    corrupted_events: number;
    interrupted_events: number;
  };
}

export interface VerifyResult {
  failure_type: string;
  failure_detected: boolean;
  observable_cause: string;
}

export const PIPELINE_STAGES = [
  "INPUT",
  "VALIDATION",
  "SERIALIZATION",
  "HASHING",
  "PERSISTENCE",
  "REPLAY",
  "VERIFICATION",
  "RECOVERY",
  "OBSERVABILITY",
] as const;

export const api = {
  health: () =>
    request<{ status: string; service: string }>("/health", { timeoutMs: 10_000 }),

  listRuns: (limit = 50) =>
    request<{ runs: RunRecord[] }>(`/runs?limit=${limit}`, { timeoutMs: 15_000 }),

  getRun: (runId: string) =>
    request<RunRecord>(`/runs/${runId}`, { timeoutMs: 15_000 }),

  getLatestReport: () =>
    request<Record<string, unknown>>("/runs/report/latest", { timeoutMs: 15_000 }),

  runLive: () => request<LiveResult>("/runs/live", { method: "POST" }),

  runReplay: () =>
    request<Record<string, unknown>>("/runs/replay", { method: "POST", timeoutMs: 60_000 }),

  runRecover: () =>
    request<Record<string, unknown>>("/runs/recover", { method: "POST", timeoutMs: 60_000 }),

  runVerify: () =>
    request<{ results: VerifyResult[] }>("/runs/verify", { method: "POST", timeoutMs: 60_000 }),

  listEvents: (log = "live", limit = 50, offset = 0) =>
    request<{
      total: number;
      offset: number;
      limit: number;
      events: RuntimeEvent[];
    }>(`/events?log=${log}&limit=${limit}&offset=${offset}`, { timeoutMs: 15_000 }),
};

export function getWebSocketUrl(): string {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws`;
}

export function connectWebSocket(onMessage: (data: StageUpdate) => void): WebSocket {
  const socket = new WebSocket(getWebSocketUrl());

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "stage") {
      onMessage(data as StageUpdate);
    }
  };

  return socket;
}

export function statusClass(value: string): string {
  if (
    value.includes("VERIFIED") ||
    value.includes("NOT_REQUIRED") ||
    value === "ok" ||
    value === "completed"
  ) {
    return "success";
  }
  if (
    value.includes("REQUIRED") ||
    value.includes("MISMATCH") ||
    value.includes("FAILED") ||
    value.includes("failed")
  ) {
    return "warning";
  }
  return "";
}
