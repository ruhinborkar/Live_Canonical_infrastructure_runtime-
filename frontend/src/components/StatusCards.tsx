import { useRuntime } from "../hooks/useRuntime";
import { badgeClass, cn, statusTone } from "../lib/utils";
import { CardSkeleton } from "./ui/Skeleton";

export default function StatusCards() {
  const { liveResult, replayStatus, recoveryStatus, loading } = useRuntime();

  if (loading && !liveResult) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  const cards = [
    { label: "Replay", value: replayStatus ?? "—" },
    { label: "Truth", value: liveResult?.truth_status ?? "—" },
    { label: "Recovery", value: recoveryStatus ?? "—" },
    {
      label: "Processed",
      value: liveResult?.runtime_execution?.processed_events?.toString() ?? "—",
    },
    {
      label: "Valid",
      value: liveResult?.runtime_execution?.valid_events?.toString() ?? "—",
    },
    {
      label: "Invalid",
      value: liveResult?.runtime_execution?.invalid_events?.toString() ?? "—",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {cards.map((card) => {
        const tone = statusTone(card.value);
        return (
          <div key={card.label} className="panel">
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              {card.label}
            </p>
            <p
              className={cn(
                "mt-2 font-mono text-xl font-semibold",
                tone === "success" && "text-emerald-400",
                tone === "warning" && "text-amber-400",
                tone === "neutral" && "text-slate-200"
              )}
            >
              {card.value}
            </p>
            {card.value !== "—" && (
              <span className={cn("mt-2 inline-block", badgeClass(tone))}>{tone}</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
