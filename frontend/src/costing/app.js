import {
  calculateCosting,
  createCustomer,
  fetchHealth,
  getCosting,
  listCostings,
  listCustomers,
  saveCosting,
  searchStock,
} from "./api.js";
import {
  NUM_CONES,
  NUM_STRAKES,
  defaultCosting,
  parseCosting,
  serializeCosting,
} from "./state.js";

const VOLUME_TREAT_LABELS = [
  "+ Volume, + Height",
  "- Volume, + Height",
  "No volume, + Height",
  "+ Volume, - Height",
  "- Volume, - Height",
  "No volume, - Height",
  "+ Volume, no height",
  "- Volume, no height",
  "No volume, no height",
];

const CONE_TYPE_OPTIONS = [
  { value: "none", label: "None" },
  { value: "conic", label: "Conical" },
  { value: "offset", label: "Offset" },
  { value: "slope", label: "Slope / floor" },
];

let state = defaultCosting();
let activeTab = "summary";
let statusMessage = "";
let customers = [];
let savedCostings = [];
let stockItems = [];
let stockFilter = "";

function syncComponentsPrice() {
  if (!state.selected_components?.length) return;
  state.summary.components_price = state.selected_components.reduce(
    (sum, c) => sum + (Number(c.cost) || 0),
    0
  );
}

function payloadForSave() {
  const { results, ...rest } = state;
  return rest;
}

function fmt(n, digits = 2) {
  if (n == null || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString(undefined, { maximumFractionDigits: digits });
}

function money(n) {
  return `$${fmt(n, 2)}`;
}

function coneType(cone) {
  if (cone.slope_select) return "slope";
  if (cone.offset_select) return "offset";
  if (cone.conic_select) return "conic";
  return "none";
}

function setConeType(cone, type) {
  cone.conic_select = type === "conic" ? 1 : 0;
  cone.offset_select = type === "offset" ? 1 : 0;
  cone.slope_select = type === "slope" ? 1 : 0;
}

function numInput(label, value, onChange, opts = {}) {
  const id = opts.id || label.replace(/\W+/g, "-").toLowerCase();
  const step = opts.step ?? "any";
  const min = opts.min != null ? ` min="${opts.min}"` : "";
  return `<label class="field" for="${id}">
    <span>${label}</span>
    <input id="${id}" type="number"${min} step="${step}" value="${value ?? ""}"
      ${opts.disabled ? "disabled" : ""} />
  </label>`;
}

function textInput(label, value, opts = {}) {
  const id = opts.id || label.replace(/\W+/g, "-").toLowerCase();
  return `<label class="field" for="${id}">
    <span>${label}</span>
    <input id="${id}" type="text" value="${value ?? ""}" />
  </label>`;
}

function selectInput(label, value, options, opts = {}) {
  const id = opts.id || label.replace(/\W+/g, "-").toLowerCase();
  const optsHtml = options
    .map((o) => `<option value="${o.value}"${o.value === value ? " selected" : ""}>${o.label}</option>`)
    .join("");
  return `<label class="field" for="${id}">
    <span>${label}</span>
    <select id="${id}">${optsHtml}</select>
  </label>`;
}

function checkboxInput(label, checked, opts = {}) {
  const id = opts.id || label.replace(/\W+/g, "-").toLowerCase();
  return `<label class="field checkbox" for="${id}">
    <input id="${id}" type="checkbox"${checked ? " checked" : ""} />
    <span>${label}</span>
  </label>`;
}

function bind(root) {
  root.querySelectorAll("[data-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeTab = btn.dataset.tab;
      render();
    });
  });

  root.querySelector("#btn-calculate")?.addEventListener("click", runCalculate);
  root.querySelector("#btn-save")?.addEventListener("click", saveJson);
  root.querySelector("#btn-save-server")?.addEventListener("click", saveToServer);
  root.querySelector("#btn-load")?.addEventListener("click", () => root.querySelector("#file-load")?.click());
  root.querySelector("#btn-load-server")?.addEventListener("change", loadFromServer);
  root.querySelector("#btn-refresh-saved")?.addEventListener("click", refreshSavedList);
  root.querySelector("#btn-add-customer")?.addEventListener("click", quickAddCustomer);
  root.querySelector("#btn-search-stock")?.addEventListener("click", loadStock);
  root.querySelector("#stock-filter")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") loadStock();
  });
  root.querySelector("#btn-new")?.addEventListener("click", () => {
    if (confirm("Start a new costing? Unsaved changes will be lost.")) {
      state = defaultCosting();
      statusMessage = "New costing started.";
      render();
    }
  });
  root.querySelector("#file-load")?.addEventListener("change", loadJsonFile);

  bindSummary(root);
  bindCones(root);
  bindStrakes(root);
  bindComponents(root);
}

