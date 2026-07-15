export async function calculateCosting(payload) {
  const response = await fetch("/api/calc/costing", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
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
  const response = await fetch(`/api/customers?${params}`);
  if (!response.ok) throw new Error("Failed to load customers");
  return response.json();
}

export async function createCustomer(data) {
  const response = await fetch("/api/customers", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to create customer");
  return response.json();
}

export async function listCostings() {
  const response = await fetch("/api/costings?limit=100");
  if (!response.ok) throw new Error("Failed to load costings");
  return response.json();
}

export async function getCosting(id) {
  const response = await fetch(`/api/costings/${id}`);
  if (!response.ok) throw new Error("Costing not found");
  return response.json();
}

export async function saveCosting(data, costingId = null) {
  const url = costingId ? `/api/costings/${costingId}` : "/api/costings";
  const response = await fetch(url, {
    method: costingId ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to save costing");
  return response.json();
}

export async function searchStock(q = "", limit = 30) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (q) params.set("item_type", q);
  const response = await fetch(`/api/stock?${params}`);
  if (!response.ok) throw new Error("Failed to load stock");
  return response.json();
}
