import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, currentContext, downloadProtected, hasRole, request } from "./api";
import type { Page } from "./api";
import { createMigrationAssessment, loadMigrationAssessment, loadMigrationAssessments, readMigrationOperation, signoffMigrationAssessment } from "./firstPathApi";
import type { MigrationAssessmentDetail, MigrationAssessmentPage, MigrationAssessmentSummary, MigrationMutationResponse, MigrationSignoffReceipt, Receipt } from "./firstPathApi";

const PAGE_SIZE = 50;
const RECOVERY_KEY = "ipam.migration-assessment.recovery.v1";
type Action = "assessment.create" | "assessment.signoff";
type Attempt = { action: Action; key: string; target_id?: string; payload: Record<string, unknown> };
type RecoveryPointer = {
  principal_id: string;
  domain: string;
  configuration_revision: number;
  configuration_digest: string;
  action: Action;
  idempotency_key: string;
  target_id?: string;
};
type LoadState<T> = { status: "loading" } | { status: "ready"; data: T } | { status: "error"; error: ApiError };
type OperationOutcome = { assessment_id: string; action: Action; replayed: boolean; original_signoff: MigrationSignoffReceipt | null };

function asError(error: unknown) {
  return error instanceof ApiError ? error : new ApiError("The protected response could not be read. Retry under the same access context.", "INVALID_RESPONSE");
}

function readableError(error: unknown) {
  const value = asError(error);
  return `${value.message} (${value.code}${value.requestId ? `; request ${value.requestId}` : ""})`;
}

function ambiguous(error: unknown) {
  const code = asError(error).code;
  return ["REQUEST_TIMEOUT", "CONNECTION_FAILED", "INVALID_RESPONSE", "INTERNAL_ERROR", "SESSION_CHANGED"].includes(code);
}

function readRecovery(): { pointer: RecoveryPointer | null; error: string } {
  try {
    const raw = sessionStorage.getItem(RECOVERY_KEY);
    if (raw === null) return { pointer: null, error: "" };
    const value = JSON.parse(raw) as RecoveryPointer;
    if (!value || typeof value.principal_id !== "string" || typeof value.domain !== "string"
      || !Number.isInteger(value.configuration_revision) || value.configuration_revision < 1
      || typeof value.configuration_digest !== "string"
      || !["assessment.create", "assessment.signoff"].includes(value.action)
      || typeof value.idempotency_key !== "string" || !value.idempotency_key || value.idempotency_key.length > 200
      || (value.action === "assessment.signoff" && (typeof value.target_id !== "string" || !value.target_id))
      || (value.target_id !== undefined && (typeof value.target_id !== "string" || !value.target_id))
      || Object.keys(value).some(key => !["principal_id", "domain", "configuration_revision", "configuration_digest", "action", "idempotency_key", "target_id"].includes(key))) {
      throw new Error("The saved recovery pointer is invalid; its outcome cannot be confirmed.");
    }
    return { pointer: value, error: "" };
  } catch (error) {
    return { pointer: null, error: `Migration recovery storage could not be read safely. New assessment writes are blocked. ${error instanceof Error ? error.message : "Storage access failed."}` };
  }
}

function samePointer(left: RecoveryPointer, right: RecoveryPointer) {
  return left.principal_id === right.principal_id && left.domain === right.domain
    && left.configuration_revision === right.configuration_revision && left.configuration_digest === right.configuration_digest
    && left.action === right.action && left.idempotency_key === right.idempotency_key && left.target_id === right.target_id;
}

function pointerFor(value: Attempt): RecoveryPointer {
  const context = currentContext();
  return { principal_id: context.principal_id, domain: context.selected_domain!,
    configuration_revision: context.configuration_revision, configuration_digest: context.configuration_digest,
    action: value.action, idempotency_key: value.key, ...(value.target_id ? { target_id: value.target_id } : {}) };
}

function eligibleReceipt(receipt: Receipt) {
  return receipt.source_kind === "inventory_staged" && receipt.application_status === "staged"
    && receipt.input_rows > 0 && receipt.accepted_rows === receipt.input_rows
    && receipt.rejected_rows === 0 && receipt.duplicate_rows === 0;
}

function pageUrl(offset: number) {
  return `/api/imports?limit=${PAGE_SIZE}&offset=${offset}`;
}

