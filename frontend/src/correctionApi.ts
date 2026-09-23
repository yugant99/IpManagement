import { ApiError, request } from "./api";
import type { Page, Scope } from "./api";
import type { Finding } from "./firstPathApi";
import type { DemoActor } from "./workflowApi";

export interface CorrectionContext {
  source_run_id: string;
  source_finding: Finding;
  scope: Scope;
  baseline_version: number;
  actors: DemoActor[];
  synthetic: true;
  limitations: string[];
}

export interface CreateCorrection {
  actor_id: string;
  idempotency_key: string;
  scope_id: string;
  source_run_id: string;
  source_finding_id: string;
  expected_baseline_version: number;
  cidr: string;
  owner: string;
  purpose: string;
  reason: string;
}

export interface CorrectionDecision {
  actor_id: string;
  action: "approve" | "reject";
  reason: string;
}

export type ResolutionState = "not_approved" | "pending_reconciliation" | "resolved_by_evidence" | "still_anomalous" | "resolution_unknown";

export interface CorrectionRequest {
  id: string;
  actor_id: string;
  idempotency_key: string;
  scope_id: string;
  source_run_id: string;
  source_finding_id: string;
  baseline_version: number;
  state: "pending" | "approved" | "rejected";
  prefix_id: string | null;
  created_at: string;
  decided_at: string | null;
  decision_actor_id: string | null;
  decision_reason: string | null;
  approved_baseline_version: number | null;
  result_run_id: string | null;
  payload: CreateCorrection;
  source_finding: Finding;
  result_finding: Finding | null;
  resolution_state: ResolutionState;
  latest_run_id: string | null;
  latest_finding: Finding | null;
  latest_resolution_state: ResolutionState;
  local_outcome: "registered" | "unchanged";
  synthetic: true;
}

export function loadCorrectionContext(runId: string, findingId: string, signal: AbortSignal) {
  const params = new URLSearchParams({ run_id: runId, finding_id: findingId });
  return request<CorrectionContext>(`/api/correction-context?${params}`, signal);
}

export function loadCorrection(id: string, signal: AbortSignal) {
  return request<CorrectionRequest>(`/api/correction-requests/${encodeURIComponent(id)}`, signal);
}

export function findCorrectionByKey(key: string, signal: AbortSignal) {
  return request<Page<CorrectionRequest>>(`/api/correction-requests?idempotency_key=${encodeURIComponent(key)}&limit=20`, signal);
}

function confirmed(value: CorrectionRequest): CorrectionRequest {
  if (!value || typeof value.id !== "string" || !value.id || !["pending", "approved", "rejected"].includes(value.state)
    || !value.payload || !value.source_finding || value.synthetic !== true
    || !["registered", "unchanged"].includes(value.local_outcome)
    || typeof value.actor_id !== "string" || typeof value.source_run_id !== "string") {
    throw new ApiError("The correction response did not confirm a saved request. Retry the same operation.", "INVALID_RESPONSE");
  }
  return value;
}

export async function createCorrection(payload: CreateCorrection, signal: AbortSignal) {
  const result = confirmed(await request<CorrectionRequest>("/api/correction-requests", signal, false,
    { method: "POST", body: JSON.stringify(payload) }));
  if (result.actor_id !== payload.actor_id || result.idempotency_key !== payload.idempotency_key
    || result.source_run_id !== payload.source_run_id || result.source_finding_id !== payload.source_finding_id) {
    throw new ApiError("The correction response belongs to a different proposal. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}

export async function decideCorrection(id: string, payload: CorrectionDecision, signal: AbortSignal) {
  const result = confirmed(await request<CorrectionRequest>(`/api/correction-requests/${encodeURIComponent(id)}/decision`, signal, false,
    { method: "POST", body: JSON.stringify(payload) }));
  if (result.id !== id || result.state !== (payload.action === "approve" ? "approved" : "rejected")
    || result.decision_actor_id !== payload.actor_id || result.decision_reason !== payload.reason.trim()) {
    throw new ApiError("The response did not confirm this correction decision. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}
