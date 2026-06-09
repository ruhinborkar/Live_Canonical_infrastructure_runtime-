import { RunMode } from "../api/client";
import { useRuntime } from "../hooks/useRuntime";
import LoadingSpinner from "./LoadingSpinner";

const ACTIONS: { mode: RunMode; label: string; primary?: boolean }[] = [
  { mode: "live", label: "Run Live", primary: true },
  { mode: "replay", label: "Replay" },
  { mode: "recover", label: "Recover" },
  { mode: "verify", label: "Verify" },
];

export default function ActionBar() {
  const { loading, run } = useRuntime();

  return (
    <div className="actions">
      {loading && <LoadingSpinner label="Pipeline running…" />}
      {ACTIONS.map(({ mode, label, primary }) => (
        <button
          key={mode}
          className={`btn ${primary ? "btn-primary" : "btn-secondary"}`}
          disabled={loading}
          onClick={() => run(mode)}
        >
          {loading && primary ? "Running…" : label}
        </button>
      ))}
    </div>
  );
}