function Counts({ assessment }: { assessment: MigrationAssessmentSummary }) {
  const receiptsReconcile = assessment.input_count === assessment.accepted_count + assessment.rejected_count + assessment.duplicate_count;
  const comparisonReconciles = assessment.accepted_count === assessment.added_count + assessment.changed_count + assessment.unchanged_count + assessment.conflicting_count;
  return <>
    <section className="detail-section" aria-labelledby="receipt-count-heading">
      <h3 id="receipt-count-heading">Import receipt counts</h3>
      <dl className="facts compact"><dt>Input rows</dt><dd>{assessment.input_count}</dd><dt>Accepted</dt><dd>{assessment.accepted_count}</dd><dt>Rejected</dt><dd>{assessment.rejected_count}</dd><dt>Duplicate</dt><dd>{assessment.duplicate_count}</dd></dl>
      <p className={receiptsReconcile ? "quiet" : "notice error"}>{receiptsReconcile ? "Receipt counts reconcile: input = accepted + rejected + duplicate." : "Receipt accounting does not reconcile. This assessment cannot be signed."}</p>
    </section>
    <section className="detail-section" aria-labelledby="comparison-count-heading">
      <h3 id="comparison-count-heading">Accepted-row comparison counts</h3>
      <dl className="facts compact"><dt>Added</dt><dd>{assessment.added_count}</dd><dt>Changed</dt><dd>{assessment.changed_count}</dd><dt>Unchanged</dt><dd>{assessment.unchanged_count}</dd><dt>Conflicting</dt><dd>{assessment.conflicting_count}</dd></dl>
      <p className={comparisonReconciles ? "quiet" : "notice error"}>{comparisonReconciles ? "Comparison counts reconcile to accepted rows." : "Comparison accounting does not reconcile. This assessment cannot be signed."}</p>
      {assessment.conflicting_count > 0 && <p className="notice error" role="status">{assessment.conflicting_count} conflict(s) need review. Conflicts are not ordinary changes and block sign-off.</p>}
    </section>
  </>;
}

function AssessmentDetailView({ assessment, onExport }: { assessment: MigrationAssessmentDetail; onExport: () => void }) {
  return <section className="detail-panel" aria-labelledby="migration-detail-heading">
    <div className="section-heading"><div><p className="eyebrow">Immutable assessment detail</p><h2 id="migration-detail-heading">Assessment {assessment.id}</h2></div><button type="button" className="secondary" onClick={onExport}>Download this assessment JSON</button></div>
    <div className={assessment.current ? "notice" : "notice error"} role="status">
      <h3>{assessment.current ? "Current against its saved lineage" : "Stale assessment"}</h3>
      <p>{assessment.current ? "The server currently reports no staleness reasons. Sign-off still checks the exact version and digest." : "A saved sign-off remains historical; current staleness is evaluated separately."}</p>
      {!!assessment.staleness_reasons.length && <ul>{assessment.staleness_reasons.map((reason, index) => <li key={`${reason}-${index}`}>{reason}</li>)}</ul>}
      <p>Saved state: <strong>{assessment.state}</strong> · version {assessment.version}</p>
    </div>
    <section className="detail-section"><h3>Source and immutable lineage</h3>
      <dl className="facts compact"><dt>Selected domain</dt><dd>{assessment.domain}</dd><dt>Source batch</dt><dd><code>{assessment.source_batch_id}</code></dd>
        <dt>Source</dt><dd>{assessment.source ? <>{assessment.source.source_id} · run <code>{assessment.source.source_run_id}</code></> : "Source reference unavailable"}</dd>
        <dt>Canonical source hash</dt><dd><code>{assessment.canonical_hash}</code></dd><dt>Assessment digest</dt><dd><code>{assessment.digest}</code></dd>
        <dt>Baseline version</dt><dd>{assessment.baseline_version}</dd><dt>Mapping revision</dt><dd><code>{assessment.mapping_revision}</code></dd>
        <dt>Authority revision</dt><dd><code>{assessment.authority_revision}</code></dd><dt>Policy revision</dt><dd><code>{assessment.policy_revision}</code></dd>
        <dt>Created</dt><dd><time>{assessment.created_at}</time></dd><dt>Creator</dt><dd>{assessment.created_by_current_principal ? "Current authenticated principal" : assessment.created_by ? "Another principal (identity hidden)" : "Creator identity is not visible to this principal"}</dd>
        <dt>Supersedes</dt><dd>{assessment.supersedes_id ? <><code>{assessment.supersedes_id}</code> · {assessment.supersedes_reason}</> : "None"}</dd>
      </dl>
    </section>
    <section className="detail-section"><h3>Saved sign-off</h3>
      {assessment.signed_at ? <><p>Historical sign-off recorded at <time>{assessment.signed_at}</time>. Current assessment state: <strong>{assessment.current ? "current" : "stale"}</strong>.</p>
        <dl className="facts compact"><dt>Signer</dt><dd>{assessment.signed_by_current_principal ? "Current authenticated principal" : assessment.signer_id ? "Another principal (identity hidden)" : "Signer identity is not visible to this principal"}</dd><dt>Sign-off reason</dt><dd>{assessment.signoff_reason ?? "No sign-off reason returned"}</dd><dt>Active-only acknowledged</dt><dd>{assessment.active_only_acknowledged ? "Yes" : "No"}</dd></dl></>
        : <p>No saved sign-off is recorded.</p>}
    </section>
    <Counts assessment={assessment} />
    <section className="detail-section" aria-labelledby="active-only-heading">
      <h3 id="active-only-heading">Active-only objects ({assessment.active_only_count} recorded; {assessment.active_only.length} shown)</h3>
      {assessment.active_only.length !== assessment.active_only_count && <p className="notice error" role="alert">The active-only detail rows do not match the saved count. Do not sign this assessment.</p>}
      {!assessment.active_only.length && <p>No active-only objects were returned.</p>}
      {!!assessment.active_only.length && <ul className="plain-list">{assessment.active_only.map((row, index) => <li key={`${row.matching_key}-${index}`}><strong><code>{row.matching_key}</code></strong><p>{row.reason}</p><details><summary>Active value and provenance</summary><pre className="source-json">{JSON.stringify(row.active, null, 2)}</pre></details></li>)}</ul>}
    </section>
    <section className="detail-section" aria-labelledby="comparison-rows-heading">
      <h3 id="comparison-rows-heading">Comparison rows ({assessment.rows.length} shown; {assessment.accepted_count} accepted)</h3>
      {assessment.rows.length !== assessment.accepted_count && <p className="notice error" role="alert">The comparison detail rows do not match the accepted-row count. Do not sign this assessment.</p>}
      {!assessment.rows.length && <p>No comparison rows were returned.</p>}
      {assessment.rows.map((row, index) => <details className="record-disclosure" key={`${row.source_record_id}-${index}`}>
        <summary><span className={`import-status ${row.disposition}`}>{row.disposition}</span> · <code>{row.matching_key}</code></summary>
        <p>{row.reason}</p><dl className="facts compact"><dt>Source record</dt><dd><code>{row.source_record_id}</code></dd></dl>
        <h4>Candidate value</h4><pre className="source-json">{JSON.stringify(row.candidate, null, 2)}</pre>
        <h4>Active value</h4>{row.active === null ? <p>No matching active object.</p> : <pre className="source-json">{JSON.stringify(row.active, null, 2)}</pre>}
      </details>)}
    </section>
  </section>;
}

