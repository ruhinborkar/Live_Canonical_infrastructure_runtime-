import { NavLink } from "react-router-dom";
import { cn } from "../../lib/utils";
import { useAuth } from "../../providers/AuthProvider";
import { config } from "../../lib/config";

const NAV = [
  { to: "/", label: "Dashboard", icon: "◉" },
  { to: "/events", label: "Events", icon: "☰" },
  { to: "/runs", label: "Runs", icon: "↻" },
  { to: "/verify", label: "Verify", icon: "⚡" },
  { to: "/reports", label: "Reports", icon: "📄" },
  { to: "/settings", label: "Settings", icon: "⚙" },
];

export default function Sidebar() {
  const { username, logout } = useAuth();

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-line bg-surface/80 backdrop-blur-md">
      <div className="border-b border-line p-5">
        <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">
          Canonical Runtime
        </p>
        <h1 className="mt-1 text-lg font-bold text-slate-100">Infrastructure</h1>
        <span
          className={cn(
            "mt-2 inline-block rounded-full px-2 py-0.5 text-[10px] font-bold uppercase",
            config.isProduction
              ? "bg-emerald-500/20 text-emerald-400"
              : "bg-amber-500/20 text-amber-400"
          )}
        >
          {config.appEnv}
        </span>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-600/20 text-blue-400"
                  : "text-slate-400 hover:bg-elevated hover:text-slate-200"
              )
            }
          >
            <span className="text-base opacity-70">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-line p-4">
        <p className="truncate text-xs text-slate-500">Signed in as</p>
        <p className="truncate text-sm font-medium text-slate-300">{username}</p>
        <button className="btn-ghost btn-sm mt-2 w-full" onClick={logout}>
          Sign out
        </button>
      </div>
    </aside>
  );
}
