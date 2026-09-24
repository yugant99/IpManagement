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
  actor_id: string | null;
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
    || (value.actor_id !== null && typeof value.actor_id !== "string")) {
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

export type NoticeAlertLevel = "alert" | "alarm";
export type NoticeState = "open" | "acknowledged" | "resolved";
export type NoticeRoutingStatus = "assigned" | "unassigned" | "unroutable" | "legacy_unbound";
export type NoticeDeliveryStatus = "awaiting_receipt" | "unassigned" | "recipient_unavailable" | "legacy_unbound" | "acknowledged";
export type NoticeAcknowledgementKind = "recipient_in_app" | "legacy_operator" | null;
export type NoticeCoverage = "complete" | "partial" | "partial_legacy" | "missing_child";
export type NoticeResolutionReason = "reservation_extended" | "reservation_converted" | "approved_local_release" | null;

export interface AssignedNoticeNotification {
  notice_id: string;
  notification_version: number;
  recipient_id: string | null;
  configuration_revision: number;
  configuration_digest: string;
  routing_status: "assigned";
  routing_reason: null;
  issued_at: string;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  acknowledgement_reason: string | null;
  delivery_status: "awaiting_receipt" | "recipient_unavailable" | "acknowledged";
  is_current_recipient: boolean;
  acknowledgement_kind: "recipient_in_app" | null;
  owner_signoff: false;
  in_app_receipt: boolean;
}

export interface UnassignedNoticeNotification {
  notice_id: string;
  notification_version: number;
  recipient_id: null;
  configuration_revision: number;
  configuration_digest: string;
  routing_status: "unassigned";
  routing_reason: "missing_mapping";
  issued_at: string;
  acknowledged_by: null;
  acknowledged_at: null;
  acknowledgement_reason: null;
  delivery_status: "unassigned";
  is_current_recipient: false;
  acknowledgement_kind: null;
  owner_signoff: false;
  in_app_receipt: false;
}

export interface UnroutableNoticeNotification {
  notice_id: string;
  notification_version: number;
  recipient_id: string | null;
  configuration_revision: number;
  configuration_digest: string;
  routing_status: "unroutable";
  routing_reason: "unknown_principal" | "disabled" | "expired" | "not_operator" | "wrong_domain";
  issued_at: string;
  acknowledged_by: null;
  acknowledged_at: null;
  acknowledgement_reason: null;
  delivery_status: "recipient_unavailable";
  is_current_recipient: false;
  acknowledgement_kind: null;
  owner_signoff: false;
  in_app_receipt: false;
}

export interface LegacyNoticeNotification {
  notice_id: string;
  notification_version: number;
  recipient_id: null;
  configuration_revision: null;
  configuration_digest: null;
  routing_status: "legacy_unbound";
  routing_reason: "legacy_unbound";
  issued_at: null;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  acknowledgement_reason: string | null;
  delivery_status: "legacy_unbound";
  is_current_recipient: false;
  acknowledgement_kind: "legacy_operator" | null;
  owner_signoff: false;
  in_app_receipt: false;
}

export type ReservationNoticeNotification =
  | AssignedNoticeNotification
  | UnassignedNoticeNotification
  | UnroutableNoticeNotification
  | LegacyNoticeNotification;

export interface ReservationNotice {
  id: string;
  reservation_id: string;
  episode_number: number;
  policy_revision: string;
  first_due_at: string;
  alert_level: NoticeAlertLevel;
  owner_reference: string;
  state: NoticeState;
  acknowledgement_version: number;
  notification_version: number;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
  acknowledgement_reason: string | null;
  acknowledgement_current: boolean;
  current_notification: ReservationNoticeNotification | null;
  notification_history: ReservationNoticeNotification[];
  notification_history_coverage: NoticeCoverage;
  delivery_status: NoticeDeliveryStatus | null;
  is_current_recipient: boolean;
  acknowledgement_kind: NoticeAcknowledgementKind;
  owner_signoff: false;
  in_app_receipt: boolean;
  resolved_at: string | null;
  resolution_reason: NoticeResolutionReason;
  synthetic: true;
}

export type ReservationNoticeNotificationVersion =
  | (AssignedNoticeNotification & { reservation_id: string; episode_number: number })
  | (UnassignedNoticeNotification & { reservation_id: string; episode_number: number })
  | (UnroutableNoticeNotification & { reservation_id: string; episode_number: number })
  | (LegacyNoticeNotification & { reservation_id: string; episode_number: number });

export interface ReservationNoticeEvaluation {
  evaluated_at: string;
  created_count: number;
  renewed_count: number;
  alarm_upgrade_count: number;
  notices: ReservationNotice[];
  synthetic: true;
}

export interface StaticOccupancyCount {
  count: number;
  unit: "IPv4 addresses";
}

export interface StaticReservedHolds extends StaticOccupancyCount {
  includes_expired: true;
}

export interface CurrentStaticOccupancy {
  metric: "current_static_ipv4_occupancy";
  pool_id: string;
  scope_id: string;
  domain: string;
  family: 4;
  unit: "IPv4 addresses";
  as_of: string;
  components: {
    active_allocations: StaticOccupancyCount;
    reserved_holds: StaticReservedHolds;
    occupied_total: StaticOccupancyCount;
    assignable_capacity: StaticOccupancyCount;
    remaining_assignable: StaticOccupancyCount;
  };
  provenance: {
    source: "current local intended ledger";
    capacity: string;
    allocations: string;
    reservations: string;
    saved_runs_modified: false;
    synthetic: true;
  };
  synthetic: true;
}

export interface AcknowledgeNotice {
  actor_id: string;
  expected_notification_version: number;
  reason: string;
}

function confirmedNotification(value: ReservationNoticeNotification, noticeId: string): ReservationNoticeNotification {
  if (!value || value.notice_id !== noticeId || !Number.isInteger(value.notification_version)
    || value.notification_version < 1 || value.owner_signoff !== false) {
    throw new ApiError("The notice notification did not match its version. Retry the same read.", "INVALID_RESPONSE");
  }
  if (value.routing_status === "assigned") {
    if (value.routing_reason !== null || typeof value.is_current_recipient !== "boolean"
      || typeof value.in_app_receipt !== "boolean") {
      throw new ApiError("The assigned notice binding is inconsistent. Retry the same read.", "INVALID_RESPONSE");
    }
  } else if (value.routing_status === "unassigned") {
    if (value.routing_reason !== "missing_mapping" || value.delivery_status !== "unassigned"
      || value.is_current_recipient !== false || value.in_app_receipt !== false) {
      throw new ApiError("The unassigned notice binding is inconsistent. Retry the same read.", "INVALID_RESPONSE");
    }
  } else if (value.routing_status === "unroutable") {
    if (!["unknown_principal", "disabled", "expired", "not_operator", "wrong_domain"].includes(value.routing_reason ?? "")
      || value.delivery_status !== "recipient_unavailable" || value.is_current_recipient !== false) {
      throw new ApiError("The unroutable notice binding is inconsistent. Retry the same read.", "INVALID_RESPONSE");
    }
  } else if (value.routing_status === "legacy_unbound") {
    if (value.routing_reason !== "legacy_unbound" || value.delivery_status !== "legacy_unbound"
      || value.in_app_receipt !== false) {
      throw new ApiError("The legacy notice binding is inconsistent. Retry the same read.", "INVALID_RESPONSE");
    }
  } else {
    throw new ApiError("The notice notification has an unknown route. Retry the same read.", "INVALID_RESPONSE");
  }
  return value;
}

function confirmedNotice(value: ReservationNotice): ReservationNotice {
  if (!value || typeof value.id !== "string" || !value.id || typeof value.reservation_id !== "string"
    || !value.reservation_id || !Number.isInteger(value.episode_number) || value.episode_number < 1
    || !["alert", "alarm"].includes(value.alert_level) || !["open", "acknowledged", "resolved"].includes(value.state)
    || !Number.isInteger(value.notification_version) || value.notification_version < 1
    || !Number.isInteger(value.acknowledgement_version) || value.acknowledgement_version < 1
    || typeof value.acknowledgement_current !== "boolean" || typeof value.is_current_recipient !== "boolean"
    || typeof value.in_app_receipt !== "boolean" || value.owner_signoff !== false || value.synthetic !== true
    || !Array.isArray(value.notification_history)
    || !["complete", "partial", "partial_legacy", "missing_child"].includes(value.notification_history_coverage)) {
    throw new ApiError("The reservation notice response is incomplete. Retry the same read.", "INVALID_RESPONSE");
  }
  for (const item of value.notification_history) {
    confirmedNotification(item, value.id);
  }
  if (value.current_notification === null) {
    if (value.notification_history_coverage !== "missing_child" || value.delivery_status !== null) {
      throw new ApiError("The notice is missing its current binding. Retry the same read.", "INVALID_RESPONSE");
    }
  } else {
    const current = confirmedNotification(value.current_notification, value.id);
    if (current.notification_version !== value.notification_version
      || current.delivery_status !== value.delivery_status
      || current.is_current_recipient !== value.is_current_recipient
      || current.acknowledgement_kind !== value.acknowledgement_kind
      || current.in_app_receipt !== value.in_app_receipt) {
      throw new ApiError("The notice receipt summary disagrees with its current binding. Retry the same read.", "INVALID_RESPONSE");
    }
  }
  return value;
}

function confirmedEvaluation(value: ReservationNoticeEvaluation): ReservationNoticeEvaluation {
  if (!value || typeof value.evaluated_at !== "string" || !value.evaluated_at
    || !Number.isInteger(value.created_count) || value.created_count < 0
    || !Number.isInteger(value.renewed_count) || value.renewed_count < 0
    || !Number.isInteger(value.alarm_upgrade_count) || value.alarm_upgrade_count < 0
    || value.alarm_upgrade_count > value.renewed_count || !Array.isArray(value.notices)
    || value.synthetic !== true) {
    throw new ApiError("The notice evaluation response is incomplete. Retry the explicit evaluation.", "INVALID_RESPONSE");
  }
  return { ...value, notices: value.notices.map(confirmedNotice) };
}

function confirmedOccupancy(value: CurrentStaticOccupancy): CurrentStaticOccupancy {
  const counts = (item: unknown): item is StaticOccupancyCount =>
    !!item && typeof (item as StaticOccupancyCount).count === "number"
    && Number.isInteger((item as StaticOccupancyCount).count)
    && (item as StaticOccupancyCount).unit === "IPv4 addresses";
  if (!value || value.metric !== "current_static_ipv4_occupancy" || typeof value.pool_id !== "string"
    || typeof value.scope_id !== "string" || typeof value.domain !== "string" || value.family !== 4
    || value.unit !== "IPv4 addresses" || typeof value.as_of !== "string" || value.synthetic !== true
    || !value.components || !counts(value.components.active_allocations)
    || !counts(value.components.reserved_holds)
    || value.components.reserved_holds.includes_expired !== true
    || !counts(value.components.occupied_total) || !counts(value.components.assignable_capacity)
    || !counts(value.components.remaining_assignable) || !value.provenance
    || value.provenance.source !== "current local intended ledger"
    || value.provenance.saved_runs_modified !== false || value.provenance.synthetic !== true) {
    throw new ApiError("The current occupancy response is incomplete. Retry the same read.", "INVALID_RESPONSE");
  }
  return value;
}

export function listNotices(limit: number, offset: number, reservationId: string | null, signal: AbortSignal) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (reservationId) params.set("reservation_id", reservationId);
  return request<{ items: ReservationNotice[]; total: number; limit: number; offset: number }>(
    `/api/reservation-notices?${params}`, signal).then(page => ({
    ...page, items: page.items.map(confirmedNotice),
  }));
}

