export function KpiCardSkeleton() {
  return (
    <div className="metric-card h-28 animate-pulse bg-elevated/40" aria-hidden="true">
      <div className="h-3 w-20 rounded bg-elevated" />
      <div className="mt-4 h-8 w-16 rounded bg-elevated" />
      <div className="mt-3 h-2 w-32 rounded bg-elevated" />
    </div>
  );
}
