import { statusClass } from "../api/client";
import { useRuntime } from "../hooks/useRuntime";

export default function StatusCards() {
  const { liveResult } = useRuntime();

  const cards = [
    {
      label: "Replay",
      value: liveResult?.replay_status ?? "—",
      cls: statusClass(liveResult?.replay_status ?? ""),
    },
    {
      label: "Truth",
      value: liveResult?.truth_status ?? "—",
      cls: statusClass(liveResult?.truth_status ?? ""),
    },
    {
      label: "Recovery",
      value: liveResult?.recovery_status ?? "—",
      cls: statusClass(liveResult?.recovery_status ?? ""),
    },
    {
      label: "Processed",
      value: liveResult?.runtime_execution?.processed_events?.toString() ?? "—",
      cls: "",
    },
    {
      label: "Valid",
      value: liveResult?.runtime_execution?.valid_events?.toString() ?? "—",
      cls: "success",
    },
    {
      label: "Invalid",
      value: liveResult?.runtime_execution?.invalid_events?.toString() ?? "—",
      cls: liveResult?.runtime_execution?.invalid_events ? "warning" : "",
    },
  ];

  return (
    <div className="grid">
      {cards.map((card) => (
        <div key={card.label} className="card glass">
          <div className="card-label">{card.label}</div>
          <div className={`card-value ${card.cls}`}>{card.value}</div>
        </div>
      ))}
    </div>
  );
}
