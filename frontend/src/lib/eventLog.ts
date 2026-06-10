export type LogType = "live" | "replay" | "recovery";

export const LOG_META: Record<
  LogType,
  { label: string; description: string; emptyHint: string }
> = {
  live: {
    label: "Live",
    description: "Canonical runtime events written during live execution",
    emptyHint: "Run Live to generate the live execution log",
  },
  replay: {
    label: "Replay",
    description: "Replayed events with hash verification and validation summary",
    emptyHint: "Run Live or Replay to populate the replay log",
  },
  recovery: {
    label: "Recovery",
    description: "Interrupted execution candidates and recovery validation records",
    emptyHint: "Run Live or Recover to populate the recovery log",
  },
};

export function formatEventRange(offset: number, limit: number, filteredTotal: number): string {
  if (filteredTotal === 0) return "0 events";
  const start = offset + 1;
  const end = Math.min(offset + limit, filteredTotal);
  return `${start}–${end} of ${filteredTotal}`;
}
