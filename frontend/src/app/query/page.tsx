"use client";

import { useState } from "react";
import { runQuery, downloadReport } from "@/lib/api";
import DataTable from "@/components/DataTable";
import ChartView from "@/components/ChartView";
import AiInsights from "@/components/AiInsights";

export default function QueryPage() {
  const [connectionId, setConnectionId] = useState("");
  const [userId, setUserId] = useState("");
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"table" | "chart">("table");

  const handleQuery = async () => {
    if (!connectionId || !userId || !query) {
      setError("Please fill in all fields.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await runQuery({
        connection_id: connectionId,
        user_id: userId,
        natural_language_query: query,
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Query failed");
    }
    setLoading(false);
  };

  const handleDownload = async (format: string) => {
    try {
      const res = await downloadReport({
        connection_id: connectionId,
        user_id: userId,
        natural_language_query: query,
        format,
      });
      const blob = new Blob([res.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const ext = format === "excel" ? "xlsx" : format;
      a.download = `report.${ext}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError("Download failed");
    }
  };

  const exampleQueries = [
    "Show total revenue in 2024",
    "Top 10 customers by sales",
    "Monthly sales trend for the last year",
    "Average order value by product category",
    "Revenue comparison between Q1 and Q2",
  ];

  return (
    <div className="max-w-6xl space-y-6">
      <h1 className="text-2xl font-bold">Query & Analyze</h1>

      {/* Connection + User IDs */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-slate-400 mb-1">Connection ID</label>
          <input
            type="text"
            value={connectionId}
            onChange={(e) => setConnectionId(e.target.value)}
            placeholder="Paste your connection ID"
            className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm text-slate-400 mb-1">User ID</label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Your user ID"
            className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2 text-sm"
          />
        </div>
      </div>

      {/* Query input */}
      <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-4">
        <label className="block text-sm text-slate-400 mb-1">
          Ask a question about your data
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='e.g. "Show total revenue in 2024" or "Top 10 customers by sales"'
          rows={3}
          className="w-full bg-[#334155] border border-slate-600 rounded-lg px-4 py-3 text-sm resize-none"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleQuery();
            }
          }}
        />

        {/* Example queries */}
        <div className="flex flex-wrap gap-2">
          {exampleQueries.map((eq) => (
            <button
              key={eq}
              onClick={() => setQuery(eq)}
              className="px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded-full text-xs text-slate-300"
            >
              {eq}
            </button>
          ))}
        </div>

        <button
          onClick={handleQuery}
          disabled={loading}
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "🔍 Run Query"}
        </button>

        {error && (
          <p className="text-sm text-red-400">❌ {error}</p>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Generated SQL */}
          <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-slate-400 mb-2">
              Generated SQL
            </h3>
            <pre className="bg-[#0f172a] rounded-lg p-3 text-sm text-green-400 overflow-x-auto">
              {result.generated_sql}
            </pre>
          </div>

          {/* AI Insights */}
          <AiInsights
            summary={result.ai_summary}
            insights={result.ai_insights}
          />

          {/* View toggle + Download */}
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode("table")}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  viewMode === "table"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-700 text-slate-300"
                }`}
              >
                📊 Table View
              </button>
              <button
                onClick={() => setViewMode("chart")}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  viewMode === "chart"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-700 text-slate-300"
                }`}
              >
                📈 Chart View
              </button>
            </div>

            <div className="flex gap-2">
              {["csv", "excel", "json", "pdf"].map((fmt) => (
                <button
                  key={fmt}
                  onClick={() => handleDownload(fmt)}
                  className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-xs font-medium uppercase"
                >
                  ⬇ {fmt}
                </button>
              ))}
            </div>
          </div>

          {/* Data display */}
          {viewMode === "table" ? (
            <DataTable columns={result.columns} data={result.data} />
          ) : (
            <ChartView columns={result.columns} data={result.data} />
          )}

          {/* Statistics */}
          {result.statistics && (
            <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-slate-400 mb-3">
                Statistics
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(result.statistics.numeric_stats || {}).map(
                  ([col, stats]: [string, any]) => (
                    <div
                      key={col}
                      className="bg-[#0f172a] rounded-lg p-3 text-xs"
                    >
                      <p className="font-semibold text-blue-400 mb-1">{col}</p>
                      <p>Mean: {stats.mean}</p>
                      <p>Median: {stats.median}</p>
                      <p>Std: {stats.std}</p>
                      <p>Min: {stats.min}</p>
                      <p>Max: {stats.max}</p>
                    </div>
                  )
                )}
              </div>
            </div>
          )}

          <p className="text-xs text-slate-500">
            {result.row_count} rows returned · Query ID: {result.query_id}
          </p>
        </div>
      )}
    </div>
  );
}
