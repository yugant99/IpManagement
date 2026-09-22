export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface ReadinessStatus {
  process_ready: boolean;
  schema_ready: boolean;
  data_ready: boolean;
  static_ready: boolean;
  configuration_ready: boolean;
  domain_state_compatible: boolean;
  reasons: string[];
}

export interface AccessContext {
  principal_id: string;
  roles: string[];
  domains: string[];
  selected_domain: string | null;
  configuration_revision: number;
  configuration_digest: string;
  policy_revision: string;
  is_evidence_coordinator: boolean;
}

export interface Scope {
  id: string;
  name: string;
  namespace: string;
  domain: string;
  region: string;
  managed_cidrs: string[];
  synthetic: true;
}

export interface Origin {
  source_id: string;
  source_run_id: string;
  source_record_id: string;
  observed_at: string;
  ingested_at: string;
  synthetic: true;
}

export interface Prefix {
  id: string;
  scope_id: string;
  scope_name: string;
  family: 4 | 6;
  cidr: string;
  parent_id: string | null;
  owner: string;
  purpose: string;
  tags: string[];
  custom_fields: Record<string, string>;
  version: number;
  address_count: string;
  origin: Origin;
}

interface AddressRange { start: string; end: string }

export interface Pool {
  id: string;
  scope_id: string;
  prefix_id: string;
  family: 4 | 6;
  name: string;
  management_mode: "dhcp" | "static";
  allocation_authority: "local" | "external";
  ranges: AddressRange[];
  exclusions: AddressRange[];
  pool_version: number;
  capacity: string;
  origin: Origin;
}

export interface Allocation {
  id: string;
  scope_id: string;
  prefix_id: string;
  pool_id: string | null;
  family: 4 | 6;
  address: string;
  owner: string;
  purpose: string;
  origin: Origin;
}

export interface PrefixDetail extends Prefix {
  pools: Pool[];
  allocations: Allocation[];
}

export class ApiError extends Error {
  constructor(message: string, public code: string, public requestId?: string) {
    super(message);
    this.name = "ApiError";
  }
}

type Session = { token: string; context: AccessContext; epoch: number };
let session: Session | null = null;
let epoch = 0;
const listeners = new Set<(reason: "revoked" | "stale") => void>();
const activeControllers = new Set<AbortController>();

export function currentContext(): AccessContext {
  if (!session) throw new ApiError("Sign in and select a permitted domain.", "AUTH_REQUIRED");
  return session.context;
}

export function hasRole(role: string): boolean {
  return currentContext().roles.includes(role.toLowerCase());
}

export function onSessionInvalidated(listener: (reason: "revoked" | "stale") => void): () => void {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
}

export function clearSession(): void {
  epoch += 1;
  session = null;
  activeControllers.forEach(controller => controller.abort());
}

export function installSession(token: string, context: AccessContext): number {
  if (!context.selected_domain || !context.domains.includes(context.selected_domain) || context.is_evidence_coordinator) {
    throw new ApiError("Select a permitted ordinary domain.", "ACCESS_CONTEXT_INVALID");
  }
  clearSession();
  session = { token, context, epoch };
  return epoch;
}

function invalidate(reason: "revoked" | "stale", captured: Session): void {
  if (session !== captured) return;
  clearSession();
  listeners.forEach((listener) => listener(reason));
}

function ensureCurrent(captured: Session, signal: AbortSignal): void {
  if (signal.aborted || session !== captured || epoch !== captured.epoch) {
    throw new ApiError("The selected access context changed. Reload this view.", "SESSION_CHANGED");
  }
}

function responseContext(response: Response, captured: Session): void {
  const revision = response.headers.get("X-IPAM-Configuration-Revision");
  const digest = response.headers.get("X-IPAM-Configuration-Digest");
  if (revision !== String(captured.context.configuration_revision) || digest !== captured.context.configuration_digest) {
    invalidate("stale", captured);
    throw new ApiError("Access configuration changed while this response was in flight. Revalidate before readback.", "SESSION_CHANGED");
  }
}

function responseError(response: Response, body: unknown): ApiError {
  const data = body as { error?: { message?: string; code?: string; request_id?: string; details?: { reason?: string } } } | null;
  const message = data?.error?.message ?? `Request failed (HTTP ${response.status}).`;
  const reason = data?.error?.details?.reason;
  return new ApiError(typeof reason === "string" ? `${message} ${reason}` : message,
    data?.error?.code ?? "REQUEST_FAILED", data?.error?.request_id ?? response.headers.get("X-Request-ID") ?? undefined);
}

export async function accessContext(token: string, signal: AbortSignal, domain?: string): Promise<AccessContext> {
  const response = await fetch("/api/access-context", { signal, headers: {
    Authorization: `Bearer ${token}`, Accept: "application/json", ...(domain ? { "X-IPAM-Domain": domain } : {}),
  } });
  if (response.status === 401) throw new ApiError("Access expired or was revoked. Enter a current token.", "AUTH_REQUIRED");
  const body = await response.json();
  if (!response.ok) throw responseError(response, body);
  const context = body as AccessContext;
  if (!context || typeof context.principal_id !== "string" || !Array.isArray(context.roles)
    || !Array.isArray(context.domains) || typeof context.configuration_revision !== "number"
    || typeof context.configuration_digest !== "string" || context.selected_domain !== (domain ?? null)) {
    throw new ApiError("The access context response is incomplete.", "INVALID_RESPONSE");
  }
  if (response.headers.get("X-IPAM-Configuration-Revision") !== String(context.configuration_revision)
    || response.headers.get("X-IPAM-Configuration-Digest") !== context.configuration_digest) {
    throw new ApiError("The access context configuration did not match its response headers.", "INVALID_RESPONSE");
  }
  return context;
}

