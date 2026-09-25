import { request } from "./api";
import type { SourceCatalogEntry } from "./firstPathApi";

export type PlaneId = "assignment" | "presence" | "behavior";
export type MechanismStatus = "loaded_synthetic_baseline" | "imported_synthetic_evidence" | "no_permitted_evidence" | "not_connected";
export type Implementation = "seeded_inventory" | "synthetic_dhcp_import" | "synthetic_routing_import" | null;

export interface Plane { id: PlaneId; name: string; question: string }

// Catalog row for one source and scope, plus batch-grain counts from its authorized saved receipt.
export interface EvidenceRow extends SourceCatalogEntry {
  in_latest_run: boolean;
  receipt: { grain: "batch"; ingested_at: string; input_rows: number; accepted_rows: number } | null;
}

export interface BaselineOrigin { source_id: string | null; source_run_id: string | null; rows: number; latest_ingested_at: string | null }

export interface MechanismScope {
  scope_id: string;
  scope_name: string;
  state: "loaded" | "empty" | "selected" | "missing";
  evidence: EvidenceRow[];
  counts?: { prefixes: number; pools: number; allocations: number };
  origins?: BaselineOrigin[];
  // Presence of intended route policy for this scope; not a per-scope eligibility decision.
  route_policy?: { catalog_selected: boolean; in_latest_run: boolean; latest_run_effective_complete: boolean | null };
}

export interface Mechanism {
  id: string;
  name: string;
  plane: PlaneId;
  establishes: string;
  unlocks: string;
  implementation: Implementation;
  implementation_note: string | null;
  status: MechanismStatus;
  status_label: string;
  scopes: MechanismScope[];
  summary: null | { scopes: number; loaded?: number; empty?: number; missing?: number; fresh?: number; stale?: number; complete?: number; partial?: number };
}

export interface SourceFunction {
  id: string;
  name: string;
  rule_ids: string[];
  requires: string[];
  requires_route_policy?: boolean;
  route_policy_scopes?: { present: number; scopes: number };
  evidence_basis: "source_presence";
  evidence_present: boolean;
}

export interface IntegrationProfile {
  id: string;
  mechanism_id: string;
  demo_only: true;
  profile: string;
  version: string;
  managed_system: string;
  proposed_interface: string;
  status: string;
  last_live_read: string;
  note: string;
}

export interface LatestRun {
  id: string;
  created_at: string;
  demo_clock_at: string;
  rule_id: string | null;
  rule_version: number | null;
  overview: { total: number; anomalous: number; healthy: number; unknown: number; not_applicable: number };
  selected_batch_ids: string[];
  projection: { kind: "selected_domain"; domain: string; scope_ids: string[]; source_run_id: string };
}

export interface EvidenceSources {
  domain: string;
  evaluated_at: string | null;
  synthetic: true;
  manifest_version: number;
  planes: Plane[];
  mechanisms: Mechanism[];
  functions: { available_now: SourceFunction[]; next_unlocks: { mechanism_id: string; name: string; plane: PlaneId; unlocks: string }[] };
  integration_profiles: IntegrationProfile[];
  latest_run: LatestRun | null;
  limitations: string[];
}

export function loadEvidenceSources(signal: AbortSignal): Promise<EvidenceSources> {
  return request<EvidenceSources>("/api/evidence-sources", signal);
}
