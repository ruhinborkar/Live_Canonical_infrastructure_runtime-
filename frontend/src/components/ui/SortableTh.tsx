import { SortDirection } from "../../lib/tableSort";
import { cn } from "../../lib/utils";

interface SortableThProps {
  label: string;
  column: string;
  sortKey: string;
  sortDir: SortDirection;
  onSort: (column: string) => void;
  className?: string;
}

export default function SortableTh({
  label,
  column,
  sortKey,
  sortDir,
  onSort,
  className,
}: SortableThProps) {
  const active = sortKey === column;
  return (
    <th className={className}>
      <button
        type="button"
        className={cn(
          "inline-flex items-center gap-1 text-left uppercase transition-colors hover:text-slate-300",
          active && "text-neon-blue"
        )}
        onClick={() => onSort(column)}
        aria-sort={active ? (sortDir === "asc" ? "ascending" : "descending") : "none"}
      >
        {label}
        <span className="font-mono text-[10px] opacity-70" aria-hidden="true">
          {active ? (sortDir === "asc" ? "↑" : "↓") : "↕"}
        </span>
      </button>
    </th>
  );
}
