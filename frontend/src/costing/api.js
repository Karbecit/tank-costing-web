import { apiFetch } from "../auth.js";

export async function calculateCosting(payload) {
  const response = await apiFetch("/api/calc/costing", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Calculation failed (${response.status})`);
  }
  return response.json();
}

export async function fetchHealth() {
  const response = await fetch("/api/health");
  if (!response.ok) throw new Error("API unavailable");
  return response.json();
}

export async function listCustomers(q = "") {
  const params = new URLSearchParams({ limit: "200" });
  if (q) params.set("q", q);
  const response = await apiFetch(`/api/customers?${params}`);
  if (!response.ok) throw new Error("Failed to load customers");
  return response.json();
}

export async function createCustomer(data) {
  const response = await apiFetch("/api/customers", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to create customer");
  return response.json();
}

export async function getCustomer(id) {
  const response = await apiFetch(`/api/customers/${id}`);
  if (!response.ok) throw new Error("Customer not found");
  return response.json();
}

export async function updateCustomer(id, data) {
  const response = await apiFetch(`/api/customers/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to update customer");
  return response.json();
}

export async function deleteCustomer(id) {
  const response = await apiFetch(`/api/customers/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete customer");
}

export async function listCostings() {
  const response = await apiFetch("/api/costings?limit=100");
  if (!response.ok) throw new Error("Failed to load costings");
  return response.json();
}

export async function getCosting(id) {
  const response = await apiFetch(`/api/costings/${id}`);
  if (!response.ok) throw new Error("Costing not found");
  return response.json();
}

export async function saveCosting(data, costingId = null) {
  const url = costingId ? `/api/costings/${costingId}` : "/api/costings";
  const response = await apiFetch(url, {
    method: costingId ? "PUT" : "POST",
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to save costing");
  return response.json();
}

export async function searchStock(q = "", limit = 30) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (q) params.set("item_type", q);
  const response = await apiFetch(`/api/stock?${params}`);
  if (!response.ok) throw new Error("Failed to load stock");
  return response.json();
}

export async function listUsers() {
  const response = await apiFetch("/api/admin/users");
  if (!response.ok) throw new Error("Failed to load users");
  return response.json();
}

export async function createUser(data) {
  const response = await apiFetch("/api/admin/users", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Failed to create user");
  }
  return response.json();
}

export async function updateUser(id, data) {
  const response = await apiFetch(`/api/admin/users/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to update user");
  return response.json();
}

export async function resetUserPassword(id, password) {
  const response = await apiFetch(`/api/admin/users/${id}/reset-password`, {
    method: "POST",
    body: JSON.stringify({ password }),
  });
  if (!response.ok) throw new Error("Failed to reset password");
}
