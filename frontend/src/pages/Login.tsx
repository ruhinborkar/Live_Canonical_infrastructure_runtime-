import { FormEvent, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { config } from "../lib/config";
import { useAuth } from "../providers/AuthProvider";

export default function Login() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (login(username, password)) {
      navigate("/");
      return;
    }
    setError("Invalid credentials");
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="panel w-full max-w-md">
        <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">
          Canonical Runtime
        </p>
        <h1 className="mt-2 text-2xl font-bold">Sign in</h1>
        <p className="mt-1 text-sm text-slate-400">
          Production console access for infrastructure operations
        </p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Username</label>
            <input
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-400">Password</label>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <button type="submit" className="btn-primary w-full">
            Sign in
          </button>
        </form>

        <p className="mt-4 text-center text-xs text-slate-500">
          Demo: {config.authUser} / {config.authPass}
        </p>
      </div>
    </div>
  );
}
