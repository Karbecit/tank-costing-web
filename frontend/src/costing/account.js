import { getUser } from "../auth.js";

function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/"/g, "&quot;");
}

export function renderAccountTab(user, mfaSetup) {
  const u = user || getUser();
  return `<section class="panel">
    <h2>Account</h2>
    <div class="account-info">
      <p><strong>${esc(u?.display_name)}</strong> · ${esc(u?.email)}</p>
      <p class="hint">Role: ${esc(u?.role)} · MFA: ${u?.mfa_enabled ? "Enabled" : "Off"}</p>
    </div>

    <h3>Change password</h3>
    <div class="field-grid">
      <label class="field"><span>Current password</span>
        <input id="acct-current-pw" type="password" autocomplete="current-password" /></label>
      <label class="field"><span>New password</span>
        <input id="acct-new-pw" type="password" autocomplete="new-password" /></label>
      <label class="field"><span>Confirm new password</span>
        <input id="acct-confirm-pw" type="password" autocomplete="new-password" /></label>
    </div>
    <button type="button" id="acct-change-pw" class="btn secondary">Update password</button>

    <h3 style="margin-top:1.5rem">Two-factor authentication</h3>
    ${u?.mfa_enabled ? `
      <p class="hint">MFA is enabled. Admins must enter a code every login.</p>
      <label class="field"><span>Code to disable</span>
        <input id="acct-mfa-disable" type="text" inputmode="numeric" maxlength="6" /></label>
      <button type="button" id="acct-mfa-off" class="btn secondary">Disable MFA</button>
    ` : mfaSetup ? `
      <p class="hint">Scan this secret in Google Authenticator or similar, then enter a code to confirm.</p>
      <p class="mono-block">${esc(mfaSetup.secret)}</p>
      <p class="hint"><a href="${esc(mfaSetup.otpauth_uri)}" target="_blank">Open in authenticator app</a></p>
      <label class="field"><span>Verification code</span>
        <input id="acct-mfa-confirm" type="text" inputmode="numeric" maxlength="6" /></label>
      <button type="button" id="acct-mfa-confirm-btn" class="btn primary">Enable MFA</button>
      <button type="button" id="acct-mfa-cancel" class="btn secondary">Cancel</button>
    ` : `
      <p class="hint">Add an extra layer of security with an authenticator app.</p>
      <button type="button" id="acct-mfa-start" class="btn secondary">Set up MFA</button>
    `}
  </section>`;
}

export function readPasswordForm(root) {
  return {
    current: root.querySelector("#acct-current-pw")?.value || "",
    newPassword: root.querySelector("#acct-new-pw")?.value || "",
    confirm: root.querySelector("#acct-confirm-pw")?.value || "",
  };
}

export function bindAccountTab(root, handlers) {
  root.querySelector("#acct-change-pw")?.addEventListener("click", handlers.onChangePassword);
  root.querySelector("#acct-mfa-start")?.addEventListener("click", handlers.onMfaStart);
  root.querySelector("#acct-mfa-confirm-btn")?.addEventListener("click", handlers.onMfaConfirm);
  root.querySelector("#acct-mfa-cancel")?.addEventListener("click", handlers.onMfaCancel);
  root.querySelector("#acct-mfa-off")?.addEventListener("click", handlers.onMfaDisable);
}