export default function MigrationCompare({ active = true, initialSourceBatchId = "" }: { active?: boolean; initialSourceBatchId?: string }) {
  const [restored] = useState(readRecovery);
  const context = currentContext();
  const mayCreate = hasRole("Operator");
  const maySign = hasRole("Approver");
  const [assessments, setAssessments] = useState<LoadState<MigrationAssessmentPage>>({ status: "loading" });
  const [receipts, setReceipts] = useState<LoadState<Page<Receipt>>>({ status: "loading" });
  const [pinnedReceipt, setPinnedReceipt] = useState<Receipt | null>(null);
  const [detail, setDetail] = useState<LoadState<MigrationAssessmentDetail> | null>(null);
  const [selectedId, setSelectedId] = useState("");
  const [sourceBatchId, setSourceBatchId] = useState("");
  const [supersedesId, setSupersedesId] = useState("");
  const [supersedesReason, setSupersedesReason] = useState("");
  const [createReason, setCreateReason] = useState("");
  const [signoffReason, setSignoffReason] = useState("");
  const [activeOnlyAcknowledged, setActiveOnlyAcknowledged] = useState(false);
  const [receiptOffset, setReceiptOffset] = useState(0);
  const [assessmentOffset, setAssessmentOffset] = useState(0);
  const [revision, setRevision] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [outcome, setOutcome] = useState<OperationOutcome | null>(null);
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [pointer, setPointer] = useState<RecoveryPointer | null>(restored.pointer);
  const [storageError, setStorageError] = useState(restored.error);
  const [recoveryStatus, setRecoveryStatus] = useState("");
  const [readbackRevision, setReadbackRevision] = useState(0);
  const operation = useRef<AbortController | null>(null);
  const download = useRef<AbortController | null>(null);
  const priorAmbiguity = useRef(false);

  useEffect(() => () => { operation.current?.abort(); download.current?.abort(); }, []);
  useEffect(() => { if (!active) download.current?.abort(); }, [active]);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setAssessments({ status: "loading" });
    loadMigrationAssessments(assessmentOffset, controller.signal).then(data => {
      if (!controller.signal.aborted) setAssessments({ status: "ready", data });
    }).catch(failure => { if (!controller.signal.aborted) setAssessments({ status: "error", error: asError(failure) }); });
    return () => controller.abort();
  }, [active, assessmentOffset, revision]);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setReceipts({ status: "loading" });
    request<Page<Receipt>>(pageUrl(receiptOffset), controller.signal).then(data => {
      if (!controller.signal.aborted) setReceipts({ status: "ready", data });
    }).catch(failure => { if (!controller.signal.aborted) setReceipts({ status: "error", error: asError(failure) }); });
    return () => controller.abort();
  }, [active, receiptOffset, revision]);

  useEffect(() => {
    if (!active || !initialSourceBatchId) return;
    setSourceBatchId(initialSourceBatchId);
    const controller = new AbortController();
    request<Receipt>(`/api/imports/${encodeURIComponent(initialSourceBatchId)}`, controller.signal).then(receipt => {
      if (!controller.signal.aborted && eligibleReceipt(receipt)) setPinnedReceipt(receipt);
      else if (!controller.signal.aborted) setError("The selected receipt is not a successful, wholly accepted staged inventory candidate.");
    }).catch(failure => { if (!controller.signal.aborted) setError(`The selected staged receipt could not be reloaded in this domain. ${asError(failure).message}`); });
    return () => controller.abort();
  }, [active, initialSourceBatchId]);

  useEffect(() => {
    if (!active || !selectedId) { setDetail(null); return; }
    const controller = new AbortController();
    setDetail({ status: "loading" });
    loadMigrationAssessment(selectedId, controller.signal).then(data => {
      if (!controller.signal.aborted) setDetail({ status: "ready", data });
    }).catch(failure => { if (!controller.signal.aborted) setDetail({ status: "error", error: asError(failure) }); });
    return () => controller.abort();
  }, [active, selectedId, revision]);

  useEffect(() => {
    if (!active || !pointer || attempt || storageError) return;
    if (pointer.principal_id !== context.principal_id || pointer.domain !== context.selected_domain) {
      setRecoveryStatus(`An unresolved ${pointer.action} operation belongs to ${pointer.principal_id} in domain ${pointer.domain}. Sign in as that original principal and select that domain to read it back. It cannot be resent as this identity.`);
      return;
    }
    const controller = new AbortController();
    setRecoveryStatus("Reading the saved operation receipt as the original authenticated principal…");
    readMigrationOperation(pointer.action, pointer.idempotency_key, controller.signal).then(async result => {
      if (controller.signal.aborted) return;
      if (!result.found || !result.assessment || !result.original_outcome) {
        setRecoveryStatus("No matching operation receipt was found. The earlier request may still commit; it remains unresolved and replacement writes are blocked.");
        return;
      }
      const outcomeId = result.original_outcome.assessment_id;
      const confirmed = result.action === pointer.action && result.assessment.id === outcomeId
        && result.original_outcome.assessment_digest === result.assessment.digest
        && (!pointer.target_id || pointer.target_id === outcomeId)
        && (pointer.action === "assessment.create"
          ? result.assessment.created_by_current_principal === true
          : result.original_outcome.signer_id === pointer.principal_id && result.assessment.signed_by_current_principal === true);
      if (!confirmed) {
        setRecoveryStatus("Authorized readback returned an outcome that does not match the saved principal, operation key and target. It remains unresolved; no replacement will be sent.");
        return;
      }
      try {
        sessionStorage.removeItem(RECOVERY_KEY);
        if (sessionStorage.getItem(RECOVERY_KEY) !== null) throw new Error("The recovery pointer could not be cleared.");
        priorAmbiguity.current = false;
        setPointer(null);
        setAttempt(null);
        setSelectedId(result.assessment.id);
        setDetail({ status: "ready", data: result.assessment });
        const originalSignoff = result.action === "assessment.signoff" ? result.original_outcome as MigrationSignoffReceipt : null;
        setOutcome({ assessment_id: result.assessment.id, action: result.action, replayed: true, original_signoff: originalSignoff });
        setRecoveryStatus("The original operation outcome was confirmed by authorized readback. Current staleness remains shown separately.");
        setRevision(value => value + 1);
      } catch (failure) {
        setStorageError(`Readback confirmed an outcome, but its recovery pointer could not be cleared. New writes remain blocked. ${failure instanceof Error ? failure.message : "Storage access failed."}`);
      }
    }).catch(failure => {
      if (!controller.signal.aborted) setRecoveryStatus(`Authorized readback failed. The earlier operation remains unresolved and replacement writes are blocked. ${readableError(failure)}`);
    });
    return () => controller.abort();
  }, [active, pointer, attempt, storageError, context.principal_id, context.selected_domain, readbackRevision]);

  function retain(value: Attempt) {
    const saved = readRecovery();
    if (saved.error) throw new Error(saved.error);
    const next = pointerFor(value);
    if (saved.pointer && !samePointer(saved.pointer, next)) throw new Error("A different migration operation remains unresolved. Read it back before starting another.");
    const serialized = JSON.stringify(next);
    sessionStorage.setItem(RECOVERY_KEY, serialized);
    if (sessionStorage.getItem(RECOVERY_KEY) !== serialized) throw new Error("The minimal migration recovery pointer could not be saved.");
    setPointer(next);
    setAttempt(value);
  }

  function clearAttempt() {
    try {
      sessionStorage.removeItem(RECOVERY_KEY);
      if (sessionStorage.getItem(RECOVERY_KEY) !== null) throw new Error("The previous migration recovery pointer remains saved.");
      priorAmbiguity.current = false;
      setPointer(null);
      setAttempt(null);
    } catch (failure) {
      setStorageError(`The operation response was received, but recovery storage could not be cleared. New writes are blocked. ${failure instanceof Error ? failure.message : "Storage access failed."}`);
    }
  }

  async function submit(value: Attempt) {
    if (operation.current || storageError || (pointer && !attempt)) return;
    try { retain(value); }
    catch (failure) { setStorageError(`No request was sent. Save a minimal recovery pointer first. ${failure instanceof Error ? failure.message : "Storage access failed."}`); return; }
    const controller = new AbortController();
    operation.current = controller;
    setBusy(true); setError(""); setMessage(""); setRecoveryStatus("");
    try {
      const response: MigrationMutationResponse = value.action === "assessment.create"
        ? await createMigrationAssessment(value.payload as Parameters<typeof createMigrationAssessment>[0], controller.signal)
        : await signoffMigrationAssessment(value.target_id!, value.payload as Parameters<typeof signoffMigrationAssessment>[1], controller.signal);
      if (controller.signal.aborted) return;
      if (!response?.assessment?.id || typeof response.replayed !== "boolean"
        || (value.action === "assessment.create" && (response.assessment.source_batch_id !== value.payload.source_batch_id
          || response.assessment.created_by_current_principal !== true || response.original_signoff !== null))
        || (value.action === "assessment.signoff" && (!response.original_signoff
          || response.original_signoff.assessment_id !== value.target_id
          || response.original_signoff.assessment_digest !== value.payload.expected_digest
          || response.original_signoff.signer_id !== context.principal_id
          || response.original_signoff.signed_version !== response.assessment.version
          || typeof response.original_signoff.signed_at !== "string"
          || !response.assessment.signed_by_current_principal))) {
        throw new ApiError("The operation response did not match the normalized assessment and original outcome.", "INVALID_RESPONSE");
      }
      setOutcome({ assessment_id: response.assessment.id, action: value.action, replayed: response.replayed, original_signoff: response.original_signoff ?? null });
      setSelectedId(response.assessment.id);
      setDetail({ status: "loading" });
      clearAttempt();
      setMessage(value.action === "assessment.create"
        ? `${response.replayed ? "The original assessment create was replayed" : "Assessment created"}. This records a comparison only; inventory remains unchanged.`
        : `${response.replayed ? "The original sign-off receipt was replayed" : "Independent sign-off recorded"}. This does not activate or promote inventory.`);
      setCreateReason(""); setSupersedesId(""); setSupersedesReason(""); setSignoffReason(""); setActiveOnlyAcknowledged(false);
    } catch (failure) {
      if (!controller.signal.aborted) {
        if (ambiguous(failure)) {
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

  function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!mayCreate || busy || attempt || pointer || storageError || assessments.status !== "ready" || !createReason.trim()) return;
    const receipt = (receipts.status === "ready" ? receipts.data.items.find(item => item.id === sourceBatchId) : undefined)
      ?? (pinnedReceipt?.id === sourceBatchId ? pinnedReceipt : undefined);
    if (!receipt || !eligibleReceipt(receipt)) {
      setError("Choose a successful, wholly accepted inventory_staged receipt from this domain. No request was sent.");
      return;
    }
    const key = crypto.randomUUID();
    const payload = {
      source_batch_id: receipt.id,
      expected_baseline_version: assessments.data.baseline_version,
      idempotency_key: key,
      reason: createReason.trim(),
      ...(supersedesId ? { supersedes_id: supersedesId, supersedes_reason: supersedesReason.trim() } : {}),
    };
    if (supersedesId && !supersedesReason.trim()) { setError("Explain why this assessment supersedes the selected assessment."); return; }
    void submit({ action: "assessment.create", key, payload });
  }

  function signoff(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (detail?.status !== "ready" || detail.data.id !== selectedId || !maySign || busy || attempt || pointer || storageError || !signoffReason.trim()) return;
    const assessment = detail.data;
    if (assessment.created_by_current_principal !== false || !assessment.current || assessment.state === "signed"
      || assessment.rejected_count !== 0 || assessment.duplicate_count !== 0 || assessment.conflicting_count !== 0
      || assessment.input_count !== assessment.accepted_count + assessment.rejected_count + assessment.duplicate_count
      || assessment.accepted_count !== assessment.added_count + assessment.changed_count + assessment.unchanged_count + assessment.conflicting_count
      || assessment.rows.length !== assessment.accepted_count || assessment.active_only.length !== assessment.active_only_count
      || !activeOnlyAcknowledged) {
      setError("This assessment is not ready for this independent sign-off. Check creator independence, current state, all counts, conflicts and active-only acknowledgement.");
      return;
    }
    const key = crypto.randomUUID();
    const payload = { expected_version: assessment.version, expected_digest: assessment.digest,
      active_only_acknowledged: true, idempotency_key: key, reason: signoffReason.trim() };
    void submit({ action: "assessment.signoff", key, target_id: assessment.id, payload });
  }

  function exportAssessment() {
    if (detail?.status !== "ready" || detail.data.id !== selectedId) return;
    download.current?.abort();
    const controller = new AbortController();
    download.current = controller;
    void downloadProtected(`/api/migration-assessments/${encodeURIComponent(detail.data.id)}/export`, "migration-assessment.json", controller.signal)
      .catch(failure => { if (!controller.signal.aborted) setError(`Protected assessment export failed. ${readableError(failure)}`); });
  }

  const eligible = receipts.status === "ready" ? receipts.data.items.filter(eligibleReceipt) : [];
  if (pinnedReceipt && eligibleReceipt(pinnedReceipt) && !eligible.some(item => item.id === pinnedReceipt.id)) eligible.unshift(pinnedReceipt);
  const selectedAssessment = assessments.status === "ready" ? assessments.data.items.find(item => item.id === selectedId) : undefined;
  const locked = busy || !!attempt || !!pointer || !!storageError;
  const canSign = detail?.status === "ready" && detail.data.id === selectedId && maySign && detail.data.created_by_current_principal === false
    && detail.data.current && detail.data.state !== "signed" && detail.data.rejected_count === 0
    && detail.data.duplicate_count === 0 && detail.data.conflicting_count === 0
    && detail.data.input_count === detail.data.accepted_count + detail.data.rejected_count + detail.data.duplicate_count
    && detail.data.accepted_count === detail.data.added_count + detail.data.changed_count + detail.data.unchanged_count + detail.data.conflicting_count
    && detail.data.rows.length === detail.data.accepted_count && detail.data.active_only.length === detail.data.active_only_count;

  return <section aria-labelledby="migration-heading">
    <div className="page-heading"><div><p className="eyebrow">Domain {context.selected_domain} · immutable comparison</p><h1 id="migration-heading">Migration assessment</h1><p className="intro">Compare a successful staged intended-inventory receipt against the current selected-domain baseline, then obtain a separate authenticated review.</p></div>
      <button type="button" className="secondary" disabled={busy} onClick={() => { setError(""); setRevision(value => value + 1); }}>Reload assessments and receipts</button></div>
    {error && <div className="notice error" role="alert"><h2>Migration operation needs attention</h2><p>{error}</p></div>}
    {message && <div className="notice" role="status"><p>{message}</p></div>}
    {storageError && <div className="notice error" role="alert"><h2>Recovery storage unavailable</h2><p>{storageError}</p></div>}
    {recoveryStatus && <div className={pointer ? "notice error" : "notice"} role="status"><p>{recoveryStatus}</p>{pointer && <button type="button" className="secondary" disabled={busy || !!attempt || !!storageError} onClick={() => setReadbackRevision(value => value + 1)}>Retry authorized readback</button>}</div>}
    {attempt && <div className="notice" role="status"><h2>Exact operation retained in this session</h2><p>The original payload and key remain in memory for exact retry. Only the minimal recovery pointer is stored in this tab. No new key or identity substitution will be used.</p><button type="button" disabled={busy || !!storageError} onClick={() => void submit(attempt)}>Retry exact operation</button></div>}

    <section className="inventory-panel" aria-labelledby="assessment-create-heading">
      <h2 id="assessment-create-heading">Create a domain assessment</h2>
      {mayCreate ? <form className="source-upload" onSubmit={create}>
        <label className="field-label">Successful staged inventory receipt<select value={sourceBatchId} disabled={locked || receipts.status !== "ready"} onChange={event => setSourceBatchId(event.target.value)} required>
          <option value="">Select an eligible receipt</option>{eligible.map(receipt => <option value={receipt.id} key={receipt.id}>{receipt.source_id} · {receipt.source_run_id} · {receipt.accepted_rows} rows · {receipt.id}</option>)}
        </select></label>
        <label className="field-label">Reason<textarea value={createReason} disabled={locked} onChange={event => setCreateReason(event.target.value)} required /></label>
        <label className="field-label">Supersede an earlier assessment (optional)<select value={supersedesId} disabled={locked || assessments.status !== "ready"} onChange={event => setSupersedesId(event.target.value)}><option value="">No predecessor</option>{assessments.status === "ready" && assessments.data.items.map(item => <option key={item.id} value={item.id}>{item.created_at} · {item.id} · {item.state}</option>)}</select></label>
        {supersedesId && <label className="field-label">Supersedes reason<input value={supersedesReason} disabled={locked} onChange={event => setSupersedesReason(event.target.value)} required /></label>}
        {assessments.status === "ready" && <p className="filter-help">Current baseline version from the assessment list: {assessments.data.baseline_version}. It is refreshed with this domain’s assessment page.</p>}
        {receipts.status === "loading" && <p role="status">Loading selected-domain import receipts…</p>}
        {receipts.status === "error" && <p className="notice error" role="alert">Could not load domain receipts. {receipts.error.message}</p>}
        {receipts.status === "ready" && !eligible.length && <p className="quiet">No successful wholly accepted staged inventory receipt is available on this receipt page. Observations, partial receipts and receipts with rejected or duplicate rows cannot be assessed.</p>}
        <button type="submit" disabled={locked || assessments.status !== "ready" || receipts.status !== "ready" || !eligible.length || !createReason.trim()}>{busy ? "Submitting…" : "Create assessment"}</button>
      </form> : <p className="quiet">Operator access is required to create an assessment. This view remains read-only for the current principal.</p>}
      {receipts.status === "ready" && <nav className="pagination" aria-label="Import receipt pages"><span>{receipts.data.total ? `${receipts.data.offset + 1}–${receipts.data.offset + receipts.data.items.length} of ${receipts.data.total}` : "0 receipts"}</span><div>
        <button type="button" className="secondary" disabled={locked || receiptOffset === 0} onClick={() => setReceiptOffset(Math.max(0, receiptOffset - PAGE_SIZE))}>Previous receipts</button>
        <button type="button" className="secondary" disabled={locked || receipts.data.offset + receipts.data.items.length >= receipts.data.total} onClick={() => setReceiptOffset(receiptOffset + PAGE_SIZE)}>Next receipts</button>
      </div></nav>}
    </section>

    <section className="inventory-panel" aria-labelledby="assessment-list-heading">
      <div className="section-heading"><h2 id="assessment-list-heading">Saved assessments</h2><span className="quiet">Selected domain: {context.selected_domain}</span></div>
      {assessments.status === "loading" && <p role="status">Loading scoped assessments and current baseline…</p>}
      {assessments.status === "error" && <div className="notice error" role="alert"><p>{assessments.error.message}</p><button type="button" className="secondary" onClick={() => setRevision(value => value + 1)}>Retry assessment list</button></div>}
      {assessments.status === "ready" && <>
        {!assessments.data.items.length && <p>No saved assessments are available in this domain.</p>}
        {!!assessments.data.items.length && <div className="table-scroll" tabIndex={0} role="region" aria-label="Saved migration assessments"><table><caption className="sr-only">Assessment list scoped to the selected domain.</caption><thead><tr><th scope="col">Created / source</th><th scope="col">Receipt rows</th><th scope="col">Comparison rows</th><th scope="col">State</th><th scope="col">Currency</th></tr></thead><tbody>{assessments.data.items.map(item => <tr key={item.id} data-selected={selectedId === item.id}>
          <td><button type="button" className="prefix-link" onClick={() => { if (item.id !== selectedId) setDetail({ status: "loading" }); setSelectedId(item.id); setActiveOnlyAcknowledged(false); setError(""); }}>{item.created_at}</button><div className="table-secondary"><code>{item.id}</code></div><div className="table-secondary">Source batch <code>{item.source_batch_id}</code></div></td>
          <td>{item.input_count} input · {item.accepted_count} accepted · {item.rejected_count} rejected · {item.duplicate_count} duplicate</td>
          <td>{item.added_count} added · {item.changed_count} changed · {item.unchanged_count} unchanged · {item.conflicting_count} conflict</td>
          <td>{item.state} · {item.active_only_count} active-only</td><td>{item.current ? "Current" : `Stale${item.staleness_reasons.length ? ` · ${item.staleness_reasons.length} reason(s)` : ""}`}</td>
        </tr>)}</tbody></table></div>}
        <nav className="pagination" aria-label="Assessment pages"><span>{assessments.data.total ? `${assessments.data.offset + 1}–${assessments.data.offset + assessments.data.items.length} of ${assessments.data.total}` : "0 assessments"}</span><div>
          <button type="button" className="secondary" disabled={locked || assessmentOffset === 0} onClick={() => setAssessmentOffset(Math.max(0, assessmentOffset - assessments.data.limit))}>Previous assessments</button>
          <button type="button" className="secondary" disabled={locked || assessments.data.offset + assessments.data.items.length >= assessments.data.total} onClick={() => setAssessmentOffset(assessmentOffset + assessments.data.limit)}>Next assessments</button>
        </div></nav>
      </>}
    </section>

    {selectedId && <section className="detail-section" aria-busy={detail?.status === "loading"}>
      {(detail?.status === "loading" || (detail?.status === "ready" && detail.data.id !== selectedId)) && <p role="status">Loading assessment detail…</p>}
      {detail?.status === "error" && <div className="notice error" role="alert"><p>{detail.error.message}</p><button type="button" className="secondary" onClick={() => setRevision(value => value + 1)}>Retry assessment detail</button></div>}
      {detail?.status === "ready" && detail.data.id === selectedId && <>
        <AssessmentDetailView assessment={detail.data} onExport={exportAssessment} />
        {outcome?.assessment_id === detail.data.id && <div className="notice" role="status"><h3>{outcome.replayed ? "Historical operation receipt replayed" : "Operation receipt"}</h3><p>{outcome.action} · assessment <code>{outcome.assessment_id}</code>. This receipt records the original outcome; the current/stale assessment state is shown above.</p></div>}
        {outcome?.assessment_id === detail.data.id && outcome.original_signoff && <div className="notice" role="status"><h3>Original sign-off receipt (historical)</h3><p>Assessment <code>{outcome.original_signoff.assessment_id}</code> · signer <code>{outcome.original_signoff.signer_id}</code> · signed <time>{outcome.original_signoff.signed_at}</time> · version {outcome.original_signoff.signed_version} · digest <code>{outcome.original_signoff.assessment_digest}</code>.</p><p>This historical receipt does not override current staleness.</p></div>}
        {canSign && <section className="inventory-panel" aria-labelledby="signoff-heading"><h2 id="signoff-heading">Independent Approver sign-off</h2><p>The authenticated principal must differ from the assessment creator. The server rechecks authority, version, digest, currency, conflicts and counts.</p>
          <form onSubmit={signoff}>
            <label><input type="checkbox" checked={activeOnlyAcknowledged} disabled={locked} onChange={event => setActiveOnlyAcknowledged(event.target.checked)} /> I reviewed the separately listed active-only objects and acknowledge this exact digest. They are not deletion proposals.</label>
            <label className="field-label">Sign-off reason<input value={signoffReason} disabled={locked} onChange={event => setSignoffReason(event.target.value)} required /></label>
            <button type="submit" disabled={locked || !activeOnlyAcknowledged || !signoffReason.trim()}>Sign exact assessment version and digest</button>
          </form>
        </section>}
        {maySign && detail.data.created_by_current_principal && <p className="notice error">This principal created the assessment. A different authenticated Approver must review and sign it.</p>}
        {!maySign && <p className="quiet">Approver access is required to sign. The current principal can still inspect the saved assessment.</p>}
        {selectedAssessment && selectedAssessment.id === detail.data.id && selectedAssessment.current !== detail.data.current && <p className="notice error">The list and detail currency differed. Reload the saved assessment before acting.</p>}
      </>}
    </section>}
  </section>;
}
