import { api as base } from "../../../api/client";
import { config } from "../../../lib/config";
import {
  RuntimeEventRow,
  RuntimeLogEntry,
  RuntimeMetrics,
  RuntimeReportArtifact,
  RuntimeReportContent,
  RuntimeRunRow,
  RuntimeStatus,
} from "./types";

const BASE = config.apiUrl;

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}/runtime${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : "Request failed");
  }
  return res.json();
}

export const runtimeApi = {
  status: () => request<RuntimeStatus>("/status"),
  runs: (limit = 20) => request<{ runs: RuntimeRunRow[]; total: number }>(`/runs?limit=${limit}`),
  events: (params: {
    log?: string;
    limit?: number;
    offset?: number;
    status?: string;
    search?: string;
    category?: string;
  } = {}) => {
    const q = new URLSearchParams();
    q.set("log", params.log ?? "live");
    q.set("limit", String(params.limit ?? 50));
    q.set("offset", String(params.offset ?? 0));
    if (params.status) q.set("status", params.status);
    if (params.search) q.set("search", params.search);
    if (params.category) q.set("category", params.category);
    return request<{
      events: RuntimeEventRow[];
      total: number;
      filtered_total: number;
      stats: Record<string, number>;
    }>(`/events?${q}`);
  },
  metrics: () => request<RuntimeMetrics>("/metrics"),
  logs: (limit = 100) => request<{ logs: RuntimeLogEntry[]; total: number }>(`/logs?limit=${limit}`),
  reports: () => request<{ reports: RuntimeReportArtifact[]; total: number }>("/reports"),
  reportContent: (name: string) =>
    request<RuntimeReportContent>(`/reports/${encodeURIComponent(name)}/content`),
  health: base.health,
};
