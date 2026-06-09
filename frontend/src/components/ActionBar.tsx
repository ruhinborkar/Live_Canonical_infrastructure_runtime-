import { useEffect, useState } from "react";
import { RunMode } from "../api/client";
import { useRuntime } from "../hooks/useRuntime";

const ACTIONS: { mode: RunMode; label: string; primary?: boolean }[] = [
  { mode: "live", label: "Run Live", primary: true },
  { mode: "replay", label: "Replay" },
  { mode: "recover", label: "Recover" },
  { mode: "verify", label: "Verify" },
];

export default function ActionBar() {
  const { loading, online, run } = useRuntime();
  const [activeMode, setActiveMode] = useState<RunMode | null>(null);

  function handleRun(mode: RunMode) {
    setActiveMode(mode);
    run(mode);
  }

  useEffect(() => {
    if (!loading) setActiveMode(null);
  }, [loading]);

  return (
    <div className="space-y-2">
      {!online && (
        <p className="text-sm text-amber-400">
          API offline — start the backend first, then try again.
        </p>
      )}
      <div className="flex flex-wrap items-center gap-3">
        {ACTIONS.map(({ mode, label, primary }) => {
          const isActive = loading && activeMode === mode;
          return (
            <button
              key={mode}
              type="button"
              className={primary ? "btn-primary" : "btn-secondary"}
              disabled={loading}
              onClick={() => handleRun(mode)}
            >
              {isActive ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Running…
                </>
              ) : (
                label
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
