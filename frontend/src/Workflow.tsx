import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, currentContext, downloadProtected, hasRole, request } from "./api";
import ServiceNowIncident from "./ServiceNowIncident";
import type { Page } from "./api";
import {
  actOnException, acknowledgeHandoff, acknowledgeNotice, attemptHandoff, createAllocation, createReservation,
  decideAllocation, decideRelease, evaluateNotices, extendReservation, findAllocationByKey, listHandoffs,
  listNotices, listReleaseRequests, loadAllocationRequest, loadHandoff, loadNotice, loadNoticeVersion,
  loadReleaseRequest, loadReservation, loadStaticOccupancy, loadWorkflow, proposeRelease, readHandoffOperation, readReservationOperation,
  readbackHandoff, reassignHandoff,
} from "./workflowApi";
import type { AllocationDecision, AllocationRequest, AuditEvent, CreateAllocation, CurrentStaticOccupancy, DemoActor, ExceptionAction,
  ExceptionFinding, ExceptionRecord, ReleaseRequest, ReservationDetail, ReservationNotice, ReservationNoticeEvaluation,
  ReservationNoticeNotification, ReservationNoticeNotificationVersion, ReservationOperationReadback,
  ReservationSummary, TicketHandoffDetail, TicketHandoffOriginalOperation, TicketHandoffSummary, TicketOperationAction, WorkflowStatus } from "./workflowApi";

const PAGE_SIZE = 20;
const RECOVERY_KEY = "ipam.workflow-t015.recovery.v1";
type WriteAction = "reservation.create" | "reservation.extend" | "reservation.release.propose"
  | "reservation.release.decision" | "allocation.create" | "allocation.decision"
  | "ticket.attempt" | "ticket.reassign" | "ticket.readback" | "ticket.acknowledge"
  | "notice.acknowledge";
type Attempt = { action: WriteAction; key: string; targetId?: string; secondaryId?: string;
  noticeVersion?: number; expected?: "approved" | "rejected"; payload: Record<string, unknown> };
type RecoveryPointer = {
  principal_id: string;
  domain: string;
  configuration_revision: number;
  configuration_digest: string;
  action: WriteAction;
  idempotency_key?: string;
  target_id?: string;
  secondary_id?: string;
  notification_version?: number;
  expected?: "approved" | "rejected";
};
const WRITE_ACTIONS: WriteAction[] = ["reservation.create", "reservation.extend", "reservation.release.propose",
  "reservation.release.decision", "allocation.create", "allocation.decision",
  "ticket.attempt", "ticket.reassign", "ticket.readback", "ticket.acknowledge", "notice.acknowledge"];
const SCENARIOS = ["success", "definitive_failure", "committed_response_lost", "no_effect_response_lost"] as const;

function readableError(error: unknown): string {
  if (error instanceof ApiError) return `${error.message} (${error.code}${error.requestId ? `; request ${error.requestId}` : ""})`;
  return error instanceof Error ? error.message : "The request failed.";
}

function exceptionOwnerLabel(owner: DemoActor | null): string {
  return owner ? `${owner.name}${owner.team ? ` · ${owner.team}` : ""}` : "Unavailable to this principal";
}

function ambiguous(error: unknown) {
  return error instanceof ApiError && ["REQUEST_TIMEOUT", "CONNECTION_FAILED", "INVALID_RESPONSE"].includes(error.code);
}

function uncertain(error: unknown) {
  return !(error instanceof ApiError)
    || ["REQUEST_TIMEOUT", "CONNECTION_FAILED", "INVALID_RESPONSE", "INTERNAL_ERROR", "SESSION_CHANGED"].includes(error.code);
}

function readRecovery(): { pointer: RecoveryPointer | null; error: string } {
  try {
    const raw = sessionStorage.getItem(RECOVERY_KEY);
    if (raw === null) return { pointer: null, error: "" };
    const value = JSON.parse(raw) as RecoveryPointer;
    const needsKey: WriteAction[] = ["reservation.create", "reservation.extend", "reservation.release.propose",
      "reservation.release.decision", "allocation.create", "ticket.attempt", "ticket.reassign", "ticket.readback", "ticket.acknowledge"];
    const needsTarget: WriteAction[] = ["reservation.extend", "reservation.release.propose",
      "reservation.release.decision", "allocation.decision", "ticket.attempt", "ticket.reassign", "ticket.readback", "ticket.acknowledge",
      "notice.acknowledge"];
    if (!value || typeof value.principal_id !== "string" || !value.principal_id
      || typeof value.domain !== "string" || !value.domain
      || !Number.isInteger(value.configuration_revision) || value.configuration_revision < 1
      || typeof value.configuration_digest !== "string" || !value.configuration_digest
      || !WRITE_ACTIONS.includes(value.action)
      || (needsKey.includes(value.action) && (typeof value.idempotency_key !== "string" || !value.idempotency_key || value.idempotency_key.length > 200))
      || (value.action === "notice.acknowledge" && value.idempotency_key !== undefined)
      || (needsTarget.includes(value.action) && (typeof value.target_id !== "string" || !value.target_id))
      || (value.action === "notice.acknowledge" && (typeof value.secondary_id !== "string" || !value.secondary_id))
      || (value.action === "notice.acknowledge" && (!Number.isInteger(value.notification_version) || (value.notification_version as number) < 1))
      || (value.action !== "notice.acknowledge" && value.notification_version !== undefined)
      || (value.action === "reservation.release.decision" && (typeof value.secondary_id !== "string" || !value.secondary_id))
      || (value.action === "allocation.decision" && value.expected !== "approved" && value.expected !== "rejected")
      || (value.action !== "allocation.decision" && value.expected !== undefined)
      || (value.idempotency_key !== undefined && (typeof value.idempotency_key !== "string" || !value.idempotency_key))
      || (value.target_id !== undefined && (typeof value.target_id !== "string" || !value.target_id))
      || (value.secondary_id !== undefined && (typeof value.secondary_id !== "string" || !value.secondary_id))
      || Object.keys(value).some(key => !["principal_id", "domain", "configuration_revision", "configuration_digest",
        "action", "idempotency_key", "target_id", "secondary_id", "notification_version", "expected"].includes(key))) {
      throw new Error("The saved workflow recovery pointer is invalid; its outcome cannot be confirmed.");
    }
    return { pointer: value, error: "" };
  } catch (error) {
    return { pointer: null, error: `Workflow recovery storage could not be read safely. New reservation, request and ticket writes are blocked. ${error instanceof Error ? error.message : "Storage access failed."}` };
  }
}

function samePointer(left: RecoveryPointer, right: RecoveryPointer) {
  return left.principal_id === right.principal_id && left.domain === right.domain
    && left.configuration_revision === right.configuration_revision && left.configuration_digest === right.configuration_digest
    && left.action === right.action && left.idempotency_key === right.idempotency_key
    && left.target_id === right.target_id && left.secondary_id === right.secondary_id
    && left.notification_version === right.notification_version
    && left.expected === right.expected;
}

function pointerFor(value: Attempt): RecoveryPointer {
  const context = currentContext();
  const pointer: RecoveryPointer = { principal_id: context.principal_id, domain: context.selected_domain!,
    configuration_revision: context.configuration_revision, configuration_digest: context.configuration_digest,
    action: value.action };
  if (value.key) pointer.idempotency_key = value.key;
  if (value.targetId) pointer.target_id = value.targetId;
  if (value.secondaryId) pointer.secondary_id = value.secondaryId;
  if (value.noticeVersion !== undefined) pointer.notification_version = value.noticeVersion;
  if (value.expected) pointer.expected = value.expected;
  return pointer;
}

function contextSignature() {
  const context = currentContext();
  return `${context.principal_id}|${context.selected_domain}|${context.configuration_revision}|${context.configuration_digest}`;
}

function PageButtons({ page, change }: { page: Page<unknown>; change: (offset: number) => void }) {
  return <nav className="pagination" aria-label="Workflow list pages"><span>{page.total ? page.offset + 1 : 0}–{page.offset + page.items.length} of {page.total}</span><div>
    <button type="button" className="secondary" disabled={page.offset === 0} onClick={() => change(Math.max(0, page.offset - PAGE_SIZE))}>Previous</button>
    <button type="button" className="secondary" disabled={page.offset + page.items.length >= page.total} onClick={() => change(page.offset + PAGE_SIZE)}>Next</button>
  </div></nav>;
}

function ExceptionEvidence({ title, finding }: { title: string; finding: ExceptionFinding }) {
  const runPath = `/api/runs/${encodeURIComponent(finding.run_id)}`;
  const [downloadError, setDownloadError] = useState("");
  async function save(path: string, name: string) {
    try { await downloadProtected(path, name, new AbortController().signal); setDownloadError(""); }
    catch (error) { setDownloadError(readableError(error)); }
  }
  return <section className="detail-section"><h4>{title}</h4>
    <p><strong>{finding.evidence_state}</strong> · severity {finding.severity}. {finding.explanation}</p>
    <dl className="facts"><dt>Subject / scope</dt><dd><code>{finding.subject.cidr}</code> · {finding.subject.scope_name}</dd>
      <dt>Saved run</dt><dd><button type="button" className="text-button" onClick={() => void save(runPath, "saved-domain-run.json")}>{finding.run_id} · download JSON</button></dd>
      <dt>Saved finding</dt><dd><button type="button" className="text-button" onClick={() => void save(`${runPath}/findings/${encodeURIComponent(finding.id)}`, "saved-domain-finding.json")}>{finding.id} · download JSON</button></dd>
    </dl>{downloadError && <p className="notice error" role="alert">{downloadError}</p>}
  </section>;
}

