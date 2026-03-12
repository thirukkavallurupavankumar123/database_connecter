"use client";

import { useState, useEffect } from "react";
import {
  createOrganization,
  listOrganizations,
  createUser,
} from "@/lib/api";

type Org = { id: string; name: string };
type UserInfo = { id: string; name: string; email: string; organization_id: string };

export default function SetupPage() {
  const [step, setStep] = useState<"org" | "user" | "done">("org");

  // Org state
  const [orgs, setOrgs] = useState<Org[]>([]);
  const [selectedOrgId, setSelectedOrgId] = useState("");
  const [newOrgName, setNewOrgName] = useState("");
  const [orgMode, setOrgMode] = useState<"select" | "create">("create");
  const [orgLoading, setOrgLoading] = useState(false);
  const [orgError, setOrgError] = useState<string | null>(null);

  // User state
  const [userName, setUserName] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [userLoading, setUserLoading] = useState(false);
  const [userError, setUserError] = useState<string | null>(null);

  // Result
  const [createdOrg, setCreatedOrg] = useState<Org | null>(null);
  const [createdUser, setCreatedUser] = useState<UserInfo | null>(null);

  useEffect(() => {
    loadOrgs();
  }, []);

  const loadOrgs = async () => {
    try {
      const res = await listOrganizations();
      setOrgs(res.data);
      if (res.data.length > 0) {
        setOrgMode("select");
        setSelectedOrgId(res.data[0].id);
      }
    } catch {
      // ignore — no orgs yet
    }
  };

  const handleOrgSubmit = async () => {
    setOrgLoading(true);
    setOrgError(null);
    try {
      if (orgMode === "create") {
        if (!newOrgName.trim()) {
          setOrgError("Enter an organization name.");
          setOrgLoading(false);
          return;
        }
        const res = await createOrganization(newOrgName.trim());
        setCreatedOrg(res.data);
        localStorage.setItem("argo_org_id", res.data.id);
        localStorage.setItem("argo_org_name", res.data.name);
      } else {
        if (!selectedOrgId) {
          setOrgError("Select an organization.");
          setOrgLoading(false);
          return;
        }
        const org = orgs.find((o) => o.id === selectedOrgId)!;
        setCreatedOrg(org);
        localStorage.setItem("argo_org_id", org.id);
        localStorage.setItem("argo_org_name", org.name);
      }
      setStep("user");
    } catch (err: any) {
      setOrgError(err.response?.data?.detail || "Failed to create organization");
    }
    setOrgLoading(false);
  };

  const handleUserSubmit = async () => {
    if (!userName.trim() || !userEmail.trim()) {
      setUserError("Fill in both name and email.");
      return;
    }
    setUserLoading(true);
    setUserError(null);
    try {
      const orgId = createdOrg!.id;
      const res = await createUser(orgId, userEmail.trim(), userName.trim());
      setCreatedUser(res.data);
      localStorage.setItem("argo_user_id", res.data.id);
      localStorage.setItem("argo_user_name", res.data.name);
      localStorage.setItem("argo_user_email", res.data.email);
      setStep("done");
    } catch (err: any) {
      setUserError(err.response?.data?.detail || "Failed to create user");
    }
    setUserLoading(false);
  };

  // Step indicator
  const steps = [
    { key: "org", label: "1. Organization" },
    { key: "user", label: "2. Your Profile" },
    { key: "done", label: "3. Ready!" },
  ];

  return (
    <div className="max-w-xl mx-auto mt-8 space-y-6">
      <h1 className="text-2xl font-bold text-center">Get Started with SQLMind</h1>
      <p className="text-slate-400 text-center text-sm">
        Set up your organization and user profile in 2 steps.
      </p>

      {/* Step indicator */}
      <div className="flex items-center justify-center gap-2 mb-6">
        {steps.map((s, i) => (
          <div key={s.key} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                step === s.key
                  ? "bg-blue-600 text-white"
                  : steps.findIndex((x) => x.key === step) > i
                  ? "bg-green-600 text-white"
                  : "bg-slate-700 text-slate-400"
              }`}
            >
              {steps.findIndex((x) => x.key === step) > i ? "✓" : i + 1}
            </div>
            <span
              className={`text-sm ${
                step === s.key ? "text-white font-medium" : "text-slate-500"
              }`}
            >
              {s.label}
            </span>
            {i < steps.length - 1 && (
              <div className="w-8 h-px bg-slate-600 mx-1" />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Organization */}
      {step === "org" && (
        <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold">Organization</h2>

          {orgs.length > 0 && (
            <div className="flex gap-2 mb-2">
              <button
                onClick={() => setOrgMode("select")}
                className={`px-3 py-1.5 rounded-lg text-sm ${
                  orgMode === "select"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-700 text-slate-300"
                }`}
              >
                Join Existing
              </button>
              <button
                onClick={() => setOrgMode("create")}
                className={`px-3 py-1.5 rounded-lg text-sm ${
                  orgMode === "create"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-700 text-slate-300"
                }`}
              >
                Create New
              </button>
            </div>
          )}

          {orgMode === "select" && orgs.length > 0 ? (
            <div>
              <label className="block text-sm text-slate-400 mb-1">
                Select Organization
              </label>
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
            </div>
          ) : (
            <div>
              <label className="block text-sm text-slate-400 mb-1">
                Organization Name
              </label>
              <input
                type="text"
                value={newOrgName}
                onChange={(e) => setNewOrgName(e.target.value)}
                placeholder="e.g. My Company"
                className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleOrgSubmit();
                }}
              />
            </div>
          )}

          <button
            onClick={handleOrgSubmit}
            disabled={orgLoading}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {orgLoading ? "Setting up..." : "Next →"}
          </button>

          {orgError && <p className="text-sm text-red-400">❌ {orgError}</p>}
        </div>
      )}

      {/* Step 2: User Profile */}
      {step === "user" && (
        <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold">Your Profile</h2>
          <p className="text-sm text-slate-400">
            Organization: <span className="text-blue-400">{createdOrg?.name}</span>
          </p>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Full Name</label>
            <input
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="e.g. Pavan Kumar"
              className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Email</label>
            <input
              type="email"
              value={userEmail}
              onChange={(e) => setUserEmail(e.target.value)}
              placeholder="e.g. pavan@company.com"
              className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2.5 text-sm"
              onKeyDown={(e) => {
                if (e.key === "Enter") handleUserSubmit();
              }}
            />
          </div>

          <button
            onClick={handleUserSubmit}
            disabled={userLoading}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium disabled:opacity-50"
          >
            {userLoading ? "Creating..." : "Create Account →"}
          </button>

          {userError && <p className="text-sm text-red-400">❌ {userError}</p>}
        </div>
      )}

      {/* Step 3: Done */}
      {step === "done" && createdUser && createdOrg && (
        <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-5">
          <div className="text-center">
            <span className="text-4xl">🎉</span>
            <h2 className="text-lg font-semibold mt-2">You're all set!</h2>
            <p className="text-sm text-slate-400 mt-1">
              Your account has been created. These IDs are saved automatically.
            </p>
          </div>

          <div className="bg-[#0f172a] rounded-lg p-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-400">Organization</span>
              <span className="text-blue-400 font-medium">{createdOrg.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Name</span>
              <span className="text-white">{createdUser.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Email</span>
              <span className="text-white">{createdUser.email}</span>
            </div>
            <div className="border-t border-slate-700 my-2" />
            <div className="flex justify-between items-center">
              <span className="text-slate-400">User ID</span>
              <code className="text-green-400 text-xs bg-slate-800 px-2 py-1 rounded">
                {createdUser.id}
              </code>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Org ID</span>
              <code className="text-green-400 text-xs bg-slate-800 px-2 py-1 rounded">
                {createdOrg.id}
              </code>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <a
              href="/connections"
              className="flex flex-col items-center gap-1 p-4 bg-[#334155] hover:bg-slate-600 border border-slate-600 hover:border-blue-500 rounded-xl transition-colors text-center"
            >
              <span className="text-2xl">🔗</span>
              <span className="font-medium text-sm">Add Database</span>
              <span className="text-xs text-slate-400">Connect your DB</span>
            </a>
            <a
              href="/query"
              className="flex flex-col items-center gap-1 p-4 bg-[#334155] hover:bg-slate-600 border border-slate-600 hover:border-blue-500 rounded-xl transition-colors text-center"
            >
              <span className="text-2xl">🔍</span>
              <span className="font-medium text-sm">Start Querying</span>
              <span className="text-xs text-slate-400">Ask your data</span>
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
