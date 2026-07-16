function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/"/g, "&quot;");
}

function renderSmtpSettings(smtp) {
  const s = smtp || {};
  return `<section class="panel">
    <h2>Email (SMTP)</h2>
    <p class="hint">Configure outbound email for user invites and notifications. Password is stored on the server only.</p>
    <button type="button" id="adm-back-users" class="btn secondary">← Users</button>
    <div class="field-grid" style="margin-top:1rem">
      <label class="field"><span>SMTP host</span>
        <input id="smtp-host" type="text" value="${esc(s.smtp_host)}" placeholder="smtp.example.com" /></label>
      <label class="field"><span>Port</span>
        <input id="smtp-port" type="number" value="${s.smtp_port || 587}" /></label>
      <label class="field"><span>Username</span>
        <input id="smtp-user" type="text" value="${esc(s.smtp_user)}" autocomplete="off" /></label>
      <label class="field"><span>Password${s.password_set ? " (leave blank to keep)" : ""}</span>
        <input id="smtp-password" type="password" autocomplete="new-password" /></label>
      <label class="field"><span>From address</span>
        <input id="smtp-from" type="email" value="${esc(s.smtp_from)}" /></label>
      <label class="field"><span>App URL (for email links)</span>
        <input id="smtp-base-url" type="url" value="${esc(s.app_base_url)}" placeholder="https://tankcalc.example.com" /></label>
      <label class="field checkbox"><span>&nbsp;</span>
        <input id="smtp-tls" type="checkbox"${s.smtp_use_tls !== false ? " checked" : ""} />
        <span>Use TLS (STARTTLS)</span></label>
    </div>
    <div class="form-actions">
      <button type="button" id="smtp-save" class="btn primary">Save settings</button>
    </div>
    <h3 style="margin-top:1.5rem">Test send</h3>
    <div class="field-grid">
      <label class="field"><span>Send test to</span>
        <input id="smtp-test-to" type="email" placeholder="you@example.com" /></label>
      <label class="field"><span>&nbsp;</span>
        <button type="button" id="smtp-test" class="btn secondary">Send test email</button></label>
    </div>
    ${s.configured ? `<p class="hint">Status: configured</p>` : `<p class="hint">Status: not configured</p>`}
  </section>`;
}

export function renderAdminTab(users, showForm, auditLog, view, smtpSettings) {
  if (view === "audit") {
    const rows = (auditLog || [])
      .map(
        (a) => `<tr>
          <td>${esc(a.created_at?.replace("T", " ").slice(0, 19))}</td>
          <td>${esc(a.actor_email || "—")}</td>
          <td>${esc(a.action)}</td>
          <td>${esc(a.detail || a.target_id || "—")}</td>
        </tr>`
      )
      .join("");
    return `<section class="panel">
      <h2>Audit log</h2>
      <button type="button" id="adm-back-users" class="btn secondary">← Users</button>
      <div class="table-wrap" style="margin-top:1rem">
        <table class="data-table">
          <thead><tr><th>When</th><th>User</th><th>Action</th><th>Detail</th></tr></thead>
          <tbody>${rows || "<tr><td colspan='4'>No entries</td></tr>"}</tbody>
        </table>
      </div>
    </section>`;
  }

  if (view === "smtp") {
    return renderSmtpSettings(smtpSettings);
  }

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
            <option value="viewer">Viewer (read-only)</option>
            <option value="admin">Admin</option>
          </select>
        </label>
        <label class="field checkbox"><span>&nbsp;</span>
          <input id="adm-send-email" type="checkbox" />
          <span>Send invite email after create</span></label>
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
        <td>${u.mfa_enabled ? "MFA" : "—"}</td>
        <td>${u.is_active ? "Active" : "Disabled"}</td>
        <td class="actions-cell">
          <select class="role-select" data-adm-role="${u.id}">
            <option value="editor"${u.role === "editor" ? " selected" : ""}>Editor</option>
            <option value="viewer"${u.role === "viewer" ? " selected" : ""}>Viewer</option>
            <option value="admin"${u.role === "admin" ? " selected" : ""}>Admin</option>
          </select>
          <button type="button" class="btn secondary btn-sm" data-adm-toggle="${u.id}"
            data-active="${u.is_active ? "1" : "0"}">${u.is_active ? "Disable" : "Enable"}</button>
          <button type="button" class="btn secondary btn-sm" data-adm-reset="${u.id}">Reset pwd</button>
          <button type="button" class="btn secondary btn-sm" data-adm-invite="${u.id}">Email</button>
        </td>
      </tr>`
    )
    .join("");

  return `<section class="panel">
    <h2>Users</h2>
    <p class="hint">Manage login accounts. Passwords: min 10 chars, upper, lower, digit.</p>
    <div class="form-actions" style="margin-top:0">
      <button type="button" id="adm-new" class="btn primary">+ New user</button>
      <button type="button" id="adm-audit" class="btn secondary">Audit log</button>
      <button type="button" id="adm-smtp" class="btn secondary">Email settings</button>
    </div>
    <div class="table-wrap" style="margin-top:1rem">
      <table class="data-table">
        <thead><tr><th>Email</th><th>Name</th><th>Role</th><th>Security</th><th>Status</th><th></th></tr></thead>
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
    sendEmail: root.querySelector("#adm-send-email")?.checked || false,
  };
}

export function readSmtpForm(root) {
  return {
    smtp_host: root.querySelector("#smtp-host")?.value?.trim(),
    smtp_port: parseInt(root.querySelector("#smtp-port")?.value || "587", 10),
    smtp_user: root.querySelector("#smtp-user")?.value?.trim() || "",
    smtp_password: root.querySelector("#smtp-password")?.value || null,
    smtp_from: root.querySelector("#smtp-from")?.value?.trim(),
    smtp_use_tls: root.querySelector("#smtp-tls")?.checked ?? true,
    app_base_url: root.querySelector("#smtp-base-url")?.value?.trim() || "",
  };
}

export function bindAdminTab(root, handlers) {
  root.querySelector("#adm-new")?.addEventListener("click", handlers.onNew);
  root.querySelector("#adm-audit")?.addEventListener("click", handlers.onAudit);
  root.querySelector("#adm-smtp")?.addEventListener("click", handlers.onSmtp);
  root.querySelector("#adm-back-users")?.addEventListener("click", handlers.onBackUsers);
  root.querySelector("#adm-save")?.addEventListener("click", handlers.onSave);
  root.querySelector("#adm-cancel")?.addEventListener("click", handlers.onCancel);
  root.querySelector("#smtp-save")?.addEventListener("click", handlers.onSmtpSave);
  root.querySelector("#smtp-test")?.addEventListener("click", handlers.onSmtpTest);
  root.querySelectorAll("[data-adm-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      handlers.onToggle(parseInt(btn.dataset.admToggle, 10), btn.dataset.active === "1");
    });
  });
  root.querySelectorAll("[data-adm-reset]").forEach((btn) => {
    btn.addEventListener("click", () => handlers.onReset(parseInt(btn.dataset.admReset, 10)));
  });
  root.querySelectorAll("[data-adm-invite]").forEach((btn) => {
    btn.addEventListener("click", () => handlers.onInvite(parseInt(btn.dataset.admInvite, 10)));
  });
  root.querySelectorAll(".role-select").forEach((sel) => {
    sel.addEventListener("change", () => {
      handlers.onRoleChange(parseInt(sel.dataset.admRole, 10), sel.value);
    });
  });
}
