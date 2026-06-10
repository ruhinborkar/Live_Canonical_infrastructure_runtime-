import { RunMode } from "../api/client";
import { useRuntime } from "../hooks/useRuntime";
import { operationLabel } from "../lib/parseRunResponse";
import { cn } from "../lib/utils";

const ACTIONS: { mode: RunMode; label: string; primary?: boolean; requiresLive?: boolean }[] = [
  { mode: "live", label: "Run Live", primary: true },
  { mode: "replay", label: "Replay", requiresLive: true },
  { mode: "recover", label: "Recover", requiresLive: true },
  { mode: "verify", label: "Verify" },
];

export default function OperationBar({ modes }: { modes?: RunMode[] }) {
  const { loadingMode, loading, online, hasLiveData, operationMeta, execute } = useRuntime();

  const visible = modes ? ACTIONS.filter((a) => modes.includes(a.mode)) : ACTIONS;

  function isDisabled(mode: RunMode, requiresLive?: boolean): boolean {
    if (!online || loading) return true;
    if (loadingMode === mode) return true;
    if (requiresLive && !hasLiveData) return true;
    return false;
  }

  function disabledReason(mode: RunMode, requiresLive?: boolean): string | undefined {
    if (!online) return "API offline";
    if (loading && loadingMode !== mode) return "Another operation is running";
    if (requiresLive && !hasLiveData) return "Run Live first to create execution logs";
    return operationMeta[mode].error ?? undefined;
  }

  return (
    <div className="space-y-3">
      {!online && (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-300">
          API offline — start backend with <code className="font-mono">.\start.ps1</code>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3" role="toolbar" aria-label="Runtime operations">
        {visible.map(({ mode, label, primary, requiresLive }) => {
          const isActive = loadingMode === mode;
          const disabled = isDisabled(mode, requiresLive);
          const reason = disabledReason(mode, requiresLive);

          return (
            <button
              key={mode}
              type="button"
              className={cn(primary ? "btn-primary" : "btn-secondary", disabled && "opacity-50")}
              disabled={disabled}
              title={reason}
              aria-label={reason ? `${label}: ${reason}` : label}
              onClick={() => void execute(mode)}
            >
              {isActive ? (
                <>
                  <span
                    className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
                    aria-hidden="true"
                  />
                  Running…
                </>
              ) : (
                label
              )}
            </button>
          );
        })}
      </div>

      {visible.some((a) => a.requiresLive) && !hasLiveData && online && (
        <p className="text-xs text-amber-400/90">
          Replay and Recover are disabled until a live run completes.
        </p>
      )}

      {visible.map(({ mode }) => {
        const meta = operationMeta[mode];
        if (!meta.error) return null;
        return (
          <p key={`err-${mode}`} className="text-sm text-red-400" role="alert">
            {operationLabel(mode)} failed: {meta.error}
          </p>
        );
      })}
    </div>
  );
}
