const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

export type RunMode = "live" | "replay" | "recover" | "verify";

export interface StageUpdate {
  type: "stage";
  stage: string;
  status: string;
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

export const api = {
  health: () => request<{ status: string }>("/health"),

  listRuns: () => request<{ runs: RunRecord[] }>("/runs"),

  getLatestReport: () => request<Record<string, unknown>>("/runs/report/latest"),

  runLive: () => request<LiveResult>("/runs/live", { method: "POST" }),

  runReplay: () => request<Record<string, unknown>>("/runs/replay", { method: "POST" }),

  runRecover: () => request<Record<string, unknown>>("/runs/recover", { method: "POST" }),

  runVerify: () =>
    request<{ results: Array<Record<string, unknown>> }>("/runs/verify", {
      method: "POST",
    }),

  listEvents: (log = "live", limit = 50, offset = 0) =>
    request<{
      total: number;
      events: Array<Record<string, unknown>>;
    }>(`/events?log=${log}&limit=${limit}&offset=${offset}`),
};

export function connectWebSocket(onMessage: (data: StageUpdate) => void): WebSocket {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  const socket = new WebSocket(`${protocol}//${host}/ws`);

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "stage") {
      onMessage(data as StageUpdate);
    }
  };

  return socket;
}
