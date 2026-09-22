import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, currentContext, downloadProtected, hasRole, request } from "./api";
import type { Page } from "./api";
import type { Finding, RunSummary, SavedRun } from "./firstPathApi";
import { createCorrection, decideCorrection, findCorrectionByKey, loadCorrection, loadCorrectionContext } from "./correctionApi";
import type { CorrectionContext, CorrectionDecision, CorrectionRequest, CreateCorrection, ResolutionState } from "./correctionApi";

const PAGE_SIZE = 20;
const LEGACY_ATTEMPT_KEY = "ipam.correction.attempt.v1";
const RECOVERY_KEY = "ipam.correction.recovery.v2";
const LEGACY_UNRESOLVED_KEY = "ipam.correction.legacy-unresolved";
const CORRECTION_RULES = ["ghost_scope", "unregistered_managed_route"];
type Attempt = { kind: "proposal"; payload: CreateCorrection } | { kind: "decision"; id: string; payload: CorrectionDecision };
type RecoveryPointer = {
  principal_id: string; domain: string; configuration_revision: number; configuration_digest: string;
  kind: "proposal" | "approve" | "reject"; idempotency_key?: string; request_id?: string;
};
const resolutionLabels: Record<ResolutionState, string> = {
  not_approved: "No approved correction",
  pending_reconciliation: "Approved; reconciliation evidence pending",
  resolved_by_evidence: "Resolved by comparable healthy evidence",
  still_anomalous: "Comparable evidence remains anomalous",
  resolution_unknown: "Comparable evidence does not establish resolution",
};

function readableError(error: unknown) {
  if (error instanceof ApiError) return `${error.message} (${error.code}${error.requestId ? `; request ${error.requestId}` : ""})`;
  return error instanceof Error ? error.message : "The request failed.";
}

function ambiguous(error: unknown) {
  return !(error instanceof ApiError) || ["REQUEST_TIMEOUT", "CONNECTION_FAILED", "INVALID_RESPONSE", "INTERNAL_ERROR", "SESSION_CHANGED"].includes(error.code);
}

function readRecovery(): { pointer: RecoveryPointer | null; error: string } {
  try {
    if (sessionStorage.getItem(LEGACY_ATTEMPT_KEY) !== null) {
      sessionStorage.removeItem(LEGACY_ATTEMPT_KEY);
      sessionStorage.setItem(LEGACY_UNRESOLVED_KEY, "1");
    }
    if (sessionStorage.getItem(LEGACY_UNRESOLVED_KEY)) return { pointer: null, error: "An older unscoped correction retry payload was purged. Its original principal and outcome cannot be verified here. New correction writes are blocked until the operator resolves this ambiguity." };
    const raw = sessionStorage.getItem(RECOVERY_KEY);
    if (raw === null) return { pointer: null, error: "" };
    const value = JSON.parse(raw) as RecoveryPointer;
    if (!value || typeof value.principal_id !== "string" || typeof value.domain !== "string"
      || !Number.isInteger(value.configuration_revision) || typeof value.configuration_digest !== "string"
      || !["proposal", "approve", "reject"].includes(value.kind)
      || (value.kind === "proposal" ? typeof value.idempotency_key !== "string" || !value.idempotency_key : typeof value.request_id !== "string" || !value.request_id)
      || Object.keys(value).some(key => !["principal_id", "domain", "configuration_revision", "configuration_digest", "kind", "idempotency_key", "request_id"].includes(key))) {
      sessionStorage.removeItem(RECOVERY_KEY);
      sessionStorage.setItem(LEGACY_UNRESOLVED_KEY, "1");
      throw new Error("An invalid recovery pointer was purged. Its operation remains unresolved.");
    }
    return { pointer: value, error: "" };
  } catch (error) {
    return { pointer: null, error: `Correction recovery could not be read. New writes are blocked. ${readableError(error)}` };
  }
}

function pointerFor(attempt: Attempt): RecoveryPointer {
  const context = currentContext();
  return { principal_id: context.principal_id, domain: context.selected_domain!,
    configuration_revision: context.configuration_revision, configuration_digest: context.configuration_digest,
    kind: attempt.kind === "proposal" ? "proposal" : attempt.payload.action,
    ...(attempt.kind === "proposal" ? { idempotency_key: attempt.payload.idempotency_key } : { request_id: attempt.id }) };
}