function bindComponents(root) {
  root.querySelectorAll("[data-add-stock]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.dataset.addStock, 10);
      const item = stockItems[idx];
      if (!item) return;
      if (!state.selected_components) state.selected_components = [];
      state.selected_components.push({
        stock_id: item.id,
        type: item.type,
        description: item.description,
        cost: Number(item.cost) || 0,
      });
      syncComponentsPrice();
      render();
    });
  });
  root.querySelectorAll("[data-remove-component]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.dataset.removeComponent, 10);
      state.selected_components.splice(idx, 1);
      syncComponentsPrice();
      render();
    });
  });
}

function bindSummary(root) {
  const s = state.summary;
  const set = (id, fn) => {
    const el = root.querySelector(`#${id}`);
    if (!el) return;
    el.addEventListener("input", () => fn(el));
  };
  set("summary-title", (el) => { state.title = el.value; });
  set("summary-diam", (el) => { s.diam = parseFloat(el.value) || 0; });
  set("summary-expan-diam", (el) => { s.expan_diam = parseFloat(el.value) || 0; });
  set("summary-expan-height", (el) => { s.expan_height = parseFloat(el.value) || 0; });
  set("summary-markup", (el) => { s.coil_mark_up_percent = parseFloat(el.value) || 0; });
  set("summary-gst", (el) => { s.gst = parseFloat(el.value) || 1.1; });
  set("summary-num-tanks", (el) => { s.num_tanks = parseInt(el.value, 10) || 1; });
  set("summary-components", (el) => { s.components_price = parseFloat(el.value) || 0; });
  set("summary-comp-markup", (el) => { s.comp_markup_percent = parseFloat(el.value) || 0; });
  set("summary-price-quoted", (el) => { s.price_quoted = parseFloat(el.value) || 0; });
  set("summary-lab-misc-hrs", (el) => { s.lab_misc_hrs = parseFloat(el.value) || 0; });
  set("summary-lab-misc-rate", (el) => { s.lab_misc_rate = parseFloat(el.value) || 0; });
  set("cones-rate", (el) => { state.cones_rate_per_hour = parseFloat(el.value) || 0; });
  const custEl = root.querySelector("#summary-customer");
  custEl?.addEventListener("change", () => {
    state.customer_id = custEl.value ? parseInt(custEl.value, 10) : null;
  });
}

