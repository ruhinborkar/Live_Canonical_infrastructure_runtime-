import { Outlet } from "react-router-dom";
import { useRuntime } from "../../hooks/useRuntime";
import ToastContainer from "../Toast";
import Sidebar from "./Sidebar";

export default function AppShell() {
  const { online, refreshAll, loadingMode } = useRuntime();

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-line bg-surface/60 px-6 py-4 backdrop-blur-sm">
          <div>
            <h2 className="text-sm font-medium text-slate-300">Operations Console</h2>
            <p className="text-xs text-slate-500">
              Deterministic execution, replay verification &amp; recovery
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="btn-secondary btn-sm"
              onClick={() => void refreshAll()}
              disabled={loadingMode !== null}
            >
              Refresh data
            </button>
            <div className="flex items-center gap-2 rounded-full border border-line bg-elevated px-3 py-1.5 font-mono text-xs">
              <span
                className={`h-2 w-2 rounded-full ${
                  online ? "animate-pulse-slow bg-emerald-400 shadow-glow-success" : "bg-red-500"
                }`}
              />
              API {online ? "online" : "offline"}
            </div>
          </div>
        </header>

        {!online && (
          <div className="border-b border-amber-500/30 bg-amber-500/10 px-6 py-2 text-center text-sm text-amber-300">
            API offline — start backend with{" "}
            <code className="font-mono">.\run-api.ps1</code> or{" "}
            <code className="font-mono">.\start.ps1</code>
          </div>
        )}

        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
      <ToastContainer />
    </div>
  );
}
