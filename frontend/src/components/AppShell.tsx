"use client";

import { useEffect, useState } from "react";
import type { ReactNode } from "react";

export default function AppShell({ children }: { children: ReactNode }) {
  const [isLoginPage, setIsLoginPage] = useState(false);
  const [userName, setUserName] = useState<string | null>(null);
  const [orgName, setOrgName] = useState<string | null>(null);

  useEffect(() => {
    setIsLoginPage(window.location.pathname === "/login");
    setUserName(localStorage.getItem("argo_user_name"));
    setOrgName(localStorage.getItem("argo_org_name"));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("argo_user_id");
    localStorage.removeItem("argo_user_name");
    localStorage.removeItem("argo_user_email");
    localStorage.removeItem("argo_org_id");
    localStorage.removeItem("argo_org_name");
    window.location.href = "/login";
  };

  // Login page — no sidebar
  if (isLoginPage) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-700 bg-[#1e293b] p-4 flex flex-col">
        <h1 className="text-xl font-bold text-blue-400 mb-6">
          🚀 ARGO Analytics
        </h1>

        <div className="flex flex-col gap-1 flex-1">
          <NavLink href="/">Dashboard</NavLink>
          <NavLink href="/connections">Database Connections</NavLink>
          <NavLink href="/query">Query & Analyze</NavLink>
          <NavLink href="/history">Query History</NavLink>
        </div>

        {/* User info + logout */}
        {userName && (
          <div className="border-t border-slate-700 pt-3 mt-3">
            <p className="text-sm font-medium text-slate-200 truncate">{userName}</p>
            {orgName && (
              <p className="text-xs text-slate-400 truncate">{orgName}</p>
            )}
            <button
              onClick={handleLogout}
              className="mt-2 w-full px-3 py-1.5 text-xs text-red-400 hover:text-red-300 hover:bg-slate-700 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 overflow-auto">{children}</main>
    </div>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
    >
      {children}
    </a>
  );
}
