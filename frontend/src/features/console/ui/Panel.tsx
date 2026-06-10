import { ReactNode } from "react";
import { cn } from "../../../lib/utils";

interface PanelProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
}

export default function Panel({
  title,
  subtitle,
  action,
  children,
  className,
  noPadding,
}: PanelProps) {
  return (
    <section className={cn("glass-panel overflow-hidden", className)}>
      <div
        className={cn(
          "flex flex-wrap items-start justify-between gap-3 border-b border-white/[0.06] px-5 py-4",
          !noPadding && "mb-0"
        )}
      >
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-slate-100">{title}</h2>
          {subtitle && <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>}
        </div>
        {action}
      </div>
      <div className={cn(!noPadding && "p-5 pt-4")}>{children}</div>
    </section>
  );
}
