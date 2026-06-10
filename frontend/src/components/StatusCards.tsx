import { useRuntime } from "../hooks/useRuntime";
import { badgeClass, cn, statusTone } from "../lib/utils";
import { CardSkeleton } from "./ui/Skeleton";

export default function StatusCards() {
  const { liveResult, replayStatus, recoveryStatus, loadingMode, operationMeta } = useRuntime();
  const bootstrapping = loadingMode === "live" && !liveResult;

  if (bootstrapping) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  const cards = [
    {
      label: "Replay",
      value: replayStatus ?? "—",
      updating: loadingMode === "replay",
      error: operationMeta.replay.error,
    },
    {
      label: "Truth",
      value: liveResult?.truth_status ?? "—",
      updating: loadingMode === "live",
    },
    {
      label: "Recovery",
      value: recoveryStatus ?? "—",
      updating: loadingMode === "recover",
      error: operationMeta.recover.error,
    },
    {
      label: "Processed",
      value: liveResult?.runtime_execution?.processed_events?.toString() ?? "—",
      updating: false,
    },
    {
      label: "Valid",
      value: liveResult?.runtime_execution?.valid_events?.toString() ?? "—",
      updating: false,
    },
    {
      label: "Invalid",
      value: liveResult?.runtime_execution?.invalid_events?.toString() ?? "—",
      updating: false,
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {cards.map((card) => {
        const tone = statusTone(card.value);
        return (
          <div key={card.label} className="panel">
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {card.label}
              </p>
              {card.updating && (
                <span className="h-3 w-3 animate-spin rounded-full border-2 border-blue-500/30 border-t-blue-400" />
              )}
            </div>
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
            {"error" in card && card.error && (
              <p className="mt-2 text-xs text-red-400">{card.error}</p>
            )}
          </div>
        );
      })}
    </div>
  );
}
