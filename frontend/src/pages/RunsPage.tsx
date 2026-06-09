import RunHistory from "../components/RunHistory";

export default function RunsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold">Runs</h1>
        <p className="text-sm text-slate-400">Execution history and run details</p>
      </div>
      <RunHistory />
    </div>
  );
}
