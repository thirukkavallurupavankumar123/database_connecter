"use client";

import { useState, useEffect } from "react";
import { getQueryHistory } from "@/lib/api";
import AuthGuard from "@/components/AuthGuard";

export default function HistoryPage() {
  return (
    <AuthGuard>
      <HistoryContent />
    </AuthGuard>
  );
}

function HistoryContent() {
  const [userId, setUserId] = useState("");
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Auto-fill user ID and auto-load history
  useEffect(() => {
    const saved = localStorage.getItem("argo_user_id");
    if (saved) {
      setUserId(saved);
      getQueryHistory(saved).then((res) => setHistory(res.data)).catch(() => {});
    }
  }, []);

  const handleLoad = async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const res = await getQueryHistory(userId);
      setHistory(res.data);
    } catch {
      setHistory([]);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-4xl space-y-6">
      <h1 className="text-2xl font-bold">Query History</h1>

      <div className="flex gap-2">
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter your user ID"
          className="flex-1 bg-[#334155] border border-slate-600 rounded-lg px-3 py-2 text-sm"
        />
        <button
          onClick={handleLoad}
          disabled={loading}
          className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium disabled:opacity-50"
        >
          {loading ? "Loading..." : "Load History"}
        </button>
      </div>

      {history.length === 0 && !loading && (
        <p className="text-slate-500 text-sm">No query history found.</p>
      )}

      <div className="space-y-3">
        {history.map((item: any) => (
          <div
            key={item.id}
            className="bg-[#1e293b] border border-slate-700 rounded-xl p-4"
          >
            <div className="flex items-start justify-between mb-2">
              <p className="font-medium text-sm">
                {item.natural_language_query}
              </p>
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  item.status === "success"
                    ? "bg-green-600/20 text-green-400"
                    : item.status === "error"
                    ? "bg-red-600/20 text-red-400"
                    : "bg-yellow-600/20 text-yellow-400"
                }`}
              >
                {item.status}
              </span>
            </div>

            {item.generated_sql && (
              <pre className="bg-[#0f172a] rounded-lg p-2 text-xs text-green-400 mb-2 overflow-x-auto">
                {item.generated_sql}
              </pre>
            )}

            {item.error_message && (
              <p className="text-xs text-red-400">{item.error_message}</p>
            )}

            <div className="flex gap-4 text-xs text-slate-500 mt-2">
              {item.row_count && <span>{item.row_count} rows</span>}
              <span>
                {new Date(item.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
