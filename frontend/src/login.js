import { login } from "./auth.js";

export function renderLogin(onSuccess) {
  const root = document.getElementById("app");
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
      await login(email, password);
      onSuccess();
    } catch (err) {
      errEl.textContent = "Invalid email or password";
      errEl.hidden = false;
    }
  });
}
