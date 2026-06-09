import { NavLink, Outlet } from "react-router-dom";
import { useRuntime } from "../hooks/useRuntime";
import ToastContainer from "./Toast";

const NAV = [
  { to: "/", label: "Dashboard" },
  { to: "/events", label: "Events" },
  { to: "/runs", label: "Runs" },
  { to: "/verify", label: "Verify" },
];

export default function Layout() {
  const { online } = useRuntime();

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Canonical Infrastructure Runtime</h1>
          <p>Deterministic execution, replay verification &amp; recovery</p>
        </div>
        <div className="health-badge">
          <span className={`health-dot ${online ? "pulse" : "offline"}`} />
          API {online ? "online" : "offline"}
        </div>
      </header>

      <nav className="nav">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            end={item.to === "/"}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <main>
        <Outlet />
      </main>

      <ToastContainer />
    </div>
  );
}
