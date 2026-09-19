import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, request } from "./api";
import type { Page } from "./api";
import { actOnException, createAllocation, decideAllocation, loadWorkflow } from "./workflowApi";
import type { AllocationDecision, AllocationRequest, AuditEvent, CreateAllocation, ExceptionAction,
  ExceptionRecord, WorkflowStatus } from "./workflowApi";

const PAGE_SIZE = 20;

function readableError(error: unknown): string {
  if (error instanceof ApiError) return `${error.message} (${error.code}${error.requestId ? `; request ${error.requestId}` : ""})`;
  return error instanceof Error ? error.message : "The request failed.";
}

function ambiguous(error: unknown) {
  return error instanceof ApiError && ["REQUEST_TIMEOUT", "CONNECTION_FAILED", "INVALID_RESPONSE"].includes(error.code);
}

function PageButtons({ page, change }: { page: Page<unknown>; change: (offset: number) => void }) {
  return <nav className="pagination" aria-label="Workflow list pages"><span>{page.total ? page.offset + 1 : 0}–{page.offset + page.items.length} of {page.total}</span><div>
    <button type="button" className="secondary" disabled={page.offset === 0} onClick={() => change(Math.max(0, page.offset - PAGE_SIZE))}>Previous</button>
    <button type="button" className="secondary" disabled={page.offset + page.items.length >= page.total} onClick={() => change(page.offset + PAGE_SIZE)}>Next</button>
  </div></nav>;
}

