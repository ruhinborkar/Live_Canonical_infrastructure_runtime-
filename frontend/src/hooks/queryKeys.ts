export const queryKeys = {
  health: ["health"] as const,
  runs: ["runs"] as const,
  run: (id: string) => ["runs", id] as const,
  events: (
    log: string,
    limit: number,
    offset: number,
    status?: string,
    search?: string,
    eventType?: string
  ) => ["events", log, limit, offset, status ?? "", search ?? "", eventType ?? ""] as const,
  eventsSummary: ["events", "summary"] as const,
  report: ["report", "latest"] as const,
  lastLive: ["lastLive"] as const,
  lastReplay: ["lastReplay"] as const,
  lastRecover: ["lastRecover"] as const,
  lastVerify: ["lastVerify"] as const,
};
