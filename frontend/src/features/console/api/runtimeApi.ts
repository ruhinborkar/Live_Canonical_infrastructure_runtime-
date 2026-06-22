import { api as base } from "../../../api/client";
import { config } from "../../../lib/config";
import {
  InjectionProof,
  ProofManifestStatus,
  RuntimeEventRow,
  RuntimeHealthStatus,
  RuntimeLogEntry,
  RuntimeMetrics,
  RuntimeReportArtifact,
  RuntimeReportContent,
  RuntimeRunRow,
  RuntimeStatus,
  StartupValidationStatus,
  TruthLedgerStatus,
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
    const path = `/events?${q}`;
    if (import.meta.env.DEV) {
      console.debug("[runtimeApi] GET", path);
    }
    return request<{
      events: RuntimeEventRow[];
      total: number;
      filtered_total: number;
      stats: Record<string, number>;
    }>(path);
  },
  metrics: () => request<RuntimeMetrics>("/metrics"),
  healthMonitor: () => request<RuntimeHealthStatus>("/health"),
  startup: () => request<StartupValidationStatus>("/startup"),
  ledger: () => request<TruthLedgerStatus>("/ledger"),
  injection: () => request<InjectionProof>("/injection"),
  manifest: () => request<ProofManifestStatus>("/manifest"),
  logs: (limit = 100) => request<{ logs: RuntimeLogEntry[]; total: number }>(`/logs?limit=${limit}`),
  reports: () => request<{ reports: RuntimeReportArtifact[]; total: number }>("/reports"),
  reportContent: (name: string) =>
    request<RuntimeReportContent>(`/reports/${encodeURIComponent(name)}/content`),
  health: base.health,
};
