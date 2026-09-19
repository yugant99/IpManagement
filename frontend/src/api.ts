export interface Page<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Health {
  status: "ready" | "setup_needed" | "error";
  process_ready: boolean;
  schema_ready: boolean;
  data_ready: boolean;
  static_ready: boolean;
  code: string | null;
  reason: string | null;
  schema_version: number | null;
  contract_revision: string;
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

// A bounded request keeps an unavailable local backend from leaving a loading screen forever.
export async function request<T>(path: string, signal: AbortSignal, readHealth = false, options: {
  method?: "GET" | "POST";
  body?: string;
  onResponse?: (response: Response) => void;
} = {}): Promise<T> {
  const controller = new AbortController();
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
      headers: { Accept: "application/json", ...(options.body !== undefined ? { "Content-Type": "application/json" } : {}) },
    });
    const requestId = response.headers.get("X-Request-ID") ?? undefined;
    if (!response.headers.get("content-type")?.includes("application/json")) {
      throw new ApiError("The API did not return JSON. Check that the backend is running and the API proxy is configured.", "INVALID_RESPONSE", requestId);
    }
    const body = await response.json();
    if (!response.ok && !(readHealth && response.status === 503 && typeof body?.status === "string")) {
      const message = body?.error?.message ?? `Request failed (HTTP ${response.status}).`;
      const reason = body?.error?.details?.reason;
      throw new ApiError(typeof reason === "string" ? `${message} ${reason}` : message, body?.error?.code ?? "REQUEST_FAILED", body?.error?.request_id ?? requestId);
    }
    options.onResponse?.(response);
    return body as T;
  } catch (error) {
    if (signal.aborted) throw error;
    if (timedOut) throw new ApiError("The API did not respond within 12 seconds. Check the backend and retry.", "REQUEST_TIMEOUT");
    if (error instanceof ApiError) throw error;
    throw new ApiError("The API could not be reached or its response could not be read. Check the backend and retry.", "CONNECTION_FAILED");
  } finally {
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