export function loadNotice(id: string, signal: AbortSignal) {
  return request<ReservationNotice>(`/api/reservation-notices/${encodeURIComponent(id)}`, signal)
    .then(confirmedNotice);
}

export function loadNoticeVersion(id: string, version: number, signal: AbortSignal) {
  if (!Number.isInteger(version) || version < 1) {
    throw new ApiError("A positive notification version is required for exact recovery.", "INVALID_RESPONSE");
  }
  return request<ReservationNoticeNotificationVersion>(
    `/api/reservation-notices/${encodeURIComponent(id)}/notifications/${version}`, signal)
    .then(value => {
      if (value.notice_id !== id || value.notification_version !== version
        || typeof value.reservation_id !== "string" || !Number.isInteger(value.episode_number)) {
        throw new ApiError("The recovered notification belongs to a different version. It remains unresolved.", "INVALID_RESPONSE");
      }
      confirmedNotification(value, id);
      return value;
    });
}

export async function evaluateNotices(actorId: string, signal: AbortSignal) {
  const result = confirmedEvaluation(await request<ReservationNoticeEvaluation>(
    "/api/reservations/evaluate", signal, false,
    { method: "POST", body: JSON.stringify({ actor_id: actorId }) }));
  return result;
}

export async function acknowledgeNotice(reservationId: string, noticeId: string, payload: AcknowledgeNotice, signal: AbortSignal) {
  const result = confirmedNotice(await request<ReservationNotice>(
    `/api/reservations/${encodeURIComponent(reservationId)}/notice`, signal, false,
    { method: "POST", body: JSON.stringify({ ...payload, notice_id: noticeId }) }));
  if (result.id !== noticeId || result.reservation_id !== reservationId
    || result.current_notification === null || !result.current_notification.in_app_receipt
    || result.current_notification.notification_version !== payload.expected_notification_version
    || result.current_notification.acknowledged_by !== payload.actor_id) {
    throw new ApiError("The acknowledgement response did not confirm your own receipt on the exact version. The exact retry is retained.", "INVALID_RESPONSE");
  }
  return result;
}