function PageButtons({ page, change, disabled, label }: { page: Page<unknown>; change: (offset: number) => void; disabled: boolean; label: string }) {
  return <nav className="pagination" aria-label={label}><span>{page.total ? page.offset + 1 : 0}–{page.offset + page.items.length} of {page.total}</span><div>
    <button type="button" className="secondary" disabled={disabled || page.offset === 0} onClick={() => change(Math.max(0, page.offset - PAGE_SIZE))}>Previous</button>
    <button type="button" className="secondary" disabled={disabled || page.offset + page.items.length >= page.total} onClick={() => change(page.offset + PAGE_SIZE)}>Next</button>
  </div></nav>;
}

function FindingEvidence({ finding, title }: { finding: Finding; title: string }) {
  const observations = finding.observations ?? [];
  return <section className="detail-section"><h3>{title}</h3>
    <p><strong>{finding.evidence_state.replaceAll("_", " ")}</strong> · {finding.rule_id} · {finding.subject.scope_name} · <code>{finding.subject.cidr}</code></p>
    <p>{finding.explanation}</p>
    <dl className="facts compact"><dt>Saved run</dt><dd><code>{finding.run_id}</code></dd><dt>Finding</dt><dd><code>{finding.id}</code></dd>
      <dt>Evidence window</dt><dd>{finding.evaluated_window.start_at} to {finding.evaluated_window.end_at}</dd></dl>
    <h4>All recorded discrepancies ({observations.length})</h4>
    {!observations.length && <p>No discrepancies are listed in this saved finding. Its evidence state and coverage determine whether absence is meaningful.</p>}
    {observations.length > 0 && <ol className="plain-list">{observations.map((observation, index) => {
      const item = observation && typeof observation === "object" ? observation as Record<string, unknown> : {};
      const value = typeof item.address === "string" ? item.address : typeof item.cidr === "string" ? item.cidr : `Discrepancy ${index + 1}`;
      return <li key={index}><code>{value}</code><details><summary>Recorded observation and source references</summary><pre className="source-json">{JSON.stringify(observation, null, 2)}</pre></details></li>;
    })}</ol>}
    {finding.limitations.length > 0 && <ul className="limitation-list">{finding.limitations.map((text, index) => <li key={index}>{text}</li>)}</ul>}
    <details className="provenance"><summary>Saved coverage and input provenance</summary><pre className="source-json">{JSON.stringify({ coverage: finding.coverage, input_references: finding.input_references }, null, 2)}</pre></details>
  </section>;
}

