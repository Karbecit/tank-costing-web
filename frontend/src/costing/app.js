import {
  changePassword,
  confirmMfa,
  disableMfa,
  fetchMe,
  getUser,
  logout,
  setupMfa,
} from "../auth.js";
import {
  calculateCosting,
  calcDipChart,
  createCustomer,
  createUser,
  deleteCustomer,
  downloadJmaExport,
  downloadQuotePdf,
  emailQuote,
  fetchHealth,
  getCosting,
  getCustomer,
  getSmtpSettings,
  importJma,
  listAudit,
  listCostings,
  listCustomers,
  listUsers,
  resetUserPassword,
  saveCosting,
  saveSmtpSettings,
  searchStock,
  sendUserInvite,
  testSmtp,
  updateCustomer,
  updateUser,
} from "./api.js";
import { bindAccountTab, readPasswordForm, renderAccountTab } from "./account.js";
import { bindAdminTab, readAdminForm, readSmtpForm, renderAdminTab } from "./admin.js";
import {
  bindCustomersTab,
  emptyCustomerForm,
  renderCustomersTab,
} from "./customers.js";
import { bindDipTab, readDipIncrement, renderDipTab } from "./dip.js";
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
let customerPickerQuery = "";
let customerPickerOpen = false;
let costingPickerQuery = "";
let costingPickerOpen = false;
let costingPickerMode = "open";
let customerTabSearch = "";
let customerForm = null;
let adminUsers = [];
let adminFormOpen = false;
let adminView = "users";
let auditLog = [];
let mfaSetupData = null;
let smtpSettings = null;
let dipData = null;

function canEdit() {
  const role = getUser()?.role;
  return role === "admin" || role === "editor";
}

function isAdmin() {
  return getUser()?.role === "admin";
}

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

function escHtml(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/"/g, "&quot;");
}

function customerDisplayName() {
  if (!state.customer_id) return "";
  const c = customers.find((x) => x.id === state.customer_id);
  return c?.company_name || "";
}

function filterCustomers(query) {
  const q = query.trim().toLowerCase();
  if (!q) return customers;
  return customers.filter((c) => {
    const hay = [c.company_name, c.contact_name, c.email, c.town]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  });
}

function customerComboboxListHtml(query) {
  const filtered = filterCustomers(query);
  const create = canEdit()
    ? '<li class="combobox-option combobox-create" data-cust-pick="new">+ Create New Customer</li>'
    : "";
  const none = '<li class="combobox-option" data-cust-pick="">— No customer —</li>';
  const items = filtered
    .map((c) => {
      const meta = c.town ? ` · ${escHtml(c.town)}` : "";
      const selected = c.id === state.customer_id ? " selected" : "";
      return `<li class="combobox-option${selected}" data-cust-pick="${c.id}">${escHtml(c.company_name)}${meta}</li>`;
    })
    .join("");
  return create + none + items;
}

function renderCustomerCombobox() {
  const display = customerPickerOpen ? customerPickerQuery : customerDisplayName();
  return `<label class="field combobox-field" for="customer-picker-input">
    <span>Customer</span>
    <div class="combobox" id="customer-picker">
      <input id="customer-picker-input" type="text" autocomplete="off"
        placeholder="Search or select customer…" value="${escHtml(display)}" />
      <ul id="customer-picker-list" class="combobox-list"${customerPickerOpen ? "" : " hidden"}>
        ${customerComboboxListHtml(customerPickerOpen ? customerPickerQuery : "")}
      </ul>
    </div>
  </label>`;
}

