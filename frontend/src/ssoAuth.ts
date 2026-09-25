// SSO client. Public endpoints return {enabled:false} when the deployment does
// not configure OIDC; the login button uses that to render itself visibly
// disabled without ever attempting an authorization redirect.

export interface SsoConfig {
  enabled: boolean;
  provider_name: string | null;
}

const HEX64 = /^[0-9a-f]{64}$/;

export async function loadSsoConfig(signal: AbortSignal): Promise<SsoConfig> {
  const response = await fetch("/api/auth/sso/config", { signal, headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`SSO config request failed (HTTP ${response.status}).`);
  const body = await response.json() as unknown;
  if (!body || typeof body !== "object" || typeof (body as SsoConfig).enabled !== "boolean") {
    throw new Error("The SSO config response is malformed.");
  }
  return body as SsoConfig;
}

export function readSsoFragmentCode(): string | null {
  if (typeof window === "undefined") return null;
  const raw = window.location.hash.startsWith("#") ? window.location.hash.slice(1) : window.location.hash;
  if (!raw) return null;
  const parameters = new URLSearchParams(raw);
  const code = parameters.get("sso");
  return code && HEX64.test(code) ? code : null;
}

export function clearSsoFragment(): void {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  url.hash = "";
  window.history.replaceState(null, "", url.toString());
}

export function beginSsoRedirect(): void {
  window.location.assign("/api/auth/sso/authorize");
}

export async function exchangeSsoCode(code: string, signal: AbortSignal): Promise<string> {
  if (!HEX64.test(code)) throw new Error("The SSO exchange code is malformed.");
  const response = await fetch("/api/auth/sso/exchange", {
    signal, method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ code }),
  });
  const body = await response.json().catch(() => null) as { token?: unknown; error?: { message?: string } } | null;
  if (!response.ok) {
    const message = body?.error?.message ?? `SSO exchange failed (HTTP ${response.status}).`;
    throw new Error(message);
  }
  const token = body?.token;
  if (typeof token !== "string" || !HEX64.test(token)) throw new Error("The SSO exchange response is malformed.");
  return token;
}

export async function ssoLogout(token: string): Promise<void> {
  await fetch("/api/auth/sso/logout", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
  }).catch(() => {
    // Logout is best-effort. Local session is cleared regardless of upstream response.
  });
}
