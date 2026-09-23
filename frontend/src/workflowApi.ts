import { ApiError, request } from "./api";
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
  reservation_id?: string;
  service_reference?: string;
  reservation_version?: number;
}

export interface AllocationRequest {
  id: string;
  actor_id: string;
  idempotency_key: string;
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
  reservation_id: string | null;
  payload: CreateAllocation;
}

export interface AllocationDecision {
  actor_id: string;
  action: "approve" | "reject";
  reason: string;
  simulate_failure?: boolean;
}

export interface ReservationSummary {
  id: string;
  scope_id: string;
  prefix_id: string;
  pool_id: string;
  family: number;
  address: string;
  owner_reference: string;
  service_reference: string;
  created_by: string | null;
  reason: string;
  created_at: string;
  expires_at: string;
  version: number;
  policy_revision: string;
  state: string;
  converted_allocation_id: string | null;
  released_at: string | null;
  synthetic: boolean;
}

export interface ReservationHistoryEntry {
  id: string;
  reservation_id: string;
  version: number;
  action: string;
  actor_id: string | null;
  occurred_at: string;
  reason: string;
  before: Record<string, unknown> | null;
  after: Record<string, unknown>;
}

export interface ReservationDetail extends ReservationSummary {
  history: ReservationHistoryEntry[];
}

export interface CreateReservation {
  actor_id: string;
  idempotency_key: string;
  pool_id: string;
  candidate: string;
  pool_version: number;
  baseline_version: number;
  owner_reference: string;
  service_reference: string;
  reason: string;
  duration_hours: number;
}

export interface ExtendReservation {
  actor_id: string;
  idempotency_key: string;
  expected_version: number;
  expected_pool_version: number;
  expected_baseline_version: number;
  duration_hours: number;
  reason: string;
}

export interface ReleaseRequest {
  id: string;
  reservation_id: string;
  reservation_version: number;
  requester_id: string | null;
  reason: string;
  expected_pool_version: number;
  expected_baseline_version: number;
  state: string;
  created_at: string;
  decided_at: string | null;
  approver_id: string | null;
  decision_reason: string | null;
  synthetic: boolean;
}

export interface ProposeRelease {
  actor_id: string;
  idempotency_key: string;
  expected_version: number;
  expected_pool_version: number;
  expected_baseline_version: number;
  reason: string;
}

export interface DecideRelease {
  actor_id: string;
  idempotency_key: string;
  action: "approve" | "reject";
  expected_version: number;
  expected_pool_version: number;
  expected_baseline_version: number;
  reason: string;
}

export type ReservationOperationAction =
  | "reservation.create"
  | "reservation.extend"
  | "reservation.release.propose"
  | "reservation.release.decision";

export interface ReservationOperationReadback {
  found: boolean;
  action: ReservationOperationAction;
  original_outcome: ReservationSummary | ReleaseRequest | null;
  current_reservation: ReservationSummary | null;
  current_release_request: ReleaseRequest | null;
}

export interface TicketRouteAssignment {
  assignment_version: number;
  configuration_revision: string;
  route_revision: string;
  team: string | null;
  reason: string | null;
  assigned_at: string;
  assigned_by: string | null;
}

export interface TicketAttempt {
  id: string;
  ordinal: number;
  route_assignment_version: number;
  synthetic_scenario: "success" | "definitive_failure" | "committed_response_lost" | "no_effect_response_lost";
  started_at: string;
  observation_deadline_at: string;
  ended_at: string | null;
  result: "pending" | "unknown" | "delivered" | "failed";
  reason: string | null;
  observed_ticket_id: string | null;
  observed_effect_id: string | null;
}

export interface TicketHandoffEvent {
  id: string;
  event_type: "readback" | "recipient_acknowledgement";
  outcome: string;
  resolution: string | null;
  attempt_id: string | null;
  effect_id: string | null;
  returned_ticket_id: string | null;
  error_code: string | null;
  acknowledgement_mode: string | null;
  occurred_at: string;
  actor_id: string | null;
}

