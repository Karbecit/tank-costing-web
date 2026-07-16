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

export async function listAudit() {
  const response = await apiFetch("/api/admin/audit?limit=100");
  if (!response.ok) throw new Error("Failed to load audit log");
  return response.json();
}

export async function resetUserPassword(id, password) {
  const response = await apiFetch(`/api/admin/users/${id}/reset-password`, {
    method: "POST",
    body: JSON.stringify({ password }),
  });
  if (!response.ok) throw new Error("Failed to reset password");
}

export async function sendUserInvite(id, password) {
  const response = await apiFetch(`/api/admin/users/${id}/send-invite`, {
    method: "POST",
    body: JSON.stringify({ password }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Failed to send invite");
  }
}

export async function getSmtpSettings() {
  const response = await apiFetch("/api/admin/settings/smtp");
  if (!response.ok) throw new Error("Failed to load SMTP settings");
  return response.json();
}

export async function saveSmtpSettings(data) {
  const response = await apiFetch("/api/admin/settings/smtp", {
    method: "PUT",
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to save SMTP settings");
  return response.json();
}

export async function testSmtp(to) {
  const response = await apiFetch("/api/admin/settings/smtp/test", {
    method: "POST",
    body: JSON.stringify({ to }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "SMTP test failed");
  }
}

export async function importJma(file) {
  const form = new FormData();
  form.append("file", file);
  const response = await apiFetch("/api/jma/import", { method: "POST", body: form });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Failed to import .jma file");
  }
  return response.json();
}

export async function downloadQuotePdf(costingId, filename = "quote.pdf") {
  const response = await apiFetch(`/api/costings/${costingId}/quote.pdf`);
  if (!response.ok) throw new Error("Failed to generate PDF");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export async function downloadJmaExport(costingId, filename = "costing.jma") {
  const response = await apiFetch(`/api/costings/${costingId}/export.jma`);
  if (!response.ok) throw new Error("Failed to export .jma");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export async function emailQuote(costingId, to, message) {
  const response = await apiFetch(`/api/costings/${costingId}/email-quote`, {
    method: "POST",
    body: JSON.stringify({ to: to || null, message: message || null }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Failed to send quote email");
  }
}

export async function calcDipChart(payload, incrementMm = 10) {
  const response = await apiFetch("/api/calc/dip-chart", {
    method: "POST",
    body: JSON.stringify({ payload, increment_mm: incrementMm }),
  });
  if (!response.ok) throw new Error("Dip chart calculation failed");
  return response.json();
}
