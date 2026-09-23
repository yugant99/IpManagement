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

export interface MigrationAssessmentSummary {
  id: string;
  source_batch_id: string;
  source: { id: string; source_id: string; source_run_id: string; source_kind: string; envelope_hash: string; ingested_at: string } | null;
  canonical_hash: string;
  domain: string;
  mapping_revision: string;
  authority_revision: string;
  policy_revision: string;
  baseline_version: number;
  input_count: number;
  accepted_count: number;
  rejected_count: number;
  duplicate_count: number;
  added_count: number;
  changed_count: number;
  unchanged_count: number;
  conflicting_count: number;
  active_only_acknowledged: boolean;
  active_only_count: number;
  created_by: string | null;
  created_by_current_principal: boolean;
  created_at: string;
  version: number;
  state: string;
  signer_id: string | null;
  signed_by_current_principal: boolean;
  signed_at: string | null;
  signoff_reason: string | null;
  supersedes_id: string | null;
  supersedes_reason: string | null;
  digest: string;
  current: boolean;
  staleness_reasons: string[];
}

export interface MigrationAssessmentDetail extends MigrationAssessmentSummary {
  rows: { source_record_id: string; matching_key: string; candidate: unknown; active: unknown | null; disposition: "added" | "changed" | "unchanged" | "conflicting"; reason: string }[];
  active_only: { matching_key: string; active: unknown; reason: string }[];
}

export interface MigrationAssessmentPage extends Page<MigrationAssessmentSummary> {
  baseline_version: number;
}

export interface MigrationSignoffReceipt {
  assessment_id: string;
  assessment_digest: string;
  signer_id: string;
  signed_at: string;
  signed_version: number;
}

export interface MigrationMutationResponse {
  assessment: MigrationAssessmentSummary;
  replayed: boolean;
  original_signoff: MigrationSignoffReceipt | null;
}

export interface MigrationOperationReadback {
  found: boolean;
  action: "assessment.create" | "assessment.signoff";
  assessment: MigrationAssessmentDetail | null;
  original_outcome: { assessment_id: string; assessment_digest: string; signer_id?: string; signed_at?: string; signed_version?: number } | null;
}

export type SelectedBatch = Pick<Receipt, "id" | "source_id" | "source_run_id" | "source_kind" | "coverage">;

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
  ledger_version?: number;
  rule_id: string;
  rule_version: number;
  synthetic: true;
  selected_batches: SelectedBatch[];
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

export function loadMigrationAssessments(offset: number, signal: AbortSignal) {
  return request<MigrationAssessmentPage>(`/api/migration-assessments?limit=50&offset=${offset}`, signal);
}

export function loadMigrationAssessment(id: string, signal: AbortSignal) {
  return request<MigrationAssessmentDetail>(`/api/migration-assessments/${encodeURIComponent(id)}`, signal);
}

export function createMigrationAssessment(payload: {
  source_batch_id: string;
  expected_baseline_version: number;
  idempotency_key: string;
  reason: string;
  supersedes_id?: string;
  supersedes_reason?: string;
}, signal: AbortSignal) {
  return request<MigrationMutationResponse>("/api/migration-assessments", signal, false, {
    method: "POST", body: JSON.stringify(payload),
  });
}

export function signoffMigrationAssessment(id: string, payload: {
  expected_version: number;
  expected_digest: string;
  active_only_acknowledged: boolean;
  idempotency_key: string;
  reason: string;
}, signal: AbortSignal) {
  return request<MigrationMutationResponse>(`/api/migration-assessments/${encodeURIComponent(id)}/signoff`, signal, false, {
    method: "POST", body: JSON.stringify(payload),
  });
}

export function readMigrationOperation(action: "assessment.create" | "assessment.signoff", key: string, signal: AbortSignal) {
  const params = new URLSearchParams({ action, idempotency_key: key });
  return request<MigrationOperationReadback>(`/api/migration-assessments/operation-receipt?${params}`, signal);
}