export interface TicketHandoffSummary {
  id: string;
  domain: string;
  source_request_id: string;
  source_request_state: string;
  action: "allocation.request";
  correlation: string;
  business_payload_digest: string;
  contract_version: "internal-ticket-simulator/v1";
  mode: "simulated";
  state: "pending" | "routing_blocked" | "unknown" | "delivered" | "failed";
  version: number;
  created_at: string;
  current_route_assignment_version: number;
  route: TicketRouteAssignment;
  attempt_limit: number;
  attempts_used: number;
  attempts_remaining: number;
  observation_budget_seconds: number;
  latest_attempt: TicketAttempt | null;
  readback_required: boolean;
  resolution_reason: string | null;
  recipient_acknowledged: boolean;
  provisioning_status: "not_requested";
  label: string;
  simulated: boolean;
  synthetic: boolean;
  availability_evaluated: boolean;
  attempt_allowed: boolean | null;
  attempt_block_reason: string | null;
  reassignment_allowed: boolean | null;
}

export interface TicketHandoffDetail extends TicketHandoffSummary {
  business_payload: Record<string, string | number>;
  route_history: TicketRouteAssignment[];
  attempts: TicketAttempt[];
  events: TicketHandoffEvent[];
}

export interface TicketAttemptOperation {
  phase: "reserve" | "effect" | "observe";
  attempt: TicketAttempt;
  effect_phase_recorded?: boolean | null;
}

export interface TicketAssignmentOperation {
  phase: "reassign";
  assignment: TicketRouteAssignment;
}

export interface TicketEventOperation {
  phase: "readback" | "acknowledge";
  event: TicketHandoffEvent;
}

export interface TicketHandoffMutation {
  handoff: TicketHandoffDetail;
  operation: TicketAttemptOperation | TicketAssignmentOperation | TicketEventOperation;
}

export type TicketOperationAction = "ticket.attempt" | "ticket.reassign" | "ticket.readback" | "ticket.acknowledge";

export interface TicketHandoffOriginalOperation {
  phase: "reserve" | "reassign" | "readback" | "acknowledge";
  attempt?: TicketAttempt | null;
  assignment?: TicketRouteAssignment | null;
  event?: TicketHandoffEvent | null;
}

export interface TicketHandoffOperationReadback {
  found: boolean;
  action: TicketOperationAction;
  original_operation: TicketHandoffOriginalOperation | null;
  current_handoff: TicketHandoffDetail | null;
}

export interface AttemptHandoff {
  actor_id: string;
  expected_version: number;
  idempotency_key: string;
  synthetic_scenario: "success" | "definitive_failure" | "committed_response_lost" | "no_effect_response_lost";
}

export interface ReadbackHandoff {
  actor_id: string;
  expected_version: number;
  idempotency_key: string;
  correlation: string;
  business_payload_digest: string;
}

export interface AcknowledgeHandoff extends ReadbackHandoff {
  effect_id: string;
  ticket_id: string;
  acknowledgement_mode: "simulated";
}

