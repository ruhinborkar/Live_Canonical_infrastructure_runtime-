import { useState } from "react";
import { api } from "../api/client";
import OperationBar from "../components/OperationBar";
import { config } from "../lib/config";
import { useRuntime } from "../hooks/useRuntime";
import { useRuntimeStatus } from "../features/console/hooks/useConsoleQueries";

export default function Settings() {
  const { online, refreshAll } = useRuntime();
  const { data: status } = useRuntimeStatus();
  const [testResult, setTestResult] = useState<string | null>(null);

  const version = status?.runtime_version ?? config.runtimeVersion;
  const environment = status?.environment ?? config.appEnvLabel;

  async function testApi() {
    try {
      const health = await api.health();
      setTestResult(
        `API OK — ${health.service} v${health.runtime_version ?? version} · ${health.environment ?? environment}`
      );
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
        <h2 className="font-semibold">Runtime</h2>
        <dl className="grid gap-3 text-sm">
          <div className="flex justify-between border-b border-line pb-2">
            <dt className="text-slate-400">Runtime version</dt>
            <dd className="font-mono">v{version}</dd>
          </div>
          <div className="flex justify-between border-b border-line pb-2">
            <dt className="text-slate-400">Environment</dt>
            <dd className="font-mono">{environment}</dd>
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
        <h2 className="font-semibold">Operations</h2>
        <OperationBar modes={["live"]} />
        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-secondary btn-sm" onClick={() => void testApi()}>
            Test API connection
          </button>
          <button type="button" className="btn-secondary btn-sm" onClick={() => void refreshAll()}>
            Refresh all data
          </button>
        </div>
        {testResult && <p className="text-sm text-slate-400" role="status">{testResult}</p>}
      </div>
    </div>
  );
}
