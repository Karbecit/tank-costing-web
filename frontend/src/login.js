import { login, verifyMfa } from "./auth.js";

let mfaState = null;

export function renderLogin(onSuccess) {
  const root = document.getElementById("app");
  if (mfaState) {
    root.innerHTML = `
      <div class="login-page">
        <form class="login-card" id="mfa-form">
          <h1>Two-factor authentication</h1>
          <p class="hint">Enter the 6-digit code from your authenticator app.</p>
          <label class="field">
            <span>Authentication code</span>
            <input id="mfa-code" type="text" inputmode="numeric" autocomplete="one-time-code"
              maxlength="6" pattern="[0-9]{6}" required />
          </label>
          ${mfaState.trustAllowed ? `<label class="field checkbox">
            <input id="mfa-trust" type="checkbox" />
            <span>Trust this browser for 90 days</span>
          </label>` : ""}
          <p id="login-error" class="login-error" hidden></p>
          <button type="submit" class="btn primary full-btn">Verify</button>
          <button type="button" id="mfa-back" class="btn secondary full-btn">Back</button>
        </form>
      </div>`;
    root.querySelector("#mfa-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const errEl = root.querySelector("#login-error");
      errEl.hidden = true;
      const code = root.querySelector("#mfa-code").value.trim();
      const trust = root.querySelector("#mfa-trust")?.checked || false;
      try {
        await verifyMfa(mfaState.mfaToken, code, trust);
        mfaState = null;
        onSuccess();
      } catch {
        errEl.textContent = "Invalid code — try again";
        errEl.hidden = false;
      }
    });
    root.querySelector("#mfa-back")?.addEventListener("click", () => {
      mfaState = null;
      renderLogin(onSuccess);
    });
    return;
  }

  root.innerHTML = `
    <div class="login-page">
      <form class="login-card" id="login-form">
        <h1>Tank Costing</h1>
        <p class="hint">Sign in to continue</p>
        <label class="field">
          <span>Email</span>
          <input id="login-email" type="email" autocomplete="username" required />
        </label>
        <label class="field">
          <span>Password</span>
          <input id="login-password" type="password" autocomplete="current-password" required />
        </label>
        <p id="login-error" class="login-error" hidden></p>
        <button type="submit" class="btn primary full-btn">Sign in</button>
      </form>
    </div>`;

  root.querySelector("#login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errEl = root.querySelector("#login-error");
    errEl.hidden = true;
    const email = root.querySelector("#login-email").value.trim();
    const password = root.querySelector("#login-password").value;
    try {
      const result = await login(email, password);
      if (result.mfaRequired) {
        mfaState = { mfaToken: result.mfaToken, trustAllowed: result.trustAllowed };
        renderLogin(onSuccess);
        return;
      }
      onSuccess();
    } catch {
      errEl.textContent = "Invalid email or password";
      errEl.hidden = false;
    }
  });
}
