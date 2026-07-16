function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/"/g, "&quot;");
}

export function renderAdminTab(users, showForm) {
  if (showForm) {
    return `<section class="panel">
      <h2>New user</h2>
      <div class="field-grid">
        <label class="field"><span>Email</span><input id="adm-email" type="email" /></label>
        <label class="field"><span>Display name</span><input id="adm-name" type="text" /></label>
        <label class="field"><span>Password</span><input id="adm-password" type="password" /></label>
        <label class="field"><span>Role</span>
          <select id="adm-role">
            <option value="editor">Editor</option>
            <option value="viewer">Viewer</option>
            <option value="admin">Admin</option>
          </select>
        </label>
      </div>
      <div class="form-actions">
        <button type="button" id="adm-save" class="btn primary">Create user</button>
        <button type="button" id="adm-cancel" class="btn secondary">Cancel</button>
      </div>
    </section>`;
  }
  const rows = users
    .map(
      (u) => `<tr>
        <td>${esc(u.email)}</td>
        <td>${esc(u.display_name)}</td>
        <td>${esc(u.role)}</td>
        <td>${u.is_active ? "Active" : "Disabled"}</td>
        <td class="actions-cell">
          <button type="button" class="btn secondary btn-sm" data-adm-toggle="${u.id}"
            data-active="${u.is_active ? "1" : "0"}">${u.is_active ? "Disable" : "Enable"}</button>
          <button type="button" class="btn secondary btn-sm" data-adm-reset="${u.id}">Reset pwd</button>
        </td>
      </tr>`
    )
    .join("");
  return `<section class="panel">
    <h2>Users</h2>
    <p class="hint">Manage login accounts. Passwords must be at least 10 characters with upper, lower, and a digit.</p>
    <button type="button" id="adm-new" class="btn primary">+ New user</button>
    <div class="table-wrap" style="margin-top:1rem">
      <table class="data-table">
        <thead><tr><th>Email</th><th>Name</th><th>Role</th><th>Status</th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  </section>`;
}

export function readAdminForm(root) {
  return {
    email: root.querySelector("#adm-email")?.value?.trim(),
    display_name: root.querySelector("#adm-name")?.value?.trim(),
    password: root.querySelector("#adm-password")?.value,
    role: root.querySelector("#adm-role")?.value || "editor",
  };
}

export function bindAdminTab(root, handlers) {
  root.querySelector("#adm-new")?.addEventListener("click", handlers.onNew);
  root.querySelector("#adm-save")?.addEventListener("click", handlers.onSave);
  root.querySelector("#adm-cancel")?.addEventListener("click", handlers.onCancel);
  root.querySelectorAll("[data-adm-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      handlers.onToggle(parseInt(btn.dataset.admToggle, 10), btn.dataset.active === "1");
    });
  });
  root.querySelectorAll("[data-adm-reset]").forEach((btn) => {
    btn.addEventListener("click", () => handlers.onReset(parseInt(btn.dataset.admReset, 10)));
  });
}
