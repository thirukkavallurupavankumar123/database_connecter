"use client";

import AuthGuard from "@/components/AuthGuard";

export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  );
}

function DashboardContent() {
  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8">
        <h1 className="text-3xl font-bold mb-2">
          Enterprise GenAI Database Analytics
        </h1>
        <p className="text-blue-100 text-lg max-w-2xl">
          Connect your databases and analyze data using natural language.
          No SQL required — just ask questions and get insights instantly.
        </p>
      </div>

      {/* Quick start cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <QuickCard
          title="1. Connect Database"
          description="Add your PostgreSQL, MySQL, or SQL Server database with read-only credentials."
          href="/connections"
          icon="🔗"
        />
        <QuickCard
          title="2. Ask Questions"
          description='Type natural language queries like "Show total revenue in 2024" and get results.'
          href="/query"
          icon="💬"
        />
        <QuickCard
          title="3. Get Insights"
          description="View AI-generated summaries, charts, statistics, and download reports."
          href="/query"
          icon="📊"
        />
      </div>

      {/* Feature grid */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Platform Features</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            "Natural Language Queries",
            "Auto SQL Generation",
            "Multi-Database Support",
            "AI-Generated Insights",
            "Statistical Analysis",
            "Interactive Charts",
            "Downloadable Reports",
            "Secure Read-Only Access",
          ].map((f) => (
            <div
              key={f}
              className="bg-[#1e293b] border border-slate-700 rounded-xl p-4 text-sm text-slate-300"
            >
              ✅ {f}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function QuickCard({
  title,
  description,
  href,
  icon,
}: {
  title: string;
  description: string;
  href: string;
  icon: string;
}) {
  return (
    <a
      href={href}
      className="block bg-[#1e293b] border border-slate-700 rounded-xl p-6 hover:border-blue-500 transition-colors"
    >
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold mb-1">{title}</h3>
      <p className="text-sm text-slate-400">{description}</p>
    </a>
  );
}
