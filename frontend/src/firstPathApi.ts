import { request } from "./api";
import type { Origin } from "./api";

export type EvidenceState = "anomalous" | "healthy" | "unknown" | "not_applicable";

export interface Coverage {
  scope_id: string;
  kind?: "interval" | "snapshot";
  window_start_at: string;
  window_end_at: string;
  declared_complete: boolean;
  effective_complete: boolean;
  batch_id?: string;
  source_id?: string;
  source_run_id?: string;
}

export interface Receipt {
  id: string;
  sequence: number;
  source_id: string;
  source_run_id: string;
  source_kind: "routing" | "route_policy" | "dhcp" | "inventory_staged";
  ingested_at: string;
  demo_clock_at: string;
  application_status: "complete" | "partial" | "staged";
  input_rows: number;
  accepted_rows: number;
  rejected_rows: number;
  duplicate_rows: number;
  synthetic: true;
  coverage: Coverage[];
  limitations: string[];
  reconciliation?: { batch_id: string; status: "succeeded" | "busy" | "failed" | "skipped"; run_id?: string; replay: boolean; audit_recorded?: boolean; error?: { code: string; message: string } };
}

export interface SourceCatalogEntry {
  source_id: string;
  source_name: string | null;
  owner: string | null;
  source_kind: "routing" | "route_policy" | "dhcp" | "inventory_staged";
  authority: string;
  authority_status: "declared" | "not_applicable";
  scope_id: string | null;
  source_run_id: string;
  batch_id: string;
  application_status: "complete" | "partial" | "staged";
  rejection_status: "accepted" | "rejected";
  rejected_rows: number;
  duplicate_rows: number;
  evaluated_at: string;
  freshness: "fresh" | "stale" | "not_applicable";
  completeness: "complete" | "partial" | "unknown";
  coverage_grain: string;
  window_start_at: string | null;
  window_end_at: string | null;
  declared_complete: boolean | null;
  effective_complete: boolean | null;
  references: { batch_id: string; receipt_id: string };
}

export type SourceCatalogResponse = { items: SourceCatalogEntry[]; total: number; limit: number; offset: number; evaluated_at?: string; limitations?: string[] };

export interface SourceRecord {
  id: string;
  batch_id: string;
  row_number: number;
  source_record_id: string | null;
  status: "accepted" | "rejected" | "duplicate";
  reason: string | null;
  raw: unknown;
  typed: unknown;
}

export interface InputReference {
  kind: string;
  batch_id?: string;
  record_id?: string;
  source_id: string;
  source_run_id: string;
  source_record_id?: string;
  audit_id?: string;
}

export interface Finding {
  id: string;
  run_id: string;
  rule_id: string;
  rule_version: number;
  subject: {
    id: string;
    scope_id: string;
    scope_name: string;
    family: 4 | 6;
    cidr: string;
    version: number;
    origin: Origin;
  };
  severity: "critical" | "high" | "warning";
  evidence_state: EvidenceState;
  explanation: string;
  input_references: InputReference[];
  evaluated_window: { kind: string; start_at: string; end_at: string; interval_convention: string };
  limitations: string[];
  proposed_action: string;
  policy: Record<string, unknown> | null;
  observations?: unknown[];
  coverage: Coverage[];
}

export interface RunSummary {
  id: string;
  created_at: string;
  demo_clock_at: string;
  ledger_version: number;
  rule_id: string;
  rule_version: number;
  synthetic: true;
  selected_batches: Receipt[];
  overview: { total: number; anomalous: number; healthy: number; unknown: number; not_applicable: number };
}

export interface SavedRun extends RunSummary { findings: Finding[] }

export async function uploadSource(body: string, signal: AbortSignal) {
  let replay = false;
  const receipt = await request<Receipt>("/api/imports", signal, false, {
    method: "POST", body,
    onResponse: (response) => { replay = response.headers.get("X-Import-Replay") === "true"; },
  });
  return { receipt, replay };
}

export async function uploadSourceWithReconciliation(body: string, signal: AbortSignal, reconcileAfterImport: boolean) {
  let replay = false;
  const receipt = await request<Receipt>(`/api/imports${reconcileAfterImport ? "?reconcile_after_import=true" : ""}`, signal, false, {
    method: "POST", body,
    onResponse: (response) => { replay = response.headers.get("X-Import-Replay") === "true"; },
  });
  return { receipt, replay };
}

export function computeRun(signal: AbortSignal) {
  return request<SavedRun>("/api/runs", signal, false, { method: "POST" });
}