export default function Workflow({ active = true }: { active?: boolean }) {
  const [restored] = useState(readRecovery);
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [pointer, setPointer] = useState<RecoveryPointer | null>(restored.pointer);
  const [storageError, setStorageError] = useState(restored.error);
  const [recoveryStatus, setRecoveryStatus] = useState("");
  const [readbackRevision, setReadbackRevision] = useState(0);
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const actorId = currentContext().principal_id;
  const [requests, setRequests] = useState<Page<AllocationRequest> | null>(null);
  const [exceptions, setExceptions] = useState<Page<ExceptionRecord> | null>(null);
  const [audit, setAudit] = useState<Page<AuditEvent> | null>(null);
  const [requestOffset, setRequestOffset] = useState(0);
  const [exceptionOffset, setExceptionOffset] = useState(0);
  const [auditOffset, setAuditOffset] = useState(0);
  const [auditSubject, setAuditSubject] = useState("");
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [candidate, setCandidate] = useState("");
  const [owner, setOwner] = useState("");
  const [purpose, setPurpose] = useState("");
  const [reason, setReason] = useState("");
  const [supersedes, setSupersedes] = useState("");
  const [linkReservation, setLinkReservation] = useState(false);
  const [linkReservationId, setLinkReservationId] = useState("");
  const [linkServiceRef, setLinkServiceRef] = useState("");
  const [linkReservationVersion, setLinkReservationVersion] = useState("");
  const [selectedRequest, setSelectedRequest] = useState<AllocationRequest | null>(null);
  const [requestHandoff, setRequestHandoff] = useState<TicketHandoffSummary | null>(null);
  const [requestHandoffChecked, setRequestHandoffChecked] = useState(false);
  const [requestHandoffFor, setRequestHandoffFor] = useState("");
  const [decisionReason, setDecisionReason] = useState("");
  const [simulateFailure, setSimulateFailure] = useState(false);
  const [reservations, setReservations] = useState<Page<ReservationSummary> | null>(null);
  const [reservationOffset, setReservationOffset] = useState(0);
  const [selectedReservationId, setSelectedReservationId] = useState("");
  const [reservationDetail, setReservationDetail] = useState<ReservationDetail | null>(null);
  const [resAddress, setResAddress] = useState("");
  const [resOwnerRef, setResOwnerRef] = useState("");
  const [resServiceRef, setResServiceRef] = useState("");
  const [resReason, setResReason] = useState("");
  const [resDuration, setResDuration] = useState("24");
  const [extendDuration, setExtendDuration] = useState("24");
  const [extendReason, setExtendReason] = useState("");
  const [releases, setReleases] = useState<Page<ReleaseRequest> | null>(null);
  const [releaseOffset, setReleaseOffset] = useState(0);
  const [selectedRelease, setSelectedRelease] = useState<ReleaseRequest | null>(null);
  const [proposeReason, setProposeReason] = useState("");
  const [releaseDecisionReason, setReleaseDecisionReason] = useState("");
  const [resOpReadback, setResOpReadback] = useState<ReservationOperationReadback | null>(null);
  const [handoffs, setHandoffs] = useState<Page<TicketHandoffSummary> | null>(null);
  const [handoffOffset, setHandoffOffset] = useState(0);
  const [handoffSourceFilter, setHandoffSourceFilter] = useState("");
  const [appliedHandoffSource, setAppliedHandoffSource] = useState("");
  const [selectedHandoffId, setSelectedHandoffId] = useState("");
  const [handoffDetail, setHandoffDetail] = useState<TicketHandoffDetail | null>(null);
  const [attemptScenario, setAttemptScenario] = useState<(typeof SCENARIOS)[number]>("success");
  const [reassignReason, setReassignReason] = useState("");
  const [lastTicketOp, setLastTicketOp] = useState("");
  const [ticketOriginal, setTicketOriginal] = useState<TicketHandoffOriginalOperation | null>(null);
  const [notices, setNotices] = useState<Page<ReservationNotice> | null>(null);
  const [noticeOffset, setNoticeOffset] = useState(0);
  const [noticeReservationFilter, setNoticeReservationFilter] = useState("");
  const [appliedNoticeReservation, setAppliedNoticeReservation] = useState("");
  const [selectedNoticeId, setSelectedNoticeId] = useState("");
  const [noticeDetail, setNoticeDetail] = useState<ReservationNotice | null>(null);
  const [evaluateResult, setEvaluateResult] = useState<ReservationNoticeEvaluation | null>(null);
  const [ackReason, setAckReason] = useState("");
  const [recoveredNoticeVersion, setRecoveredNoticeVersion] = useState<ReservationNoticeNotificationVersion | null>(null);
  const [occupancy, setOccupancy] = useState<CurrentStaticOccupancy | null>(null);
  const [occupancyError, setOccupancyError] = useState("");
  const [selectedException, setSelectedException] = useState<ExceptionRecord | null>(null);
  const [exceptionOpenRevision, setExceptionOpenRevision] = useState(0);
  const [exceptionReason, setExceptionReason] = useState("");
  const [exceptionAttempt, setExceptionAttempt] = useState<{ id: string; payload: ExceptionAction } | null>(null);
  const operation = useRef<AbortController | null>(null);
  const priorAmbiguity = useRef(false);
  const signature = useRef<string | null>(null);
  useEffect(() => () => operation.current?.abort(), []);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setLoading(true);
    Promise.all([
      loadWorkflow(controller.signal),
      request<Page<AllocationRequest>>(`/api/allocation-requests?limit=${PAGE_SIZE}&offset=${requestOffset}`, controller.signal),
      request<Page<ExceptionRecord>>(`/api/exceptions?limit=${PAGE_SIZE}&offset=${exceptionOffset}`, controller.signal),
    ]).then(([current, items, queue]) => {
      if (controller.signal.aborted) return;
      setStatus(current); setRequests(items); setExceptions(queue);
      setSelectedRequest(previous => previous ? items.items.find(item => item.id === previous.id) ?? null : null);
      setSelectedException(previous => previous ? queue.items.find(item => item.id === previous.id) ?? null : null);
    }).catch((failure: unknown) => {
      if (!controller.signal.aborted) setError(`Refresh failed; previously shown data retains its earlier state. ${readableError(failure)}`);
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [active, revision, requestOffset, exceptionOffset]);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(auditOffset) });
    if (auditSubject) params.set("subject_id", auditSubject);
    setAudit(null);
    request<Page<AuditEvent>>(`/api/audit?${params}`, controller.signal)
      .then(items => { if (!controller.signal.aborted) setAudit(items); })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Audit history failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, revision, auditOffset, auditSubject]);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    request<Page<ReservationSummary>>(`/api/reservations?limit=${PAGE_SIZE}&offset=${reservationOffset}`, controller.signal)
      .then(items => {
        if (controller.signal.aborted) return;
        setReservations(items);
        if (selectedReservationId && !items.items.some(item => item.id === selectedReservationId)) setSelectedReservationId("");
      })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Reservation list failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, revision, reservationOffset]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active || !selectedReservationId) { setReservationDetail(null); setReleases(null); setSelectedRelease(null); return; }
    const controller = new AbortController();
    setReservationDetail(null); setReleases(null); setSelectedRelease(null);
    loadReservation(selectedReservationId, controller.signal)
      .then(detail => {
        if (controller.signal.aborted) return;
        setReservationDetail(detail);
        history(detail.id);
      })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Reservation detail failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, selectedReservationId, revision]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active || !selectedReservationId) return;
    const controller = new AbortController();
    listReleaseRequests(selectedReservationId, PAGE_SIZE, releaseOffset, controller.signal)
      .then(items => {
        if (controller.signal.aborted) return;
        setReleases(items);
        setSelectedRelease(previous => previous ? items.items.find(item => item.id === previous.id) ?? null : null);
      })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Release proposals failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, selectedReservationId, revision, releaseOffset]);

  useEffect(() => {
    if (!active || !selectedRelease) return;
    const controller = new AbortController();
    loadReleaseRequest(selectedRelease.reservation_id, selectedRelease.id, controller.signal)
      .then(detail => { if (!controller.signal.aborted) setSelectedRelease(detail); })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Release proposal detail failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, selectedRelease?.id, selectedRelease?.reservation_id, revision]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    listHandoffs(PAGE_SIZE, handoffOffset, appliedHandoffSource || null, controller.signal)
      .then(items => {
        if (controller.signal.aborted) return;
        setHandoffs(items);
        if (selectedHandoffId && !items.items.some(item => item.id === selectedHandoffId)) setSelectedHandoffId("");
      })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Ticket handoffs failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, revision, handoffOffset, appliedHandoffSource]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    listNotices(PAGE_SIZE, noticeOffset, appliedNoticeReservation || null, controller.signal)
      .then(items => {
        if (controller.signal.aborted) return;
        setNotices(items);
      })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Reservation notices failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, revision, noticeOffset, appliedNoticeReservation]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active || !selectedNoticeId) { setNoticeDetail(null); return; }
    const controller = new AbortController();
    setNoticeDetail(null);
    loadNotice(selectedNoticeId, controller.signal)
      .then(detail => {
        if (controller.signal.aborted) return;
        setNoticeDetail(detail);
        history(detail.reservation_id);
      })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Reservation notice detail failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, selectedNoticeId, revision]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setOccupancyError("");
    loadStaticOccupancy(controller.signal)
      .then(current => { if (!controller.signal.aborted) setOccupancy(current); })
      .catch((failure: unknown) => {
        if (!controller.signal.aborted) {
          setOccupancy(null);
          setOccupancyError(`Current static occupancy is unknown. ${readableError(failure)}`);
        }
      });
    return () => controller.abort();
  }, [active, revision]);

  useEffect(() => {
    if (!active || !selectedHandoffId) { setHandoffDetail(null); return; }
    const controller = new AbortController();
    setHandoffDetail(null);
    loadHandoff(selectedHandoffId, controller.signal)
      .then(detail => {
        if (controller.signal.aborted) return;
        setHandoffDetail(detail);
        history(detail.source_request_id);
      })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Ticket handoff detail failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, selectedHandoffId, revision]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active || !selectedRequest) { setRequestHandoff(null); setRequestHandoffChecked(false); setRequestHandoffFor(""); return; }
    const lookupId = selectedRequest.id;
    const controller = new AbortController();
    setRequestHandoff(null); setRequestHandoffChecked(false); setRequestHandoffFor("");
    listHandoffs(1, 0, lookupId, controller.signal)
      .then(items => {
        if (controller.signal.aborted) return;
        setRequestHandoff(items.items[0] ?? null);
        setRequestHandoffChecked(true);
        setRequestHandoffFor(lookupId);
      })
      .catch(() => { if (!controller.signal.aborted) { setRequestHandoff(null); setRequestHandoffChecked(false); setRequestHandoffFor(""); } });
    return () => controller.abort();
  }, [active, selectedRequest?.id, revision]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!active) return;
    try {
      const current = contextSignature();
      if (signature.current === null) { signature.current = current; return; }
      if (signature.current !== current) {
        signature.current = current;
        operation.current?.abort();
        setAttempt(null);
        setResOpReadback(null);
        setLastTicketOp("");
        setTicketOriginal(null);
        setNotices(null);
        setSelectedNoticeId("");
        setNoticeDetail(null);
        setEvaluateResult(null);
        setAckReason("");
        setRecoveredNoticeVersion(null);
        setOccupancy(null);
        setOccupancyError("");
        if (pointer) {
          setRecoveryStatus(`The access context changed. In-memory payloads were cleared and the saved ${pointer.action} pointer is quarantined. Reauthenticate the original principal ${pointer.principal_id} in domain ${pointer.domain} to read it back. It cannot be resent as this identity.`);
        }
      }
    } catch { signature.current = null; }
  });

  useEffect(() => {
    if (!active || !pointer || attempt || storageError) return;
    let context: ReturnType<typeof currentContext>;
    try { context = currentContext(); }
    catch { return; }
    if (pointer.principal_id !== context.principal_id || pointer.domain !== context.selected_domain) {
      setRecoveryStatus(`An unresolved ${pointer.action} operation belongs to ${pointer.principal_id} in domain ${pointer.domain}. Sign in as that original principal and select that domain to read it back. It cannot be resent as this identity.`);
      return;
    }
    const controller = new AbortController();
    setRecoveryStatus("Reading the saved operation receipt as the original authenticated principal…");
    (async () => {
      try {
        if (pointer.action === "allocation.create") {
          const page = await findAllocationByKey(pointer.idempotency_key!, controller.signal);
          if (controller.signal.aborted) return;
          const saved = page.items.find(item => item.idempotency_key === pointer.idempotency_key
            && item.actor_id === pointer.principal_id) ?? null;
          if (!saved) {
            setRecoveryStatus("No matching allocation request was found. The earlier request may still commit; it remains unresolved and replacement writes are blocked.");
            return;
          }
          confirmPointerClear();
          priorAmbiguity.current = false;
          selectRequest(saved); setRequestOffset(0); history(saved.id);
          setRecoveryStatus("The original allocation request was confirmed by authorized readback.");
          setRevision(value => value + 1);
        } else if (pointer.action === "allocation.decision") {
          const saved = await loadAllocationRequest(pointer.target_id!, controller.signal);
          if (controller.signal.aborted) return;
          const terminal = saved.state === pointer.expected;
          if (!terminal || saved.id !== pointer.target_id || saved.decision_actor_id !== pointer.principal_id) {
            setRecoveryStatus("The original decision remains unresolved. No matching terminal decision by this principal for the intended action was confirmed. Do not submit a replacement decision.");
            return;
          }
          confirmPointerClear();
          priorAmbiguity.current = false;
          selectRequest(saved); history(saved.id);
          setRecoveryStatus("The original allocation decision was confirmed by authorized readback.");
          setRevision(value => value + 1);
        } else if (pointer.action.startsWith("reservation.")) {
          const result = await readReservationOperation(
            pointer.action as ReservationOperationReadback["action"], pointer.idempotency_key!,
            pointer.action === "reservation.release.propose" ? pointer.target_id! : null, controller.signal);
          if (controller.signal.aborted) return;
          if (!result.found || !result.original_outcome) {
            setRecoveryStatus("No matching reservation operation receipt was found. The earlier request may still commit; it remains unresolved and replacement writes are blocked.");
            return;
          }
          const outcome = result.original_outcome as { id?: string; reservation_id?: string };
          const matches = pointer.action === "reservation.release.propose"
            ? outcome.reservation_id === pointer.target_id
            : pointer.action === "reservation.release.decision"
              ? outcome.id === pointer.secondary_id && outcome.reservation_id === pointer.target_id
              : outcome.id === pointer.target_id || pointer.action === "reservation.create";
          if (!matches || result.action !== pointer.action) {
            setRecoveryStatus("Authorized readback returned an outcome that does not match the saved key and target. It remains unresolved; no replacement will be sent.");
            return;
          }
          setResOpReadback(result);
          confirmPointerClear();
          priorAmbiguity.current = false;
          if (result.current_reservation) {
            setSelectedReservationId(result.current_reservation.id);
            setReservationOffset(0);
            history(result.current_reservation.id);
          }
          if (result.current_release_request) {
            setSelectedRelease(result.current_release_request);
            setReleaseOffset(0);
          }
          setRecoveryStatus("The original reservation operation was confirmed by authorized readback. Current state is shown separately.");
          setRevision(value => value + 1);
        } else if (pointer.action === "notice.acknowledge") {
          const recovered = await loadNoticeVersion(pointer.target_id!, pointer.notification_version!, controller.signal);
          if (controller.signal.aborted) return;
          const ownReceipt = recovered.acknowledged_by === pointer.principal_id
            && recovered.acknowledgement_kind === "recipient_in_app"
            && recovered.in_app_receipt === true
            && recovered.delivery_status === "acknowledged"
            && recovered.reservation_id === pointer.secondary_id;
          if (!ownReceipt) {
            setRecoveryStatus("Authorized exact-version readback did not confirm your own receipt on the original version. It remains unknown and replacement writes are blocked; no silent replacement will be sent.");
            return;
          }
          setRecoveredNoticeVersion(recovered);
          confirmPointerClear();
          priorAmbiguity.current = false;
          setSelectedNoticeId(recovered.notice_id);
          setNoticeOffset(0);
          history(recovered.reservation_id);
          setRecoveryStatus("The original notice receipt was confirmed by authorized exact-version readback. Current notice state is shown separately and may differ after renewal.");
          setRevision(value => value + 1);
        } else {
          const result = await readHandoffOperation(pointer.action as TicketOperationAction, pointer.idempotency_key!, controller.signal);
          if (controller.signal.aborted) return;
          if (!result.found || !result.original_operation || !result.current_handoff) {
            setRecoveryStatus("No matching ticket operation receipt was found. The earlier request may still commit; it remains unresolved and replacement writes are blocked.");
            return;
          }
          const phase = result.original_operation.phase;
          const expected = pointer.action === "ticket.attempt" ? "reserve"
            : pointer.action === "ticket.reassign" ? "reassign"
            : pointer.action === "ticket.readback" ? "readback" : "acknowledge";
          const current = result.current_handoff;
          const shapeOk = phase === expected && result.action === pointer.action
            && current.id === pointer.target_id
            && (phase === "reserve"
              ? result.original_operation.attempt !== null && result.original_operation.attempt !== undefined
                && Number.isInteger(result.original_operation.attempt.ordinal)
                && current.attempts.some(item => item.id === result.original_operation!.attempt!.id
                  && item.ordinal === result.original_operation!.attempt!.ordinal
                  && item.synthetic_scenario === result.original_operation!.attempt!.synthetic_scenario)
              : phase === "reassign"
                ? result.original_operation.assignment !== null && result.original_operation.assignment !== undefined
                  && Number.isInteger(result.original_operation.assignment.assignment_version)
                  && current.route_history.some(item => item.assignment_version === result.original_operation!.assignment!.assignment_version
                    && item.team === result.original_operation!.assignment!.team)
                : result.original_operation.event !== null && result.original_operation.event !== undefined
                  && typeof result.original_operation.event.id === "string"
                  && current.events.some(item => item.id === result.original_operation!.event!.id
                    && item.event_type === result.original_operation!.event!.event_type
                    && item.outcome === result.original_operation!.event!.outcome));
          if (!shapeOk) {
            setRecoveryStatus("Authorized readback returned an operation that does not match the saved action, key, target and canonical shape. It remains unresolved; no replacement will be sent.");
            return;
          }
          confirmPointerClear();
          priorAmbiguity.current = false;
          setSelectedHandoffId(current.id);
          setHandoffDetail(current);
          setTicketOriginal(result.original_operation);
          if (pointer.action === "ticket.attempt" && result.original_operation.attempt) {
            const ordinal = result.original_operation.attempt.ordinal;
            setLastTicketOp(`Original attempt receipt confirms reserved ordinal ${ordinal}. This proves the ordinal only.`);
            setRecoveryStatus(`The original attempt receipt confirms reserved ordinal ${ordinal}. Current handoff state is ${current.state}; an unknown current state needs a separate manual readback with the current version, correlation and digest.`);
          } else {
            setRecoveryStatus("The original ticket operation was confirmed by authorized readback. Current handoff state is shown separately.");
          }
          setRevision(value => value + 1);
        }
      } catch (failure) {
        if (!controller.signal.aborted) {
          setRecoveryStatus(`Authorized readback failed. The earlier operation remains unresolved and replacement writes are blocked. ${readableError(failure)}`);
        }
      }
    })();
    return () => controller.abort();
  }, [active, pointer, attempt, storageError, readbackRevision]); // eslint-disable-line react-hooks/exhaustive-deps

  function confirmPointerClear() {
    sessionStorage.removeItem(RECOVERY_KEY);
    if (sessionStorage.getItem(RECOVERY_KEY) !== null) throw new Error("The recovery pointer could not be cleared.");
    setPointer(null);
    setAttempt(null);
  }

  function retain(value: Attempt) {
    let saved: { pointer: RecoveryPointer | null; error: string };
    try {
      saved = readRecovery();
    } catch (error) {
      throw new Error(`No request was sent. Recovery storage failed. ${error instanceof Error ? error.message : "Storage access failed."}`);
    }
    if (saved.error) throw new Error(saved.error);
    const next = pointerFor(value);
    if (saved.pointer && !samePointer(saved.pointer, next)) throw new Error("A different workflow operation remains unresolved. Read it back before starting another.");
    const serialized = JSON.stringify(next);
    sessionStorage.setItem(RECOVERY_KEY, serialized);
    if (sessionStorage.getItem(RECOVERY_KEY) !== serialized) throw new Error("The minimal workflow recovery pointer could not be saved.");
    setPointer(next);
    setAttempt(value);
  }

  function clearAttempt() {
    try {
      sessionStorage.removeItem(RECOVERY_KEY);
      if (sessionStorage.getItem(RECOVERY_KEY) !== null) throw new Error("The previous workflow recovery pointer remains saved.");
      priorAmbiguity.current = false;
      setPointer(null);
      setAttempt(null);
    } catch (failure) {
      setStorageError(`The operation response was received, but recovery storage could not be cleared. New writes are blocked. ${failure instanceof Error ? failure.message : "Storage access failed."}`);
    }
  }

  function refresh() { setError(""); setRevision(value => value + 1); }
  function history(id: string) { setAuditSubject(id); setAuditOffset(0); }

  function selectRequest(item: AllocationRequest | null) {
    setSelectedRequest(item);
    setRequestHandoff(null);
    setRequestHandoffChecked(false);
    setRequestHandoffFor("");
    setDecisionReason("");
  }

  async function submit(value: Attempt) {
    if (operation.current || storageError || (pointer && !attempt)) return;
    try { retain(value); }
    catch (failure) { setStorageError(`No request was sent. Save a minimal recovery pointer first. ${failure instanceof Error ? failure.message : "Storage access failed."}`); return; }
    const controller = new AbortController();
    operation.current = controller;
    setBusy(true); setError(""); setMessage(""); setRecoveryStatus(""); setResOpReadback(null);
    try {
      if (value.action === "reservation.create") {
        const created = await createReservation(value.payload as unknown as Parameters<typeof createReservation>[0], controller.signal);
        if (controller.signal.aborted) return;
        setSelectedReservationId(created.id); setReservationOffset(0); clearAttempt();
        setMessage(`Reservation ${created.address} is ${created.state}. Expiry does not free the hold.`);
        setResAddress(""); setResOwnerRef(""); setResServiceRef(""); setResReason(""); setResDuration("24");
        history(created.id);
      } else if (value.action === "reservation.extend") {
        const extended = await extendReservation(value.targetId!, value.payload as unknown as Parameters<typeof extendReservation>[1], controller.signal);
        if (controller.signal.aborted) return;
        setSelectedReservationId(extended.id); clearAttempt();
        setMessage(`Reservation ${extended.address} extended to ${extended.expires_at} at version ${extended.version}.`);
        setExtendDuration("24"); setExtendReason("");
        history(extended.id);
      } else if (value.action === "reservation.release.propose") {
        const proposed = await proposeRelease(value.targetId!, value.payload as unknown as Parameters<typeof proposeRelease>[1], controller.signal);
        if (controller.signal.aborted) return;
        setSelectedRelease(proposed); setReleaseOffset(0); clearAttempt();
        setMessage(`Release proposal ${proposed.id} is pending. A different Approver must decide it; the hold stays reserved until approval.`);
        setProposeReason("");
        history(proposed.id);
      } else if (value.action === "reservation.release.decision") {
        const decided = await decideRelease(value.targetId!, value.secondaryId!, value.payload as unknown as Parameters<typeof decideRelease>[2], controller.signal);
        if (controller.signal.aborted) return;
        setSelectedRelease(decided); clearAttempt();
        setMessage(`Release proposal ${decided.state}. The reservation hold changes only on an independent approval.`);
        setReleaseDecisionReason("");
        history(decided.id);
      } else if (value.action === "allocation.create") {
        const created = await createAllocation(value.payload as unknown as CreateAllocation, controller.signal);
        if (controller.signal.aborted) return;
        selectRequest(created); setRequestOffset(0); clearAttempt();
        setMessage(`Request ${created.id} is ${created.state}. Creation does not reserve the address.`);
        setCandidate(""); setOwner(""); setPurpose(""); setReason(""); setSupersedes("");
        setLinkReservation(false); setLinkReservationId(""); setLinkServiceRef(""); setLinkReservationVersion("");
        history(created.id);
      } else if (value.action === "allocation.decision") {
        const decided = await decideAllocation(value.targetId!, value.payload as unknown as AllocationDecision, controller.signal);
        if (controller.signal.aborted) return;
        selectRequest(decided); clearAttempt();
        setMessage(`Request ${decided.state}. Local outcome: ${decided.local_outcome}. External provisioning: ${decided.downstream_status ?? "not requested"}.`);
        setDecisionReason("");
        history(decided.id);
      } else if (value.action === "ticket.attempt") {
        const mutated = await attemptHandoff(value.targetId!, value.payload as unknown as Parameters<typeof attemptHandoff>[1], controller.signal);
        if (controller.signal.aborted) return;
        setHandoffDetail(mutated.handoff); setSelectedHandoffId(mutated.handoff.id); clearAttempt();
        const ordinal = "attempt" in mutated.operation ? mutated.operation.attempt.ordinal : null;
        setLastTicketOp(`Original operation phase ${mutated.operation.phase}${ordinal !== null ? `, ordinal ${ordinal}` : ""}.`);
        setMessage(`Ticket attempt recorded. Handoff state is ${mutated.handoff.state}; unknown outcomes need a separate manual readback.`);
        history(mutated.handoff.source_request_id);
      } else if (value.action === "ticket.readback") {
        const mutated = await readbackHandoff(value.targetId!, value.payload as unknown as Parameters<typeof readbackHandoff>[1], controller.signal);
        if (controller.signal.aborted) return;
        if (!("event" in mutated.operation)) throw new ApiError("The readback response did not confirm a recorded event. The exact retry is retained.", "INVALID_RESPONSE");
        setHandoffDetail(mutated.handoff); setSelectedHandoffId(mutated.handoff.id); clearAttempt();
        setLastTicketOp(`Original readback event outcome ${mutated.operation.event.outcome}.`);
        setMessage(`Manual readback recorded: ${mutated.operation.event.outcome}. Handoff state is ${mutated.handoff.state}.`);
        history(mutated.handoff.source_request_id);
      } else if (value.action === "ticket.acknowledge") {
        const mutated = await acknowledgeHandoff(value.targetId!, value.payload as unknown as Parameters<typeof acknowledgeHandoff>[1], controller.signal);
        if (controller.signal.aborted) return;
        if (!("event" in mutated.operation)) throw new ApiError("The acknowledgement response did not confirm a recorded event. The exact retry is retained.", "INVALID_RESPONSE");
        setHandoffDetail(mutated.handoff); setSelectedHandoffId(mutated.handoff.id); clearAttempt();
        setLastTicketOp("Original acknowledgement event recorded in simulated mode.");
        setMessage("Simulated recipient acknowledgement recorded. It approves no IPAM change and resolves no finding.");
        history(mutated.handoff.source_request_id);
      } else if (value.action === "notice.acknowledge") {
        const acknowledged = await acknowledgeNotice(value.secondaryId!, value.targetId!,
          value.payload as unknown as Parameters<typeof acknowledgeNotice>[2], controller.signal);
        if (controller.signal.aborted) return;
        setNoticeDetail(acknowledged); setSelectedNoticeId(acknowledged.id); clearAttempt();
        setAckReason("");
        setMessage("Recipient acknowledgement recorded in-app. The hold stays reserved and the condition stays open until extension, conversion or an approved release resolves it. This is not external delivery.");
        history(acknowledged.reservation_id);
      } else {
        const mutated = await reassignHandoff(value.targetId!, value.payload as unknown as Parameters<typeof reassignHandoff>[1], controller.signal);
        if (controller.signal.aborted) return;
        if (!("assignment" in mutated.operation)) throw new ApiError("The reassignment response did not confirm a saved assignment. The exact retry is retained.", "INVALID_RESPONSE");
        setHandoffDetail(mutated.handoff); setSelectedHandoffId(mutated.handoff.id); clearAttempt();
        setLastTicketOp(`Original reassignment to team ${mutated.operation.assignment.team ?? "unassigned"}.`);
        setMessage("Route reassigned to the current reviewed team. The handoff returns to pending with zero attempts.");
        setReassignReason("");
        history(mutated.handoff.source_request_id);
      }
    } catch (failure) {
      if (!controller.signal.aborted) {
        if (value.action === "ticket.attempt") {
          setError(`${readableError(failure)} The attempt spans three committed transactions; the ordinal or effect may have committed. The pointer is preserved. Check the saved attempt receipt by its exact key before any new attempt.`);
          setRecoveryStatus("Checking the saved attempt receipt by its exact key is required. A found receipt proves the ordinal only; an unknown current state needs a separate manual readback. No automatic retry will run.");
        } else if (uncertain(failure)) {
          priorAmbiguity.current = true;
          setError(`${readableError(failure)} The outcome is uncertain. Retry preserves the exact payload and key in this session.`);
        } else if (priorAmbiguity.current) {
          setError(`${readableError(failure)} This refusal applies to the latest retry only; the earlier submission remains unresolved. Read it back under the original principal before any replacement.`);
          if (!(failure instanceof ApiError && ["AUTH_REQUIRED", "ACCESS_CONTEXT_STALE"].includes(failure.code))) {
            setAttempt(null);
            setRecoveryStatus("Checking the earlier uncertain operation by its original recovery pointer…");
            setReadbackRevision(value => value + 1);
          }
        } else {
          setError(`${readableError(failure)} The server refused this first submission; inspect the reason and reload before creating a new operation.`);
          clearAttempt();
        }
      }
    } finally {
      operation.current = null;
      if (!controller.signal.aborted) {
        setBusy(false);
        setRevision(value => value + 1);
      }
    }
  }

  function parseDuration(raw: string): number | null {
    if (!/^\d+$/.test(raw.trim())) return null;
    const value = Number(raw.trim());
    return Number.isInteger(value) && value >= 1 && value <= 168 ? value : null;
  }

  function submitReservationCreate(event: FormEvent) {
    event.preventDefault();
    if (!status || busy || attempt || pointer || storageError) return;
    const duration = parseDuration(resDuration);
    if (!resAddress.trim() || !resOwnerRef.trim() || !resServiceRef.trim() || !resReason.trim() || duration === null) {
      setError("Enter an IPv4 candidate, owner reference, service reference, reason and a whole-hour duration from 1 to 168. No request was sent.");
      return;
    }
    const key = crypto.randomUUID();
    void submit({ action: "reservation.create", key, payload: {
      actor_id: actorId, idempotency_key: key, pool_id: status.pool.id, candidate: resAddress.trim(),
      pool_version: status.pool.pool_version, baseline_version: status.baseline_version,
      owner_reference: resOwnerRef.trim(), service_reference: resServiceRef.trim(),
      reason: resReason.trim(), duration_hours: duration } as unknown as Record<string, unknown>,
    });
  }

  function keyedAttempt(action: Attempt["action"], key: string, payload: Record<string, unknown>, targetId?: string, secondaryId?: string) {
    void submit({ action, key, targetId, secondaryId, payload });
  }

  async function submitRequest(event: FormEvent) {
    event.preventDefault();
    if (!status || busy || attempt || pointer || storageError) return;
    const key = crypto.randomUUID();
    const payload: Record<string, unknown> = {
      actor_id: actorId, idempotency_key: key, pool_id: status.pool.id,
      candidate: candidate.trim(), owner: owner.trim(), purpose: purpose.trim(), reason: reason.trim(),
      pool_version: status.pool.pool_version,
      baseline_version: status.baseline_version, ...(supersedes ? { supersedes_request_id: supersedes } : {}),
    };
    if (linkReservation) {
      const reservationVersion = /^\d+$/.test(linkReservationVersion.trim()) ? Number(linkReservationVersion.trim()) : NaN;
      if (!linkReservationId.trim() || !linkServiceRef.trim() || !Number.isInteger(reservationVersion) || reservationVersion < 1) {
        setError("A linked allocation needs the exact reservation ID, service reference and a positive reservation version. No request was sent.");
        return;
      }
      payload.reservation_id = linkReservationId.trim();
      payload.service_reference = linkServiceRef.trim();
      payload.reservation_version = reservationVersion;
    }
    payload.idempotency_key = key;
    keyedAttempt("allocation.create", key, payload);
  }

  function decide(action: "approve" | "reject") {
    if (!selectedRequest || busy || attempt || pointer || storageError) return;
    const key = crypto.randomUUID();
    const tracked = trackingResolved && requestHandoff !== null;
    const payload: Record<string, unknown> = { actor_id: actorId, action, reason: decisionReason };
    if (!tracked) payload.simulate_failure = action === "approve" && simulateFailure;
    void submit({ action: "allocation.decision", key, targetId: selectedRequest.id,
      expected: action === "approve" ? "approved" : "rejected", payload });
  }

  function submitExtend() {
    if (!reservationDetail || busy || attempt || pointer || storageError) return;
    const duration = parseDuration(extendDuration);
    if (duration === null || !extendReason.trim()) {
      setError("Enter a whole-hour duration from 1 to 168 and a reason. No request was sent.");
      return;
    }
    const key = crypto.randomUUID();
    keyedAttempt("reservation.extend", key, {
      actor_id: actorId, idempotency_key: key, expected_version: reservationDetail.version,
      expected_pool_version: status?.pool.pool_version, expected_baseline_version: status?.baseline_version,
      duration_hours: duration, reason: extendReason.trim(),
    }, reservationDetail.id);
  }

  function submitPropose() {
    if (!reservationDetail || busy || attempt || pointer || storageError) return;
    if (!proposeReason.trim()) { setError("Enter a reason for the unused release proposal. No request was sent."); return; }
    const key = crypto.randomUUID();
    keyedAttempt("reservation.release.propose", key, {
      actor_id: actorId, idempotency_key: key, expected_version: reservationDetail.version,
      expected_pool_version: status?.pool.pool_version, expected_baseline_version: status?.baseline_version,
      reason: proposeReason.trim(),
    }, reservationDetail.id);
  }

  function decideReleaseAction(action: "approve" | "reject") {
    if (!selectedRelease || busy || attempt || pointer || storageError) return;
    if (!releaseDecisionReason.trim()) { setError("Enter a decision reason. No request was sent."); return; }
    const key = crypto.randomUUID();
    keyedAttempt("reservation.release.decision", key, {
      actor_id: actorId, idempotency_key: key, action,
      expected_version: selectedRelease.reservation_version,
      expected_pool_version: selectedRelease.expected_pool_version,
      expected_baseline_version: selectedRelease.expected_baseline_version,
      reason: releaseDecisionReason.trim(),
    }, selectedRelease.reservation_id, selectedRelease.id);
  }

  function submitAttempt() {
    if (!handoffDetail || busy || attempt || pointer || storageError) return;
    const key = crypto.randomUUID();
    keyedAttempt("ticket.attempt", key, {
      actor_id: actorId, expected_version: handoffDetail.version,
      idempotency_key: key, synthetic_scenario: attemptScenario,
    }, handoffDetail.id);
  }

  function submitReadback() {
    if (!handoffDetail || busy || attempt || pointer || storageError) return;
    const key = crypto.randomUUID();
    keyedAttempt("ticket.readback", key, {
      actor_id: actorId, expected_version: handoffDetail.version,
      idempotency_key: key, correlation: handoffDetail.correlation,
      business_payload_digest: handoffDetail.business_payload_digest,
    }, handoffDetail.id);
  }

  function submitAcknowledge() {
    if (!handoffDetail || busy || attempt || pointer || storageError) return;
    const latest = handoffDetail.latest_attempt;
    if (handoffDetail.state !== "delivered" || !latest?.observed_effect_id || !latest?.observed_ticket_id) {
      setError("Only a delivered handoff with an observed effect and ticket can be acknowledged. No request was sent.");
      return;
    }
    const key = crypto.randomUUID();
    keyedAttempt("ticket.acknowledge", key, {
      actor_id: actorId, expected_version: handoffDetail.version,
      idempotency_key: key, correlation: handoffDetail.correlation,
      business_payload_digest: handoffDetail.business_payload_digest,
      effect_id: latest.observed_effect_id, ticket_id: latest.observed_ticket_id,
      acknowledgement_mode: "simulated",
    }, handoffDetail.id);
  }

  function submitReassign() {
    if (!handoffDetail || busy || attempt || pointer || storageError) return;
    if (handoffDetail.reassignment_allowed !== true || !reassignReason.trim()) {
      setError("Reassignment needs server permission and a reason. It is allowed only with zero attempts. No request was sent.");
      return;
    }
    const key = crypto.randomUUID();
    keyedAttempt("ticket.reassign", key, {
      actor_id: actorId, expected_version: handoffDetail.version,
      idempotency_key: key, reason: reassignReason.trim(),
    }, handoffDetail.id);
  }

  async function submitEvaluate() {
    if (busy || attempt || pointer || storageError || operation.current) return;
    if (!hasRole("Operator")) {
      setError("An Operator must authenticate to run an explicit notice evaluation. No request was sent.");
      return;
    }
    const controller = new AbortController();
    operation.current = controller;
    setBusy(true); setError(""); setMessage(""); setEvaluateResult(null);
    try {
      const result = await evaluateNotices(actorId, controller.signal);
      if (controller.signal.aborted) return;
      setEvaluateResult(result);
      setNoticeOffset(0);
      setMessage(`Evaluation at ${result.evaluated_at}: ${result.created_count} created, ${result.renewed_count} renewed, ${result.alarm_upgrade_count} alarm upgrades. GET never changes state; this explicit evaluation is the only writer.`);
      setRevision(value => value + 1);
    } catch (failure) {
      if (!controller.signal.aborted) {
        setError(`${readableError(failure)} The evaluation outcome is unknown until an authorized notice-list readback. A later manual evaluation is a new evaluation, not proof of this response.`);
      }
    } finally {
      operation.current = null;
      if (!controller.signal.aborted) setBusy(false);
    }
  }

  function submitNoticeAcknowledge() {
    if (!noticeDetail || busy || attempt || pointer || storageError) return;
    if (!noticeDetail.is_current_recipient || !hasRole("Operator")) {
      setError("Only the current bound recipient, authenticated as Operator, may acknowledge this version. No request was sent.");
      return;
    }
    if (noticeDetail.state === "resolved") {
      setError("A resolved notice cannot be acknowledged. Resolution never means delivery. No request was sent.");
      return;
    }
    if (noticeDetail.current_notification === null || noticeDetail.current_notification.routing_status !== "assigned"
      || noticeDetail.current_notification.delivery_status === "acknowledged") {
      setError("This version is not eligible for acknowledgement. No request was sent.");
      return;
    }
    if (!ackReason.trim()) {
      setError("Enter an explicit acknowledgement reason for the current exact version. No request was sent.");
      return;
    }
    const current = noticeDetail.current_notification;
    void submit({ action: "notice.acknowledge", key: "", targetId: noticeDetail.id,
      secondaryId: noticeDetail.reservation_id, noticeVersion: current.notification_version,
      payload: { actor_id: actorId, expected_notification_version: current.notification_version,
        reason: ackReason.trim() } });
  }

  async function checkNoticeReceipt() {
    if (!pointer || pointer.action !== "notice.acknowledge" || !pointer.target_id
      || pointer.notification_version === undefined || !pointer.secondary_id
      || operation.current || busy || storageError) return;
    let context: ReturnType<typeof currentContext>;
    try { context = currentContext(); }
    catch (failure) { setError(readableError(failure)); return; }
    if (pointer.principal_id !== context.principal_id || pointer.domain !== context.selected_domain) {
      setRecoveryStatus(`The saved notice acknowledgement belongs to ${pointer.principal_id} in domain ${pointer.domain}. Reauthenticate that original context before reading it back.`);
      return;
    }
    const controller = new AbortController();
    operation.current = controller;
    setBusy(true); setError(""); setMessage("");
    try {
      const recovered = await loadNoticeVersion(pointer.target_id, pointer.notification_version, controller.signal);
      if (controller.signal.aborted) return;
      const ownReceipt = recovered.acknowledged_by === pointer.principal_id
        && recovered.acknowledgement_kind === "recipient_in_app"
        && recovered.in_app_receipt === true
        && recovered.delivery_status === "acknowledged"
        && recovered.reservation_id === pointer.secondary_id;
      if (!ownReceipt) {
        setRecoveryStatus("Authorized exact-version readback did not confirm your own receipt on the original version and parent. It remains unknown and replacement writes are blocked; the exact retry payload is retained and no silent replacement will be sent.");
        return;
      }
      setRecoveredNoticeVersion(recovered);
      confirmPointerClear();
      priorAmbiguity.current = false;
      setSelectedNoticeId(recovered.notice_id);
      setNoticeOffset(0);
      history(recovered.reservation_id);
      setRecoveryStatus("The original notice receipt was confirmed by authorized exact-version readback. Current notice state is shown separately and may differ after renewal.");
      setRevision(value => value + 1);
    } catch (failure) {
      if (!controller.signal.aborted) {
        setRecoveryStatus(`Authorized exact-version readback failed. The earlier acknowledgement remains unresolved and replacement writes are blocked; the exact retry payload is retained. ${readableError(failure)}`);
      }
    } finally {
      operation.current = null;
      if (!controller.signal.aborted) setBusy(false);
    }
  }

  function noticeDeliveryLabel(detail: ReservationNotice, actorId: string): string {
    const current = detail.current_notification;
    const resolution = detail.state === "resolved"
      ? "resolved — retained history only; resolution never means delivery. "
      : "";
    if (current === null) return `${resolution}current binding unknown — missing child`;
    if (current.delivery_status === "acknowledged") {
      return current.acknowledged_by === actorId
        ? `${resolution}acknowledged — your own in-app receipt on this version`
        : `${resolution}acknowledged — in-app receipt recorded; recipient identity redacted for this principal`;
    }
    if (current.delivery_status === "awaiting_receipt") return `${resolution}awaiting receipt — bound recipient has not acknowledged`;
    if (current.delivery_status === "unassigned") return `${resolution}unassigned — no reviewed recipient mapping`;
    if (current.delivery_status === "recipient_unavailable") return `${resolution}recipient unavailable — configured recipient ineligible or route changed`;
    return `${resolution}legacy unbound — old operator acknowledgement only, never recipient receipt`;
  }

  function notificationLabel(item: ReservationNoticeNotification): string {
    if (item.routing_status === "assigned" && item.delivery_status === "acknowledged") return "acknowledged";
    if (item.routing_status === "assigned" && item.delivery_status === "awaiting_receipt") return "awaiting receipt";
    if (item.routing_status === "assigned") return "recipient unavailable";
    if (item.routing_status === "unassigned") return "unassigned";
    if (item.routing_status === "unroutable") return "recipient unavailable";
    return "legacy unbound";
  }

  async function checkAttemptReceipt() {
    if (!pointer || pointer.action !== "ticket.attempt" || !pointer.idempotency_key
      || operation.current || busy || storageError) return;
    let context: ReturnType<typeof currentContext>;
    try { context = currentContext(); }
    catch (failure) { setError(readableError(failure)); return; }
    if (pointer.principal_id !== context.principal_id || pointer.domain !== context.selected_domain) {
      setRecoveryStatus(`The saved attempt belongs to ${pointer.principal_id} in domain ${pointer.domain}. Reauthenticate that original context before reading it back.`);
      return;
    }
    const controller = new AbortController();
    operation.current = controller;
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await readHandoffOperation("ticket.attempt", pointer.idempotency_key, controller.signal);
      if (controller.signal.aborted) return;
      if (!result.found || !result.original_operation?.attempt || !result.current_handoff
        || result.original_operation.phase !== "reserve" || result.action !== "ticket.attempt"
        || result.current_handoff.id !== pointer.target_id
        || !Number.isInteger(result.original_operation.attempt.ordinal)
        || !result.current_handoff.attempts.some(item => item.id === result.original_operation!.attempt!.id
          && item.ordinal === result.original_operation!.attempt!.ordinal)) {
        setRecoveryStatus("No saved attempt receipt was found for this exact key. The attempt may still commit; it remains unresolved and replacement writes are blocked. A missing receipt never authorizes a new key.");
        return;
      }
      const ordinal = result.original_operation.attempt.ordinal;
      clearAttempt();
      setSelectedHandoffId(result.current_handoff.id);
      setHandoffDetail(result.current_handoff);
      setTicketOriginal(result.original_operation);
      setLastTicketOp(`Original attempt receipt confirms reserved ordinal ${ordinal}. This proves the ordinal only.`);
      setRecoveryStatus(`The saved attempt receipt confirms reserved ordinal ${ordinal}. Current handoff state is ${result.current_handoff.state}; an unknown current state needs a separate manual readback with the current version, correlation and digest.`);
      setRevision(value => value + 1);
    } catch (failure) {
      if (!controller.signal.aborted) {
        setRecoveryStatus(`Saved attempt receipt lookup failed. The attempt remains unresolved and replacement writes are blocked. ${readableError(failure)}`);
      }
    } finally {
      operation.current = null;
      if (!controller.signal.aborted) setBusy(false);
    }
  }

  async function exceptionAction(action: ExceptionAction["action"]) {
    if ((!selectedException || !status) && !exceptionAttempt) return;
    const attemptValue = exceptionAttempt ?? { id: selectedException!.id, payload: {
      actor_id: actorId, version: selectedException!.version, action, reason: exceptionReason,
    } };
    setExceptionAttempt(attemptValue);
    setBusy(true); setError(""); setMessage("");
    try {
      const updated = await actOnException(attemptValue.id, attemptValue.payload, new AbortController().signal);
      setSelectedException(updated); setExceptionReason(""); setExceptionAttempt(null);
      setMessage(`${updated.replay ? "Previous exception action recovered. " : ""}Case ${updated.lifecycle_state}; disposition ${updated.state}; latest evidence ${updated.latest_evidence_state}, resolution ${updated.evidence_resolution}. Owner: ${exceptionOwnerLabel(updated.owner)}. Original evidence is unchanged.`);
      history(updated.id); setRevision(value => value + 1);
    } catch (failure) {
      setError(readableError(failure));
      if (!ambiguous(failure)) setExceptionAttempt(null);
      setRevision(value => value + 1);
    }
    finally { setBusy(false); }
  }

  const mayDecide = hasRole("Approver") && selectedRequest?.actor_id !== actorId;
  const mayHandle = selectedException?.owner_actor_id === actorId && hasRole("Operator");
  const mayReserve = hasRole("Operator");
  const mayDecideRelease = hasRole("Approver") && selectedRelease?.requester_id !== actorId;
  const mayAttemptTicket = hasRole("Operator");
  const mayEvaluateNotice = hasRole("Operator");
  const mayAcknowledgeNotice = noticeDetail !== null && noticeDetail.is_current_recipient
    && noticeDetail.state !== "resolved" && noticeDetail.current_notification !== null
    && noticeDetail.current_notification.routing_status === "assigned"
    && noticeDetail.current_notification.delivery_status !== "acknowledged"
    && hasRole("Operator");
  const locked = busy || !!attempt || !!pointer || !!storageError;
  const trackingResolved = requestHandoffChecked && requestHandoffFor === selectedRequest?.id;
  const trackedRequest = trackingResolved && requestHandoff !== null;
  const exceptionHeading = useRef<HTMLHeadingElement | null>(null);
  useEffect(() => {
    if (!selectedException) return;
    exceptionHeading.current?.focus({ preventScroll: true });
    exceptionHeading.current?.scrollIntoView({ block: "start" });
  }, [selectedException?.id, exceptionOpenRevision]);

  return <section aria-labelledby="workflow-heading">
    <div className="page-heading"><div><p className="eyebrow">Current workflow · saved evidence boundary</p><h1 id="workflow-heading">Allocation and review</h1>
      <p className="intro">Reserve an exact IPv4 hold, request its conversion, obtain independent decisions, and track the separate simulated ticket handoff.</p></div>
      <button className="secondary" disabled={loading || busy} onClick={refresh}>Refresh workflow</button></div>
    <div className="evidence-banner"><strong>Synthetic workflow</strong><span>The local ledger is real: reservations and allocations are database changes. Ticket handoff is simulated. External provisioning is unsupported and not requested; any stored legacy simulated status is historical only. Queue actions leave calculated findings unchanged.</span></div>
    <p className="quiet">The queue shows evidence from its last refresh. Returning to this view refreshes it; use Refresh workflow to include runs acquired while this view stays open.</p>
    {error && <div className="notice" role="alert"><strong>Action or refresh failed</strong><p>{error}</p></div>}
    {message && <div className="notice" role="status">{message}</div>}
    {storageError && <div className="notice error" role="alert"><h2>Recovery storage unavailable</h2><p>{storageError}</p></div>}
    {recoveryStatus && <div className={pointer ? "notice error" : "notice"} role="status"><p>{recoveryStatus}</p>
      {pointer && <button type="button" className="secondary" disabled={busy || !!attempt || !!storageError} onClick={() => setReadbackRevision(value => value + 1)}>Retry authorized readback</button>}</div>}
    {attempt && <div className="notice" role="status"><h2>Exact {attempt.action} retained in this session</h2>
      <p>The original key and target remain for exact retry or exact-key readback. Only the minimal recovery pointer is stored in this tab; no token, reason, service reference or receipt is stored. No new key or identity substitution will be used.</p>
      <button type="button" disabled={busy || !!storageError} onClick={() => void submit(attempt)}>Retry exact operation</button>
      {attempt.action === "ticket.attempt" && <button type="button" className="secondary" disabled={busy || !!storageError} onClick={() => void checkAttemptReceipt()}>Check saved attempt receipt (exact key)</button>}
      {attempt.action === "notice.acknowledge" && <span className="quiet"> The exact notice, version, reservation and reason are retained in memory only. The stored pointer carries the original principal, domain, configuration, notice, version and reservation — no token, reason or receipt.</span>}</div>}
    {exceptionAttempt && <div className="notice" role="status"><p>The response for exception <code>{exceptionAttempt.id}</code> is unconfirmed. Retry retains action <strong>{exceptionAttempt.payload.action}</strong>, actor <code>{exceptionAttempt.payload.actor_id}</code>, reviewed version {exceptionAttempt.payload.version}, reason and recipient. An intervening update may require a fresh review.</p>
      <button disabled={busy} onClick={() => void exceptionAction(exceptionAttempt.payload.action)}>Retry exact exception action</button></div>}
    {loading && <p role="status">Loading saved workflow records…</p>}
    {status && <>
      <p className="filter-help">Authenticated principal: {actorId}. Requests require Requester; independent decisions require Approver; reservation, extension, release proposal and ticket actions require Operator.</p>

      <section className="inventory-panel" aria-labelledby="reservation-heading"><div className="section-heading"><h2 id="reservation-heading">Reserve from {status.pool.name}</h2></div>
        <p>Ranges: {status.pool.ranges.map(range => `${range.start}–${range.end}`).join(", ")}. Exclusions: {status.pool.exclusions.map(range => `${range.start}–${range.end}`).join(", ") || "none"}.</p>
        <p className="quiet">Reviewed pool version {status.pool.pool_version}; intended ledger version {status.baseline_version}. Current DHCP contradictions are rechecked at demo clock {status.demo_clock_at}.</p>
        <form onSubmit={event => {
          event.preventDefault();
          submitReservationCreate(event);
        }}>
          <fieldset disabled={locked || !mayReserve}><legend>Exact IPv4 hold for this review</legend><div className="filters">
            <label>IPv4 address<input value={resAddress} required maxLength={45} onChange={event => setResAddress(event.target.value)} placeholder="Enter one address within the range" /></label>
            <label>Owner reference<input value={resOwnerRef} required maxLength={200} onChange={event => setResOwnerRef(event.target.value)} /></label>
            <label>Service reference<input value={resServiceRef} required maxLength={200} onChange={event => setResServiceRef(event.target.value)} /></label>
            <label>Reservation reason<input value={resReason} required maxLength={2000} onChange={event => setResReason(event.target.value)} /></label>
            <label>Duration hours (1–168)<input value={resDuration} required inputMode="numeric" onChange={event => setResDuration(event.target.value)} /></label>
          </div></fieldset>
          {!mayReserve && <p>An Operator must authenticate to reserve this hold.</p>}
          <button disabled={locked || !mayReserve} type="submit">Create reserved hold</button>
        </form>
      </section>

      <section className="inventory-panel" aria-labelledby="reservations-heading"><div className="section-heading"><h2 id="reservations-heading">Saved reservation holds</h2></div>
        {reservations && <><div className="table-scroll"><table><thead><tr><th>Address</th><th>State</th><th>Owner / service</th><th>Expires</th><th>Review</th></tr></thead><tbody>
          {reservations.items.map(item => <tr key={item.id} data-selected={selectedReservationId === item.id}><td><code>{item.address}</code><div className="quiet">v{item.version}</div></td><td>{item.state}</td>
            <td>{item.owner_reference} · {item.service_reference}</td><td>{item.expires_at}</td>
            <td><button className="secondary" disabled={locked} onClick={() => { setSelectedReservationId(item.id); setReleaseOffset(0); setExtendReason(""); setProposeReason(""); setResOpReadback(null); }}>Open hold</button></td></tr>)}
        </tbody></table></div>{!reservations.total && <p>No reservation holds have been stored.</p>}<PageButtons page={reservations} change={setReservationOffset} /></>}
        {resOpReadback?.found && resOpReadback.original_outcome && <div className="notice" role="status"><h3>Original operation receipt · {resOpReadback.action}</h3>
          {"reservation_version" in resOpReadback.original_outcome
            ? <dl className="facts"><dt>Original proposal</dt><dd><code>{resOpReadback.original_outcome.id}</code> · hold <code>{resOpReadback.original_outcome.reservation_id}</code> at version {resOpReadback.original_outcome.reservation_version}</dd>
              <dt>Original outcome</dt><dd>{resOpReadback.original_outcome.state}{resOpReadback.original_outcome.decided_at ? ` · decided ${resOpReadback.original_outcome.decided_at}` : ""}</dd>
              {resOpReadback.original_outcome.decision_reason && <><dt>Original decision reason</dt><dd>{resOpReadback.original_outcome.decision_reason}</dd></>}</dl>
            : <dl className="facts"><dt>Original hold</dt><dd><code>{resOpReadback.original_outcome.id}</code> · {resOpReadback.original_outcome.address} · version {resOpReadback.original_outcome.version}</dd>
              <dt>Original outcome</dt><dd>{resOpReadback.original_outcome.state} · expires {resOpReadback.original_outcome.expires_at}</dd></dl>}
          {resOpReadback.current_reservation && <p>Current hold: {resOpReadback.current_reservation.address} · {resOpReadback.current_reservation.state} · version {resOpReadback.current_reservation.version} · expires {resOpReadback.current_reservation.expires_at}.</p>}
          {resOpReadback.current_release_request && <p>Current proposal: {resOpReadback.current_release_request.state} · hold version {resOpReadback.current_release_request.reservation_version}.</p>}
          <p className="quiet">The receipt proves the original outcome only; current values above may differ.</p></div>}
        {reservationDetail && <div className="notice"><h3>Hold {reservationDetail.address} · {reservationDetail.state}</h3>
          <p><code>{reservationDetail.id}</code> · version {reservationDetail.version}</p>
          <p>Owner reference: {reservationDetail.owner_reference}. Service reference: {reservationDetail.service_reference}. Reason: {reservationDetail.reason}</p>
          <p>Expires {reservationDetail.expires_at}. An expired hold still holds until extension, conversion or an approved unused release.</p>
          {reservationDetail.converted_allocation_id && <p>Converted to allocation <code>{reservationDetail.converted_allocation_id}</code>.</p>}
          {reservationDetail.released_at && <p>Released at {reservationDetail.released_at}.</p>}
          {reservationDetail.state === "reserved" && <>
            <label>Extension duration hours (1–168)<input value={extendDuration} disabled={locked} onChange={event => setExtendDuration(event.target.value)} /></label>
            <label>Extension reason<input value={extendReason} maxLength={2000} disabled={locked} onChange={event => setExtendReason(event.target.value)} /></label>
            <div className="pagination"><button disabled={locked || !mayReserve} onClick={submitExtend}>Extend exact hold</button></div>
            {!mayReserve && <p>An Operator must authenticate to extend this hold.</p>}
          </>}
          <details><summary>Hold history ({reservationDetail.history.length})</summary>
            <ul className="plain-list">{reservationDetail.history.map(entry => <li key={entry.id}>{entry.action} · v{entry.version} · {entry.occurred_at} · {entry.reason}</li>)}</ul>
          </details>
        </div>}
      </section>

      <section className="inventory-panel" aria-labelledby="release-heading"><div className="section-heading"><h2 id="release-heading">Unused release proposals</h2></div>
        {!selectedReservationId && <p className="quiet">Open a reservation hold to propose or decide its unused release.</p>}
        {selectedReservationId && releases && <><div className="table-scroll"><table><thead><tr><th>Proposal</th><th>State</th><th>Reason</th><th>Review</th></tr></thead><tbody>
          {releases.items.map(item => <tr key={item.id} data-selected={selectedRelease?.id === item.id}><td><code>{item.id}</code><div className="quiet">hold v{item.reservation_version}</div></td>
            <td>{item.state}</td><td>{item.reason}</td>
            <td><button className="secondary" disabled={locked} onClick={() => { setSelectedRelease(item); setReleaseDecisionReason(""); }}>Open proposal</button></td></tr>)}
        </tbody></table></div>{!releases.total && <p>No release proposals for this hold.</p>}<PageButtons page={releases} change={setReleaseOffset} /></>}
        {reservationDetail?.state === "reserved" && <>
          <label>Unused release reason<input value={proposeReason} maxLength={2000} disabled={locked} onChange={event => setProposeReason(event.target.value)} /></label>
          <div className="pagination"><button disabled={locked || !mayReserve || !proposeReason.trim()} onClick={submitPropose}>Propose unused release</button></div>
          {!mayReserve && <p>An Operator must authenticate to propose release.</p>}
          <p className="quiet">A pending proposal is not a release. A linked hold with a pending, routing-blocked or unknown ticket intent cannot be released until that ticket resolves.</p>
        </>}
        {selectedRelease && <div className="notice"><h3>Proposal <code>{selectedRelease.id}</code> · {selectedRelease.state}</h3>
          <p>Hold <code>{selectedRelease.reservation_id}</code> at version {selectedRelease.reservation_version}. Reason: {selectedRelease.reason}</p>
          {selectedRelease.decided_at && <p>Decided {selectedRelease.decided_at}: {selectedRelease.decision_reason}</p>}
          {selectedRelease.state === "pending" && <>
            {!mayDecideRelease && <p>A different actor with approval permission must decide this proposal.</p>}
            <label>Decision reason<input value={releaseDecisionReason} maxLength={2000} disabled={locked} onChange={event => setReleaseDecisionReason(event.target.value)} /></label>
            <div className="pagination"><button disabled={locked || !mayDecideRelease || !releaseDecisionReason.trim()} onClick={() => void decideReleaseAction("approve")}>Approve unused release</button>
              <button className="secondary" disabled={locked || !mayDecideRelease || !releaseDecisionReason.trim()} onClick={() => void decideReleaseAction("reject")}>Reject proposal</button></div>
          </>}
        </div>}
      </section>

      <section className="inventory-panel" aria-labelledby="request-heading"><div className="section-heading"><h2 id="request-heading">Request from {status.pool.name}</h2></div>
        <form onSubmit={event => void submitRequest(event)}>
          <fieldset disabled={locked || !hasRole("Requester")}><legend>Exact candidate for this review</legend><div className="filters">
            <label>IPv4 address<input value={candidate} required maxLength={45} onChange={event => setCandidate(event.target.value)} placeholder="Enter one address within the range" /></label>
            <label>Intended owner<input value={owner} required maxLength={200} onChange={event => setOwner(event.target.value)} /></label>
            <label>Purpose<input value={purpose} required maxLength={200} onChange={event => setPurpose(event.target.value)} /></label>
            <label>Request reason<input value={reason} required maxLength={500} onChange={event => setReason(event.target.value)} /></label>
          </div>
          <label><input type="checkbox" checked={linkReservation} disabled={locked} onChange={event => setLinkReservation(event.target.checked)} /> Link this request to an existing reserved hold (approval converts that exact hold)</label>
          {linkReservation && <div className="filters">
            <label>Reservation ID<input value={linkReservationId} maxLength={200} disabled={locked} onChange={event => setLinkReservationId(event.target.value)} placeholder="Reserved hold to convert" /></label>
            <label>Service reference<input value={linkServiceRef} maxLength={200} disabled={locked} onChange={event => setLinkServiceRef(event.target.value)} /></label>
            <label>Reservation version<input value={linkReservationVersion} inputMode="numeric" disabled={locked} onChange={event => setLinkReservationVersion(event.target.value)} /></label>
          </div>}</fieldset>
          {supersedes && <p>Renewed review supersedes request <code>{supersedes}</code>.</p>}
          {attempt?.action === "allocation.create" && <p role="status">The previous response was uncertain. Retry sends the same candidate, actor, versions and creation key.</p>}
          <button disabled={locked || !hasRole("Requester")} type="submit">{attempt?.action === "allocation.create" ? "Retry exact request" : "Create pending request"}</button>
        </form>
      </section>

      <section className="inventory-panel" aria-labelledby="requests-heading"><div className="section-heading"><h2 id="requests-heading">Saved allocation requests</h2></div>
        {requests && <><div className="table-scroll"><table><thead><tr><th>Candidate</th><th>State</th><th>Requested by</th><th>Reviewed versions</th><th>Review</th></tr></thead><tbody>
          {requests.items.map(item => <tr key={item.id}><td><code>{item.candidate}</code></td><td>{item.state}</td><td>{status.actors.find(value => value.id === item.actor_id)?.name ?? item.actor_id ?? "Another principal (identity hidden)"}</td>
            <td>Pool {item.pool_version} / ledger {item.baseline_version}</td><td><button className="secondary" disabled={locked} onClick={() => { selectRequest(item); history(item.id); }}>Open request</button></td></tr>)}
        </tbody></table></div>{!requests.total && <p>No allocation requests have been stored.</p>}<PageButtons page={requests} change={setRequestOffset} /></>}
        {selectedRequest && <div className="notice"><h3>Review {selectedRequest.candidate}</h3><p><code>{selectedRequest.id}</code> · {selectedRequest.state}</p>
          <p>Owner: {selectedRequest.payload.owner}. Purpose: {selectedRequest.payload.purpose}. Request reason: {selectedRequest.payload.reason}</p>
          <p>Local outcome: <strong>{selectedRequest.local_outcome}</strong>. Provisioning: <strong>{selectedRequest.downstream_status ?? "not requested"}</strong>{selectedRequest.downstream_status === "simulated_success" || selectedRequest.downstream_status === "simulated_failure" ? " (historical legacy result)" : ""}.</p>
          {selectedRequest.reservation_id && <p>Linked hold <code>{selectedRequest.reservation_id}</code> · service {selectedRequest.payload.service_reference} · hold version {selectedRequest.payload.reservation_version}.</p>}
          {selectedRequest.allocation_id && <p>Allocation ID: <code>{selectedRequest.allocation_id}</code></p>}
          {selectedRequest.decision_reason && <p>Decision reason: {selectedRequest.decision_reason}</p>}
          <p>Ticket tracking: {trackingResolved ? requestHandoff ? <><strong>{requestHandoff.state}</strong> · correlation <code>{requestHandoff.correlation}</code> · attempts {requestHandoff.attempts_used}/{requestHandoff.attempt_limit}</> : "Confirmed absent — legacy request, not tracked by ticketing" : "Unknown — resolving ticket tracking…"}</p>
          {!trackingResolved && selectedRequest.state === "pending" && <p className="notice">Ticket tracking is unknown for this request, so decisions are unavailable until tracking resolves to a handoff or a confirmed absence. No tracked-versus-legacy guess will be used. <button type="button" className="secondary" disabled={locked} onClick={() => setRevision(value => value + 1)}>Retry ticket tracking lookup</button></p>}
          {trackedRequest && <p className="quiet">Tracked requests use the separate simulated ticket handoff. The local decision never simulates delivery or provisioning; provisioning is not requested and unsupported.</p>}
          {((selectedRequest.state === "pending" && trackingResolved) || attempt?.action === "allocation.decision") && <>
            {!mayDecide && attempt?.action !== "allocation.decision" && <p>A different actor with approval permission must decide this request.</p>}
            <label>Decision reason<input value={decisionReason} maxLength={500} disabled={locked} onChange={event => setDecisionReason(event.target.value)} /></label>
            {trackingResolved && !trackedRequest && <label><input type="checkbox" checked={simulateFailure} disabled={locked} onChange={event => setSimulateFailure(event.target.checked)} /> Simulate downstream provisioning failure after a local approval (legacy requests only; stored as a historical legacy status)</label>}
            {attempt?.action === "allocation.decision" ? <><p>Decision response is uncertain. Retry preserves the exact decision; it cannot allocate twice.</p><button disabled={busy} onClick={() => void submit(attempt)}>Retry exact decision</button></> :
              <div className="pagination"><button disabled={locked || !mayDecide || !decisionReason.trim()} onClick={() => void decide("approve")}>Approve exact candidate</button>
                <button className="secondary" disabled={locked || !mayDecide || !decisionReason.trim()} onClick={() => void decide("reject")}>Reject request</button></div>}
          </>}
          <button className="secondary" disabled={locked || selectedRequest.actor_id !== actorId} onClick={() => {
            setCandidate(selectedRequest.candidate); setOwner(selectedRequest.payload.owner); setPurpose(selectedRequest.payload.purpose);
            setReason(""); setSupersedes(selectedRequest.id); refresh();
          }}>Prepare renewed review with current versions</button>
        </div>}
      </section>

      <section className="inventory-panel" aria-labelledby="handoffs-heading"><div className="section-heading"><h2 id="handoffs-heading">Simulated ticket handoffs</h2></div>
        <p className="quiet">Simulated ticketing handoff — ServiceNow mapping pending. Local approval affects only the local ledger; delivery is simulated separately and provisioning is unsupported and not requested.</p>
        <form onSubmit={event => { event.preventDefault(); setHandoffOffset(0); setAppliedHandoffSource(handoffSourceFilter.trim()); }}>
          <label>Filter by source request ID (optional)<input value={handoffSourceFilter} disabled={locked} onChange={event => setHandoffSourceFilter(event.target.value)} placeholder="Allocation request ID" /></label>
          <button className="secondary" disabled={locked} type="submit">Apply source filter</button>
        </form>
        {handoffs && <><div className="table-scroll"><table><thead><tr><th>Correlation</th><th>State</th><th>Attempts</th><th>Route team</th><th>Review</th></tr></thead><tbody>
          {handoffs.items.map(item => <tr key={item.id} data-selected={selectedHandoffId === item.id}><td><code>{item.correlation}</code><div className="quiet">{item.source_request_state}</div></td>
            <td>{item.state}{item.readback_required ? " · readback required" : ""}</td>
            <td>{item.attempts_used}/{item.attempt_limit} manual</td><td>{item.route.team ?? "routing blocked"}</td>
            <td><button className="secondary" disabled={locked} onClick={() => { setSelectedHandoffId(item.id); setAttemptScenario("success"); setReassignReason(""); setLastTicketOp(""); setTicketOriginal(null); }}>Open handoff</button></td></tr>)}
        </tbody></table></div>{!handoffs.total && <p>No ticket handoffs are tracked in this view. A legacy request without a handoff is not a failed delivery.</p>}<PageButtons page={handoffs} change={setHandoffOffset} /></>}
        {handoffDetail && <div className="notice"><h3>Handoff {handoffDetail.state} · {handoffDetail.attempts_used}/{handoffDetail.attempt_limit} manual attempts</h3>
          <p><code>{handoffDetail.id}</code> · version {handoffDetail.version}</p>
          <dl className="facts"><dt>Fixed correlation</dt><dd><code>{handoffDetail.correlation}</code></dd>
            <dt>Source request</dt><dd><code>{handoffDetail.source_request_id}</code> · {handoffDetail.source_request_state}</dd>
            <dt>Local versus ticket</dt><dd>Local request {handoffDetail.source_request_state}; ticket {handoffDetail.state}. Ticket delivery never decides the local ledger.</dd>
            <dt>Route assignment</dt><dd>{handoffDetail.route.team ?? "routing blocked"} · assignment v{handoffDetail.current_route_assignment_version} · route revision {handoffDetail.route.route_revision}</dd>
            <dt>Provisioning</dt><dd>not requested · unsupported in Tier A</dd>
            <dt>Recipient acknowledgement</dt><dd>{handoffDetail.recipient_acknowledged ? "Simulated acknowledgement recorded" : "No simulated acknowledgement"}</dd></dl>
          {lastTicketOp && <p role="status">{lastTicketOp} Current state above may differ from that original operation.</p>}
          {ticketOriginal && <details><summary>Original ticket operation ({ticketOriginal.phase}) — historical, separate from current state</summary>
            {ticketOriginal.phase === "reserve" && ticketOriginal.attempt && <dl className="facts"><dt>Reserved ordinal</dt><dd>{ticketOriginal.attempt.ordinal}</dd>
              <dt>Scenario</dt><dd>{ticketOriginal.attempt.synthetic_scenario}</dd>
              <dt>Route assignment version</dt><dd>{ticketOriginal.attempt.route_assignment_version}</dd>
              <dt>Reserved at</dt><dd>{ticketOriginal.attempt.started_at}</dd></dl>}
            {ticketOriginal.phase === "reassign" && ticketOriginal.assignment && <dl className="facts"><dt>Assigned team</dt><dd>{ticketOriginal.assignment.team ?? "unassigned"}</dd>
              <dt>Assignment version</dt><dd>{ticketOriginal.assignment.assignment_version}</dd>
              <dt>Route revision</dt><dd>{ticketOriginal.assignment.route_revision} · config {ticketOriginal.assignment.configuration_revision}</dd>
              <dt>Assigned</dt><dd>{ticketOriginal.assignment.assigned_at}{ticketOriginal.assignment.reason ? ` · ${ticketOriginal.assignment.reason}` : ""}</dd></dl>}
            {(ticketOriginal.phase === "readback" || ticketOriginal.phase === "acknowledge") && ticketOriginal.event && <dl className="facts"><dt>Event</dt><dd>{ticketOriginal.event.event_type} · {ticketOriginal.event.outcome}</dd>
              {ticketOriginal.event.resolution && <><dt>Resolution</dt><dd>{ticketOriginal.event.resolution}</dd></>}
              {ticketOriginal.event.returned_ticket_id && <><dt>Ticket</dt><dd>{ticketOriginal.event.returned_ticket_id}</dd></>}
              <dt>Recorded</dt><dd>{ticketOriginal.event.occurred_at}</dd></dl>}
          </details>}
          {handoffDetail.attempt_allowed === false && handoffDetail.attempt_block_reason && <p>New attempts blocked: {handoffDetail.attempt_block_reason}. Authorized readback and history remain available.</p>}
          {handoffDetail.readback_required && <p>A manual readback with the current version, correlation and digest is required.</p>}
          {handoffDetail.attempts.length > 0 && <details><summary>Manual attempts ({handoffDetail.attempts.length})</summary>
            <ul className="plain-list">{handoffDetail.attempts.map(attemptItem => <li key={attemptItem.id}>Ordinal {attemptItem.ordinal} · {attemptItem.synthetic_scenario} · {attemptItem.result}{attemptItem.observed_ticket_id ? ` · ticket ${attemptItem.observed_ticket_id}` : ""}{attemptItem.reason ? ` · ${attemptItem.reason}` : ""}</li>)}</ul>
          </details>}
          {handoffDetail.events.length > 0 && <details><summary>Readback and acknowledgement events ({handoffDetail.events.length})</summary>
            <ul className="plain-list">{handoffDetail.events.map(event => <li key={event.id}>{event.event_type} · {event.outcome}{event.resolution ? ` · ${event.resolution}` : ""}{event.returned_ticket_id ? ` · ticket ${event.returned_ticket_id}` : ""} · {event.occurred_at}</li>)}</ul>
          </details>}
          {handoffDetail.route_history.length > 0 && <details><summary>Route assignment history ({handoffDetail.route_history.length})</summary>
            <ul className="plain-list">{handoffDetail.route_history.map(entry => <li key={`${handoffDetail.id}-${entry.assignment_version}`}>v{entry.assignment_version} · {entry.team ?? "unassigned"} · route {entry.route_revision} · {entry.assigned_at}</li>)}</ul>
          </details>}
          <fieldset disabled={locked || !mayAttemptTicket}><legend>Manual ticket actions · no automatic retry</legend>
            <label>Synthetic scenario for the next manual attempt<select value={attemptScenario} disabled={locked} onChange={event => setAttemptScenario(event.target.value as (typeof SCENARIOS)[number])}>
              {SCENARIOS.map(scenario => <option key={scenario} value={scenario}>{scenario}</option>)}
            </select></label>
            <p className="quiet">One attempt spans three committed transactions: reserve the ordinal, commit the synthetic effect, then observe the response. Any failure preserves the pointer; check the saved receipt by its exact key and run a separate manual readback.</p>
            <div className="pagination">
              <button disabled={locked || !mayAttemptTicket || handoffDetail.attempt_allowed === false} onClick={submitAttempt}>Run manual attempt</button>
              <button className="secondary" disabled={locked || !mayAttemptTicket} onClick={submitReadback}>Run manual readback (exact correlation and digest)</button>
              <button className="secondary" disabled={locked || !mayAttemptTicket || handoffDetail.state !== "delivered"} onClick={submitAcknowledge}>Record simulated acknowledgement</button>
            </div>
            <label>Reassignment reason (zero attempts only)<input value={reassignReason} maxLength={2000} disabled={locked} onChange={event => setReassignReason(event.target.value)} /></label>
            <div className="pagination"><button className="secondary" disabled={locked || !mayAttemptTicket || handoffDetail.reassignment_allowed !== true || !reassignReason.trim()} onClick={submitReassign}>Reassign to current reviewed team</button></div>
            {handoffDetail.reassignment_allowed !== true && <p className="quiet">Route reassignment is available only while pending or routing-blocked with zero attempts, and only to the current reviewed team.</p>}
          </fieldset>
          {!mayAttemptTicket && <p>An Operator must authenticate for manual ticket actions.</p>}
          <ServiceNowIncident handoffId={handoffDetail.id} actorId={actorId} mayOperate={mayAttemptTicket} locked={locked} />
        </div>}
      </section>

      <section className="inventory-panel" aria-labelledby="notices-heading"><div className="section-heading"><h2 id="notices-heading">Reservation notices · recipient receipt</h2></div>
        <p className="quiet">A notice is a local reservation lifecycle record, not a saved-run finding or proof of owner delivery. Acknowledgement never frees a hold or resolves its condition. Owner signoff is always false; a configured recipient is not a proven business owner.</p>
        <div className="pagination">
          <button disabled={locked || !mayEvaluateNotice} onClick={() => void submitEvaluate()}>Run explicit notice evaluation</button>
          {!mayEvaluateNotice && <span className="quiet">An Operator must authenticate for explicit evaluation.</span>}
        </div>
        <p className="quiet">Explicit manual evaluation only. GET never changes state; there is no background scheduler or automatic POST retry. A failed evaluation stays unknown until an authorized notice-list readback; a later evaluation is a new evaluation, not proof of the earlier response.</p>
        {evaluateResult && <div className="notice" role="status"><p>Evaluated at {evaluateResult.evaluated_at}: {evaluateResult.created_count} created · {evaluateResult.renewed_count} renewed · {evaluateResult.alarm_upgrade_count} alarm upgrades.</p></div>}
        <form onSubmit={event => { event.preventDefault(); setNoticeOffset(0); setAppliedNoticeReservation(noticeReservationFilter.trim()); }}>
          <label>Filter by reservation ID (optional)<input value={noticeReservationFilter} disabled={locked} onChange={event => setNoticeReservationFilter(event.target.value)} placeholder="Reservation ID" /></label>
          <button className="secondary" disabled={locked} type="submit">Apply reservation filter</button>
        </form>
        {notices && <><div className="table-scroll"><table><thead><tr><th>Episode / level</th><th>State / receipt</th><th>Version</th><th>Review</th></tr></thead><tbody>
          {notices.items.map(item => <tr key={item.id} data-selected={selectedNoticeId === item.id}><td>Episode {item.episode_number} · {item.alert_level}<div className="quiet">hold <code>{item.reservation_id}</code></div></td>
            <td>{item.state} · {item.delivery_status ?? "unknown"}</td>
            <td>v{item.notification_version} · {item.notification_history_coverage.replaceAll("_", " ")}</td>
            <td><button className="secondary" disabled={locked} onClick={() => { setSelectedNoticeId(item.id); setAckReason(""); setRecoveredNoticeVersion(null); }}>Open notice</button></td></tr>)}
        </tbody></table></div>{!notices.total && <p>No reservation notices in this view. Run an explicit evaluation after a hold passes its expiry.</p>}<PageButtons page={notices} change={setNoticeOffset} />
        {selectedNoticeId && !notices.items.some(item => item.id === selectedNoticeId) && <p className="quiet">The selected notice is outside this list page or filter; the selection is retained and its current detail loads independently below, or is reported unknown if unavailable. A recovered original receipt, if any, is historical only and never substitutes for current state.</p>}</>}
        {pointer?.action === "notice.acknowledge" && <div className="notice error" role="status"><p>Unresolved acknowledgement for notice <code>{pointer.target_id}</code> version {pointer.notification_version} in reservation <code>{pointer.secondary_id}</code>. It belongs to {pointer.principal_id} in domain {pointer.domain}. A missing, denied or mismatched receipt stays unknown and blocks replacement; no silent replacement will be sent.</p>
          <button type="button" className="secondary" disabled={busy || !!storageError} onClick={() => void checkNoticeReceipt()}>Confirm original receipt (exact version)</button></div>}
        {recoveredNoticeVersion && <div className="notice" role="status"><h3>Recovered original receipt · version {recoveredNoticeVersion.notification_version}</h3>
          <dl className="facts"><dt>Notice</dt><dd><code>{recoveredNoticeVersion.notice_id}</code> · reservation <code>{recoveredNoticeVersion.reservation_id}</code> · episode {recoveredNoticeVersion.episode_number}</dd>
            <dt>Receipt</dt><dd>{recoveredNoticeVersion.acknowledged_by ?? "redacted"} · {recoveredNoticeVersion.acknowledged_at ?? "unknown time"} · {recoveredNoticeVersion.acknowledgement_reason ?? "redacted"}</dd>
            <dt>Kind</dt><dd>{recoveredNoticeVersion.acknowledgement_kind ?? "none"} · in-app receipt {String(recoveredNoticeVersion.in_app_receipt)}</dd></dl>
          <p className="quiet">This recovered receipt is historical and separate from the mutable current notice and version above. Cleared only on this confirmed receipt.</p></div>}
        {noticeDetail && <div className="notice"><h3>Notice episode {noticeDetail.episode_number} · {noticeDetail.alert_level} · {noticeDetail.state}</h3>
          <p><code>{noticeDetail.id}</code> · hold <code>{noticeDetail.reservation_id}</code> · version {noticeDetail.notification_version}</p>
          <dl className="facts"><dt>First due (server)</dt><dd>{noticeDetail.first_due_at}</dd>
            <dt>Owner reference</dt><dd>{noticeDetail.owner_reference}</dd>
            <dt>Policy revision</dt><dd>{noticeDetail.policy_revision}</dd>
            <dt>Receipt</dt><dd>{noticeDeliveryLabel(noticeDetail, actorId)}</dd>
            <dt>Current recipient</dt><dd>{noticeDetail.is_current_recipient ? "you are the current bound recipient" : "you are not the current recipient"}</dd>
            <dt>Acknowledgement kind</dt><dd>{noticeDetail.acknowledgement_kind ?? "none"}</dd>
            <dt>Owner signoff</dt><dd>{String(noticeDetail.owner_signoff)} — never implied by acknowledgement</dd>
            <dt>In-app receipt</dt><dd>{String(noticeDetail.in_app_receipt)}</dd>
            <dt>Acknowledgement current</dt><dd>{String(noticeDetail.acknowledgement_current)}</dd>
            <dt>History coverage</dt><dd>{noticeDetail.notification_history_coverage.replaceAll("_", " ")}</dd>
            {noticeDetail.resolved_at && <><dt>Resolved</dt><dd>{noticeDetail.resolved_at} · {noticeDetail.resolution_reason ?? "unknown reason"}</dd></>}
            {noticeDetail.acknowledged_at && <><dt>Acknowledged</dt><dd>{noticeDetail.acknowledged_at} · {noticeDetail.acknowledged_by ?? "redacted for this principal"} · {noticeDetail.acknowledgement_reason ?? "redacted for this principal"}</dd></>}</dl>
          {noticeDetail.current_notification && <details><summary>Current notification version {noticeDetail.current_notification.notification_version} · {notificationLabel(noticeDetail.current_notification)}</summary>
            <dl className="facts"><dt>Route</dt><dd>{noticeDetail.current_notification.routing_status}{noticeDetail.current_notification.routing_reason ? ` · ${noticeDetail.current_notification.routing_reason}` : ""}</dd>
              <dt>Recipient</dt><dd>{noticeDetail.current_notification.recipient_id ?? "redacted or unbound"}</dd>
              <dt>Issued</dt><dd>{noticeDetail.current_notification.issued_at ?? "legacy — no issue time retained"}</dd>
              <dt>Configuration</dt><dd>{noticeDetail.current_notification.configuration_revision ?? "legacy"} · {noticeDetail.current_notification.configuration_digest ?? "legacy"}</dd></dl></details>}
          {noticeDetail.notification_history.length > 0 && <details><summary>Notification history ({noticeDetail.notification_history.length}) — immutable per-version bindings</summary>
            <ul className="plain-list">{noticeDetail.notification_history.map(item => <li key={`${item.notice_id}-${item.notification_version}`}>v{item.notification_version} · {item.routing_status} · {notificationLabel(item)}{item.acknowledged_at ? ` · ${item.acknowledged_at}` : ""}</li>)}</ul>
            <p className="quiet">A legacy operator acknowledgement is history only, never recipient receipt or delivery proof. Redacted recipient, actor and reason fields stay null for other principals.</p></details>}
          {noticeDetail.state === "resolved" && <p className="quiet">Resolved episodes retain history while acknowledgement_current is false. Resolution never means delivery or acknowledgement.</p>}
          {mayAcknowledgeNotice ? <>
            <label>Acknowledgement reason for exact version {noticeDetail.current_notification?.notification_version}<input value={ackReason} maxLength={2000} disabled={locked} onChange={event => setAckReason(event.target.value)} /></label>
            <div className="pagination"><button disabled={locked || !ackReason.trim()} onClick={submitNoticeAcknowledge}>Acknowledge exact version as current recipient</button></div>
            <p className="quiet">The minimal pointer (original principal, domain, configuration, notice, version and reservation) is stored before sending; the reason stays in memory only. Acknowledgement never frees the hold.</p>
          </> : <p className="quiet">{noticeDetail.is_current_recipient ? "Acknowledgement needs an Operator role, an eligible assigned version and an explicit reason." : "Acknowledgement is offered only to the server-declared current recipient on an eligible version. A different principal cannot acknowledge for the recipient; evaluate to bind the current recipient first."}</p>}
        </div>}
      </section>

      <section className="inventory-panel" aria-labelledby="occupancy-heading"><div className="section-heading"><h2 id="occupancy-heading">Current static IPv4 occupancy</h2><button className="secondary" disabled={busy} onClick={refresh}>Reload occupancy</button></div>
        <p className="quiet">Current ledger occupancy only — metric current_static_ipv4_occupancy in IPv4 addresses. Separate from immutable saved DHCP runs, their run time, p95, forecast and unknowns. Saved runs are never modified.</p>
        {occupancyError && <p className="notice error" role="alert">{occupancyError}</p>}
        {occupancy ? <dl className="facts"><dt>Pool / scope / domain</dt><dd><code>{occupancy.pool_id}</code> · <code>{occupancy.scope_id}</code> · {occupancy.domain} · IPv{occupancy.family}</dd>
          <dt>As of (server UTC)</dt><dd>{occupancy.as_of}</dd>
          <dt>Unit</dt><dd>{occupancy.unit}</dd>
          <dt>Active allocations</dt><dd>{occupancy.components.active_allocations.count} {occupancy.components.active_allocations.unit}</dd>
          <dt>Reserved holds (expired included)</dt><dd>{occupancy.components.reserved_holds.count} {occupancy.components.reserved_holds.unit}</dd>
          <dt>Occupied total</dt><dd>{occupancy.components.occupied_total.count} {occupancy.components.occupied_total.unit}</dd>
          <dt>Assignable capacity</dt><dd>{occupancy.components.assignable_capacity.count} {occupancy.components.assignable_capacity.unit}</dd>
          <dt>Remaining assignable</dt><dd>{occupancy.components.remaining_assignable.count} {occupancy.components.remaining_assignable.unit}</dd>
          <dt>Provenance</dt><dd>{occupancy.provenance.source} · {occupancy.provenance.capacity} · {occupancy.provenance.allocations} · {occupancy.provenance.reservations}</dd></dl>
          : !occupancyError && <p role="status">Loading current occupancy…</p>}
      </section>

      <section className="inventory-panel" aria-labelledby="exceptions-heading"><div className="section-heading"><h2 id="exceptions-heading">In-app exception queue</h2></div>
        <p>Each case preserves its original anomaly and shows the latest comparable evidence separately. Only healthy evidence establishes resolution. Closing or reopening a case changes its operational lifecycle, not its saved findings.</p>
        <p className="quiet">Recurrence or a materially new discrepancy renews the owner's notification. Repeating an unchanged anomaly does not create another notification.</p>
        {exceptions && <><p role="status">{exceptions.items.filter(item => item.notification_pending).length} notifications awaiting owner acknowledgement on this page.</p>
          <div className="table-scroll"><table><thead><tr><th>Original finding / subject</th><th>Latest evidence / resolution</th><th>Owner</th><th>Case / disposition</th><th>Action</th></tr></thead><tbody>
            {exceptions.items.map(item => <tr key={item.id} data-selected={selectedException?.id === item.id}><td>{item.original_finding.rule_id}<div><code>{item.original_finding.subject.cidr}</code> · {item.original_finding.subject.scope_name}</div><div>Original: {item.original_finding.evidence_state} · {item.original_finding.severity}</div></td>
              <td>{item.latest_evidence_state}<div>{item.evidence_resolution === "resolved" ? "Resolved by healthy evidence" : item.evidence_resolution === "active" ? "Active discrepancy" : "Resolution unknown"}</div><div className="quiet">{item.latest_evidence_reason.replaceAll("_", " ")}</div></td>
              <td>{exceptionOwnerLabel(item.owner)}</td><td>{item.lifecycle_state} · disposition {item.state}<div>Notification {item.notification_version}{item.notification_pending ? " · acknowledgement due" : " · none pending"}</div></td>
              <td><button className="secondary" aria-expanded={selectedException?.id === item.id} aria-controls={selectedException?.id === item.id ? "exception-detail" : undefined} disabled={busy || !!exceptionAttempt} onClick={() => { setSelectedException(item); setExceptionOpenRevision(value => value + 1); setExceptionReason(""); history(item.id); }}>{selectedException?.id === item.id ? "Opened" : "Open exception"}</button></td></tr>)}
          </tbody></table></div>{!exceptions.total && <p>No permitted saved exceptions are available. The evidence operator manages reconciliation.</p>}<PageButtons page={exceptions} change={setExceptionOffset} /></>}
        {selectedException && <section className="notice exception-detail" id="exception-detail" aria-labelledby="exception-detail-heading"><h3 id="exception-detail-heading" ref={exceptionHeading} tabIndex={-1}>{selectedException.original_finding.rule_id} · {selectedException.original_finding.subject.cidr} · {selectedException.original_finding.subject.scope_name} · case {selectedException.lifecycle_state}</h3>
          <p>Owner: {exceptionOwnerLabel(selectedException.owner)}. Operational disposition: {selectedException.state}; reviewed version {selectedException.version}.</p>
          <dl className="facts"><dt>Latest evidence</dt><dd>{selectedException.latest_evidence_state}</dd>
            <dt>Latest evidence reason</dt><dd>{selectedException.latest_evidence_reason.replaceAll("_", " ")}</dd>
            <dt>Evidence resolution</dt><dd>{selectedException.evidence_resolution === "resolved" ? "Resolved by healthy comparable evidence" : selectedException.evidence_resolution === "active" ? "Active discrepancy in the latest evidence" : "Unknown — current evidence does not establish resolution"}</dd>
            <dt>Case closed at</dt><dd>{selectedException.closed_at ?? "Case is open"}</dd>
            <dt>Notification / episode</dt><dd>Notification {selectedException.notification_version} · episode {selectedException.episode_count} · {selectedException.notification_pending ? "owner acknowledgement due" : "no notification pending"}</dd>
            <dt>Notification reason</dt><dd>{selectedException.notification_reason.replaceAll("_", " ")}</dd>
          </dl>
          {selectedException.evidence_resolution === "unknown" && <p className="run-warning">Missing, unknown or not-applicable evidence does not establish resolution, even if the case was previously closed.</p>}
          {selectedException.lifecycle_state === "open" && selectedException.evidence_resolution === "resolved" && <p>Healthy evidence supports closure. The case stays open until its owner explicitly closes it with a reason.</p>}
          <ExceptionEvidence title="Original anomaly · preserved evidence" finding={selectedException.original_finding} />
          {selectedException.latest_finding ? selectedException.latest_comparable ? <ExceptionEvidence title="Latest comparable finding" finding={selectedException.latest_finding} /> :
            <section className="detail-section"><h4>Latest finding · not comparable</h4><p className="run-warning">{selectedException.latest_evidence_reason.replaceAll("_", " ")}. This finding does not establish current resolution for the original case.</p>
              <ExceptionEvidence title="Latest saved finding" finding={selectedException.latest_finding} />
            </section> :
            <section className="detail-section"><h4>Latest comparable finding unavailable</h4><p>{selectedException.latest_run_id ? "The latest run contains no comparable finding. Resolution remains unknown." : "No latest evaluation has been recorded for this case. Reconcile current inputs to refresh its evidence."}</p>
              {selectedException.latest_run_id && <p>Latest evaluated run: <button type="button" className="text-button" onClick={() => { void downloadProtected(`/api/runs/${encodeURIComponent(selectedException.latest_run_id!)}`, "saved-domain-run.json", new AbortController().signal).catch(failure => setError(readableError(failure))); }}>{selectedException.latest_run_id} · download JSON</button>.</p>}
            </section>}
          {selectedException.handoff_at && <p>Handed off from {status.actors.find(item => item.id === selectedException.handoff_from_actor_id)?.name ?? "another principal (identity hidden)"} at {selectedException.handoff_at}. Recipient acknowledgement: {selectedException.acknowledged_at ?? "pending"}.</p>}
          <label>Action reason<input value={exceptionAttempt?.payload.reason ?? exceptionReason} maxLength={500} disabled={busy || !mayHandle || !!exceptionAttempt} onChange={event => setExceptionReason(event.target.value)} /></label>
          {!mayHandle && <p>The assigned Operator must authenticate independently to handle this exception.</p>}
          <fieldset disabled={busy || !mayHandle || !!exceptionAttempt}><legend>Owner actions · findings remain unchanged</legend>
            <div className="pagination"><button disabled={selectedException.lifecycle_state === "closed" || !exceptionReason.trim() || !!selectedException.acknowledged_at} onClick={() => void exceptionAction("acknowledge")}>Acknowledge as owner</button>
              <button className="secondary" disabled={selectedException.lifecycle_state === "closed" || !exceptionReason.trim() || selectedException.state === "escalated"} onClick={() => void exceptionAction("escalate")}>Escalate exception</button>
              <button className="secondary" disabled>Handoff unavailable without an authorized recipient roster</button></div>
            <div className="pagination"><button disabled={!exceptionReason.trim() || selectedException.lifecycle_state !== "open" || !selectedException.latest_comparable || selectedException.latest_evidence_state !== "healthy" || selectedException.evidence_resolution !== "resolved"} onClick={() => void exceptionAction("close")}>Close case from healthy evidence</button>
              <button className="secondary" disabled={!exceptionReason.trim() || selectedException.lifecycle_state !== "closed"} onClick={() => void exceptionAction("reopen")}>Reopen case</button></div>
            <p className="quiet">Close requires a latest healthy finding. Reopen starts operational review again; it does not turn healthy or unknown evidence into an anomaly.</p>
            {selectedException.lifecycle_state === "closed" && <p>Reopen the case before acknowledging, escalating or handing it off.</p>}
          </fieldset>
        </section>}
      </section>
    </>}

    <section className="inventory-panel" aria-labelledby="audit-heading"><div className="section-heading"><h2 id="audit-heading">Stored audit history</h2><button className="secondary" onClick={() => history("")}>Show all events</button></div>
      {auditSubject && <p>Events for <code>{auditSubject}</code>.</p>}
      {audit ? <><div className="table-scroll"><table><thead><tr><th>When / actor</th><th>Action / outcome</th><th>Reason</th><th>Recorded details</th></tr></thead><tbody>
        {audit.items.map(item => <tr key={item.id}><td>{item.created_at}<div>{item.actor_id} · {item.actor_role}</div></td><td>{item.action}<div>{item.outcome}</div></td><td>{item.reason}</td>
          <td><details><summary>Before, after and references</summary><pre>{JSON.stringify(item.details, null, 2)}</pre></details></td></tr>)}
      </tbody></table></div>{!audit.total && <p>No matching audit events.</p>}<PageButtons page={audit} change={setAuditOffset} /></> : <p>Audit history is loading or unavailable; any loading failure appears above.</p>}
    </section>
  </section>;
}