export function loadStaticOccupancy(signal: AbortSignal) {
  return request<CurrentStaticOccupancy>("/api/current-static-occupancy", signal).then(confirmedOccupancy);
}

export interface ServiceNowIncidentRecord {
  version: number;
  state: "unknown" | "delivered" | "failed" | "absent" | "duplicate_review";
  state_reason: string;
  send_count: number;
  instance_host: string;
  sent_at: string;
  sent_by: string | null;
  sys_id: string | null;
  number: string | null;
  assignment_group: string | null;
  assigned_to: string | null;
  assignment_matches_configuration: boolean | null;
  external_state: string | null;
  external_state_label: string | null;
  observed_at: string | null;
  duplicate_numbers: string[];
  last_error_code: string | null;
  last_error_at: string | null;
  updated_at: string;
}

export interface ServiceNowIncidentView {
  intent_id: string;
  domain: string;
  correlation: string;
  label: string;
  sandbox: boolean;
  synthetic: boolean;
  source_request_state: string;
  simulated_handoff_state: string;
  provisioning_status: "not_requested";
  configuration: { status: "disabled" | "invalid" | "enabled"; problems: string[]; instance_host: string | null; domain_allowed: boolean | null };
  record: ServiceNowIncidentRecord | null;
  send_allowed: boolean;
  send_block_reason: string | null;
  lookup_allowed: boolean;
  lookup_block_reason: string | null;
  refresh_allowed: boolean;
  refresh_block_reason: string | null;
  events: { action: string; outcome: string; result: string | null; occurred_at: string; actor_id: string | null }[];
}

function confirmedIncident(value: ServiceNowIncidentView, id: string): ServiceNowIncidentView {
  if (!value || value.intent_id !== id || !value.configuration || !Array.isArray(value.events)) {
    throw new ApiError("The sandbox Incident response is incomplete. Reload the handoff before acting.", "INVALID_RESPONSE");
  }
  return value;
}

export function loadServiceNowIncident(id: string, signal: AbortSignal) {
  return request<ServiceNowIncidentView>(`/api/handoffs/${encodeURIComponent(id)}/servicenow`, signal)
    .then(value => confirmedIncident(value, id));
}

export async function actOnServiceNowIncident(id: string, action: "send" | "lookup" | "refresh",
  payload: { actor_id: string; expected_version: number; idempotency_key?: string }, signal: AbortSignal) {
  const result = await request<ServiceNowIncidentView>(`/api/handoffs/${encodeURIComponent(id)}/servicenow/${action}`,
    signal, false, { method: "POST", body: JSON.stringify(payload) });
  return confirmedIncident(result, id);
}
