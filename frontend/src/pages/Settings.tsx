import { useState } from "react";
import { api } from "../api/client";
import { config } from "../lib/config";
import { useRuntime } from "../hooks/useRuntime";

export default function Settings() {
  const { online, run, refreshAll, loading } = useRuntime();
  const [testResult, setTestResult] = useState<string | null>(null);

  async function testApi() {
    try {
      const health = await api.health();
      setTestResult(`API OK — ${health.service} (${health.status})`);
    } catch (e) {
      setTestResult(`API failed — ${e instanceof Error ? e.message : "unknown error"}`);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-bold">Settings</h1>
        <p className="text-sm text-slate-400">Environment and integration configuration</p>
      </div>

      <div className="panel space-y-4">
        <h2 className="font-semibold">Environment</h2>
        <dl className="grid gap-3 text-sm">
          <div className="flex justify-between border-b border-line pb-2">
            <dt className="text-slate-400">Mode</dt>
            <dd className="font-mono">{config.appEnv}</dd>
          </div>
          <div className="flex justify-between border-b border-line pb-2">
            <dt className="text-slate-400">API URL</dt>
            <dd className="font-mono">{config.apiUrl}</dd>
          </div>
          <div className="flex justify-between border-b border-line pb-2">
            <dt className="text-slate-400">API status</dt>
            <dd className={online ? "text-emerald-400" : "text-red-400"}>
              {online ? "Online" : "Offline"}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-slate-400">Health poll</dt>
            <dd className="font-mono">{config.healthPollMs}ms</dd>
          </div>
        </dl>
      </div>

      <div className="panel space-y-3">
        <h2 className="font-semibold">Actions</h2>
        <div className="flex flex-wrap gap-2">
          <button className="btn-secondary btn-sm" onClick={() => testApi()}>
            Test API connection
          </button>
          <button className="btn-secondary btn-sm" onClick={() => refreshAll()}>
            Refresh all data
          </button>
          <button
            type="button"
            className="btn-primary btn-sm"
            disabled={loading}
            onClick={() => run("live")}
          >
            {loading ? "Running…" : "Run Live from settings"}
          </button>
        </div>
        {testResult && <p className="text-sm text-slate-400">{testResult}</p>}
      </div>
    </div>
  );
}
