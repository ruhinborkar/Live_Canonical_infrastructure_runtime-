import { useQuery } from "@tanstack/react-query";
import { runtimeApi } from "../api/runtimeApi";

export const consoleKeys = {
  status: ["console", "status"] as const,
  runs: (limit: number) => ["console", "runs", limit] as const,
  events: (
    log: string,
    limit: number,
    offset: number,
    status?: string,
    search?: string,
    category?: string
  ) =>
    ["console", "events", log, limit, offset, status ?? "", search ?? "", category ?? ""] as const,
  metrics: ["console", "metrics"] as const,
  logs: (limit: number) => ["console", "logs", limit] as const,
  reports: ["console", "reports"] as const,
  reportContent: (name: string) => ["console", "report-content", name] as const,
};

export function useRuntimeStatus() {
  return useQuery({
    queryKey: consoleKeys.status,
    queryFn: runtimeApi.status,
    refetchInterval: 15_000,
  });
}

export function useRuntimeRuns(limit = 15) {
  return useQuery({
    queryKey: consoleKeys.runs(limit),
    queryFn: () => runtimeApi.runs(limit),
    staleTime: 0,
  });
}

export function useRuntimeEvents(
  log = "live",
  limit = 25,
  offset = 0,
  status?: string,
  search?: string,
  category?: string
) {
  return useQuery({
    queryKey: consoleKeys.events(log, limit, offset, status, search, category),
    queryFn: () => runtimeApi.events({ log, limit, offset, status, search, category }),
    staleTime: 0,
    gcTime: 0,
    refetchOnMount: "always",
  });
}

export function useRuntimeMetrics() {
  return useQuery({
    queryKey: consoleKeys.metrics,
    queryFn: runtimeApi.metrics,
    refetchInterval: 10_000,
  });
}

export function useRuntimeLogs(limit = 80) {
  return useQuery({
    queryKey: consoleKeys.logs(limit),
    queryFn: () => runtimeApi.logs(limit),
    refetchInterval: 5_000,
  });
}

export function useRuntimeReports() {
  return useQuery({
    queryKey: consoleKeys.reports,
    queryFn: runtimeApi.reports,
    refetchInterval: 30_000,
  });
}

export function useReportContent(name: string | null) {
  return useQuery({
    queryKey: consoleKeys.reportContent(name ?? ""),
    queryFn: () => runtimeApi.reportContent(name!),
    enabled: Boolean(name),
  });
}

export function useInvalidateConsole() {
  return ["console"] as const;
}
