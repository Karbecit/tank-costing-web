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
