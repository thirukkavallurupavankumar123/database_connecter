"use client";

import { useState, useEffect } from "react";
import { connectSession, runQuery, downloadReport } from "@/lib/api";
import DataTable from "@/components/DataTable";
import ChartView from "@/components/ChartView";
import AiInsights from "@/components/AiInsights";
import AuthGuard from "@/components/AuthGuard";

type ConnectionOption = {
  id: string;
  name: string;
  label?: string | null;
  is_default?: boolean;
  db_type: string;
  host: string;
  database_name: string;
};

type SessionInfo = {
  user_id: string;
  user_name: string;
  organization_id: string;
  organization_name: string;
  connections: ConnectionOption[];
};

export default function QueryPage() {
  return (
    <AuthGuard>
      <QueryContent />
    </AuthGuard>
  );
}

function QueryContent() {
  // Session state — persists across queries
  const [session, setSession] = useState<SessionInfo | null>(null);
  const AUTO = "__auto__";
  const [selectedConnectionId, setSelectedConnectionId] = useState(AUTO);
  const [connectLoading, setConnectLoading] = useState(false);

  // Auto-connect on mount using auth session
  useEffect(() => {
    const userId = localStorage.getItem("argo_user_id");
    if (userId) {
      setConnectLoading(true);
      connectSession(userId)
        .then((res) => {
          setSession(res.data);
          if (res.data.connections.length > 0) {
            const defaultConn = res.data.connections.find((c: any) => c.is_default);
            setSelectedConnectionId(defaultConn ? defaultConn.id : AUTO);
          }
        })
        .catch(() => {})
        .finally(() => setConnectLoading(false));
    }
  }, []);
  const [connectError, setConnectError] = useState<string | null>(null);

  // Query state
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"table" | "chart">("table");

  // Download state
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleConnect = async () => {
    const userId = localStorage.getItem("argo_user_id");
    if (!userId) return;
    setConnectLoading(true);
    setConnectError(null);
    try {
      const res = await connectSession(userId);
      setSession(res.data);
      if (res.data.connections.length > 0) {
        const defaultConn = res.data.connections.find((c: any) => c.is_default);
        setSelectedConnectionId(defaultConn ? defaultConn.id : AUTO);
      }
    } catch (err: any) {
      setConnectError(err.response?.data?.detail || "Failed to connect.");
    }
    setConnectLoading(false);
  };

  const handleDisconnect = () => {
    setSession(null);
    setSelectedConnectionId("");
    setResult(null);
    setError(null);
    setQuery("");
  };

  const handleQuery = async () => {
    if (!session || !query.trim()) {
      setError("Please enter a query.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await runQuery({
        connection_id: selectedConnectionId === AUTO ? null : selectedConnectionId,
        user_id: session.user_id,
        natural_language_query: query.trim(),
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Query failed");
    }
    setLoading(false);
  };

  const handleDownload = async (format: string) => {
    if (!session || !query.trim()) return;
    setDownloading(format);
    try {
      const res = await downloadReport({
        connection_id: selectedConnectionId === AUTO ? null : selectedConnectionId,
        user_id: session.user_id,
        natural_language_query: query.trim(),
        format,
      });
      const blob = new Blob([res.data]);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const ext = format === "excel" ? "xlsx" : format;
      a.download = `report.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch {
      setError(`Download failed for format: ${format}`);
    }
    setDownloading(null);
  };

  const exampleQueries = [
    "Show total revenue in 2024",
    "Top 10 customers by sales",
    "Monthly sales trend for the last year",
    "Average order value by product category",
    "Revenue comparison between Q1 and Q2",
  ];

  const selectedConn = session?.connections.find(
    (c) => c.id === selectedConnectionId
  );

  // ─── Not connected yet ─────────────────────────────────
  if (!session) {
    return (
      <div className="max-w-xl mx-auto mt-16 space-y-6">
        <h1 className="text-2xl font-bold text-center">Connect to Your Data</h1>
        <p className="text-slate-400 text-center text-sm">
          {connectLoading
            ? "Loading your database connections..."
            : "Click below to load your database connections."}
        </p>

        <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-4">
          <button
            onClick={handleConnect}
            disabled={connectLoading}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {connectLoading ? "Connecting..." : "🔗 Connect"}
          </button>
          {connectError && (
            <p className="text-sm text-red-400">❌ {connectError}</p>
          )}
        </div>
      </div>
    );
  }

  // ─── Connected — show query interface ──────────────────
  return (
    <div className="max-w-6xl space-y-6">
      {/* Session header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Query & Analyze</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-400">
            <span className="text-green-400 font-medium">{session.user_name}</span>
            {" · "}
            {session.organization_name}
          </span>
          <button
            onClick={handleDisconnect}
            className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-xs"
          >
            Disconnect
          </button>
        </div>
      </div>

      {/* Connection selector */}
      <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-4">
        <div className="flex items-center gap-4">
          <label className="text-sm text-slate-400 whitespace-nowrap">
            Database Connection
          </label>
          {session.connections.length === 0 ? (
            <p className="text-sm text-yellow-400">
              No connections found. Go to Connections page to add one.
            </p>
          ) : (
            <select
              value={selectedConnectionId}
              onChange={(e) => setSelectedConnectionId(e.target.value)}
              className="flex-1 bg-[#334155] border border-slate-600 rounded-lg px-3 py-2 text-sm"
            >
              <option value={AUTO}>Auto-select (let SQLMind route)</option>
              {session.connections.map((conn) => (
                <option key={conn.id} value={conn.id}>
                  {conn.name} ({conn.db_type} — {conn.host}/{conn.database_name})
                </option>
              ))}
            </select>
          )}
          {selectedConn && (
            <span className="inline-flex items-center gap-1.5 text-xs text-green-400">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Connected
            </span>
          )}
        </div>
      </div>

      {/* Query input */}
      <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-4">
        <label className="block text-sm text-slate-400">
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
          disabled={loading || !selectedConnectionId}
          className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "🔍 Run Query"}
        </button>

        {error && <p className="text-sm text-red-400">❌ {error}</p>}
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

          {/* View toggle */}
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
          </div>

          {/* Data display */}
          {viewMode === "table" ? (
            <DataTable columns={result.columns} data={result.data} />
          ) : (
            <ChartView columns={result.columns} data={result.data} />
          )}

          {/* Download Panel */}
          <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-slate-400 mb-3">
              📥 Download Results
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { format: "csv", label: "CSV", desc: "Comma-separated values", icon: "📄" },
                { format: "excel", label: "Excel", desc: "XLSX spreadsheet", icon: "📊" },
                { format: "json", label: "JSON", desc: "Structured data", icon: "🔗" },
                { format: "pdf", label: "PDF", desc: "Formatted report", icon: "📑" },
              ].map(({ format, label, desc, icon }) => (
                <button
                  key={format}
                  onClick={() => handleDownload(format)}
                  disabled={downloading !== null}
                  className="flex flex-col items-center gap-1.5 p-4 bg-[#334155] hover:bg-slate-600 border border-slate-600 hover:border-blue-500 rounded-xl transition-colors disabled:opacity-50"
                >
                  <span className="text-2xl">{icon}</span>
                  <span className="font-medium text-sm">
                    {downloading === format ? "Downloading..." : label}
                  </span>
                  <span className="text-xs text-slate-400">{desc}</span>
                </button>
              ))}
            </div>
          </div>

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
