import { cn, statusTone } from "../../../lib/utils";

export default function StatusPill({ value }: { value: string }) {
  const tone = statusTone(value);
  const classes = {
    success: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
    warning: "border-amber-500/40 bg-amber-500/10 text-amber-300",
    danger: "border-red-500/40 bg-red-500/10 text-red-300",
    neutral: "border-line bg-elevated text-slate-400",
  };
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2 py-0.5 font-mono text-[10px] font-semibold uppercase",
        classes[tone === "neutral" ? "neutral" : tone]
      )}
    >
      {value}
    </span>
  );
}