function bindCones(root) {
  state.cones.forEach((cone, i) => {
    const prefix = `cone-${i}`;
    const typeEl = root.querySelector(`#${prefix}-type`);
    if (typeEl) {
      typeEl.addEventListener("change", () => {
        setConeType(cone, typeEl.value);
        render();
      });
    }
    const fields = [
      ["name", "text", (el) => { cone.name = el.value; }],
      ["diam-large", "number", (el) => { cone.diam_large = parseFloat(el.value) || 0; }],
      ["diam-small", "number", (el) => { cone.diam_small = parseFloat(el.value) || 0; }],
      ["angle", "number", (el) => { cone.angle = parseFloat(el.value) || 0; }],
      ["height", "number", (el) => { cone.height = parseFloat(el.value) || 0; }],
      ["knuckle", "number", (el) => { cone.knuckle_rad = parseFloat(el.value) || 0; }],
      ["offset", "number", (el) => { cone.offset_amt = parseFloat(el.value) || 0; }],
      ["skirt", "number", (el) => { cone.skirt = parseFloat(el.value) || 0; }],
      ["waste", "number", (el) => { cone.waste = parseFloat(el.value) || 0; }],
      ["thick", "number", (el) => { cone.thick = parseFloat(el.value) || 0; }],
      ["width", "number", (el) => { cone.width = parseFloat(el.value) || 0; }],
      ["price-kg", "number", (el) => { cone.price_kg = parseFloat(el.value) || 0; }],
      ["weight-cucm", "number", (el) => { cone.weight_cucm = parseFloat(el.value) || 0; }],
      ["volume-treat", "select", (el) => { cone.volume_treat = parseInt(el.value, 10) || 0; }],
    ];
    fields.forEach(([key, kind, handler]) => {
      const el = root.querySelector(`#${prefix}-${key}`);
      if (!el) return;
      el.addEventListener("input", () => handler(el));
      if (kind === "select") el.addEventListener("change", () => handler(el));
    });
    const angleSel = root.querySelector(`#${prefix}-angle-select`);
    const heightSel = root.querySelector(`#${prefix}-height-select`);
    angleSel?.addEventListener("change", () => {
      cone.angle_select = angleSel.checked;
      cone.height_select = !angleSel.checked;
      render();
    });
    heightSel?.addEventListener("change", () => {
      cone.height_select = heightSel.checked;
      cone.angle_select = !heightSel.checked;
      render();
    });
  });
}

function bindStrakes(root) {
  state.strakes.forEach((strake, i) => {
    const prefix = `strake-${i}`;
    const usedEl = root.querySelector(`#${prefix}-used`);
    usedEl?.addEventListener("change", () => {
      strake.used = usedEl.checked ? 1 : 0;
      render();
    });
    const fields = [
      ["name", (el) => { strake.name = el.value; }],
      ["width", (el) => { strake.width = parseFloat(el.value) || 0; }],
      ["thick", (el) => { strake.thick = parseFloat(el.value) || 0; }],
      ["trim", (el) => { strake.trim_strakes = parseFloat(el.value) || 0; }],
      ["coil-length", (el) => { strake.coil_length = parseFloat(el.value) || 0; }],
      ["count", (el) => { strake.num_iden_strakes = parseInt(el.value, 10) || 1; }],
      ["price-kg", (el) => { strake.price_kg = parseFloat(el.value) || 0; }],
      ["rate-hour", (el) => { strake.rate_hour = parseFloat(el.value) || 0; }],
      ["num-hours", (el) => { strake.num_hours = parseFloat(el.value) || 0; }],
      ["weight-cucm", (el) => { strake.weight_cucm = parseFloat(el.value) || 0; }],
      ["volume-treat", (el) => { strake.volume_treat = parseInt(el.value, 10) || 0; }],
    ];
    fields.forEach(([key, handler]) => {
      const el = root.querySelector(`#${prefix}-${key}`);
      if (!el) return;
      el.addEventListener("input", () => handler(el));
      el.addEventListener("change", () => handler(el));
    });
  });
}

async function runCalculate() {
  syncComponentsPrice();
  statusMessage = "Calculating…";
  render();
  try {
    const payload = {
      cones: state.cones,
      strakes: state.strakes,
      summary: state.summary,
      cones_rate_per_hour: state.cones_rate_per_hour,
    };
    state.results = await calculateCosting(payload);
    statusMessage = "Calculation complete.";
    activeTab = "totals";
  } catch (err) {
    statusMessage = `Error: ${err.message}`;
  }
  render();
}

