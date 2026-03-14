import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// --- Auth ---
export const signup = (data: {
  email: string;
  name: string;
  password: string;
  organization_name?: string;
  organization_password?: string;
  organization_id?: string;
}) => api.post("/api/auth/signup", data);

export const login = (data: { email: string; password: string }) =>
  api.post("/api/auth/login", data);

export const getMe = (userId: string) =>
  api.get(`/api/auth/me/${userId}`);

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
  user_id: string;
  name: string;
  label?: string;
  tags?: string;
  is_default?: boolean;
  db_type: string;
  host: string;
  port?: string;
  database_name: string;
  username: string;
  password: string;
  ssl_enabled?: boolean;
}) => api.post("/api/connections/", data);

export const listConnections = (orgId: string) => {
  const userId = localStorage.getItem("argo_user_id") || "";
  return api.get(`/api/connections/org/${orgId}?user_id=${userId}`);
};

export const getSchema = (connId: string) => {
  const userId = localStorage.getItem("argo_user_id") || "";
  return api.get(`/api/connections/${connId}/schema?user_id=${userId}`);
};

export const deleteConnection = (connId: string) => {
  const userId = localStorage.getItem("argo_user_id") || "";
  return api.delete(`/api/connections/${connId}?user_id=${userId}`);
};

// --- Queries ---
export const connectSession = (userId: string) =>
  api.post("/api/query/connect", { user_id: userId });

export const runQuery = (data: {
  connection_id?: string | null;
  user_id: string;
  natural_language_query: string;
}) => api.post("/api/query/", data);

export const downloadReport = (
  data: {
    connection_id?: string | null;
    user_id: string;
    natural_language_query: string;
    format: string;
  },
) =>
  api.post("/api/query/download", data, { responseType: "blob" });

export const getQueryHistory = (userId: string) =>
  api.get(`/api/query/history/${userId}`);

export default api;
