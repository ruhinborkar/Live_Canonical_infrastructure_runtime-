import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useRuntime } from "../hooks/useRuntime";

const COLORS = ["#22c55e", "#ef4444", "#f59e0b", "#3b82f6"];

const tooltipStyle = {
  background: "#111827",
  border: "1px solid #2a3548",
  borderRadius: 8,
  fontSize: 12,
};

export default function RuntimeCharts() {
  const { liveResult } = useRuntime();

  if (!liveResult) {
    return (
      <div className="panel">
        <h2 className="font-semibold">Analytics</h2>
        <p className="mt-2 text-sm text-slate-500">Run live mode to see charts</p>
      </div>
    );
  }

  const validationData = [
    { name: "Valid", value: liveResult.runtime_execution.valid_events },
    { name: "Invalid", value: liveResult.runtime_execution.invalid_events },
  ];

  const datasetData = [
    { name: "Normal", value: liveResult.dataset.normal_events },
    { name: "Corrupted", value: liveResult.dataset.corrupted_events },
    { name: "Interrupted", value: liveResult.dataset.interrupted_events },
  ];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="panel">
        <h2 className="mb-4 font-semibold">Validation Split</h2>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={validationData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={2}
            >
              {validationData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={tooltipStyle} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="panel">
        <h2 className="mb-4 font-semibold">Dataset Composition</h2>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={datasetData}>
            <XAxis dataKey="name" tick={{ fill: "#8b9cb3", fontSize: 11 }} />
            <YAxis tick={{ fill: "#8b9cb3", fontSize: 11 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