function saveJson() {
  const blob = new Blob([serializeCosting(state)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${(state.title || "costing").replace(/\W+/g, "-").toLowerCase()}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  statusMessage = "Costing saved.";
  render();
}

async function saveToServer() {
  syncComponentsPrice();
  statusMessage = "Saving to server…";
  render();
  try {
    const body = {
      title: state.title || "Untitled costing",
      customer_id: state.customer_id,
      payload: payloadForSave(),
    };
    const saved = await saveCosting(body, state.costing_id);
    state.costing_id = saved.id;
    state.title = saved.title;
    statusMessage = `Saved to server (id ${saved.id}).`;
    await refreshSavedList();
  } catch (err) {
    statusMessage = `Save failed: ${err.message}`;
  }
  render();
}

async function loadFromServer(event) {
  const id = parseInt(event.target.value, 10);
  if (!id) return;
  statusMessage = "Loading…";
  render();
  try {
    const row = await getCosting(id);
    state = {
      ...parseCosting(row.payload),
      costing_id: row.id,
      customer_id: row.customer_id,
      title: row.title,
      results: null,
    };
    syncComponentsPrice();
    statusMessage = `Loaded costing #${id}.`;
  } catch (err) {
    statusMessage = `Load failed: ${err.message}`;
  }
  render();
}

async function refreshSavedList() {
  try {
    savedCostings = await listCostings();
    customers = await listCustomers();
    render();
  } catch {
    /* ignore */
  }
}

async function quickAddCustomer() {
  const name = prompt("Company name:");
  if (!name?.trim()) return;
  try {
    const c = await createCustomer({ company_name: name.trim() });
    customers = await listCustomers();
    state.customer_id = c.id;
    statusMessage = `Customer "${c.company_name}" added.`;
    render();
  } catch (err) {
    statusMessage = `Error: ${err.message}`;
    render();
  }
}

async function loadStock() {
  const input = document.getElementById("stock-filter");
  stockFilter = input?.value || "";
  try {
    stockItems = await searchStock(stockFilter, 40);
    activeTab = "components";
    render();
  } catch (err) {
    statusMessage = `Stock search failed: ${err.message}`;
    render();
  }
}

function loadJsonFile(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      state = parseCosting(reader.result);
      statusMessage = `Loaded ${file.name}`;
      render();
    } catch (err) {
      statusMessage = `Load failed: ${err.message}`;
      render();
    }
  };
  reader.readAsText(file);
  event.target.value = "";
}

function renderSummary() {
  const s = state.summary;
  const custOpts = [{ value: "", label: "— No customer —" }].concat(
    customers.map((c) => ({ value: String(c.id), label: c.company_name }))
  );
  const savedOpts = [{ value: "", label: "— Load saved costing —" }].concat(
    savedCostings.map((c) => ({
      value: String(c.id),
      label: `#${c.id} ${c.title}${c.customer_name ? ` (${c.customer_name})` : ""}`,
    }))
  );
  return `<section class="panel">
    <h2>Tank summary</h2>
    <div class="field-grid">
      ${textInput("Job title", state.title, { id: "summary-title" })}
      ${selectInput("Customer", state.customer_id ? String(state.customer_id) : "", custOpts, { id: "summary-customer" })}
      <label class="field">
        <span>&nbsp;</span>
        <button type="button" id="btn-add-customer" class="btn secondary">+ New customer</button>
      </label>
      ${selectInput("Open saved", "", savedOpts, { id: "btn-load-server" })}
      <label class="field">
        <span>&nbsp;</span>
        <button type="button" id="btn-refresh-saved" class="btn secondary">Refresh list</button>
      </label>
      ${state.costing_id ? `<p class="hint full-width">Server id: ${state.costing_id}</p>` : ""}
      ${numInput("Tank diameter (mm)", s.diam, null, { id: "summary-diam", min: 0 })}
      ${numInput("Expansion diam (mm)", s.expan_diam, null, { id: "summary-expan-diam" })}
      ${numInput("Expansion height (mm)", s.expan_height, null, { id: "summary-expan-height" })}
      ${numInput("Steel markup (%)", s.coil_mark_up_percent, null, { id: "summary-markup" })}
      ${numInput("GST multiplier", s.gst, null, { id: "summary-gst", step: "0.01" })}
      ${numInput("Number of tanks", s.num_tanks, null, { id: "summary-num-tanks", min: 1 })}
      ${numInput("Components price", s.components_price, null, { id: "summary-components" })}
      ${numInput("Components markup (%)", s.comp_markup_percent, null, { id: "summary-comp-markup" })}
      ${numInput("Price quoted (0 = auto)", s.price_quoted, null, { id: "summary-price-quoted" })}
      ${numInput("Misc labour hours", s.lab_misc_hrs, null, { id: "summary-lab-misc-hrs" })}
      ${numInput("Misc labour rate", s.lab_misc_rate, null, { id: "summary-lab-misc-rate" })}
      ${numInput("Cones labour rate ($/hr)", state.cones_rate_per_hour, null, { id: "cones-rate" })}
    </div>
  </section>`;
}