export async function downloadProtected(path: string, filename: string, signal: AbortSignal,
  expectedHeader?: { name: string; value: string }): Promise<void> {
  const captured = session;
  if (!captured) throw new ApiError("Sign in and select a permitted domain.", "AUTH_REQUIRED");
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal.addEventListener("abort", abort, { once: true });
  if (signal.aborted) abort();
  activeControllers.add(controller);
  try {
    const response = await fetch(path, { signal: controller.signal, headers: {
      Accept: filename.endsWith(".csv") ? "text/csv" : "application/json",
      Authorization: `Bearer ${captured.token}`, "X-IPAM-Domain": captured.context.selected_domain!,
      "X-IPAM-Configuration-Revision": String(captured.context.configuration_revision),
      "X-IPAM-Configuration-Digest": captured.context.configuration_digest,
    } });
    ensureCurrent(captured, signal);
    if (response.status === 401) { invalidate("revoked", captured); throw new ApiError("Your access has expired or was revoked. Sign in again.", "AUTH_REQUIRED"); }
    if (response.status === 409) {
      const body = await response.json().catch(() => null);
      ensureCurrent(captured, signal);
      if ((body as { error?: { code?: string } } | null)?.error?.code === "ACCESS_CONTEXT_STALE") invalidate("stale", captured);
      throw responseError(response, body);
    }
    responseContext(response, captured);
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      ensureCurrent(captured, signal);
      throw responseError(response, body);
    }
    if (expectedHeader && response.headers.get(expectedHeader.name) !== expectedHeader.value) {
      throw new ApiError("The export did not match the displayed saved version. Reload before retrying.", "INVALID_RESPONSE");
    }
    const blob = await response.blob();
    ensureCurrent(captured, signal);
    const url = URL.createObjectURL(blob);
    try {
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
    } finally { window.setTimeout(() => URL.revokeObjectURL(url), 1000); }
  } finally {
    activeControllers.delete(controller);
    signal.removeEventListener("abort", abort);
  }
}

// A bounded request keeps an unavailable local backend from leaving a loading screen forever.
export async function request<T>(path: string, signal: AbortSignal, readHealth = false, options: {
  method?: "GET" | "POST";
  body?: string;
  onResponse?: (response: Response) => void;
} = {}): Promise<T> {
  const captured = session;
  if (!captured) throw new ApiError("Sign in and select a permitted domain.", "AUTH_REQUIRED");
  const controller = new AbortController();
  activeControllers.add(controller);
  let timedOut = false;
  const abort = () => controller.abort();
  signal.addEventListener("abort", abort, { once: true });
  if (signal.aborted) abort();
  const timeout = window.setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, 12000);
  try {
    const response = await fetch(path, {
      signal: controller.signal,
      method: options.method ?? "GET",
      body: options.body,
      headers: { Accept: "application/json", Authorization: `Bearer ${captured.token}`,
        "X-IPAM-Domain": captured.context.selected_domain!,
        "X-IPAM-Configuration-Revision": String(captured.context.configuration_revision),
        "X-IPAM-Configuration-Digest": captured.context.configuration_digest,
        ...(options.body !== undefined ? { "Content-Type": "application/json" } : {}) },
    });
    ensureCurrent(captured, signal);
    const requestId = response.headers.get("X-Request-ID") ?? undefined;
    if (response.status === 401) {
      invalidate("revoked", captured);
      throw new ApiError("Your access has expired or was revoked. Sign in again.", "AUTH_REQUIRED", requestId);
    }
    if (!response.headers.get("content-type")?.includes("application/json")) {
      throw new ApiError("The API did not return JSON. Check that the backend is running and the API proxy is configured.", "INVALID_RESPONSE", requestId);
    }
    const body = await response.json();
    ensureCurrent(captured, signal);
    if (response.status === 409 && body?.error?.code === "ACCESS_CONTEXT_STALE") {
      invalidate("stale", captured);
      throw new ApiError("Access configuration changed. Revalidate your domain before viewing data.", "ACCESS_CONTEXT_STALE", requestId);
    }
    responseContext(response, captured);
    if (!response.ok && !(readHealth && response.status === 503 && typeof body?.process_ready === "boolean")) throw responseError(response, body);
    options.onResponse?.(response);
    ensureCurrent(captured, signal);
    return body as T;
  } catch (error) {
    if (signal.aborted) throw error;
    if (timedOut) throw new ApiError("The API did not respond within 12 seconds. Check the backend and retry.", "REQUEST_TIMEOUT");
    if (error instanceof ApiError) throw error;
    throw new ApiError("The API could not be reached or its response could not be read. Check the backend and retry.", "CONNECTION_FAILED");
  } finally {
    activeControllers.delete(controller);
    window.clearTimeout(timeout);
    signal.removeEventListener("abort", abort);
  }
}

export async function loadScopes(signal: AbortSignal): Promise<Scope[]> {
  const scopes: Scope[] = [];
  let offset = 0;
  while (true) {
    const page = await request<Page<Scope>>(`/api/scopes?limit=200&offset=${offset}`, signal);
    scopes.push(...page.items);
    offset += page.items.length;
    if (offset >= page.total) return scopes;
    if (page.items.length === 0) throw new ApiError("The scope list is incomplete. Retry to reload the inventory.", "INCOMPLETE_RESPONSE");
  }
}