function bindCustomerCombobox(root) {
  const input = root.querySelector("#customer-picker-input");
  const list = root.querySelector("#customer-picker-list");
  if (!input || !list) return;

  const pickCustomer = (value) => {
    if (value === "new") {
      if (!canEdit()) return;
      customerForm = { isNew: true, data: emptyCustomerForm() };
      activeTab = "customers";
      customerPickerOpen = false;
      render();
      return;
    }
    state.customer_id = value ? parseInt(value, 10) : null;
    customerPickerQuery = "";
    customerPickerOpen = false;
    input.value = customerDisplayName();
    list.hidden = true;
  };

  const updateList = () => {
    list.innerHTML = customerComboboxListHtml(customerPickerQuery);
    list.querySelectorAll("[data-cust-pick]").forEach((li) => {
      li.addEventListener("mousedown", (e) => {
        e.preventDefault();
        pickCustomer(li.dataset.custPick);
      });
    });
  };

  input.addEventListener("focus", () => {
    customerPickerOpen = true;
    customerPickerQuery = input.value === customerDisplayName() ? "" : input.value;
    list.hidden = false;
    updateList();
  });

  input.addEventListener("input", () => {
    customerPickerQuery = input.value;
    customerPickerOpen = true;
    list.hidden = false;
    updateList();
  });

  input.addEventListener("blur", () => {
    setTimeout(() => {
      customerPickerOpen = false;
      customerPickerQuery = "";
      input.value = customerDisplayName();
      list.hidden = true;
    }, 150);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      customerPickerOpen = false;
      customerPickerQuery = "";
      input.value = customerDisplayName();
      list.hidden = true;
      input.blur();
    }
  });

  updateList();
}

function costingDisplayName() {
  if (!state.costing_id && state.title === "Untitled costing") return "";
  let label = state.title || "Untitled costing";
  if (state.quote_ref) label += ` [${state.quote_ref}]`;
  if (state.costing_id) label = `#${state.costing_id} ${label}`;
  return label;
}

function filterCostings(query) {
  const q = query.trim().toLowerCase();
  if (!q) return savedCostings;
  return savedCostings.filter((c) => {
    const hay = [c.title, c.quote_ref, c.customer_name, String(c.id)]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  });
}

function costingComboboxListHtml(query) {
  const filtered = filterCostings(query);
  const edit = canEdit();
  const createNew = edit
    ? '<li class="combobox-option combobox-create" data-cost-pick="new">+ Create New</li>'
    : "";
  const createCopy = edit
    ? '<li class="combobox-option combobox-create" data-cost-pick="copy">+ Create New from Existing</li>'
    : "";
  const items = filtered
    .map((c) => {
      const meta = [
        c.quote_ref ? `[${escHtml(c.quote_ref)}]` : "",
        c.customer_name ? escHtml(c.customer_name) : "",
      ]
        .filter(Boolean)
        .join(" · ");
      const suffix = meta ? ` · ${meta}` : "";
      const selected = c.id === state.costing_id ? " selected" : "";
      return `<li class="combobox-option${selected}" data-cost-pick="${c.id}">#${c.id} ${escHtml(c.title)}${suffix}</li>`;
    })
    .join("");
  const empty =
    filtered.length === 0 && query
      ? '<li class="combobox-option combobox-muted">No matching costings</li>'
      : "";
  return createNew + createCopy + items + empty;
}

function renderCostingCombobox() {
  const display = costingPickerOpen ? costingPickerQuery : costingDisplayName();
  const placeholder =
    costingPickerMode === "copy"
      ? "Select a costing to copy…"
      : "Open existing or create new…";
  return `<label class="field combobox-field costing-picker-field" for="costing-picker-input">
    <span>Open existing or create new</span>
    <div class="combobox" id="costing-picker">
      <input id="costing-picker-input" type="text" autocomplete="off"
        placeholder="${placeholder}" value="${escHtml(display)}" />
      <ul id="costing-picker-list" class="combobox-list"${costingPickerOpen ? "" : " hidden"}>
        ${costingComboboxListHtml(costingPickerOpen ? costingPickerQuery : "")}
      </ul>
    </div>
  </label>`;
}

