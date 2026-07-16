export function emptyCustomerForm() {
  return {
    company_name: "",
    contact_name: "",
    email: "",
    phone: "",
    billing_address: "",
    delivery_address: "",
    town: "",
    state: "",
    postal_code: "",
    country: "Australia",
    notes: "",
  };
}

function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/"/g, "&quot;");
}

function textField(label, value, id) {
  return `<label class="field" for="${id}">
    <span>${label}</span>
    <input id="${id}" type="text" value="${esc(value)}" />
  </label>`;
}

function textAreaField(label, value, id) {
  return `<label class="field full-width" for="${id}">
    <span>${label}</span>
    <textarea id="${id}" rows="3">${esc(value)}</textarea>
  </label>`;
}

function renderCustomerForm(form, isNew) {
  return `<section class="panel">
    <h2>${isNew ? "New customer" : `Edit customer: ${esc(form.company_name)}`}</h2>
    <div class="field-grid">
      ${textField("Company name *", form.company_name, "cust-company")}
      ${textField("Contact name", form.contact_name, "cust-contact")}
      ${textField("Email", form.email, "cust-email")}
      ${textField("Phone", form.phone, "cust-phone")}
      ${textAreaField("Billing address", form.billing_address, "cust-billing")}
      ${textAreaField("Delivery address", form.delivery_address, "cust-delivery")}
      ${textField("Town", form.town, "cust-town")}
      ${textField("State", form.state, "cust-state")}
      ${textField("Postal code", form.postal_code, "cust-postal")}
      ${textField("Country", form.country, "cust-country")}
      ${textAreaField("Notes", form.notes, "cust-notes")}
    </div>
    <div class="form-actions">
      <button type="button" id="btn-cust-save" class="btn primary">Save customer</button>
      <button type="button" id="btn-cust-cancel" class="btn secondary">Cancel</button>
    </div>
  </section>`;
}

function renderCustomerList(customers, search, readOnly) {
  const actions = (c) => readOnly
    ? `<button type="button" class="btn secondary btn-sm" data-cust-use="${c.id}">Use</button>`
    : `<button type="button" class="btn secondary btn-sm" data-cust-use="${c.id}">Use</button>
          <button type="button" class="btn secondary btn-sm" data-cust-edit="${c.id}">Edit</button>
          <button type="button" class="btn secondary btn-sm" data-cust-delete="${c.id}">Delete</button>`;
  const rows = customers
    .map(
      (c) => `<tr>
        <td><strong>${esc(c.company_name)}</strong></td>
        <td>${esc(c.contact_name || "—")}</td>
        <td>${esc(c.town || "—")}</td>
        <td>${esc(c.email || "—")}</td>
        <td class="actions-cell">${actions(c)}</td>
      </tr>`
    )
    .join("");
  return `<section class="panel">
    <h2>Customers</h2>
    <p class="hint">${readOnly ? "View customer records." : "Manage customer records."} Use <strong>Use</strong> to attach to the current costing.</p>
    <div class="field-grid toolbar-row">
      ${textField("Search", search, "cust-search")}
      <label class="field"><span>&nbsp;</span>
        <button type="button" id="btn-cust-search" class="btn secondary">Search</button>
      </label>
      ${readOnly ? "" : `<label class="field"><span>&nbsp;</span>
        <button type="button" id="btn-cust-new" class="btn primary">+ New customer</button>
      </label>`}
    </div>
    ${customers.length
      ? `<div class="table-wrap"><table class="data-table">
          <thead><tr><th>Company</th><th>Contact</th><th>Town</th><th>Email</th><th></th></tr></thead>
          <tbody>${rows}</tbody>
        </table></div>`
      : `<p class="hint">No customers found. Add one to get started.</p>`}
  </section>`;
}

export function renderCustomersTab({ customers, search, form, readOnly }) {
  if (form && !readOnly) return renderCustomerForm(form.data, form.isNew);
  return renderCustomerList(customers, search, readOnly);
}

export function readCustomerForm(root) {
  const val = (id) => root.querySelector(`#${id}`)?.value?.trim() ?? "";
  return {
    company_name: val("cust-company"),
    contact_name: val("cust-contact") || null,
    email: val("cust-email") || null,
    phone: val("cust-phone") || null,
    billing_address: val("cust-billing") || null,
    delivery_address: val("cust-delivery") || null,
    town: val("cust-town") || null,
    state: val("cust-state") || null,
    postal_code: val("cust-postal") || null,
    country: val("cust-country") || "Australia",
    notes: val("cust-notes") || null,
  };
}

export function bindCustomersTab(root, handlers) {
  root.querySelector("#btn-cust-new")?.addEventListener("click", handlers.onNew);
  root.querySelector("#btn-cust-search")?.addEventListener("click", handlers.onSearch);
  root.querySelector("#cust-search")?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handlers.onSearch();
  });
  root.querySelector("#btn-cust-save")?.addEventListener("click", () => {
    handlers.onSave(readCustomerForm(root));
  });
  root.querySelector("#btn-cust-cancel")?.addEventListener("click", handlers.onCancel);
  root.querySelectorAll("[data-cust-edit]").forEach((btn) => {
    btn.addEventListener("click", () => handlers.onEdit(parseInt(btn.dataset.custEdit, 10)));
  });
  root.querySelectorAll("[data-cust-delete]").forEach((btn) => {
    btn.addEventListener("click", () => handlers.onDelete(parseInt(btn.dataset.custDelete, 10)));
  });
  root.querySelectorAll("[data-cust-use]").forEach((btn) => {
    btn.addEventListener("click", () => handlers.onUse(parseInt(btn.dataset.custUse, 10)));
  });
}
