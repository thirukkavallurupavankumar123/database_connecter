"use client";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar, Line, Pie } from "react-chartjs-2";
import { useState } from "react";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const CHART_COLORS = [
  "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
  "#ec4899", "#06b6d4", "#f97316", "#14b8a6", "#6366f1",
];

type ChartType = "bar" | "line" | "pie";

export default function ChartView({
  columns,
  data,
}: {
  columns: string[];
  data: Record<string, any>[];
}) {
  const [chartType, setChartType] = useState<ChartType>("bar");
  const [labelCol, setLabelCol] = useState(columns[0] || "");
  const [valueCol, setValueCol] = useState(columns[1] || "");

  if (!data || data.length === 0) {
    return (
      <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 text-center text-slate-500">
        No data to chart.
      </div>
    );
  }

  const labels = data.slice(0, 50).map((row) => String(row[labelCol] ?? ""));
  const values = data.slice(0, 50).map((row) => Number(row[valueCol]) || 0);

  const chartData = {
    labels,
    datasets: [
      {
        label: valueCol,
        data: values,
        backgroundColor: chartType === "pie"
          ? CHART_COLORS.slice(0, labels.length)
          : CHART_COLORS[0],
        borderColor: chartType === "line" ? CHART_COLORS[0] : undefined,
        borderWidth: chartType === "line" ? 2 : 0,
        tension: 0.3,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { labels: { color: "#94a3b8" } },
      title: { display: false },
    },
    scales:
      chartType !== "pie"
        ? {
            x: { ticks: { color: "#94a3b8" }, grid: { color: "#1e293b" } },
            y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
          }
        : undefined,
  };

  return (
    <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-xs text-slate-400 mb-1">Chart Type</label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value as ChartType)}
            className="bg-[#334155] border border-slate-600 rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="bar">Bar Chart</option>
            <option value="line">Line Chart</option>
            <option value="pie">Pie Chart</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Labels (X-Axis)</label>
          <select
            value={labelCol}
            onChange={(e) => setLabelCol(e.target.value)}
            className="bg-[#334155] border border-slate-600 rounded-lg px-3 py-1.5 text-sm"
          >
            {columns.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1">Values (Y-Axis)</label>
          <select
            value={valueCol}
            onChange={(e) => setValueCol(e.target.value)}
            className="bg-[#334155] border border-slate-600 rounded-lg px-3 py-1.5 text-sm"
          >
            {columns.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        {chartType === "bar" && <Bar data={chartData} options={options as any} />}
        {chartType === "line" && <Line data={chartData} options={options as any} />}
        {chartType === "pie" && <Pie data={chartData} options={options as any} />}
      </div>
    </div>
  );
}
