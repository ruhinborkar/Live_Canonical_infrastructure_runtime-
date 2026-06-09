import ActionBar from "../components/ActionBar";
import EventsTable from "../components/EventsTable";
import PipelineMonitor from "../components/PipelineMonitor";
import RunHistory from "../components/RunHistory";
import RuntimeCharts from "../components/RuntimeCharts";
import StatusCards from "../components/StatusCards";
import { useRuntime } from "../hooks/useRuntime";

export default function Dashboard() {
  const { refreshAll, loading } = useRuntime();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold">Dashboard</h1>
          <p className="text-sm text-slate-400">Runtime status and pipeline operations</p>
        </div>
        <button
          className="btn-secondary btn-sm"
          onClick={() => refreshAll()}
          disabled={loading}
        >
          Refresh data
        </button>
      </div>
      <StatusCards />
      <ActionBar />
      <PipelineMonitor />
      <RuntimeCharts />
      <div className="grid gap-6 xl:grid-cols-2">
        <EventsTable compact />
        <RunHistory compact />
      </div>
    </div>
  );
}
