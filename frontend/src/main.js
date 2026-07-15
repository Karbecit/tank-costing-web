async function api(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} failed: ${response.status}`);
  }
  return response.json();
}

function table(headers, rows) {
  if (!rows.length) {
    return "<p>No records found.</p>";
  }
  const head = headers.map((h) => `<th>${h}</th>`).join("");
  const body = rows
    .map((row) => {
      const cells = headers.map((h) => `<td>${row[h] ?? ""}</td>`).join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");
  return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

async function init() {
  const health = await api("/api/health");
  const stats = await api("/api/stats");
  const rates = await api("/api/rates?limit=8");
  const stock = await api("/api/stock?limit=8");
  const clients = await api("/api/clients?limit=8");
  const quotes = await api("/api/quotes?limit=8");

  document.getElementById("stats").innerHTML = `
    <strong>${health.app}</strong> v${health.version} — API healthy<br/>
    Rates: ${stats.rates} · Stock: ${stats.stock} · Clients: ${stats.clients} · Quotes: ${stats.quote_num}
  `;

  document.getElementById("rates").innerHTML = table(
    ["grade", "thickness", "width", "price_kg"],
    rates
  );
  document.getElementById("stock").innerHTML = table(
    ["type", "description", "cost", "manufacturer"],
    stock
  );
  document.getElementById("clients").innerHTML = table(
    ["company_name", "town", "phone_number"],
    clients
  );
  document.getElementById("quotes").innerHTML = table(
    ["number_quote", "company_name", "job_description", "status_name"],
    quotes
  );
}

init().catch((error) => {
  document.getElementById("stats").textContent = `Failed to load API: ${error.message}`;
});
