const TOKEN_KEY = "tc_token";
const USER_KEY = "tc_user";

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  const raw = sessionStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setSession(token, user) {
  sessionStorage.setItem(TOKEN_KEY, token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}

export function logout() {
  clearSession();
  window.location.reload();
}

export async function apiFetch(url, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !headers["Content-Type"] && typeof options.body === "string") {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(url, { ...options, headers, credentials: "include" });
  if (response.status === 401 && getToken()) {
    clearSession();
    window.location.reload();
  }
  return response;
}

export async function login(email, password) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error("Invalid email or password");
  }
  const data = await response.json();
  if (data.mfa_required) {
    return { mfaRequired: true, mfaToken: data.mfa_token, trustAllowed: data.trust_allowed };
  }
  setSession(data.access_token, data.user);
  return { mfaRequired: false, user: data.user };
}

export async function verifyMfa(mfaToken, code, trustDevice = false) {
  const response = await fetch("/api/auth/mfa/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mfa_token: mfaToken, code, trust_device: trustDevice }),
    credentials: "include",
  });
  if (!response.ok) throw new Error("Invalid authentication code");
  const data = await response.json();
  setSession(data.access_token, data.user);
  return data.user;
}

export async function fetchMe() {
  const response = await apiFetch("/api/auth/me");
  if (!response.ok) throw new Error("Session expired");
  const user = await response.json();
  setSession(getToken(), user);
  return user;
}

export async function changePassword(currentPassword, newPassword) {
  const response = await apiFetch("/api/auth/change-password", {
    method: "POST",
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Failed to change password");
  }
}

export async function setupMfa() {
  const response = await apiFetch("/api/auth/mfa/setup", { method: "POST" });
  if (!response.ok) throw new Error("Failed to start MFA setup");
  return response.json();
}

export async function confirmMfa(code) {
  const response = await apiFetch("/api/auth/mfa/confirm", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
  if (!response.ok) throw new Error("Invalid code");
}

export async function disableMfa(code) {
  const response = await apiFetch("/api/auth/mfa/disable", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
  if (!response.ok) throw new Error("Invalid code");
}