function renderCone(i, cone) {
  const type = coneType(cone);
  const active = type !== "none";
  const res = state.results?.cones?.[i];
  const vtOptions = VOLUME_TREAT_LABELS.map((label, v) => ({ value: String(v), label: `${v}: ${label}` }));
  return `<article class="sub-card${active ? "" : " muted"}">
    <h3>Cone ${i + 1}${cone.name ? `: ${cone.name}` : ""}</h3>
    <div class="field-grid">
      ${selectInput("Type", type, CONE_TYPE_OPTIONS, { id: `cone-${i}-type` })}
      ${textInput("Name", cone.name, { id: `cone-${i}-name` })}
      ${selectInput("Volume treatment", String(cone.volume_treat), vtOptions, { id: `cone-${i}-volume-treat` })}
      ${active ? checkboxInput("Use angle (uncheck for height)", cone.angle_select, { id: `cone-${i}-angle-select` }) : ""}
      ${active && cone.angle_select ? numInput("Angle (°)", cone.angle, null, { id: `cone-${i}-angle` }) : ""}
      ${active && cone.height_select ? numInput("Height (mm)", cone.height, null, { id: `cone-${i}-height` }) : ""}
      ${active ? numInput("Diam large (mm)", cone.diam_large, null, { id: `cone-${i}-diam-large` }) : ""}
      ${active && type !== "slope" ? numInput("Diam small (mm)", cone.diam_small, null, { id: `cone-${i}-diam-small` }) : ""}
      ${active ? numInput("Knuckle rad (mm)", cone.knuckle_rad, null, { id: `cone-${i}-knuckle` }) : ""}
      ${active && type === "offset" ? numInput("Offset (mm)", cone.offset_amt, null, { id: `cone-${i}-offset` }) : ""}
      ${active && type === "slope" ? numInput("Skirt (mm)", cone.skirt, null, { id: `cone-${i}-skirt` }) : ""}
      ${active ? numInput("Waste (mm)", cone.waste, null, { id: `cone-${i}-waste` }) : ""}
      ${active ? numInput("Thickness (mm)", cone.thick, null, { id: `cone-${i}-thick` }) : ""}
      ${active ? numInput("Coil width (mm)", cone.width, null, { id: `cone-${i}-width` }) : ""}
      ${active ? numInput("Price/kg", cone.price_kg, null, { id: `cone-${i}-price-kg`, step: "0.01" }) : ""}
      ${active ? numInput("Weight cum", cone.weight_cucm, null, { id: `cone-${i}-weight-cucm` }) : ""}
    </div>
    ${res ? `<div class="results-inline">
      <span>Vol: <strong>${fmt(res.volume)} L</strong></span>
      <span>Height: <strong>${fmt(res.height)} mm</strong></span>
      <span>Steel: <strong>${money(res.steel_price)}</strong></span>
    </div>` : ""}
  </article>`;
}

