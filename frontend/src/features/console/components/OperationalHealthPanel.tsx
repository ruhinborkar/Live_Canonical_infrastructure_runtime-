import { useRuntimeHealth, useStartupValidation } from "../hooks/useConsoleQueries";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";

export default function OperationalHealthPanel() {
  const { data: health } = useRuntimeHealth();
  const { data: startup } = useStartupValidation();

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Panel title="Health Monitor" subtitle="/api/runtime/health">
        {health ? (
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Overall</span>
              <StatusPill value={health.overall} />
            </div>
            {(
              [
                ["Runtime", health.runtime_health],
                ["Replay", health.replay_health],
                ["Persistence", health.persistence_health],
                ["Recovery", health.recovery_health],
              ] as const
            ).map(([label, value]) => (
              <div key={label} className="flex items-center justify-between font-mono">
                <span className="text-slate-500">{label}</span>
                <span className="text-slate-300">{value}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Loading health status…</p>
        )}
      </Panel>

      <Panel title="Startup Validation" subtitle="/api/runtime/startup">
        {startup ? (
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Status</span>
              <StatusPill value={startup.status} />
            </div>
            {Object.entries(startup.checks).map(([check, passed]) => (
              <div key={check} className="flex items-center justify-between font-mono">
                <span className="text-slate-500">{check}</span>
                <span className={passed ? "text-emerald-400" : "text-red-400"}>
                  {passed ? "PASS" : "FAIL"}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Loading startup validation…</p>
        )}
      </Panel>
    </div>
  );
}
