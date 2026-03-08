import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// --- Organizations ---
export const createOrganization = (name: string) =>
  api.post("/api/organizations/", { name });

export const listOrganizations = () => api.get("/api/organizations/");

export const createUser = (orgId: string, email: string, name: string) =>
  api.post(`/api/organizations/${orgId}/users`, {
    email,
    name,
    organization_id: orgId,
  });

// --- Connections ---
export const testConnection = (data: {
  db_type: string;
  host: string;
  port?: string;
  database_name: string;
  username: string;
  password: string;
  ssl_enabled?: boolean;
}) => api.post("/api/connections/test", data);

export const createConnection = (data: {
  organization_id: string;
  name: string;
  db_type: string;
  host: string;
  port?: string;
  database_name: string;
  username: string;
  password: string;
  ssl_enabled?: boolean;
}) => api.post("/api/connections/", data);

export const listConnections = (orgId: string) =>
  api.get(`/api/connections/org/${orgId}`);

export const getSchema = (connId: string) =>
  api.get(`/api/connections/${connId}/schema`);

export const deleteConnection = (connId: string) =>
  api.delete(`/api/connections/${connId}`);

// --- Queries ---
export const runQuery = (data: {
  connection_id: string;
  user_id: string;
  natural_language_query: string;
}) => api.post("/api/query/", data);

export const downloadReport = (
  data: {
    connection_id: string;
    user_id: string;
    natural_language_query: string;
    format: string;
  },
) =>
  api.post("/api/query/download", data, { responseType: "blob" });

export const getQueryHistory = (userId: string) =>
  api.get(`/api/query/history/${userId}`);

export default api;
