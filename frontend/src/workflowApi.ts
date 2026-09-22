import { request } from "./api";
import type { Pool } from "./api";
import type { EvidenceState } from "./firstPathApi";

export interface DemoActor {
  id: string;
  name: string;
  role: string;
  team: string;
  permissions: string[];
}

export interface WorkflowStatus {
  actors: DemoActor[];
  pool: Pool;
  baseline_version: number;
  demo_clock_at: string;
  limitations: string[];
}

export interface CreateAllocation {
  actor_id: string;
  idempotency_key: string;
  pool_id: string;
  candidate: string;
  pool_version: number;
  baseline_version: number;
  owner: string;
  purpose: string;
  reason: string;
  supersedes_request_id?: string;
}

export interface AllocationRequest {
  id: string;
  actor_id: string;
  scope_id: string;
  pool_id: string;
  candidate: string;
  pool_version: number;
  baseline_version: number;
  state: "pending" | "approved" | "rejected";
  allocation_id: string | null;
  created_at: string;
  decided_at: string | null;
  decision_actor_id: string | null;
  decision_reason: string | null;
  downstream_status: "simulated_success" | "simulated_failure" | "not_requested" | null;
  local_outcome: "allocated" | "unchanged";
  payload: CreateAllocation;
}

export interface AllocationDecision {
  actor_id: string;
  action: "approve" | "reject";
  reason: string;
  simulate_failure: boolean;
}

export interface ExceptionFinding {
  id: string;
  run_id: string;
  rule_id: string;
  severity: string;
  evidence_state: EvidenceState;
  explanation: string;
  subject: { id: string; scope_id: string; family: number; cidr: string; scope_name: string };
}

export interface ExceptionRecord {
  id: string;
  run_id: string;
  finding_id: string;
  owner_actor_id: string;
  owner: DemoActor;
  state: "open" | "acknowledged" | "escalated";
  version: number;
  created_at: string;
  updated_at: string;
  handoff_from_actor_id: string | null;
  handoff_at: string | null;
  acknowledged_at: string | null;
  notification_pending: boolean;
  notification_version: number;
  notification_reason: "initial" | "new_discrepancy" | "recurrence" | "handoff" | "owner_reopen";
  episode_count: number;
  material_keys: string[];
  lifecycle_state: "open" | "closed";
  closed_at: string | null;
  evidence_resolution: "resolved" | "active" | "unknown";
  latest_evidence_state: EvidenceState | "missing";
  latest_comparable: boolean;
  latest_evidence_reason: string;
  latest_run_id: string | null;
  latest_finding_id: string | null;
  original_finding: ExceptionFinding;
  latest_finding: ExceptionFinding | null;
  finding: ExceptionFinding;
}

export interface ExceptionAction {
  actor_id: string;
  version: number;
  action: "acknowledge" | "escalate" | "handoff" | "close" | "reopen";
  reason: string;
  recipient_actor_id?: string;
}

export interface AuditEvent {
  id: string;
  created_at: string;
  actor_id: string;
  actor_role: string;
  action: string;
  outcome: string;
  reason: string;
  request_id: string | null;
  subject_id: string | null;
  scope_id: string | null;
  pool_id: string | null;
  address: string | null;
  details: Record<string, unknown>;
}

export function loadWorkflow(signal: AbortSignal) {
  return request<WorkflowStatus>("/api/workflow", signal);
}

export function createAllocation(payload: CreateAllocation, signal: AbortSignal) {
  return request<AllocationRequest>("/api/allocation-requests", signal, false,
    { method: "POST", body: JSON.stringify(payload) });
}

export function decideAllocation(id: string, payload: AllocationDecision, signal: AbortSignal) {
  return request<AllocationRequest>(`/api/allocation-requests/${id}/decision`, signal, false,
    { method: "POST", body: JSON.stringify(payload) });
}

export function actOnException(id: string, payload: ExceptionAction, signal: AbortSignal) {
  return request<ExceptionRecord & { replay: boolean }>(`/api/exceptions/${id}`, signal, false,
    { method: "POST", body: JSON.stringify(payload) });
}
