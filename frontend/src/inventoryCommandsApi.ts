import { ApiError, request } from "./api";
import type { Page, Prefix, PrefixDetail, Scope } from "./api";

export interface InventoryActor {
  id: string;
  name: string;
  role: string;
  team: string;
  permissions: string[];
}

export interface EditContext {
  prefix: PrefixDetail;
  scope: Scope;
  baseline_version: number;
  children_count: number;
  history_impact: {
    metadata: [];
    structural: { pool_id: string; name: string; cidr: string }[];
  };
}

export interface ChildPreview {
  parent_id: string;
  parent_cidr: string;
  parent_version: number;
  scope_id: string;
  baseline_version: number;
  prefix_length: number;
  total_children: string;
  blocked_children: string;
  free_children: string;
  items: string[];
  limit: number;
  synthetic: true;
}

export interface EditablePrefix {
  actor_id: string;
  reason: string;
  expected_baseline_version: number;
  cidr: string;
  owner: string;
  purpose: string;
  tags: string[];
  custom_fields: Record<string, string>;
}

export interface PrefixMutation {
  prefix: PrefixDetail;
  baseline_version: number;
  audit_id: string;
}

export async function loadScopedPrefixes(scopeId: string, signal: AbortSignal): Promise<Prefix[]> {
  const items: Prefix[] = [];
  let offset = 0;
  while (true) {
    const query = new URLSearchParams({ scope_id: scopeId, limit: "200", offset: String(offset) });
    const page = await request<Page<Prefix>>(`/api/prefixes?${query}`, signal);
    items.push(...page.items);
    offset += page.items.length;
    if (offset >= page.total) return items;
    if (!page.items.length) throw new ApiError("The scoped prefix list is incomplete. Reload inventory.", "INCOMPLETE_RESPONSE");
  }
}

export function loadEditContext(prefixId: string, signal: AbortSignal) {
  return request<EditContext>(`/api/prefixes/${encodeURIComponent(prefixId)}/edit-context`, signal);
}

export function loadChildPreview(parentId: string, prefixLength: number, signal: AbortSignal) {
  return request<ChildPreview>(`/api/prefixes/${encodeURIComponent(parentId)}/child-preview?prefix_length=${prefixLength}&limit=10`, signal);
}

export function createChildPrefix(payload: EditablePrefix & { scope_id: string; parent_id: string; expected_parent_version: number }, signal: AbortSignal) {
  return request<PrefixMutation>("/api/prefixes", signal, false, { method: "POST", body: JSON.stringify(payload) });
}

export function updatePrefix(prefixId: string, payload: EditablePrefix & { expected_version: number }, signal: AbortSignal) {
  return request<PrefixMutation>(`/api/prefixes/${encodeURIComponent(prefixId)}/edit`, signal, false, { method: "POST", body: JSON.stringify(payload) });
}
