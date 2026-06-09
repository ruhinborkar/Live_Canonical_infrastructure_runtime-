import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { useRuntime } from "../hooks/useRuntime";

const COLORS = ["#22c55e", "#ef4444", "#f59e0b", "#3b82f6"];

export default function RuntimeCharts() {
  const { liveResult } = useRuntime();

  if (!liveResult) {
    return (
      <div className="panel glass">
        <h2>Analytics</h2>
        <p className="loading">Run live mode to see charts</p>
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
    <div className="two-col">
      <div className="panel glass">
        <h2>Validation Split</h2>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={validationData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={2}
            >
              {validationData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#111827",
                border: "1px solid #2a3548",
                borderRadius: 8,
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="chart-legend">
          {validationData.map((d, i) => (
            <span key={d.name}>
              <span className="legend-dot" style={{ background: COLORS[i] }} />
              {d.name}: {d.value}
            </span>
          ))}
        </div>
      </div>

      <div className="panel glass">
        <h2>Dataset Composition</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={datasetData}>
            <XAxis dataKey="name" tick={{ fill: "#8b9cb3", fontSize: 12 }} />
            <YAxis tick={{ fill: "#8b9cb3", fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                background: "#111827",
                border: "1px solid #2a3548",
                borderRadius: 8,
              }}
            />
            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
