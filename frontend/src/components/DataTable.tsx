"use client";

export default function DataTable({
  columns,
  data,
}: {
  columns: string[];
  data: Record<string, any>[];
}) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 text-center text-slate-500">
        No data to display.
      </div>
    );
  }

  return (
    <div className="bg-[#1e293b] border border-slate-700 rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[#0f172a]">
              {columns.map((col) => (
                <th
                  key={col}
                  className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-700"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {data.map((row, idx) => (
              <tr
                key={idx}
                className="hover:bg-[#334155]/50 transition-colors"
              >
                {columns.map((col) => (
                  <td
                    key={col}
                    className="px-4 py-2.5 text-slate-300 whitespace-nowrap"
                  >
                    {formatValue(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function formatValue(value: any): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    return value.toLocaleString();
  }
  return String(value);
}
