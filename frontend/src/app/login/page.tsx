"use client";

import { useState, useEffect } from "react";
import { login, signup, listOrganizations } from "@/lib/api";

type Org = { id: string; name: string };

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [orgMode, setOrgMode] = useState<"new" | "existing">("new");
  const [orgName, setOrgName] = useState("");
  const [orgPassword, setOrgPassword] = useState("");
  const [selectedOrgId, setSelectedOrgId] = useState("");
  const [orgs, setOrgs] = useState<Org[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if already logged in
  useEffect(() => {
    const userId = localStorage.getItem("argo_user_id");
    if (userId) {
      window.location.href = "/";
    }
  }, []);

  // Load organizations for "join existing" option
  useEffect(() => {
    if (mode === "signup") {
      listOrganizations()
        .then((res) => {
          setOrgs(res.data);
          if (res.data.length > 0) setSelectedOrgId(res.data[0].id);
        })
        .catch(() => {});
    }
  }, [mode]);

  const handleLogin = async () => {
    if (!email || !password) {
      setError("Enter email and password.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await login({ email, password });
      saveSession(res.data);
      window.location.href = "/";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    }
    setLoading(false);
  };

  const handleSignup = async () => {
    if (!email || !password || !name) {
      setError("Fill in all fields.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    if (orgMode === "new" && !orgName.trim()) {
      setError("Enter an organization name.");
      return;
    }
    if (orgMode === "existing" && !selectedOrgId) {
      setError("Select an organization.");
      return;
    }
    if (!orgPassword || orgPassword.length < 4) {
      setError("Organization password is required (min 4 characters).");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await signup({
        email,
        name,
        password,
        organization_name: orgMode === "new" ? orgName.trim() : undefined,
        organization_password: orgPassword,
        organization_id: orgMode === "existing" ? selectedOrgId : undefined,
      });
      saveSession(res.data);
      window.location.href = "/";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Signup failed");
    }
    setLoading(false);
  };

  const saveSession = (data: any) => {
    localStorage.setItem("argo_user_id", data.user_id);
    localStorage.setItem("argo_user_name", data.user_name);
    localStorage.setItem("argo_user_email", data.email);
    localStorage.setItem("argo_org_id", data.organization_id);
    localStorage.setItem("argo_org_name", data.organization_name);
  };

  const handleSubmit = () => {
    if (mode === "login") handleLogin();
    else handleSignup();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f172a]">
      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-blue-400">🚀 SQLMind</h1>
          <p className="text-sm text-slate-400 mt-2">
            Enterprise GenAI Database Analytics Platform
          </p>
        </div>

        {/* Tab toggle */}
        <div className="flex bg-[#1e293b] rounded-lg p-1">
          <button
            onClick={() => { setMode("login"); setError(null); }}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === "login"
                ? "bg-blue-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Login
          </button>
          <button
            onClick={() => { setMode("signup"); setError(null); }}
            className={`flex-1 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === "signup"
                ? "bg-blue-600 text-white"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Form */}
        <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-4">
          {mode === "signup" && (
            <div>
              <label className="block text-sm text-slate-400 mb-1">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Pavan Kumar"
                className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
              />
            </div>
          )}

          <div>
            <label className="block text-sm text-slate-400 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSubmit();
              }}
            />
          </div>

          {/* Signup: Organization */}
          {mode === "signup" && (
            <div className="space-y-3 pt-2 border-t border-slate-700">
              <p className="text-sm text-slate-400 pt-2">Organization</p>

              <div className="flex gap-2">
                <button
                  onClick={() => setOrgMode("new")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium ${
                    orgMode === "new"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-700 text-slate-300"
                  }`}
                >
                  Create New
                </button>
                {orgs.length > 0 && (
                  <button
                    onClick={() => setOrgMode("existing")}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium ${
                      orgMode === "existing"
                        ? "bg-blue-600 text-white"
                        : "bg-slate-700 text-slate-300"
                    }`}
                  >
                    Join Existing
                  </button>
                )}
              </div>

              {orgMode === "new" ? (
                <input
                  type="text"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  placeholder="Organization name"
                  className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
                />
              ) : (
                <select
                  value={selectedOrgId}
                  onChange={(e) => setSelectedOrgId(e.target.value)}
                  className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
                >
                  {orgs.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name}
                    </option>
                  ))}
                </select>
              )}

              <div>
                <label className="block text-xs text-slate-500 mb-1">
                  {orgMode === "new" ? "Set Organization Password" : "Organization Password"}
                </label>
                <input
                  type="password"
                  value={orgPassword}
                  onChange={(e) => setOrgPassword(e.target.value)}
                  placeholder={orgMode === "new" ? "Create a password for your org" : "Enter the org password to join"}
                  className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
                />
              </div>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {loading
              ? "Please wait..."
              : mode === "login"
              ? "Login"
              : "Create Account"}
          </button>

          {error && <p className="text-sm text-red-400 text-center">❌ {error}</p>}
        </div>

        <p className="text-xs text-center text-slate-500">
          {mode === "login"
            ? "Don't have an account? Click Sign Up above."
            : "Already have an account? Click Login above."}
        </p>
      </div>
    </div>
  );
}