function bindCostingCombobox(root) {
  const input = root.querySelector("#costing-picker-input");
  const list = root.querySelector("#costing-picker-list");
  if (!input || !list) return;

  const pickCosting = async (value) => {
    if (value === "new") {
      state = defaultCosting();
      costingPickerMode = "open";
      costingPickerQuery = "";
      costingPickerOpen = false;
      statusMessage = "New costing started.";
      input.value = costingDisplayName();
      list.hidden = true;
      render();
      return;
    }
    if (value === "copy") {
      costingPickerMode = "copy";
      costingPickerQuery = "";
      input.value = "";
      input.placeholder = "Select a costing to copy…";
      list.hidden = false;
      updateList();
      statusMessage = "Select a costing to copy as new.";
      return;
    }
    const id = parseInt(value, 10);
    if (!id) return;
    const asCopy = costingPickerMode === "copy";
    costingPickerMode = "open";
    costingPickerOpen = false;
    costingPickerQuery = "";
    list.hidden = true;
    statusMessage = asCopy ? "Copying…" : "Loading…";
    render();
    try {
      const row = await getCosting(id);
      state = {
        ...parseCosting(row.payload),
        costing_id: asCopy ? null : row.id,
        customer_id: row.customer_id,
        title: asCopy ? `${row.title} (copy)` : row.title,
        quote_ref: asCopy ? "" : row.quote_ref || "",
        results: null,
      };
      syncComponentsPrice();
      statusMessage = asCopy
        ? `Copied from costing #${id} — save to create new record.`
        : `Loaded costing #${id}.`;
    } catch (err) {
      statusMessage = `Load failed: ${err.message}`;
    }
    render();
  };

  const updateList = () => {
    list.innerHTML = costingComboboxListHtml(costingPickerQuery);
    list.querySelectorAll("[data-cost-pick]").forEach((li) => {
      if (li.dataset.costPick === "" || li.classList.contains("combobox-muted")) return;
      li.addEventListener("mousedown", (e) => {
        e.preventDefault();
        pickCosting(li.dataset.costPick);
      });
    });
  };

  input.addEventListener("focus", () => {
    costingPickerOpen = true;
    costingPickerQuery = input.value === costingDisplayName() ? "" : input.value;
    list.hidden = false;
    updateList();
  });

  input.addEventListener("input", () => {
    costingPickerQuery = input.value;
    costingPickerOpen = true;
    list.hidden = false;
    updateList();
  });

  input.addEventListener("blur", () => {
    setTimeout(() => {
      costingPickerOpen = false;
      costingPickerQuery = "";
      costingPickerMode = "open";
      input.value = costingDisplayName();
      input.placeholder = "Open existing or create new…";
      list.hidden = true;
    }, 150);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      costingPickerMode = "open";
      costingPickerOpen = false;
      costingPickerQuery = "";
      input.value = costingDisplayName();
      input.placeholder = "Open existing or create new…";
      list.hidden = true;
      input.blur();
    }
  });

  updateList();
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
  root.querySelector("#btn-load-jma")?.addEventListener("click", () => root.querySelector("#file-load-jma")?.click());
  root.querySelector("#btn-pdf")?.addEventListener("click", downloadPdf);
  root.querySelector("#btn-export-jma")?.addEventListener("click", exportJma);
  root.querySelector("#btn-email-quote")?.addEventListener("click", sendQuoteEmail);
  root.querySelector("#btn-refresh-saved")?.addEventListener("click", async () => {
    await refreshSavedList();
    render();
  });
  root.querySelector("#btn-search-stock")?.addEventListener("click", loadStock);
  root.querySelector("#stock-filter")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") loadStock();
  });
  root.querySelector("#btn-logout")?.addEventListener("click", logout);
  root.querySelector("#btn-new")?.addEventListener("click", () => {
    if (confirm("Start a new costing? Unsaved changes will be lost.")) {
      state = defaultCosting();
      statusMessage = "New costing started.";
      render();
    }
  });
  root.querySelector("#file-load")?.addEventListener("change", loadJsonFile);
  root.querySelector("#file-load-jma")?.addEventListener("change", loadJmaFile);

  bindSummary(root);
  bindCones(root);
  bindStrakes(root);
  bindComponents(root);
  if (activeTab === "customers") {
    bindCustomersTab(root, {
      onNew: () => {
        if (!canEdit()) return;
        customerForm = { isNew: true, data: emptyCustomerForm() };
        render();
      },
      onSearch: searchCustomersTab,
      onSave: saveCustomerForm,
      onCancel: () => {
        customerForm = null;
        render();
      },
      onEdit: async (id) => {
        try {
          const c = await getCustomer(id);
          customerForm = {
            isNew: false,
            id,
            data: {
              company_name: c.company_name,
              contact_name: c.contact_name || "",
              email: c.email || "",
              phone: c.phone || "",
              billing_address: c.billing_address || "",
              delivery_address: c.delivery_address || "",
              town: c.town || "",
              state: c.state || "",
              postal_code: c.postal_code || "",
              country: c.country || "Australia",
              notes: c.notes || "",
            },
          };
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onDelete: async (id) => {
        const c = customers.find((x) => x.id === id);
        if (!confirm(`Delete customer "${c?.company_name || id}"?`)) return;
        try {
          await deleteCustomer(id);
          if (state.customer_id === id) state.customer_id = null;
          customers = await listCustomers(customerTabSearch);
          statusMessage = "Customer deleted.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onUse: (id) => {
        state.customer_id = id;
        activeTab = "summary";
        statusMessage = "Customer attached to costing.";
        render();
      },
    });
  }
  if (activeTab === "admin" && isAdmin()) {
    bindAdminTab(root, {
      onNew: () => {
        adminFormOpen = true;
        adminView = "users";
        render();
      },
      onAudit: async () => {
        try {
          auditLog = await listAudit();
          adminView = "audit";
          adminFormOpen = false;
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onSmtp: async () => {
        try {
          smtpSettings = await getSmtpSettings();
          adminView = "smtp";
          adminFormOpen = false;
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onBackUsers: () => {
        adminView = "users";
        render();
      },
      onCancel: () => {
        adminFormOpen = false;
        render();
      },
      onSave: async () => {
        const data = readAdminForm(root);
        try {
          const user = await createUser({
            email: data.email,
            display_name: data.display_name,
            password: data.password,
            role: data.role,
          });
          adminFormOpen = false;
          adminUsers = await listUsers();
          statusMessage = `User ${data.email} created.`;
          if (data.sendEmail && data.password) {
            try {
              await sendUserInvite(user.id, data.password);
              statusMessage += " Invite email sent.";
            } catch (err) {
              statusMessage += ` Email failed: ${err.message}`;
            }
          }
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onToggle: async (id, active) => {
        try {
          await updateUser(id, { is_active: !active });
          adminUsers = await listUsers();
          statusMessage = "User updated.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onReset: async (id) => {
        const pwd = prompt("New password (min 10 chars, upper, lower, digit):");
        if (!pwd) return;
        try {
          await resetUserPassword(id, pwd);
          statusMessage = "Password reset.";
          if (confirm("Send password reset email to user?")) {
            await sendUserInvite(id, pwd);
            statusMessage = "Password reset and email sent.";
          }
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onInvite: async (id) => {
        const pwd = prompt("Enter password to include in invite email:");
        if (!pwd) return;
        try {
          await sendUserInvite(id, pwd);
          statusMessage = "Invite email sent.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onRoleChange: async (id, role) => {
        try {
          await updateUser(id, { role });
          adminUsers = await listUsers();
          statusMessage = "Role updated.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          adminUsers = await listUsers();
          render();
        }
      },
      onSmtpSave: async () => {
        const data = readSmtpForm(root);
        try {
          smtpSettings = await saveSmtpSettings(data);
          statusMessage = "SMTP settings saved.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onSmtpTest: async () => {
        const to = root.querySelector("#smtp-test-to")?.value?.trim();
        if (!to) {
          statusMessage = "Enter a test recipient email.";
          render();
          return;
        }
        try {
          await testSmtp(to);
          statusMessage = `Test email sent to ${to}.`;
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
    });
  }
  if (activeTab === "dip") {
    bindDipTab(root, {
      onGenerate: async () => {
        if (!state.results) {
          statusMessage = "Calculate the costing first.";
          render();
          return;
        }
        const inc = readDipIncrement(root);
        try {
          dipData = await calcDipChart(payloadForSave(), inc);
          statusMessage = "Dip chart generated.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
    });
  }
  if (activeTab === "account") {
    bindAccountTab(root, {
      onChangePassword: async () => {
        const { current, newPassword, confirm } = readPasswordForm(root);
        if (!current || !newPassword) {
          statusMessage = "Enter current and new password.";
          render();
          return;
        }
        if (newPassword !== confirm) {
          statusMessage = "New passwords do not match.";
          render();
          return;
        }
        try {
          await changePassword(current, newPassword);
          statusMessage = "Password updated.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onMfaStart: async () => {
        try {
          mfaSetupData = await setupMfa();
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onMfaConfirm: async () => {
        const code = root.querySelector("#acct-mfa-confirm")?.value?.trim();
        if (!code) return;
        try {
          await confirmMfa(code);
          mfaSetupData = null;
          await fetchMe();
          statusMessage = "MFA enabled.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
      onMfaCancel: () => {
        mfaSetupData = null;
        render();
      },
      onMfaDisable: async () => {
        const code = root.querySelector("#acct-mfa-disable")?.value?.trim();
        if (!code) return;
        try {
          await disableMfa(code);
          await fetchMe();
          statusMessage = "MFA disabled.";
          render();
        } catch (err) {
          statusMessage = `Error: ${err.message}`;
          render();
        }
      },
    });
  }
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
  set("summary-quote-ref", (el) => { state.quote_ref = el.value; });
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
  bindCostingCombobox(root);
  bindCustomerCombobox(root);
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
      quote_ref: state.quote_ref || null,
      customer_id: state.customer_id,
      payload: payloadForSave(),
    };
    const saved = await saveCosting(body, state.costing_id);
    state.costing_id = saved.id;
    state.title = saved.title;
    state.quote_ref = saved.quote_ref || "";
    statusMessage = `Saved to server (id ${saved.id}).`;
    await refreshSavedList();
  } catch (err) {
    statusMessage = `Save failed: ${err.message}`;
  }
  render();
}

async function refreshSavedList() {
  try {
    savedCostings = await listCostings();
    customers = await listCustomers();
  } catch {
    /* ignore */
  }
}

async function searchCustomersTab() {
  const input = document.getElementById("cust-search");
  customerTabSearch = input?.value?.trim() || "";
  try {
    customers = await listCustomers(customerTabSearch);
    render();
  } catch (err) {
    statusMessage = `Search failed: ${err.message}`;
    render();
  }
}

async function saveCustomerForm(data) {
  if (!data.company_name) {
    statusMessage = "Company name is required.";
    render();
    return;
  }
  try {
    if (customerForm?.isNew) {
      const c = await createCustomer(data);
      state.customer_id = c.id;
      statusMessage = `Customer "${c.company_name}" created.`;
    } else {
      await updateCustomer(customerForm.id, data);
      statusMessage = `Customer "${data.company_name}" updated.`;
    }
    customerForm = null;
    customerTabSearch = "";
    customers = await listCustomers();
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

async function loadJmaFile(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  statusMessage = "Importing .jma…";
  render();
  try {
    const saved = await importJma(file);
    state = {
      ...parseCosting(saved.payload),
      costing_id: saved.id,
      customer_id: saved.customer_id,
      title: saved.title,
      quote_ref: saved.quote_ref || "",
      results: null,
    };
    syncComponentsPrice();
    statusMessage = `Imported ${file.name} (id ${saved.id}).`;
    await refreshSavedList();
  } catch (err) {
    statusMessage = `Import failed: ${err.message}`;
  }
  event.target.value = "";
  render();
}

async function downloadPdf() {
  if (!state.costing_id) {
    statusMessage = "Save to server first to generate a PDF quote.";
    render();
    return;
  }
  statusMessage = "Generating PDF…";
  render();
  try {
    const name = `${(state.title || "quote").replace(/\W+/g, "-").toLowerCase()}.pdf`;
    await downloadQuotePdf(state.costing_id, name);
    statusMessage = "PDF downloaded.";
  } catch (err) {
    statusMessage = `PDF failed: ${err.message}`;
  }
  render();
}

async function exportJma() {
  if (!state.costing_id) {
    statusMessage = "Save to server first to export .jma.";
    render();
    return;
  }
  try {
    const name = `${(state.title || "costing").replace(/\W+/g, "-").toLowerCase()}.jma`;
    await downloadJmaExport(state.costing_id, name);
    statusMessage = ".jma exported.";
  } catch (err) {
    statusMessage = `Export failed: ${err.message}`;
  }
  render();
}

async function sendQuoteEmail() {
  if (!state.costing_id) {
    statusMessage = "Save to server first to email quote.";
    render();
    return;
  }
  const to = prompt("Send quote to email (leave blank to use customer email):");
  if (to === null) return;
  const message = prompt("Optional message to include in email:") || "";
  statusMessage = "Sending quote email…";
  render();
  try {
    await emailQuote(state.costing_id, to.trim() || null, message.trim() || null);
    statusMessage = "Quote email sent.";
  } catch (err) {
    statusMessage = `Email failed: ${err.message}`;
  }
  render();
}

function renderSummary() {
  const s = state.summary;
  return `<section class="panel">
    <h2>Tank summary</h2>
    <div class="field-grid">
      ${renderCostingCombobox()}
      <label class="field">
        <span>&nbsp;</span>
        <button type="button" id="btn-refresh-saved" class="btn secondary">Refresh list</button>
      </label>
      ${state.costing_id ? `<p class="hint full-width">Server id: ${state.costing_id}</p>` : ""}
      ${textInput("Job title", state.title, { id: "summary-title" })}
      ${textInput("Quote / job ref", state.quote_ref, { id: "summary-quote-ref" })}
      ${renderCustomerCombobox()}
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
    ["customers", "Customers"],
    ["totals", "Totals"],
    ["dip", "Dip chart"],
    ["account", "Account"],
  ];
  if (isAdmin()) tabs.push(["admin", "Admin"]);
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
    case "customers":
      return renderCustomersTab({
        customers,
        search: customerTabSearch,
        form: customerForm,
        readOnly: !canEdit(),
      });
    case "account":
      return renderAccountTab(getUser(), mfaSetupData);
    case "admin":
      return isAdmin()
        ? renderAdminTab(adminUsers, adminFormOpen, auditLog, adminView, smtpSettings)
        : renderSummary();
    case "totals": return renderTotals();
    case "dip": return renderDipTab(dipData);
    default: return renderSummary();
  }
}

function render() {
  const user = getUser();
  const edit = canEdit();
  const root = document.getElementById("app");
  root.innerHTML = `
    <header>
      <div class="header-row">
        <div>
          <h1>Tank Costing</h1>
          <p class="subtitle">${state.title || "Untitled"}${state.quote_ref ? ` · ${state.quote_ref}` : ""}</p>
        </div>
        <div class="header-user">
          <span>${user?.display_name || user?.email || ""}</span>
          <button type="button" id="btn-logout" class="btn secondary btn-sm">Sign out</button>
        </div>
      </div>
    </header>
    <div class="toolbar">
      <div class="tabs">${renderTabs()}</div>
      <div class="actions">
        ${edit ? `<button type="button" id="btn-new" class="btn secondary">New</button>
        <button type="button" id="btn-load" class="btn secondary">Load JSON</button>
        <button type="button" id="btn-load-jma" class="btn secondary">Load .jma</button>
        <input type="file" id="file-load" accept=".json,application/json" hidden />
        <input type="file" id="file-load-jma" accept=".jma" hidden />
        <button type="button" id="btn-save" class="btn secondary">Save JSON</button>
        <button type="button" id="btn-save-server" class="btn secondary">Save to server</button>
        <button type="button" id="btn-export-jma" class="btn secondary">Export .jma</button>
        <button type="button" id="btn-pdf" class="btn secondary">PDF quote</button>
        <button type="button" id="btn-email-quote" class="btn secondary">Email quote</button>
        <button type="button" id="btn-calculate" class="btn primary">Calculate</button>` : `<span class="hint">Read-only access</span>
        <button type="button" id="btn-pdf" class="btn secondary">PDF quote</button>`}
      </div>
    </div>
    ${statusMessage ? `<p class="status">${statusMessage}</p>` : ""}
    ${renderPanel()}
  `;
  bind(root);
}

export async function initCostingApp() {
  try {
    await fetchMe();
    const health = await fetchHealth();
    statusMessage = `${health.app} v${health.version} — ready`;
    await refreshSavedList();
    if (isAdmin()) {
      try {
        adminUsers = await listUsers();
      } catch {
        adminUsers = [];
      }
    }
  } catch {
    statusMessage = "API not reachable — start the backend on port 8080";
  }
  render();
}
