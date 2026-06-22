import { useFailureInjectionResults, useProofManifest, useTruthLedgerStatus } from "../hooks/useConsoleQueries";
import Panel from "../ui/Panel";
import StatusPill from "../ui/StatusPill";

export default function OperationalProofPanels() {
  const { data: ledger } = useTruthLedgerStatus();
  const { data: injection } = useFailureInjectionResults();
  const { data: manifest } = useProofManifest();

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Panel title="Truth Ledger Status" subtitle="/api/runtime/ledger">
        {ledger?.available ? (
          <div className="space-y-2 text-xs">
            <StatusPill value={ledger.truth_reconstruction ?? "UNKNOWN"} />
            <p className="font-mono text-slate-400">source: {ledger.source}</p>
            <p className="font-mono text-slate-400">runtime_state: {ledger.runtime_state}</p>
            <p className="font-mono text-slate-500">
              snapshots: {ledger.snapshots_reconstructed ?? 0}
            </p>
          </div>
        ) : (
          <p className="text-sm text-slate-500">Run Live or `python run_system.py --mode ledger`</p>
        )}
      </Panel>

      <Panel title="Failure Injection Results" subtitle="/api/runtime/injection">
        {injection?.available && injection.results?.length ? (
          <div className="space-y-2">
            <p className="text-xs text-slate-500">
              detected: {injection.detected_count}/{injection.results.length}
            </p>
            {injection.results.map((row) => (
              <div
                key={row.failure_type}
                className="flex items-center justify-between rounded border border-line/60 px-2 py-1 text-xs"
              >
                <span className="font-mono text-slate-400">{row.failure_type}</span>
                <span className={row.detected ? "text-red-400" : "text-emerald-400"}>
                  {row.system_response}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Run `python run_system.py --mode inject`</p>
        )}
      </Panel>

      <Panel title="Proof Manifest" subtitle="/api/runtime/manifest">
        {manifest?.available ? (
          <div className="space-y-2 text-xs">
            <StatusPill value={manifest.overall ?? "UNKNOWN"} />
            {manifest.checks &&
              Object.entries(manifest.checks).map(([key, ok]) => (
                <p key={key} className="font-mono text-slate-400">
                  {key}: {ok ? "PASS" : "FAIL"}
                </p>
              ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Run `python run_system.py --mode manifest`</p>
        )}
      </Panel>
    </div>
  );
}
