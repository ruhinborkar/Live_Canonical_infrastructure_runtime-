import { cn } from "../../../lib/utils";

interface MetricTileProps {
  label: string;
  value: string | number;
  sub?: string;
  tone?: "default" | "success" | "warning" | "danger" | "info";
}

const toneMap = {
  default: "text-slate-100",
  success: "text-neon-green",
  warning: "text-neon-amber",
  danger: "text-red-400",
  info: "text-neon-blue",
};

export default function MetricTile({ label, value, sub, tone = "default" }: MetricTileProps) {
  return (
    <div className="metric-card">
      <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-500">
        {label}
      </p>
      <p className={cn("mt-1 font-mono text-lg font-bold tabular-nums", toneMap[tone])}>
        {value}
      </p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  );
}