function renderCones() {
  return `<section class="panel">
    <h2>Cones &amp; floors (${NUM_CONES})</h2>
    ${state.cones.map((c, i) => renderCone(i, c)).join("")}
  </section>`;
}

function renderStrake(i, strake) {
  const res = state.results?.strakes?.[i];
  const vtOptions = VOLUME_TREAT_LABELS.map((label, v) => ({ value: String(v), label: `${v}: ${label}` }));
  return `<article class="sub-card${strake.used ? "" : " muted"}">
    <h3>Strake ${i + 1}${strake.name ? `: ${strake.name}` : ""}</h3>
    <div class="field-grid">
      ${checkboxInput("Used", strake.used === 1, { id: `strake-${i}-used` })}
      ${textInput("Name", strake.name, { id: `strake-${i}-name` })}
      ${numInput("Width (mm)", strake.width, null, { id: `strake-${i}-width` })}
      ${numInput("Thickness (mm)", strake.thick, null, { id: `strake-${i}-thick` })}
      ${numInput("Trim (mm)", strake.trim_strakes, null, { id: `strake-${i}-trim` })}
      ${numInput("Coil length (mm, 0=circum)", strake.coil_length, null, { id: `strake-${i}-coil-length` })}
      ${numInput("Count", strake.num_iden_strakes, null, { id: `strake-${i}-count`, min: 1 })}
      ${numInput("Price/kg", strake.price_kg, null, { id: `strake-${i}-price-kg`, step: "0.01" })}
      ${numInput("Labour hours", strake.num_hours, null, { id: `strake-${i}-num-hours` })}
      ${numInput("Labour rate", strake.rate_hour, null, { id: `strake-${i}-rate-hour` })}
      ${numInput("Weight cum", strake.weight_cucm, null, { id: `strake-${i}-weight-cucm` })}
      ${selectInput("Volume treatment", String(strake.volume_treat), vtOptions, { id: `strake-${i}-volume-treat` })}
    </div>
    ${res && strake.used ? `<div class="results-inline">
      <span>Vol: <strong>${fmt(res.volume)} L</strong></span>
      <span>Steel: <strong>${money(res.steel_price)}</strong></span>
    </div>` : ""}
  </article>`;
}

function renderStrakes() {
  return `<section class="panel">
    <h2>Strakes (${NUM_STRAKES})</h2>
    ${state.strakes.map((s, i) => renderStrake(i, s)).join("")}
  </section>`;
}

function renderComponents() {
  const list = (state.selected_components || [])
    .map(
      (c, i) => `<li>${c.description || c.type} — ${money(c.cost)}
        <button type="button" class="btn-link" data-remove-component="${i}">Remove</button></li>`
    )
    .join("");
  const stockRows = stockItems
    .map(
      (item, i) => `<tr>
        <td>${item.type || ""}</td>
        <td>${item.description || ""}</td>
        <td>${money(item.cost)}</td>
        <td><button type="button" class="btn secondary" data-add-stock="${i}">Add</button></td>
      </tr>`
    )
    .join("");
  return `<section class="panel">
    <h2>Components (stock)</h2>
    <p class="hint">Selected components sum into <strong>Components price</strong> on Summary.</p>
    <ul class="component-list">${list || "<li class='hint'>No components selected.</li>"}</ul>
    <p>Total selected: <strong>${money(state.summary.components_price)}</strong></p>
    <div class="field-grid">
      ${textInput("Search stock (type filter)", stockFilter, { id: "stock-filter" })}
      <label class="field"><span>&nbsp;</span>
        <button type="button" id="btn-search-stock" class="btn secondary">Search</button>
      </label>
    </div>
    ${stockItems.length ? `<table><thead><tr><th>Type</th><th>Description</th><th>Cost</th><th></th></tr></thead><tbody>${stockRows}</tbody></table>` : ""}
  </section>`;
}