export default function Corrections({ active = true }: { active?: boolean }) {
  const [restored] = useState(readRecovery);
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [pointer, setPointer] = useState<RecoveryPointer | null>(restored.pointer);
  const [recoveryStatus, setRecoveryStatus] = useState("");
  const [storageError, setStorageError] = useState(restored.error);
  const actorId = currentContext().principal_id;
  const [runs, setRuns] = useState<Page<RunSummary> | null>(null);
  const [runOffset, setRunOffset] = useState(0);
  const [runId, setRunId] = useState("");
  const [run, setRun] = useState<SavedRun | null>(null);
  const [findingId, setFindingId] = useState("");
  const [context, setContext] = useState<CorrectionContext | null>(null);
  const [requests, setRequests] = useState<Page<CorrectionRequest> | null>(null);
  const [requestOffset, setRequestOffset] = useState(0);
  const [selectedId, setSelectedId] = useState("");
  const [selected, setSelected] = useState<CorrectionRequest | null>(null);
  const [cidr, setCidr] = useState("");
  const [owner, setOwner] = useState("");
  const [purpose, setPurpose] = useState("");
  const [reason, setReason] = useState("");
  const [decisionReason, setDecisionReason] = useState("");
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const operation = useRef<AbortController | null>(null);
  useEffect(() => () => operation.current?.abort(), []);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setLoading(true);
    Promise.all([
      request<Page<RunSummary>>(`/api/runs?limit=${PAGE_SIZE}&offset=${runOffset}`, controller.signal),
      request<Page<CorrectionRequest>>(`/api/correction-requests?limit=${PAGE_SIZE}&offset=${requestOffset}`, controller.signal),
    ]).then(([savedRuns, items]) => {
      if (controller.signal.aborted) return;
      setRuns(savedRuns); setRequests(items);
      setRunId(previous => previous || savedRuns.items[0]?.id || "");
    }).catch((failure: unknown) => {
      if (!controller.signal.aborted) setError(`Refresh failed; previously displayed records may be stale. ${readableError(failure)}`);
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [active, revision, runOffset, requestOffset]);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setRun(null);
    if (runId) request<SavedRun>(`/api/runs/${encodeURIComponent(runId)}`, controller.signal).then(value => {
      if (!controller.signal.aborted) setRun(value);
    }).catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Saved run could not be loaded. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, runId, revision]);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setContext(null);
    if (runId && findingId) loadCorrectionContext(runId, findingId, controller.signal).then(value => {
      if (!controller.signal.aborted) setContext(value);
    }).catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Correction review context could not be loaded. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, runId, findingId, revision]);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setSelected(null);
    if (selectedId) loadCorrection(selectedId, controller.signal).then(value => {
      if (!controller.signal.aborted) setSelected(value);
    }).catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Correction request could not be loaded. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [active, selectedId, revision]);

  useEffect(() => {
    if (!active || !pointer || attempt || storageError) return;
    const context = currentContext();
    if (pointer.principal_id !== context.principal_id || pointer.domain !== context.selected_domain) {
      setRecoveryStatus(`Unresolved ${pointer.kind} belongs to principal ${pointer.principal_id} in domain ${pointer.domain}. Authenticate that original context to read it back. No new correction will be submitted.`);
      return;
    }
    const controller = new AbortController();
    setRecoveryStatus("Checking the original correction outcome under this authenticated domain…");
    const readback = pointer.kind === "proposal"
      ? findCorrectionByKey(pointer.idempotency_key!, controller.signal).then(page => page.items.find(item => item.idempotency_key === pointer.idempotency_key) ?? null)
      : loadCorrection(pointer.request_id!, controller.signal);
    readback.then(saved => {
      if (controller.signal.aborted) return;
      const confirmed = !!saved && (pointer.kind === "proposal"
        ? saved.actor_id === pointer.principal_id && saved.idempotency_key === pointer.idempotency_key
        : saved.id === pointer.request_id && saved.decision_actor_id === pointer.principal_id && saved.state === (pointer.kind === "approve" ? "approved" : "rejected"));
      if (!confirmed) {
        setRecoveryStatus("The original operation remains unresolved. No matching principal, key/request ID and outcome was confirmed. Do not submit a replacement operation.");
        return;
      }
      try {
        sessionStorage.removeItem(RECOVERY_KEY);
        if (sessionStorage.getItem(RECOVERY_KEY) !== null) throw new Error("Recovery pointer could not be cleared.");
        setPointer(null); setSelectedId(saved!.id); setSelected(saved!);
        setRecoveryStatus("Original correction outcome confirmed by authorized readback.");
      } catch (failure) { setStorageError(`Readback confirmed the outcome, but recovery storage could not be cleared. ${readableError(failure)}`); }
    }).catch(failure => {
      if (!controller.signal.aborted) setRecoveryStatus(`Original correction remains unresolved. Authorized readback failed: ${readableError(failure)} No replacement will be submitted.`);
    });
    return () => controller.abort();
  }, [active, pointer, attempt, storageError, revision]);

  function retain(value: Attempt) {
    const saved = readRecovery();
    if (saved.error) throw new Error(saved.error);
    const next = pointerFor(value);
    if (saved.pointer && JSON.stringify(saved.pointer) !== JSON.stringify(next)) throw new Error("A different correction operation remains unresolved. Read it back before another write.");
    const serialized = JSON.stringify(next);
    sessionStorage.setItem(RECOVERY_KEY, serialized);
    if (sessionStorage.getItem(RECOVERY_KEY) !== serialized) throw new Error("The minimal recovery pointer could not be saved.");
    setPointer(next);
    setAttempt(value);
  }

  function clearAttempt() {
    try {
      sessionStorage.removeItem(RECOVERY_KEY);
      if (sessionStorage.getItem(RECOVERY_KEY) !== null) throw new Error("The previous recovery pointer remains saved.");
      setPointer(null);
      setAttempt(null);
    } catch (failure) {
      setStorageError(`The response was received, but the recovery pointer could not be cleared. New writes are blocked. ${readableError(failure)}`);
    }
  }

  async function submit(value: Attempt) {
    if (operation.current || storageError || (pointer && !attempt)) return;
    try { retain(value); }
    catch (failure) {
      setStorageError(`No request was sent. A minimal recovery pointer must be saved first. ${readableError(failure)}`); return;
    }
    const controller = new AbortController();
    operation.current = controller; setBusy(true); setError(""); setMessage("");
    try {
      const saved = value.kind === "proposal" ? await createCorrection(value.payload, controller.signal)
        : await decideCorrection(value.id, value.payload, controller.signal);
      if (controller.signal.aborted) return;
      setSelectedId(saved.id); setSelected(saved); setRequestOffset(0); clearAttempt();
      setMessage(`Correction ${saved.id} is ${saved.state}. Local inventory outcome: ${saved.local_outcome}. ${saved.state === "approved" ? "Await the evidence operator's next saved run before claiming resolution." : "A pending or rejected proposal does not change inventory."}`);
      if (value.kind === "proposal") { setCidr(""); setOwner(""); setPurpose(""); setReason(""); }
      else setDecisionReason("");
    } catch (failure) {
      if (!controller.signal.aborted) {
        setError(`${readableError(failure)} ${ambiguous(failure) ? "The response is uncertain. Retry preserves the exact operation." : "The server rejected this operation; review its reason and refresh before submitting again."}`);
        if (!ambiguous(failure)) clearAttempt();
      }
    } finally {
      operation.current = null;
      if (!controller.signal.aborted) { setBusy(false); setRevision(value => value + 1); }
    }
  }

  function propose(event: FormEvent) {
    event.preventDefault();
    if (!context || !hasRole("Requester") || attempt || pointer || storageError) return;
    void submit({ kind: "proposal", payload: { actor_id: actorId, idempotency_key: crypto.randomUUID(),
      scope_id: context.scope.id, source_run_id: context.source_run_id, source_finding_id: context.source_finding.id,
      expected_baseline_version: context.baseline_version, cidr, owner, purpose, reason } });
  }

  function decide(action: CorrectionDecision["action"]) {
    if (!selected || !mayDecide || attempt || pointer || storageError) return;
    void submit({ kind: "decision", id: selected.id, payload: { actor_id: actorId, action, reason: decisionReason } });
  }

  const mayDecide = hasRole("Approver") && selected?.actor_id !== actorId;
  const availableFindings = run?.findings.filter(finding => CORRECTION_RULES.includes(finding.rule_id) && finding.evidence_state === "anomalous") ?? [];
  const related = context && run ? run.findings.filter(finding => CORRECTION_RULES.includes(finding.rule_id)
    && finding.subject.id === context.source_finding.subject.id && finding.id !== context.source_finding.id) : [];
  const locked = busy || !!attempt || !!pointer || !!storageError;

  return <section aria-labelledby="corrections-heading">
    <div className="page-heading"><div><p className="eyebrow">Current workflow · reviewed intended inventory</p><h1 id="corrections-heading">Inventory corrections</h1>
      <p className="intro">Propose missing registered space, obtain an independent decision, then inspect later saved evidence.</p></div>
      <button type="button" className="secondary" disabled={busy || loading} onClick={() => { setError(""); setRevision(value => value + 1); }}>Refresh corrections</button></div>
    <div className="evidence-banner"><strong>Local synthetic workflow</strong><span>Approval registers a prefix in this application's inventory. It does not change DHCP, routers or any external system. Resolution requires a subsequent comparable finding.</span></div>
    <p className="quiet">Evidence is a loaded snapshot. Returning to this view refreshes it; use Refresh corrections to include runs acquired while this view stays open.</p>
    {error && <div className="notice error" role="alert">{error}</div>}
    {message && <div className="notice" role="status">{message}</div>}
    {storageError && <div className="notice error" role="alert"><p>{storageError}</p></div>}
    {recoveryStatus && <div className={pointer ? "notice error" : "notice"} role="status"><p>{recoveryStatus}</p>{pointer && <button type="button" className="secondary" disabled={busy} onClick={() => { setRecoveryStatus(""); setRevision(value => value + 1); }}>Retry authorized readback</button>}</div>}
    {attempt && <div className="notice" role="status"><h2>Exact {attempt.kind} retained in this session</h2><p>A new operation is blocked until this request receives a confirmed response. After reload, only its original-context recovery pointer remains; the protected payload is cleared.</p>
      <button type="button" disabled={busy || !!storageError} onClick={() => void submit(attempt)}>Retry exact {attempt.kind}</button></div>}
    {loading && <p role="status">Refreshing saved records…</p>}
    <p className="filter-help">Authenticated principal: {actorId}. Requester can propose; an independently authenticated Approver may decide.</p>

    <section className="inventory-panel" aria-labelledby="correction-source-heading"><h2 id="correction-source-heading">1. Review saved discrepancy evidence</h2>
      <label className="field-label">Saved run<select value={runId} disabled={locked} onChange={event => { setRunId(event.target.value); setFindingId(""); setContext(null); }}>
        <option value="">Select a saved run</option>
        {runId && !runs?.items.some(item => item.id === runId) && <option value={runId}>{runId} · selected run</option>}
        {runs?.items.map(item => <option key={item.id} value={item.id}>{item.created_at} · scenario {item.demo_clock_at} · {item.id}</option>)}
      </select></label>
      {runs && <PageButtons page={runs} change={setRunOffset} disabled={locked || loading} label="Saved run pages" />}
      {runs?.total === 0 && <p>Awaiting domain evidence. The evidence operator manages global reconciliation.</p>}
      {run && <><p className="quiet">Pinned scenario time {run.demo_clock_at}; saved ledger version {run.ledger_version}.</p>
        <label className="field-label">Anomalous inventory omission<select value={findingId} disabled={locked} onChange={event => { setFindingId(event.target.value); setContext(null); }}>
          <option value="">Select a ghost or unregistered-route finding</option>{availableFindings.map(finding => <option key={finding.id} value={finding.id}>{finding.subject.scope_name} · {finding.subject.cidr} · {finding.rule_id}</option>)}
        </select></label>{!availableFindings.length && <p>This saved run has no anomalous ghost-scope or unregistered-route finding eligible for this workflow.</p>}</>}
      {context && <><FindingEvidence finding={context.source_finding} title="Selected original finding" />
        {related.map(finding => <FindingEvidence key={finding.id} finding={finding} title="Other registration evidence in the same perimeter" />)}
        <p className="run-warning">Review every listed address and route. Correcting one prefix does not resolve another discrepancy elsewhere in this perimeter; later feed episodes may add new ones.</p>
        <p>Managed scope: {context.scope.name} · namespace <code>{context.scope.namespace}</code>. Perimeters: {context.scope.managed_cidrs.join(", ")}.</p>
        {context.limitations.length > 0 && <ul className="limitation-list">{context.limitations.map((text, index) => <li key={index}>{text}</li>)}</ul>}
      </>}
    </section>

    <section className="inventory-panel" aria-labelledby="correction-proposal-heading"><h2 id="correction-proposal-heading">2. Propose a missing prefix</h2>
      <p>The proposal is a new top-level prefix inside the existing managed perimeter. Existing fixture bounds, intended routing policy and pools are unchanged.</p>
      <form onSubmit={propose}><fieldset disabled={locked || !context || !hasRole("Requester")}><legend>Concrete prefix for independent review</legend>
        <div className="filters"><label>Prefix CIDR<input required maxLength={80} value={cidr} onChange={event => setCidr(event.target.value)} placeholder="Enter the missing network and prefix length" /></label>
          <label>Intended owner<input required maxLength={120} value={owner} onChange={event => setOwner(event.target.value)} /></label>
          <label>Purpose<input required maxLength={500} value={purpose} onChange={event => setPurpose(event.target.value)} /></label>
          <label>Proposal reason<input required maxLength={500} value={reason} onChange={event => setReason(event.target.value)} /></label></div>
        <p className="quiet">{context ? `Reviewed current ledger version ${context.baseline_version}. ` : "Select an eligible saved finding first. "}Pending proposals do not change or reserve inventory.</p>
        <button type="submit" disabled={!cidr.trim() || !owner.trim() || !purpose.trim() || !reason.trim()}>Create pending correction</button>
      </fieldset></form>
    </section>

    <section className="inventory-panel" aria-labelledby="correction-review-heading"><h2 id="correction-review-heading">3. Review and decide a saved proposal</h2>
      {requests && <><div className="table-scroll"><table><thead><tr><th>Proposed prefix</th><th>Requester / version</th><th>Decision</th><th>Latest saved evidence</th><th>Review</th></tr></thead><tbody>
        {requests.items.map(item => <tr key={item.id}><td><code>{item.payload.cidr}</code><div>{item.source_finding.subject.scope_name}</div></td><td>{item.actor_id}<div>Ledger {item.baseline_version}</div></td>
          <td>{item.state}<div>Local: {item.local_outcome}</div></td><td>{resolutionLabels[item.latest_resolution_state]}</td><td><button type="button" className="secondary" disabled={locked} onClick={() => { setSelectedId(item.id); setDecisionReason(""); }}>Open correction</button></td></tr>)}
      </tbody></table></div>{!requests.total && <p>No correction requests have been saved.</p>}<PageButtons page={requests} change={setRequestOffset} disabled={locked || loading} label="Correction request pages" /></>}
      {selected && <div className="notice"><h3>Correction <code>{selected.payload.cidr}</code> · {selected.state}</h3>
        <dl className="facts"><dt>Request ID</dt><dd><code>{selected.id}</code></dd><dt>Requested by</dt><dd>{selected.actor_id}</dd><dt>Reviewed ledger</dt><dd>{selected.baseline_version}</dd>
          <dt>Owner / purpose</dt><dd>{selected.payload.owner} · {selected.payload.purpose}</dd><dt>Proposal reason</dt><dd>{selected.payload.reason}</dd><dt>Local inventory outcome</dt><dd>{selected.local_outcome}</dd>
          <dt>New prefix ID</dt><dd>{selected.prefix_id ? <code>{selected.prefix_id}</code> : "No prefix registered"}</dd><dt>Decision actor / reason</dt><dd>{selected.decision_actor_id ?? "No decision"} · {selected.decision_reason ?? "No decision reason"}</dd>
          <dt>First linked result</dt><dd>{resolutionLabels[selected.resolution_state]}</dd></dl>
        {selected.state === "pending" && <><p>Approval rechecks the current ledger, scope, containment and overlap. A different authorized actor must decide.</p>
          <label className="field-label">Decision reason<input value={decisionReason} maxLength={500} disabled={locked} onChange={event => setDecisionReason(event.target.value)} /></label>
          <div className="compute-actions"><button type="button" disabled={locked || !mayDecide || !decisionReason.trim()} onClick={() => decide("approve")}>Approve registration</button>
            <button type="button" className="secondary" disabled={locked || !mayDecide || !decisionReason.trim()} onClick={() => decide("reject")}>Reject proposal</button></div>
          {!mayDecide && <p className="filter-help">An independently authenticated Approver must decide this proposal.</p>}</>}
        <FindingEvidence finding={selected.source_finding} title="Original evidence attached to the proposal" />
        {selected.result_finding ? <FindingEvidence finding={selected.result_finding} title="First result after approval — retained" />
          : <p>No comparable result is linked to this correction yet. Approval alone does not establish finding resolution.</p>}
        <p className="quiet">The first linked result is retained. The latest evidence below is evaluated separately and can change after another reconciliation.</p>
        <section className="detail-section"><h3>Latest saved post-approval evidence</h3>
          <p><strong>{resolutionLabels[selected.latest_resolution_state]}</strong></p>
          {selected.latest_run_id && <p>Latest run <code>{selected.latest_run_id}</code> · <button type="button" className="text-button" onClick={() => { void downloadProtected(`/api/runs/${encodeURIComponent(selected.latest_run_id!)}/export`, "correction-domain-run.json", new AbortController().signal).catch(failure => setError(readableError(failure))); }}>Download permitted saved projection (JSON)</button></p>}
          {selected.latest_finding ? <FindingEvidence finding={selected.latest_finding} title="Finding in the latest saved run" />
            : <p>No comparable finding is available from the latest post-approval evidence. An absent, unknown or not-applicable result does not establish resolution; an older healthy finding is not substituted.</p>}
        </section>
      </div>}
    </section>

    <section className="path-step" aria-labelledby="correction-outcome-heading"><h2 id="correction-outcome-heading">4. Inspect later saved evidence</h2>
      <p>The evidence operator manages global reconciliation. Refresh this domain view after a new saved run is available to inspect comparable findings.</p>
      <p className="quiet">A new prefix has no intended announcement policy. Its missing-route result can remain unknown even after a perimeter discrepancy becomes healthy. No pool or external provisioning is created.</p>
    </section>
  </section>;
}
