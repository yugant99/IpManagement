import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, request } from "./api";
import type { Page } from "./api";
import { computeRun } from "./firstPathApi";
import type { Finding, RunSummary, SavedRun } from "./firstPathApi";
import type { DemoActor } from "./workflowApi";
import { createCorrection, decideCorrection, loadCorrection, loadCorrectionContext } from "./correctionApi";
import type { CorrectionContext, CorrectionDecision, CorrectionRequest, CreateCorrection, ResolutionState } from "./correctionApi";

const PAGE_SIZE = 20;
const ATTEMPT_KEY = "ipam.correction.attempt.v1";
const CORRECTION_RULES = ["ghost_scope", "unregistered_managed_route"];
type Attempt = { kind: "proposal"; payload: CreateCorrection } | { kind: "decision"; id: string; payload: CorrectionDecision };
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
  return !(error instanceof ApiError) || ["REQUEST_TIMEOUT", "CONNECTION_FAILED", "INVALID_RESPONSE", "INTERNAL_ERROR"].includes(error.code);
}

function readAttempt(): { attempt: Attempt | null; error: string } {
  try {
    const raw = sessionStorage.getItem(ATTEMPT_KEY);
    if (raw === null) return { attempt: null, error: "" };
    const value = JSON.parse(raw) as Attempt;
    if (!value || typeof value !== "object" || !value.payload || typeof value.payload !== "object") throw new Error("Unreadable saved operation.");
    const payload = value.payload as unknown as Record<string, unknown>;
    const fields = value.kind === "proposal"
      ? ["actor_id", "idempotency_key", "scope_id", "source_run_id", "source_finding_id", "cidr", "owner", "purpose", "reason"]
      : ["actor_id", "action", "reason"];
    if (fields.some(field => typeof payload[field] !== "string" || !(payload[field] as string).trim())
      || (value.kind === "proposal" && (!Number.isInteger(value.payload.expected_baseline_version) || value.payload.expected_baseline_version < 1))
      || (value.kind === "decision" && (typeof value.id !== "string" || !value.id || !["approve", "reject"].includes(value.payload.action)))
      || !["proposal", "decision"].includes(value.kind)) throw new Error("The saved operation has an invalid shape.");
    return { attempt: value, error: "" };
  } catch (error) {
    return { attempt: null, error: `The saved correction retry could not be read. It has been preserved; new writes are blocked. ${readableError(error)}` };
  }
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

export default function Corrections() {
  const [restored] = useState(readAttempt);
  const [attempt, setAttempt] = useState<Attempt | null>(restored.attempt);
  const [storageError, setStorageError] = useState(restored.error);
  const [actors, setActors] = useState<DemoActor[]>([]);
  const [actorId, setActorId] = useState(restored.attempt?.payload.actor_id ?? "demo-requester");
  const [runs, setRuns] = useState<Page<RunSummary> | null>(null);
  const [runOffset, setRunOffset] = useState(0);
  const [runId, setRunId] = useState(restored.attempt?.kind === "proposal" ? restored.attempt.payload.source_run_id : "");
  const [run, setRun] = useState<SavedRun | null>(null);
  const [findingId, setFindingId] = useState(restored.attempt?.kind === "proposal" ? restored.attempt.payload.source_finding_id : "");
  const [context, setContext] = useState<CorrectionContext | null>(null);
  const [requests, setRequests] = useState<Page<CorrectionRequest> | null>(null);
  const [requestOffset, setRequestOffset] = useState(0);
  const [selectedId, setSelectedId] = useState(restored.attempt?.kind === "decision" ? restored.attempt.id : "");
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
  const [lastRun, setLastRun] = useState<SavedRun | null>(null);
  const operation = useRef<AbortController | null>(null);
  useEffect(() => () => operation.current?.abort(), []);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    Promise.all([
      request<DemoActor[]>("/api/actors", controller.signal),
      request<Page<RunSummary>>(`/api/runs?limit=${PAGE_SIZE}&offset=${runOffset}`, controller.signal),
      request<Page<CorrectionRequest>>(`/api/correction-requests?limit=${PAGE_SIZE}&offset=${requestOffset}`, controller.signal),
    ]).then(([people, savedRuns, items]) => {
      if (controller.signal.aborted) return;
      setActors(people); setRuns(savedRuns); setRequests(items);
      setRunId(previous => previous || savedRuns.items[0]?.id || "");
    }).catch((failure: unknown) => {
      if (!controller.signal.aborted) setError(`Refresh failed; previously displayed records may be stale. ${readableError(failure)}`);
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [revision, runOffset, requestOffset]);

  useEffect(() => {
    const controller = new AbortController();
    setRun(null);
    if (runId) request<SavedRun>(`/api/runs/${encodeURIComponent(runId)}`, controller.signal).then(value => {
      if (!controller.signal.aborted) setRun(value);
    }).catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Saved run could not be loaded. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [runId, revision]);

  useEffect(() => {
    const controller = new AbortController();
    setContext(null);
    if (runId && findingId) loadCorrectionContext(runId, findingId, controller.signal).then(value => {
      if (!controller.signal.aborted) setContext(value);
    }).catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Correction review context could not be loaded. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [runId, findingId, revision]);

  useEffect(() => {
    const controller = new AbortController();
    setSelected(null);
    if (selectedId) loadCorrection(selectedId, controller.signal).then(value => {
      if (!controller.signal.aborted) setSelected(value);
    }).catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Correction request could not be loaded. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [selectedId, revision]);

  function retain(value: Attempt) {
    const saved = readAttempt();
    if (saved.error) throw new Error(saved.error);
    if (saved.attempt && JSON.stringify(saved.attempt) !== JSON.stringify(value)) throw new Error("A different operation is already saved in this tab. Reload its retry request first.");
    const serialized = JSON.stringify(value);
    sessionStorage.setItem(ATTEMPT_KEY, serialized);
    if (sessionStorage.getItem(ATTEMPT_KEY) !== serialized) throw new Error("The exact retry request could not be saved.");
    setAttempt(value);
  }

  function clearAttempt() {
    try {
      sessionStorage.removeItem(ATTEMPT_KEY);
      if (sessionStorage.getItem(ATTEMPT_KEY) !== null) throw new Error("The previous retry remains saved.");
      setAttempt(null);
    } catch (failure) {
      setStorageError(`The response was received, but the saved retry could not be cleared. New writes are blocked. ${readableError(failure)}`);
    }
  }

  function reloadRetry() {
    const saved = readAttempt();
    setStorageError(saved.error);
    if (saved.attempt) { setAttempt(saved.attempt); setActorId(saved.attempt.payload.actor_id); }
  }

  async function submit(value: Attempt) {
    if (operation.current || storageError) return;
    try { retain(value); }
    catch (failure) {
      setAttempt(value); setStorageError(`No request was sent. A durable retry must be saved first. ${readableError(failure)}`); return;
    }
    const controller = new AbortController();
    operation.current = controller; setBusy(true); setError(""); setMessage("");
    try {
      const saved = value.kind === "proposal" ? await createCorrection(value.payload, controller.signal)
        : await decideCorrection(value.id, value.payload, controller.signal);
      if (controller.signal.aborted) return;
      setSelectedId(saved.id); setSelected(saved); setRequestOffset(0); clearAttempt();
      setMessage(`Correction ${saved.id} is ${saved.state}. Local inventory outcome: ${saved.local_outcome}. ${saved.state === "approved" ? "Reconcile and inspect evidence before claiming resolution." : "A pending or rejected proposal does not change inventory."}`);
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
    if (!context || !actor?.permissions.includes("request") || attempt) return;
    void submit({ kind: "proposal", payload: { actor_id: actorId, idempotency_key: crypto.randomUUID(),
      scope_id: context.scope.id, source_run_id: context.source_run_id, source_finding_id: context.source_finding.id,
      expected_baseline_version: context.baseline_version, cidr, owner, purpose, reason } });
  }

  function decide(action: CorrectionDecision["action"]) {
    if (!selected || !mayDecide || attempt) return;
    void submit({ kind: "decision", id: selected.id, payload: { actor_id: actorId, action, reason: decisionReason } });
  }

  async function reconcile() {
    if (operation.current || attempt || storageError) return;
    const controller = new AbortController();
    operation.current = controller; setBusy(true); setError(""); setMessage("");
    try {
      const computed = await computeRun(controller.signal);
      if (controller.signal.aborted) return;
      setLastRun(computed); setRunOffset(0);
      setMessage(`Reconciliation saved run ${computed.id} at scenario time ${computed.demo_clock_at}. Review the linked correction result and every remaining discrepancy.`);
    } catch (failure) {
      if (!controller.signal.aborted) setError(`Reconciliation response was not confirmed. ${readableError(failure)} Refresh saved requests and runs before starting another reconciliation; a timed-out response may still have committed a run.`);
    } finally {
      operation.current = null;
      if (!controller.signal.aborted) { setBusy(false); setRevision(value => value + 1); }
    }
  }

  const actor = actors.find(item => item.id === actorId);
  const mayDecide = !!actor?.permissions.includes("approve") && selected?.actor_id !== actorId;
  const availableFindings = run?.findings.filter(finding => CORRECTION_RULES.includes(finding.rule_id) && finding.evidence_state === "anomalous") ?? [];
  const related = context && run ? run.findings.filter(finding => CORRECTION_RULES.includes(finding.rule_id)
    && finding.subject.id === context.source_finding.subject.id && finding.id !== context.source_finding.id) : [];
  const recentFinding = selected && lastRun ? lastRun.findings.find(finding => finding.rule_id === selected.source_finding.rule_id
    && finding.subject.id === selected.source_finding.subject.id && finding.subject.scope_id === selected.scope_id) : null;
  const locked = busy || !!attempt || !!storageError;

  return <section aria-labelledby="corrections-heading">
    <div className="page-heading"><div><p className="eyebrow">Reviewed intended inventory</p><h1 id="corrections-heading">Inventory corrections</h1>
      <p className="intro">Propose missing registered space, obtain an independent decision, then reconcile and inspect the evidence.</p></div>
      <button type="button" className="secondary" disabled={busy || loading} onClick={() => { setError(""); setRevision(value => value + 1); }}>Refresh corrections</button></div>
    <div className="evidence-banner"><strong>Local synthetic workflow</strong><span>Approval registers a prefix in this application's inventory. It does not change DHCP, routers or any external system. Resolution requires a subsequent comparable finding.</span></div>
    {error && <div className="notice error" role="alert">{error}</div>}
    {message && <div className="notice" role="status">{message}</div>}
    {storageError && <div className="notice error" role="alert"><p>{storageError}</p><button type="button" className="secondary" disabled={busy} onClick={reloadRetry}>Reload saved retry</button></div>}
    {attempt && <div className="notice" role="status"><h2>Exact {attempt.kind} retained</h2><p>A new operation is blocked until this request receives a confirmed response. Its actor, values and retry identity survive reloads in this tab.</p>
      <details><summary>Retained request</summary><pre className="source-json">{JSON.stringify(attempt, null, 2)}</pre></details>
      <button type="button" disabled={busy || !!storageError} onClick={() => void submit(attempt)}>Retry exact {attempt.kind}</button></div>}
    {loading && <p role="status">Refreshing saved records…</p>}
    <div className="filters"><label>Named demo actor<select value={actorId} disabled={locked} onChange={event => setActorId(event.target.value)}>
      {actors.map(person => <option key={person.id} value={person.id}>{person.name} · {person.role} · {person.team}</option>)}
    </select></label><p className="filter-help">The API enforces actor permissions and independent approval. This local identity switch is not a sign-in system.</p></div>

    <section className="inventory-panel" aria-labelledby="correction-source-heading"><h2 id="correction-source-heading">1. Review saved discrepancy evidence</h2>
      <label className="field-label">Saved run<select value={runId} disabled={locked} onChange={event => { setRunId(event.target.value); setFindingId(""); setContext(null); }}>
        <option value="">Select a saved run</option>
        {runId && !runs?.items.some(item => item.id === runId) && <option value={runId}>{runId} · selected run</option>}
        {runs?.items.map(item => <option key={item.id} value={item.id}>{item.created_at} · scenario {item.demo_clock_at} · {item.id}</option>)}
      </select></label>
      {runs && <PageButtons page={runs} change={setRunOffset} disabled={locked || loading} label="Saved run pages" />}
      {runs?.total === 0 && <p>No saved run exists yet. Import synthetic evidence and compute a reconciliation in Source evidence.</p>}
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
      <form onSubmit={propose}><fieldset disabled={locked || !context || !actor?.permissions.includes("request")}><legend>Concrete prefix for independent review</legend>
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
          {!mayDecide && <p className="filter-help">Select a different actor with approval permission.</p>}</>}
        <FindingEvidence finding={selected.source_finding} title="Original evidence attached to the proposal" />
        {selected.result_finding ? <FindingEvidence finding={selected.result_finding} title="First comparable result after approval — retained" />
          : <p>No comparable result is linked to this correction yet. Approval alone does not establish finding resolution.</p>}
        <p className="quiet">The first linked result is retained. The latest evidence below is evaluated separately and can change after another reconciliation.</p>
        <section className="detail-section"><h3>Latest saved post-approval evidence</h3>
          <p><strong>{resolutionLabels[selected.latest_resolution_state]}</strong></p>
          {selected.latest_run_id && <p>Latest run <code>{selected.latest_run_id}</code> · <a href={`/api/runs/${encodeURIComponent(selected.latest_run_id)}/export`}>Inspect complete saved run (JSON)</a></p>}
          {selected.latest_finding ? <FindingEvidence finding={selected.latest_finding} title="Finding in the latest saved run" />
            : <p>No comparable finding is available from the latest post-approval evidence. An absent, unknown or not-applicable result does not establish resolution; an older healthy finding is not substituted.</p>}
        </section>
      </div>}
    </section>

    <section className="path-step" aria-labelledby="correction-outcome-heading"><h2 id="correction-outcome-heading">4. Reconcile actual inventory and inspect the outcome</h2>
      <p>Reconciliation reads the stored inventory and source evidence. It saves a new run and links pending approved corrections to their first subsequent comparable finding. It does not advance the synthetic clock.</p>
      <button type="button" disabled={locked || selected?.state !== "approved"} onClick={() => void reconcile()}>Reconcile stored inventory</button>
      <p className="quiet">A new prefix has no intended announcement policy. Its missing-route result can remain unknown even after a perimeter discrepancy becomes healthy. No pool or external provisioning is created.</p>
      {lastRun && <div className="notice"><h3>Most recent reconciliation computed in this tab</h3><p>Run <code>{lastRun.id}</code> · scenario {lastRun.demo_clock_at} · ledger {lastRun.ledger_version}.</p>
        {recentFinding ? <FindingEvidence finding={recentFinding} title="Comparable finding in this computed run" /> : <p>No comparable finding for the selected correction is shown in this run. This does not establish resolution.</p>}
        <p><a href={`/api/runs/${encodeURIComponent(lastRun.id)}/export`}>Inspect this complete saved run (JSON)</a></p></div>}
    </section>
  </section>;
}
