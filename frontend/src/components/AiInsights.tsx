"use client";

export default function AiInsights({
  summary,
  insights,
}: {
  summary?: string;
  insights?: string[];
}) {
  if (!summary && (!insights || insights.length === 0)) return null;

  return (
    <div className="bg-gradient-to-r from-[#1e293b] to-[#1a2332] border border-blue-800/30 rounded-xl p-6 space-y-3">
      <h3 className="text-sm font-semibold text-blue-400 flex items-center gap-2">
        🤖 AI Analysis
      </h3>

      {summary && (
        <div>
          <p className="text-xs text-slate-400 mb-1 font-medium">Summary</p>
          <p className="text-sm text-slate-200">{summary}</p>
        </div>
      )}

      {insights && insights.length > 0 && (
        <div>
          <p className="text-xs text-slate-400 mb-1 font-medium">Insights</p>
          <ul className="space-y-1">
            {insights.map((insight, idx) => (
              <li key={idx} className="text-sm text-slate-300 flex gap-2">
                <span className="text-blue-400 mt-0.5">•</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