function renderTotals() {
  const t = state.results?.totals;
  if (!t) {
    return `<section class="panel"><p class="hint">Click <strong>Calculate</strong> to see totals.</p></section>`;
  }
  return `<section class="panel">
    <h2>Calculated totals</h2>
    <div class="totals-grid">
      <div class="total-block">
        <h3>Volume</h3>
        <dl>
          <dt>Total volume</dt><dd>${fmt(t.total_vol)} L</dd>
          <dt>Strakes volume</dt><dd>${fmt(t.strakes_vol)} L</dd>
          <dt>Cones volume</dt><dd>${fmt(t.cones_vol)} L</dd>
          <dt>Expansion volume</dt><dd>${fmt(t.expan_vol)} L</dd>
        </dl>
      </div>
      <div class="total-block">
        <h3>Height</h3>
        <dl>
          <dt>Tank liquid height</dt><dd>${fmt(t.tank_height)} mm</dd>
          <dt>Strake height</dt><dd>${fmt(t.tot_strake_height)} mm</dd>
          <dt>Cone height</dt><dd>${fmt(t.tot_cone_height)} mm</dd>
        </dl>
      </div>
      <div class="total-block">
        <h3>Steel</h3>
        <dl>
          <dt>Cones steel</dt><dd>${money(t.cone_total)}</dd>
          <dt>Strakes steel</dt><dd>${money(t.strake_total)}</dd>
          <dt>Subtotal</dt><dd>${money(t.steel_sub_tot)}</dd>
          <dt>Markup</dt><dd>${money(t.steel_mark_up_amount)}</dd>
          <dt>Steel total</dt><dd><strong>${money(t.steel_total)}</strong></dd>
        </dl>
      </div>
      <div class="total-block highlight">
        <h3>Quote</h3>
        <dl>
          <dt>Components</dt><dd>${money(t.comp_tot_inc_markup)}</dd>
          <dt>Labour</dt><dd>${money(t.labour_tot)}</dd>
          <dt>Single tank (ex GST)</dt><dd>${money(t.single_tank_less_gst)}</dd>
          <dt>Single tank (inc GST)</dt><dd><strong>${money(t.single_tank_inc_gst)}</strong></dd>
        </dl>
      </div>
    </div>
  </section>`;
}

function renderTabs() {
  const tabs = [
    ["summary", "Summary"],
    ["cones", "Cones"],
    ["strakes", "Strakes"],
    ["components", "Components"],
    ["totals", "Totals"],
  ];
  return tabs
    .map(([id, label]) =>
      `<button type="button" class="tab${activeTab === id ? " active" : ""}" data-tab="${id}">${label}</button>`
    )
    .join("");
}

function renderPanel() {
  switch (activeTab) {
    case "cones": return renderCones();
    case "strakes": return renderStrakes();
    case "components": return renderComponents();
    case "totals": return renderTotals();
    default: return renderSummary();
  }
}

function render() {
  const root = document.getElementById("app");
  root.innerHTML = `
    <header>
      <h1>Tank Costing</h1>
      <p class="subtitle">${state.title || "Untitled"}</p>
    </header>
    <div class="toolbar">
      <div class="tabs">${renderTabs()}</div>
      <div class="actions">
        <button type="button" id="btn-new" class="btn secondary">New</button>
        <button type="button" id="btn-load" class="btn secondary">Load JSON</button>
        <input type="file" id="file-load" accept=".json,application/json" hidden />
        <button type="button" id="btn-save" class="btn secondary">Save JSON</button>
        <button type="button" id="btn-save-server" class="btn secondary">Save to server</button>
        <button type="button" id="btn-calculate" class="btn primary">Calculate</button>
      </div>
    </div>
    ${statusMessage ? `<p class="status">${statusMessage}</p>` : ""}
    ${renderPanel()}
  `;
  bind(root);
}

export async function initCostingApp() {
  try {
    const health = await fetchHealth();
    statusMessage = `${health.app} v${health.version} — ready`;
    await refreshSavedList();
  } catch {
    statusMessage = "API not reachable — start the backend on port 8080";
  }
  render();
}