export interface ReassignHandoff {
  actor_id: string;
  expected_version: number;
  idempotency_key: string;
  reason: string;
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

function confirmedAllocation(value: AllocationRequest): AllocationRequest {
  if (!value || typeof value.id !== "string" || !value.id || !["pending", "approved", "rejected"].includes(value.state)
    || !value.payload || !["allocated", "unchanged"].includes(value.local_outcome)
    || typeof value.actor_id !== "string") {
    throw new ApiError("The allocation response did not confirm a saved request. Retry the same operation.", "INVALID_RESPONSE");
  }
  return value;
}

export function loadAllocationRequest(id: string, signal: AbortSignal) {
  return request<AllocationRequest>(`/api/allocation-requests/${encodeURIComponent(id)}`, signal).then(confirmedAllocation);
}

export function findAllocationByKey(key: string, signal: AbortSignal) {
  return request<{ items: AllocationRequest[]; total: number; limit: number; offset: number }>(
    `/api/allocation-requests?idempotency_key=${encodeURIComponent(key)}&limit=20`, signal);
}

export async function createAllocation(payload: CreateAllocation, signal: AbortSignal) {
  const result = confirmedAllocation(await request<AllocationRequest>("/api/allocation-requests", signal, false,
    { method: "POST", body: JSON.stringify(payload) }));
  if (result.actor_id !== payload.actor_id || result.candidate !== String(payload.candidate).trim()
    || result.payload.idempotency_key !== payload.idempotency_key) {
    throw new ApiError("The allocation response belongs to a different request. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}

export async function decideAllocation(id: string, payload: AllocationDecision, signal: AbortSignal) {
  const result = confirmedAllocation(await request<AllocationRequest>(`/api/allocation-requests/${encodeURIComponent(id)}/decision`, signal, false,
    { method: "POST", body: JSON.stringify(payload) }));
  const expected = payload.action === "approve" ? "approved" : "rejected";
  if (result.id !== id || result.state !== expected
    || result.decision_actor_id !== payload.actor_id || (result.decision_reason ?? "") !== payload.reason.trim()) {
    throw new ApiError("The response did not confirm this allocation decision. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}

function confirmedReservation(value: ReservationSummary): ReservationSummary {
  if (!value || typeof value.id !== "string" || !value.id || typeof value.address !== "string"
    || !Number.isInteger(value.version) || value.version < 1 || typeof value.state !== "string") {
    throw new ApiError("The reservation response did not confirm a saved hold. Retry the same operation.", "INVALID_RESPONSE");
  }
  return value;
}

export function listReservations(limit: number, offset: number, signal: AbortSignal) {
  return request<{ items: ReservationSummary[]; total: number; limit: number; offset: number }>(
    `/api/reservations?limit=${limit}&offset=${offset}`, signal);
}

export function loadReservation(id: string, signal: AbortSignal) {
  return request<ReservationDetail>(`/api/reservations/${encodeURIComponent(id)}`, signal).then(value => {
    confirmedReservation(value);
    if (!Array.isArray(value.history)) {
      throw new ApiError("The reservation detail is missing its history. Retry the same operation.", "INVALID_RESPONSE");
    }
    return value;
  });
}

export async function createReservation(payload: CreateReservation, signal: AbortSignal) {
  const result = confirmedReservation(await request<ReservationSummary>("/api/reservations", signal, false,
    { method: "POST", body: JSON.stringify(payload) }));
  if (result.pool_id !== payload.pool_id || result.address !== payload.candidate) {
    throw new ApiError("The reservation response belongs to a different hold. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}

export async function extendReservation(id: string, payload: ExtendReservation, signal: AbortSignal) {
  const result = confirmedReservation(await request<ReservationSummary>(`/api/reservations/${encodeURIComponent(id)}/extend`, signal, false,
    { method: "POST", body: JSON.stringify(payload) }));
  if (result.id !== id) {
    throw new ApiError("The extension response belongs to a different hold. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}

function confirmedRelease(value: ReleaseRequest): ReleaseRequest {
  if (!value || typeof value.id !== "string" || !value.id || typeof value.reservation_id !== "string"
    || !["pending", "approved", "rejected"].includes(value.state)) {
    throw new ApiError("The release response did not confirm a saved proposal. Retry the same operation.", "INVALID_RESPONSE");
  }
  return value;
}

export function listReleaseRequests(reservationId: string, limit: number, offset: number, signal: AbortSignal) {
  return request<{ items: ReleaseRequest[]; total: number; limit: number; offset: number }>(
    `/api/reservations/${encodeURIComponent(reservationId)}/release-requests?limit=${limit}&offset=${offset}`, signal);
}

export function loadReleaseRequest(reservationId: string, requestId: string, signal: AbortSignal) {
  return request<ReleaseRequest>(
    `/api/reservations/${encodeURIComponent(reservationId)}/release-requests/${encodeURIComponent(requestId)}`, signal)
    .then(value => {
      const saved = confirmedRelease(value);
      if (saved.id !== requestId || saved.reservation_id !== reservationId) {
        throw new ApiError("The release detail belongs to a different proposal. Retry the same operation.", "INVALID_RESPONSE");
      }
      return saved;
    });
}

export async function proposeRelease(reservationId: string, payload: ProposeRelease, signal: AbortSignal) {
  const result = confirmedRelease(await request<ReleaseRequest>(
    `/api/reservations/${encodeURIComponent(reservationId)}/release-requests`, signal, false,
    { method: "POST", body: JSON.stringify(payload) }));
  if (result.reservation_id !== reservationId) {
    throw new ApiError("The release proposal belongs to a different hold. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}

export async function decideRelease(reservationId: string, requestId: string, payload: DecideRelease, signal: AbortSignal) {
  const result = confirmedRelease(await request<ReleaseRequest>(
    `/api/reservations/${encodeURIComponent(reservationId)}/release-requests/${encodeURIComponent(requestId)}/decision`,
    signal, false, { method: "POST", body: JSON.stringify(payload) }));
  const expected = payload.action === "approve" ? "approved" : "rejected";
  if (result.id !== requestId || result.reservation_id !== reservationId || result.state !== expected
    || result.approver_id !== payload.actor_id || (result.decision_reason ?? "") !== payload.reason.trim()) {
    throw new ApiError("The response did not confirm this release decision. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}

export function readReservationOperation(action: ReservationOperationAction, key: string, reservationId: string | null, signal: AbortSignal) {
  const params = new URLSearchParams({ action, idempotency_key: key });
  if (action === "reservation.release.propose" && reservationId) params.set("reservation_id", reservationId);
  return request<ReservationOperationReadback>(`/api/reservation-operations?${params}`, signal);
}

function confirmedHandoff(value: TicketHandoffDetail): TicketHandoffDetail {
  if (!value || typeof value.id !== "string" || !value.id || typeof value.correlation !== "string"
    || typeof value.business_payload_digest !== "string" || !Number.isInteger(value.version) || value.version < 1
    || !Number.isInteger(value.attempt_limit) || !Array.isArray(value.attempts) || !Array.isArray(value.events)) {
    throw new ApiError("The ticket handoff response is incomplete. Retry the same operation.", "INVALID_RESPONSE");
  }
  return value;
}

export function listHandoffs(limit: number, offset: number, sourceRequestId: string | null, signal: AbortSignal) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (sourceRequestId) params.set("source_request_id", sourceRequestId);
  return request<{ items: TicketHandoffSummary[]; total: number; limit: number; offset: number }>(
    `/api/handoffs?${params}`, signal);
}

export function loadHandoff(id: string, signal: AbortSignal) {
  return request<TicketHandoffDetail>(`/api/handoffs/${encodeURIComponent(id)}`, signal).then(confirmedHandoff);
}

function confirmedMutation(value: TicketHandoffMutation, id: string): TicketHandoffMutation {
  if (!value || !value.handoff || !value.operation || value.handoff.id !== id) {
    throw new ApiError("The ticket response belongs to a different handoff. The exact retry is retained.", "INVALID_RESPONSE");
  }
  confirmedHandoff(value.handoff);
  return value;
}

export async function attemptHandoff(id: string, payload: AttemptHandoff, signal: AbortSignal) {
  const result = await request<TicketHandoffMutation>(`/api/handoffs/${encodeURIComponent(id)}/attempt`, signal, false,
    { method: "POST", body: JSON.stringify(payload) });
  return confirmedMutation(result, id);
}

export async function readbackHandoff(id: string, payload: ReadbackHandoff, signal: AbortSignal) {
  const result = await request<TicketHandoffMutation>(`/api/handoffs/${encodeURIComponent(id)}/readback`, signal, false,
    { method: "POST", body: JSON.stringify(payload) });
  return confirmedMutation(result, id);
}

export async function acknowledgeHandoff(id: string, payload: AcknowledgeHandoff, signal: AbortSignal) {
  const result = await request<TicketHandoffMutation>(`/api/handoffs/${encodeURIComponent(id)}/acknowledge`, signal, false,
    { method: "POST", body: JSON.stringify(payload) });
  return confirmedMutation(result, id);
}

export async function reassignHandoff(id: string, payload: ReassignHandoff, signal: AbortSignal) {
  const result = await request<TicketHandoffMutation>(`/api/handoffs/${encodeURIComponent(id)}/reassign`, signal, false,
    { method: "POST", body: JSON.stringify(payload) });
  return confirmedMutation(result, id);
}

export function readHandoffOperation(action: TicketOperationAction, key: string, signal: AbortSignal) {
  const params = new URLSearchParams({ action, idempotency_key: key });
  return request<TicketHandoffOperationReadback>(`/api/handoff-operations?${params}`, signal);
}

export function actOnException(id: string, payload: ExceptionAction, signal: AbortSignal) {
  return request<ExceptionRecord & { replay: boolean }>(`/api/exceptions/${id}`, signal, false,
    { method: "POST", body: JSON.stringify(payload) });
}
