import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "ARGO Analytics — Enterprise GenAI Database Platform",
  description:
    "AI-powered enterprise analytics platform. Connect databases, ask questions in natural language, get insights.",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0f172a] text-slate-100 antialiased">
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="w-64 border-r border-slate-700 bg-[#1e293b] p-4 flex flex-col gap-2">
            <h1 className="text-xl font-bold text-blue-400 mb-6">
              🚀 ARGO Analytics
            </h1>
            <NavLink href="/">Dashboard</NavLink>
            <NavLink href="/connections">Database Connections</NavLink>
            <NavLink href="/query">Query & Analyze</NavLink>
            <NavLink href="/history">Query History</NavLink>
          </aside>

          {/* Main content */}
          <main className="flex-1 p-6 overflow-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}

function NavLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
    >
      {children}
    </a>
  );
}