export default function Workflow() {
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [actorId, setActorId] = useState("demo-requester");
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
  const [createAttempt, setCreateAttempt] = useState<CreateAllocation | null>(null);
  const [selectedRequest, setSelectedRequest] = useState<AllocationRequest | null>(null);
  const [decisionReason, setDecisionReason] = useState("");
  const [simulateFailure, setSimulateFailure] = useState(false);
  const [decisionAttempt, setDecisionAttempt] = useState<{ id: string; payload: AllocationDecision } | null>(null);
  const [selectedException, setSelectedException] = useState<ExceptionRecord | null>(null);
  const [exceptionReason, setExceptionReason] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    Promise.all([
      loadWorkflow(controller.signal),
      request<Page<AllocationRequest>>(`/api/allocation-requests?limit=${PAGE_SIZE}&offset=${requestOffset}`, controller.signal),
      request<Page<ExceptionRecord>>(`/api/exceptions?limit=${PAGE_SIZE}&offset=${exceptionOffset}`, controller.signal),
    ]).then(([current, items, queue]) => {
      if (controller.signal.aborted) return;
      setStatus(current); setRequests(items); setExceptions(queue);
      setSelectedRequest(previous => previous ? items.items.find(item => item.id === previous.id) ?? previous : null);
      setSelectedException(previous => previous ? queue.items.find(item => item.id === previous.id) ?? previous : null);
    }).catch((failure: unknown) => {
      if (!controller.signal.aborted) setError(`Refresh failed; previously shown data retains its earlier state. ${readableError(failure)}`);
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [revision, requestOffset, exceptionOffset]);

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(auditOffset) });
    if (auditSubject) params.set("subject_id", auditSubject);
    setAudit(null);
    request<Page<AuditEvent>>(`/api/audit?${params}`, controller.signal)
      .then(items => { if (!controller.signal.aborted) setAudit(items); })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Audit history failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [revision, auditOffset, auditSubject]);

  function refresh() { setError(""); setRevision(value => value + 1); }
  function history(id: string) { setAuditSubject(id); setAuditOffset(0); }

  async function submitRequest(event: FormEvent) {
    event.preventDefault();
    if (!status) return;
    const payload = createAttempt ?? {
      actor_id: actorId, idempotency_key: crypto.randomUUID(), pool_id: status.pool.id,
      candidate, owner, purpose, reason, pool_version: status.pool.pool_version,
      baseline_version: status.baseline_version, ...(supersedes ? { supersedes_request_id: supersedes } : {}),
    };
    setCreateAttempt(payload); setBusy(true); setError(""); setMessage("");
    try {
      const created = await createAllocation(payload, new AbortController().signal);
      setSelectedRequest(created); setCreateAttempt(null); setRequestOffset(0);
      setMessage(`Request ${created.id} is ${created.state}. Creation does not reserve the address.`);
      history(created.id); setRevision(value => value + 1);
    } catch (failure) {
      setError(readableError(failure));
      if (!ambiguous(failure)) setCreateAttempt(null);
    } finally { setBusy(false); }
  }

  async function decide(action: "approve" | "reject") {
    if (!selectedRequest) return;
    const attempt = decisionAttempt ?? { id: selectedRequest.id,
      payload: { actor_id: actorId, action, reason: decisionReason, simulate_failure: action === "approve" && simulateFailure } };
    setDecisionAttempt(attempt); setBusy(true); setError(""); setMessage("");
    try {
      const decided = await decideAllocation(attempt.id, attempt.payload, new AbortController().signal);
      setSelectedRequest(decided); setDecisionAttempt(null);
      setMessage(`Request ${decided.state}. Local outcome: ${decided.local_outcome}. External provisioning: ${decided.downstream_status}.`);
      history(decided.id); setRevision(value => value + 1);
    } catch (failure) {
      setError(readableError(failure));
      if (!ambiguous(failure)) setDecisionAttempt(null);
      setRevision(value => value + 1);
    } finally { setBusy(false); }
  }

  async function exceptionAction(action: ExceptionAction["action"]) {
    if (!selectedException || !status) return;
    const recipient = status.actors.find(actor => actor.id !== actorId);
    setBusy(true); setError(""); setMessage("");
    try {
      const updated = await actOnException(selectedException.id, { actor_id: actorId, version: selectedException.version,
        action, reason: exceptionReason, ...(action === "handoff" ? { recipient_actor_id: recipient?.id } : {}) }, new AbortController().signal);
      setSelectedException(updated); setExceptionReason("");
      setMessage(`Exception ${updated.state}; assigned to ${updated.owner.name}, ${updated.owner.team}. Saved evidence is unchanged.`);
      history(updated.id); setRevision(value => value + 1);
    } catch (failure) { setError(readableError(failure)); setRevision(value => value + 1); }
    finally { setBusy(false); }
  }

  const actor = status?.actors.find(item => item.id === actorId);
  const mayDecide = actor?.permissions.includes("approve") && selectedRequest?.actor_id !== actorId;
  const mayHandle = selectedException?.owner_actor_id === actorId;

  return <section aria-labelledby="workflow-heading">
    <div className="page-heading"><div><p className="eyebrow">Local decisions and recorded exceptions</p><h1 id="workflow-heading">Allocation and review</h1>
      <p className="intro">Request an exact IPv4 address, review it as a second demo actor, and inspect the stored audit trail.</p></div>
      <button className="secondary" disabled={loading || busy} onClick={refresh}>Refresh workflow</button></div>
    <div className="evidence-banner"><strong>Synthetic workflow</strong><span>Local allocations are real database changes. External provisioning is simulated. Queue actions leave calculated findings unchanged.</span></div>
    {error && <div className="notice" role="alert"><strong>Action or refresh failed</strong><p>{error}</p></div>}
    {message && <div className="notice" role="status">{message}</div>}
    {loading && <p role="status">Loading saved workflow records…</p>}
    {status && <>
      <div className="filters"><label>Named demo actor<select value={actorId} disabled={busy || !!createAttempt || !!decisionAttempt} onChange={event => setActorId(event.target.value)}>
        {status.actors.map(item => <option key={item.id} value={item.id}>{item.name} · {item.role} · {item.team}</option>)}
      </select></label><p className="filter-help">The server derives permissions from this identity. This switch is a local demonstration, not a sign-in system.</p></div>

      <section className="inventory-panel" aria-labelledby="request-heading"><div className="section-heading"><h2 id="request-heading">Request from {status.pool.name}</h2></div>
        <p>Ranges: {status.pool.ranges.map(range => `${range.start}–${range.end}`).join(", ")}. Exclusions: {status.pool.exclusions.map(range => `${range.start}–${range.end}`).join(", ") || "none"}.</p>
        <p className="quiet">Reviewed pool version {status.pool.pool_version}; intended ledger version {status.baseline_version}. Current DHCP contradictions are rechecked at demo clock {status.demo_clock_at}.</p>
        <form onSubmit={event => void submitRequest(event)}>
          <fieldset disabled={busy || !!createAttempt}><legend>Exact candidate for this review</legend><div className="filters">
            <label>IPv4 address<input value={candidate} required maxLength={45} onChange={event => setCandidate(event.target.value)} placeholder="Enter one address within the range" /></label>
            <label>Intended owner<input value={owner} required maxLength={200} onChange={event => setOwner(event.target.value)} /></label>
            <label>Purpose<input value={purpose} required maxLength={200} onChange={event => setPurpose(event.target.value)} /></label>
            <label>Request reason<input value={reason} required maxLength={500} onChange={event => setReason(event.target.value)} /></label>
          </div></fieldset>
          {supersedes && <p>Renewed review supersedes request <code>{supersedes}</code>.</p>}
          {createAttempt && <p role="status">The previous response was uncertain. Retry sends the same candidate, actor, versions and creation key.</p>}
          <button disabled={busy || loading} type="submit">{createAttempt ? "Retry exact request" : "Create pending request"}</button>
        </form>
      </section>

      <section className="inventory-panel" aria-labelledby="requests-heading"><div className="section-heading"><h2 id="requests-heading">Saved allocation requests</h2></div>
        {requests && <><div className="table-scroll"><table><thead><tr><th>Candidate</th><th>State</th><th>Requested by</th><th>Reviewed versions</th><th>Review</th></tr></thead><tbody>
          {requests.items.map(item => <tr key={item.id}><td><code>{item.candidate}</code></td><td>{item.state}</td><td>{status.actors.find(value => value.id === item.actor_id)?.name ?? item.actor_id}</td>
            <td>Pool {item.pool_version} / ledger {item.baseline_version}</td><td><button className="secondary" disabled={busy || !!decisionAttempt} onClick={() => { setSelectedRequest(item); setDecisionReason(""); history(item.id); }}>Open request</button></td></tr>)}
        </tbody></table></div>{!requests.total && <p>No allocation requests have been stored.</p>}<PageButtons page={requests} change={setRequestOffset} /></>}
        {selectedRequest && <div className="notice"><h3>Review {selectedRequest.candidate}</h3><p><code>{selectedRequest.id}</code> · {selectedRequest.state}</p>
          <p>Owner: {selectedRequest.payload.owner}. Purpose: {selectedRequest.payload.purpose}. Request reason: {selectedRequest.payload.reason}</p>
          <p>Local outcome: <strong>{selectedRequest.local_outcome}</strong>. Provisioning: <strong>{selectedRequest.downstream_status ?? "not requested"}</strong>.</p>
          {selectedRequest.allocation_id && <p>Allocation ID: <code>{selectedRequest.allocation_id}</code></p>}
          {selectedRequest.decision_reason && <p>Decision reason: {selectedRequest.decision_reason}</p>}
          {(selectedRequest.state === "pending" || decisionAttempt) && <>
            {!mayDecide && !decisionAttempt && <p>A different actor with approval permission must decide this request.</p>}
            <label>Decision reason<input value={decisionReason} maxLength={500} disabled={busy || !!decisionAttempt} onChange={event => setDecisionReason(event.target.value)} /></label>
            <label><input type="checkbox" checked={simulateFailure} disabled={busy || !!decisionAttempt} onChange={event => setSimulateFailure(event.target.checked)} /> Simulate downstream provisioning failure after a local approval</label>
            {decisionAttempt ? <><p>Decision response is uncertain. Retry preserves the exact decision; it cannot allocate twice.</p><button disabled={busy} onClick={() => void decide(decisionAttempt.payload.action)}>Retry exact decision</button></> :
              <div className="pagination"><button disabled={busy || !mayDecide || !decisionReason.trim()} onClick={() => void decide("approve")}>Approve exact candidate</button>
                <button className="secondary" disabled={busy || !mayDecide || !decisionReason.trim()} onClick={() => void decide("reject")}>Reject request</button></div>}
          </>}
          <button className="secondary" disabled={busy || !!createAttempt || !!decisionAttempt || selectedRequest.actor_id !== actorId} onClick={() => {
            setCandidate(selectedRequest.candidate); setOwner(selectedRequest.payload.owner); setPurpose(selectedRequest.payload.purpose);
            setReason(""); setSupersedes(selectedRequest.id); refresh();
          }}>Prepare renewed review with current versions</button>
        </div>}
      </section>

      <section className="inventory-panel" aria-labelledby="exceptions-heading"><div className="section-heading"><h2 id="exceptions-heading">In-app exception queue</h2></div>
        <p>Newly calculated anomalies enter this queue once per scoped rule and subject. Acknowledgement and escalation are operational states; the saved evidence stays pinned to its original run.</p>
        {exceptions && <><p role="status">{exceptions.items.filter(item => item.notification_pending).length} notifications awaiting owner acknowledgement on this page.</p>
          <div className="table-scroll"><table><thead><tr><th>Finding / subject</th><th>Saved evidence</th><th>Owner</th><th>Queue state</th><th>Action</th></tr></thead><tbody>
            {exceptions.items.map(item => <tr key={item.id}><td>{item.finding.rule_id}<div><code>{item.finding.subject.cidr}</code> · {item.finding.subject.scope_name}</div></td>
              <td>{item.finding.evidence_state} · {item.finding.severity}</td><td>{item.owner.name} · {item.owner.team}</td><td>{item.state}{item.notification_pending ? " · acknowledgement due" : ""}</td>
              <td><button className="secondary" disabled={busy} onClick={() => { setSelectedException(item); setExceptionReason(""); history(item.id); }}>Open exception</button></td></tr>)}
          </tbody></table></div>{!exceptions.total && <p>No calculated anomalies have entered the queue. Create a reconciliation run from imported evidence to produce findings.</p>}<PageButtons page={exceptions} change={setExceptionOffset} /></>}
        {selectedException && <div className="notice"><h3>{selectedException.finding.rule_id}</h3><p>{selectedException.finding.explanation}</p>
          <p>Saved run <code>{selectedException.run_id}</code>; finding <code>{selectedException.finding_id}</code>. Evidence: {selectedException.finding.evidence_state}.</p>
          <p>Owner: {selectedException.owner.name}, {selectedException.owner.team}. Queue: {selectedException.state}; version {selectedException.version}.</p>
          {selectedException.handoff_at && <p>Handed off from {status.actors.find(item => item.id === selectedException.handoff_from_actor_id)?.name} at {selectedException.handoff_at}. Recipient acknowledgement: {selectedException.acknowledged_at ?? "pending"}.</p>}
          <label>Action reason<input value={exceptionReason} maxLength={500} disabled={busy || !mayHandle} onChange={event => setExceptionReason(event.target.value)} /></label>
          {!mayHandle && <p>Switch to the assigned recipient to acknowledge or handle this exception.</p>}
          <div className="pagination"><button disabled={busy || !mayHandle || !exceptionReason.trim() || !!selectedException.acknowledged_at} onClick={() => void exceptionAction("acknowledge")}>Acknowledge as owner</button>
            <button className="secondary" disabled={busy || !mayHandle || !exceptionReason.trim() || selectedException.state === "escalated"} onClick={() => void exceptionAction("escalate")}>Escalate exception</button>
            <button className="secondary" disabled={busy || !mayHandle || !exceptionReason.trim()} onClick={() => void exceptionAction("handoff")}>Hand off to {status.actors.find(item => item.id !== actorId)?.name}</button></div>
        </div>}
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
