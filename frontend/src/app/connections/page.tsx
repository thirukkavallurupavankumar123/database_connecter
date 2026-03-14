"use client";

import { useState, useEffect } from "react";
import type { ChangeEvent } from "react";
import { testConnection, createConnection, listConnections, deleteConnection } from "@/lib/api";
import AuthGuard from "@/components/AuthGuard";

type ConnectionFormState = {
  name: string;
  label: string;
  tags: string;
  is_default: boolean;
  db_type: "postgresql" | "mysql" | "sqlserver";
  host: string;
  port: string;
  database_name: string;
  username: string;
  password: string;
  ssl_enabled: boolean;
};

type SavedConnection = {
  id: string;
  name: string;
  label?: string | null;
  is_default?: boolean;
  db_type: string;
  host: string;
  port?: string | null;
  database_name: string;
};

const DB_TYPES = [
  { value: "postgresql", label: "PostgreSQL" },
  { value: "mysql", label: "MySQL" },
  { value: "sqlserver", label: "SQL Server" },
];

export default function ConnectionsPage() {
  return (
    <AuthGuard>
      <ConnectionsContent />
    </AuthGuard>
  );
}

function ConnectionsContent() {
  const [form, setForm] = useState<ConnectionFormState>({
    name: "",
    label: "",
    tags: "",
    is_default: false,
    db_type: "postgresql",
    host: "",
    port: "",
    database_name: "",
    username: "",
    password: "",
    ssl_enabled: true,
  });

  const [orgId, setOrgId] = useState("");
  const [connections, setConnections] = useState<SavedConnection[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Auto-fill org ID from localStorage and auto-load connections
  useEffect(() => {
    const saved = localStorage.getItem("argo_org_id");
    if (saved) {
      setOrgId(saved);
      listConnections(saved).then((res) => setConnections(res.data)).catch(() => {});
    }
  }, []);

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleTest = async () => {
    setLoading(true);
    setStatus(null);
    try {
      await testConnection({
        db_type: form.db_type,
        host: form.host,
        port: form.port || undefined,
        database_name: form.database_name,
        username: form.username,
        password: form.password,
        ssl_enabled: form.ssl_enabled,
      });
      setStatus("✅ Connection successful!");
    } catch (err: any) {
      setStatus(`❌ ${err.response?.data?.detail || "Connection failed"}`);
    }
    setLoading(false);
  };

  const handleSave = async () => {
    if (!orgId) {
      setStatus("⚠️ Enter an Organization ID first.");
      return;
    }
    setLoading(true);
    setStatus(null);
    try {
      await createConnection({
        organization_id: orgId,
        user_id: localStorage.getItem("argo_user_id") || "",
        name: form.name,
        label: form.label || undefined,
        tags: form.tags || undefined,
        is_default: form.is_default,
        db_type: form.db_type,
        host: form.host,
        port: form.port || undefined,
        database_name: form.database_name,
        username: form.username,
        password: form.password,
        ssl_enabled: form.ssl_enabled,
      });
      setStatus("✅ Connection saved!");
      handleLoadConnections();
    } catch (err: any) {
      setStatus(`❌ ${err.response?.data?.detail || "Save failed"}`);
    }
    setLoading(false);
  };

  const handleLoadConnections = async () => {
    if (!orgId) return;
    try {
      const res = await listConnections(orgId);
      setConnections(res.data);
    } catch {
      setConnections([]);
    }
  };

  const handleDelete = async (connId: string) => {
    try {
      await deleteConnection(connId);
      handleLoadConnections();
    } catch (err: any) {
      setStatus(`❌ ${err.response?.data?.detail || "Delete failed"}`);
    }
  };

  return (
    <div className="max-w-4xl space-y-8">
      <h1 className="text-2xl font-bold">Database Connections</h1>

      {/* Org ID */}
      <div>
        <label className="block text-sm text-slate-400 mb-1">
          Organization ID
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            placeholder="Enter your organization ID"
            className="flex-1 bg-[#334155] border border-slate-600 rounded-lg px-3 py-2 text-sm"
          />
          <button
            onClick={handleLoadConnections}
            className="px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded-lg text-sm"
          >
            Load Connections
          </button>
        </div>
      </div>

      {/* Connection form */}
      <div className="bg-[#1e293b] border border-slate-700 rounded-xl p-6 space-y-4">
        <h2 className="text-lg font-semibold">Add New Connection</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="Connection Name" name="name" value={form.name} onChange={handleChange} placeholder="My Production DB" />

          <Field label="Label (for routing)" name="label" value={form.label} onChange={handleChange} placeholder="e.g. sales, support" />

          <Field label="Tags (comma-separated)" name="tags" value={form.tags} onChange={handleChange} placeholder="orders, customers, finance" />

          <div>
            <label className="block text-sm text-slate-400 mb-1">Database Type</label>
            <select
              name="db_type"
              value={form.db_type}
              onChange={handleChange}
              className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2 text-sm"
            >
              {DB_TYPES.map((db) => (
                <option key={db.value} value={db.value}>{db.label}</option>
              ))}
            </select>
          </div>

          <Field label="Host" name="host" value={form.host} onChange={handleChange} placeholder="db.example.com" />
          <Field label="Port" name="port" value={form.port} onChange={handleChange} placeholder="5432" />
          <Field label="Database Name" name="database_name" value={form.database_name} onChange={handleChange} placeholder="analytics_db" />
          <Field label="Username" name="username" value={form.username} onChange={handleChange} placeholder="readonly_user" />
          <Field label="Password" name="password" value={form.password} onChange={handleChange} placeholder="••••••••" type="password" />

          <div className="flex items-center gap-2 mt-6">
            <input
              type="checkbox"
              name="ssl_enabled"
              checked={form.ssl_enabled}
              onChange={handleChange}
              className="rounded"
            />
            <label className="text-sm text-slate-400">SSL Enabled</label>
          </div>

          <div className="flex items-center gap-2 mt-6">
            <input
              type="checkbox"
              name="is_default"
              checked={form.is_default}
              onChange={handleChange}
              className="rounded"
            />
            <label className="text-sm text-slate-400">Set as default for this org</label>
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button
            onClick={handleTest}
            disabled={loading}
            className="px-5 py-2 bg-yellow-600 hover:bg-yellow-500 text-white rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {loading ? "Testing..." : "Test Connection"}
          </button>
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {loading ? "Saving..." : "Save Connection"}
          </button>
        </div>

        {status && (
          <p className="text-sm mt-2">{status}</p>
        )}
      </div>

      {/* Saved connections */}
      {connections.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Saved Connections</h2>
          {connections.map((conn) => (
            <div
              key={conn.id}
              className="bg-[#1e293b] border border-slate-700 rounded-xl p-4 flex items-center justify-between"
            >
              <div>
                <p className="font-medium">{conn.name}</p>
                <p className="text-sm text-slate-400">
                  {conn.db_type} — {conn.host}:{conn.port}/{conn.database_name}
                </p>
                {conn.label && (
                  <p className="text-xs text-slate-400">Label: {conn.label}</p>
                )}
                {conn.is_default && (
                  <p className="text-xs text-green-400">Default connection</p>
                )}
              </div>
              <button
                onClick={() => handleDelete(conn.id)}
                className="px-3 py-1 bg-red-600/20 text-red-400 hover:bg-red-600/40 rounded-lg text-sm"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Field({
  label,
  name,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  name: string;
  value: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  type?: string;
}) {
  return (
    <div>
      <label className="block text-sm text-slate-400 mb-1">{label}</label>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full bg-[#334155] border border-slate-600 rounded-lg px-3 py-2 text-sm"
      />
    </div>
  );
}
