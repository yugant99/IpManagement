import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, request } from "./api";
import type { Page, Scope } from "./api";
import { computeRun, uploadSourceWithReconciliation } from "./firstPathApi";
import type { Coverage, EvidenceState, Finding, Receipt, RunSummary, SavedRun, SourceCatalogEntry, SourceRecord } from "./firstPathApi";

type Resource<T> = { status: "loading" } | { status: "ready"; data: T } | { status: "error"; error: ApiError };
const PAGE_SIZE = 20;
const stateLabels: Record<EvidenceState, string> = { anomalous: "Anomalous", healthy: "Healthy", unknown: "Unknown", not_applicable: "Not applicable" };
const asError = (error: unknown) => error instanceof ApiError ? error : new ApiError("The response could not be read. Reload the saved data and try again.", "INVALID_RESPONSE");

function useApiResource<T>(path: string, revision = 0): Resource<T> {
  const [state, setState] = useState<{ path: string; result: Resource<T> }>({ path, result: { status: "loading" } });
  useEffect(() => {
    const controller = new AbortController();
    setState({ path, result: { status: "loading" } });
    request<T>(path, controller.signal)
      .then((data) => { if (!controller.signal.aborted) setState({ path, result: { status: "ready", data } }); })
      .catch((error: unknown) => { if (!controller.signal.aborted) setState({ path, result: { status: "error", error: asError(error) } }); });
    return () => controller.abort();
  }, [path, revision]);
  return state.path === path ? state.result : { status: "loading" };
}

function ErrorNotice({ error, title = "Request failed", retry }: { error: ApiError; title?: string; retry?: () => void }) {
  return <div className="notice error" role="alert"><h3>{title}</h3><p>{error.message}</p><p className="diagnostic"><code>{error.code}</code>{error.requestId && <> · Request <code>{error.requestId}</code></>}</p>{retry && <button className="secondary" onClick={retry}>Retry request</button>}</div>;
}

function EvidenceBadge({ state }: { state: EvidenceState }) {
  return <span className={`evidence-state state-${state}`}>{stateLabels[state]}</span>;
}

function JsonValue({ value }: { value: unknown }) {
  return <pre className="source-json"><code>{JSON.stringify(value, null, 2)}</code></pre>;
}

function Pagination({ page, onChange, label }: { page: Page<unknown>; onChange: (offset: number) => void; label: string }) {
  return <nav className="pagination" aria-label={label}><span className="quiet">{page.total ? `${page.offset + 1}–${page.offset + page.items.length} of ${page.total}` : "0 records"}</span><div><button className="secondary" disabled={page.offset === 0} onClick={() => onChange(Math.max(0, page.offset - page.limit))}>Previous</button><button className="secondary" disabled={page.offset + page.items.length >= page.total} onClick={() => onChange(page.offset + page.limit)}>Next</button></div></nav>;
}

function CoverageList({ coverage, scopes }: { coverage: Coverage[]; scopes: Scope[] }) {
  if (!coverage.length) return <p className="quiet">No coverage recorded. Absence of telemetry does not establish a missing route.</p>;
  return <ul className="plain-list coverage-list">{coverage.map((item, index) => <li key={`${item.batch_id ?? "batch"}-${item.scope_id}-${index}`}>
    <strong>{scopes.find((scope) => scope.id === item.scope_id)?.name ?? item.scope_id}</strong>
    <dl className="facts compact">
      <dt>Scope ID</dt><dd><code>{item.scope_id}</code></dd>
      <dt>Coverage start</dt><dd><time>{item.window_start_at}</time></dd>
      <dt>Coverage end</dt><dd><time>{item.window_end_at}</time></dd>
      <dt>Declared complete</dt><dd>{item.declared_complete ? "Yes" : "No"}</dd>
      <dt>Effective complete</dt><dd>{item.effective_complete ? "Yes" : "No — insufficient to establish absence"}</dd>
      {item.kind && <><dt>Coverage kind</dt><dd>{item.kind}</dd></>}
      {item.source_id && <><dt>Source</dt><dd><code>{item.source_id}</code></dd></>}
      {item.source_run_id && <><dt>Source run</dt><dd><code>{item.source_run_id}</code></dd></>}
      {item.batch_id && <><dt>Batch</dt><dd><code>{item.batch_id}</code></dd></>}
    </dl>
  </li>)}</ul>;
}

function RawRecord({ id }: { id: string }) {
  const [revision, setRevision] = useState(0);
  const record = useApiResource<SourceRecord>(`/api/source-records/${encodeURIComponent(id)}`, revision);
  return <section className="raw-record" aria-busy={record.status === "loading"}>
    <h4>Stored source record</h4>
    {record.status === "loading" && <p role="status">Loading immutable source record…</p>}
    {record.status === "error" && <ErrorNotice error={record.error} retry={() => setRevision((value) => value + 1)} />}
    {record.status === "ready" && <>
      <dl className="facts compact"><dt>Record ID</dt><dd><code>{record.data.id}</code></dd><dt>Batch</dt><dd><code>{record.data.batch_id}</code></dd><dt>Input row</dt><dd>{record.data.row_number} (one-based)</dd><dt>Source record</dt><dd><code>{record.data.source_record_id ?? "Not supplied"}</code></dd><dt>Import status</dt><dd>{record.data.status}</dd><dt>Reason</dt><dd>{record.data.reason ?? "No rejection or duplicate reason"}</dd></dl>
      <h4 className="json-heading">Original input</h4><JsonValue value={record.data.raw} />
      <details className="provenance"><summary>Normalized stored value</summary><JsonValue value={record.data.typed} /></details>
    </>}
  </section>;
}

function ImportRecords({ batchId }: { batchId: string }) {
  const [status, setStatus] = useState("rejected");
  const [offset, setOffset] = useState(0);
  const [revision, setRevision] = useState(0);
  const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(offset) });
  if (status) params.set("status", status);
  const records = useApiResource<Page<SourceRecord>>(`/api/imports/${encodeURIComponent(batchId)}/records?${params}`, revision);
  return <section className="detail-section" aria-busy={records.status === "loading"}>
    <h3>Stored input rows</h3>
    <label className="field-label">Import status<select value={status} onChange={(event) => { setStatus(event.target.value); setOffset(0); }}><option value="rejected">Rejected</option><option value="duplicate">Duplicate</option><option value="accepted">Accepted</option><option value="">All input rows</option></select></label>
    {records.status === "loading" && <p role="status" className="loading-line">Loading input rows…</p>}
    {records.status === "error" && <ErrorNotice error={records.error} retry={() => setRevision((value) => value + 1)} />}
    {records.status === "ready" && <>
      {!records.data.items.length && <p className="inline-empty">No {status || "stored"} rows in this selection.</p>}
      {records.data.items.map((record) => <details className="record-disclosure" key={record.id}><summary>Row {record.row_number} · {record.status} · {record.source_record_id ?? "No source record ID"}</summary><p>{record.reason ?? "Accepted for typed storage."}</p><p className="quiet">Row numbers are one-based within the original input.</p><h4>Original input</h4><JsonValue value={record.raw} /><details className="provenance"><summary>Normalized stored value</summary><JsonValue value={record.typed} /></details></details>)}
      <Pagination page={records.data} onChange={setOffset} label="Import record pages" />
    </>}
  </section>;
}

function Envelope({ batchId }: { batchId: string }) {
  const [revision, setRevision] = useState(0);
  const envelope = useApiResource<unknown>(`/api/imports/${encodeURIComponent(batchId)}/envelope`, revision);
  if (envelope.status === "loading") return <p role="status">Loading original envelope…</p>;
  if (envelope.status === "error") return <ErrorNotice error={envelope.error} retry={() => setRevision((value) => value + 1)} />;
  return <JsonValue value={envelope.data} />;
}

function ReceiptDetail({ id, scopes, onClose }: { id: string; scopes: Scope[]; onClose: () => void }) {
  const [revision, setRevision] = useState(0);
  const [showEnvelope, setShowEnvelope] = useState(false);
  const receipt = useApiResource<Receipt>(`/api/imports/${encodeURIComponent(id)}`, revision);
  return <section className="detail-panel receipt-detail" aria-labelledby="receipt-heading" aria-busy={receipt.status === "loading"}>
    <div className="section-heading"><h3 id="receipt-heading">Saved import receipt</h3><button className="text-button" onClick={onClose}>Close receipt</button></div>
    {receipt.status === "loading" && <p className="loading-line" role="status">Loading receipt…</p>}
    {receipt.status === "error" && <ErrorNotice error={receipt.error} retry={() => setRevision((value) => value + 1)} />}
    {receipt.status === "ready" && <>
      <section className="detail-section"><h3>{receipt.data.application_status === "staged" ? "Inventory staged — active ledger unchanged" : receipt.data.application_status === "partial" ? "Partial import — inspect coverage and input rows" : "Import complete"}</h3><p className="quiet">A saved import is input evidence. It is not a calculation result or proof of healthy routing.</p>
        <dl className="facts"><dt>Receipt ID</dt><dd><code>{receipt.data.id}</code></dd><dt>Sequence</dt><dd>{receipt.data.sequence}</dd><dt>Source</dt><dd><code>{receipt.data.source_id}</code></dd><dt>Source run</dt><dd><code>{receipt.data.source_run_id}</code></dd><dt>Kind / authority</dt><dd>{receipt.data.source_kind === "route_policy" ? "Route policy / intended policy" : receipt.data.source_kind === "dhcp" ? "DHCP / observed" : receipt.data.source_kind === "inventory_staged" ? "Staged intended inventory" : "Routing / observed"}</dd><dt>Input rows</dt><dd>{receipt.data.input_rows}</dd><dt>Accepted / rejected / duplicate</dt><dd>{receipt.data.accepted_rows} / {receipt.data.rejected_rows} / {receipt.data.duplicate_rows}</dd><dt>Demo clock</dt><dd><time>{receipt.data.demo_clock_at}</time></dd><dt>Ingested at</dt><dd><time>{receipt.data.ingested_at}</time></dd></dl>
        {receipt.data.limitations.length > 0 && <ul className="limitation-list">{receipt.data.limitations.map((item, index) => <li key={index}>{item}</li>)}</ul>}
      </section>
      <section className="detail-section"><h3>Declared and effective coverage</h3><CoverageList coverage={receipt.data.coverage} scopes={scopes} /></section>
      <ImportRecords batchId={id} />
      <section className="detail-section"><button className="secondary" aria-expanded={showEnvelope} onClick={() => setShowEnvelope(!showEnvelope)}>{showEnvelope ? "Hide" : "Load"} original envelope</button>{showEnvelope && <Envelope batchId={id} />}</section>
    </>}
  </section>;
}

function ImportHistory({ revision, selectedId, onSelect, refresh }: { revision: number; selectedId: string | null; onSelect: (id: string) => void; refresh: () => void }) {
  const [offset, setOffset] = useState(0);
  const receipts = useApiResource<Page<Receipt>>(`/api/imports?limit=${PAGE_SIZE}&offset=${offset}`, revision);
  return <section className="inventory-panel" aria-labelledby="imports-heading" aria-busy={receipts.status === "loading"}>
    <div className="section-heading"><h3 id="imports-heading">Saved imports</h3><button className="text-button" onClick={refresh}>Reload imports</button></div>
    {receipts.status === "loading" && <p className="panel-message" role="status">Loading saved imports…</p>}
    {receipts.status === "error" && <ErrorNotice error={receipts.error} retry={refresh} />}
    {receipts.status === "ready" && <>
      {!receipts.data.items.length && <p className="panel-message">No saved imports on this page. Upload a DHCP, routing or intended-policy envelope to begin.</p>}
      {!!receipts.data.items.length && <div className="table-scroll" tabIndex={0} role="region" aria-label="Saved source imports"><table><caption className="sr-only">Import receipts, newest ingestion sequence first.</caption><thead><tr><th scope="col">Source / run</th><th scope="col">Import status</th><th scope="col">Accepted / rejected / duplicate</th></tr></thead><tbody>{receipts.data.items.map((receipt) => <tr key={receipt.id} data-selected={selectedId === receipt.id}><td><button className="prefix-link" onClick={() => onSelect(receipt.id)}>{receipt.source_id}</button><div className="table-secondary mono">{receipt.source_run_id}</div><div className="table-secondary">Sequence {receipt.sequence} · {receipt.source_kind === "route_policy" ? "Intended policy" : receipt.source_kind === "dhcp" ? "Observed DHCP" : receipt.source_kind === "inventory_staged" ? "Staged inventory" : "Observed routing"}</div></td><td><span className={`import-status ${receipt.application_status}`}>{receipt.application_status}</span><div className="table-secondary">{receipt.input_rows} input rows</div></td><td>{receipt.accepted_rows} / {receipt.rejected_rows} / {receipt.duplicate_rows}</td></tr>)}</tbody></table></div>}
      <Pagination page={receipts.data} onChange={setOffset} label="Saved import pages" />
    </>}
  </section>;
}

function RunHistory({ revision, currentId, busy, onSelect, refresh }: { revision: number; currentId?: string; busy: boolean; onSelect: (id: string) => void; refresh: () => void }) {
  const [offset, setOffset] = useState(0);
  const runs = useApiResource<Page<RunSummary>>(`/api/runs?limit=${PAGE_SIZE}&offset=${offset}`, revision);
  return <details className="saved-runs"><summary>Open a saved calculation run</summary><div className="section-heading"><p className="quiet">Opening a run preserves its original inputs and result.</p><button className="text-button" onClick={refresh}>Reload runs</button></div>
    {runs.status === "loading" && <p role="status">Loading saved runs…</p>}
    {runs.status === "error" && <ErrorNotice error={runs.error} retry={refresh} />}
    {runs.status === "ready" && <>
      {!runs.data.items.length && <p>No saved runs on this page.</p>}
      <ul className="plain-list run-history">{runs.data.items.map((run) => <li key={run.id}><div><time>{run.created_at}</time><code>{run.id}</code><span className="quiet">{run.overview.anomalous} anomalous · {run.overview.healthy} healthy · {run.overview.unknown} unknown · {run.overview.not_applicable} not applicable</span></div><button className="secondary" disabled={busy || run.id === currentId} onClick={() => onSelect(run.id)}>{run.id === currentId ? "Open now" : "Open run"}</button></li>)}</ul>
      <Pagination page={runs.data} onChange={setOffset} label="Saved run pages" />
    </>}
  </details>;
}

function SourceCatalog({ scopes }: { scopes: Scope[] }) {
  const catalog = useApiResource<Page<SourceCatalogEntry>>("/api/source-catalog?limit=200&offset=0");
  return <section className="inventory-panel" aria-labelledby="source-catalog-heading" aria-busy={catalog.status === "loading"}>
    <div className="section-heading"><div><h2 id="source-catalog-heading">Imported-source catalog</h2><p className="quiet">Receipt-derived source identity and per-scope coverage. This is not automatic discovery.</p></div></div>
    {catalog.status === "loading" && <p className="panel-message" role="status">Loading source catalog…</p>}
    {catalog.status === "error" && <ErrorNotice error={catalog.error} />}
    {catalog.status === "ready" && <div className="table-scroll" tabIndex={0} role="region" aria-label="Imported source catalog"><table><caption className="sr-only">Imported sources selected at the seeded demo clock.</caption><thead><tr><th>Source / run</th><th>Scope</th><th>Authority / status</th><th>Freshness / completeness</th></tr></thead><tbody>{catalog.data.items.map((item) => <tr key={`${item.batch_id}-${item.scope_id}`}><td><strong>{item.source_name}</strong><div className="table-secondary mono">{item.source_id} · {item.source_run_id}</div><div className="table-secondary">{item.source_kind} · batch <code>{item.batch_id}</code></div></td><td>{scopes.find((scope) => scope.id === item.scope_id)?.name ?? item.scope_id}</td><td>{item.authority} · {item.authority_status}<div className="table-secondary">{item.application_status} · {item.rejection_status}</div></td><td>{item.freshness} · {item.completeness}<div className="table-secondary">{item.window_start_at} → {item.window_end_at}</div></td></tr>)}</tbody></table></div>}
  </section>;
}

function FindingDetail({ runId, findingId, scopes, onClose }: { runId: string; findingId: string; scopes: Scope[]; onClose: () => void }) {
  const [revision, setRevision] = useState(0);
  const [rawId, setRawId] = useState<string | null>(null);
  const heading = useRef<HTMLHeadingElement>(null);
  const finding = useApiResource<Finding>(`/api/runs/${encodeURIComponent(runId)}/findings/${encodeURIComponent(findingId)}`, revision);
  useEffect(() => { heading.current?.focus({ preventScroll: true }); heading.current?.scrollIntoView({ block: "nearest" }); }, []);
  return <aside className="detail-panel" id="finding-detail" aria-labelledby="finding-heading" aria-busy={finding.status === "loading"}>
    <div className="section-heading"><p className="eyebrow">Saved evidence detail</p><button className="text-button" onClick={onClose}>Close detail</button></div>
    <h3 id="finding-heading" ref={heading} tabIndex={-1} className="detail-title">{finding.status === "ready" ? finding.data.subject.cidr : "Selected finding"}</h3>
    <p className="detail-subtitle">Pinned run <code>{runId}</code> · Synthetic calculation</p>
    {finding.status === "loading" && <p className="loading-line" role="status">Loading saved finding…</p>}
    {finding.status === "error" && <ErrorNotice error={finding.error} retry={() => setRevision((value) => value + 1)} />}
    {finding.status === "ready" && <>
      <section className="detail-section"><h3>Result and meaning</h3><div className="result-state"><EvidenceBadge state={finding.data.evidence_state} /><span>Rule severity: {finding.data.severity}</span></div><p>{finding.data.explanation}</p><dl className="facts compact"><dt>Network scope</dt><dd>{finding.data.subject.scope_name}</dd><dt>Scope ID</dt><dd><code>{finding.data.subject.scope_id}</code></dd><dt>Address family</dt><dd>IPv{finding.data.subject.family}</dd><dt>Subject ID / version</dt><dd><code>{finding.data.subject.id}</code> / {finding.data.subject.version}</dd><dt>Finding ID</dt><dd><code>{finding.data.id}</code></dd><dt>Rule / version</dt><dd><code>{finding.data.rule_id}</code> / {finding.data.rule_version}</dd></dl><h4 className="json-heading">Proposed next action</h4><p>{finding.data.proposed_action}</p><p className="quiet">This view records a calculation. It does not execute a network change.</p></section>
      <section className="detail-section"><h3>Time and applicability</h3><dl className="facts compact"><dt>Evaluation kind</dt><dd>{finding.data.evaluated_window.kind}</dd><dt>Start / demo clock</dt><dd><time>{finding.data.evaluated_window.start_at}</time></dd><dt>End</dt><dd><time>{finding.data.evaluated_window.end_at}</time></dd><dt>Validity convention</dt><dd><code>{finding.data.evaluated_window.interval_convention}</code></dd></dl><p className="quiet">Active route validity uses an inclusive start and exclusive end. Coverage end is the source assertion cutoff.</p></section>
      <section className="detail-section"><h3>{finding.data.rule_id === "metadata_gap" ? "Saved metadata evaluation" : "Saved rule policy"}</h3>
        {finding.data.rule_id === "metadata_gap" && <p>Owner and purpose below are the values evaluated in this saved run. Use Prefix planning to make an audited correction, then compute a new run to compare the result. Original source references remain creation history.</p>}
        {finding.data.policy ? <JsonValue value={finding.data.policy} /> : <p>No separate policy payload applies. See the rule explanation and evidence.</p>}</section>
      {finding.data.observations && <section className="detail-section"><h3>Observed discrepancies and references</h3><JsonValue value={finding.data.observations} /></section>}
      <section className="detail-section"><h3>Selected source coverage</h3><CoverageList coverage={finding.data.coverage} scopes={scopes} /></section>
      <section className="detail-section"><h3>Limitations</h3>{finding.data.limitations.length ? <ul className="limitation-list">{finding.data.limitations.map((item, index) => <li key={index}>{item}</li>)}</ul> : <p>No additional limitations recorded for this finding.</p>}<p className="quiet">Unknown is insufficient evidence. Not applicable means this rule does not apply to the subject. Neither is a healthy routing claim.</p></section>
      <section className="detail-section"><h3>Input provenance</h3><details className="provenance"><summary>Intended inventory origin</summary><JsonValue value={finding.data.subject.origin} /></details>
        {!finding.data.input_references.length && <p>No input references were recorded.</p>}
        {finding.data.input_references.map((reference, index) => <article className="inventory-record" key={`${reference.record_id ?? reference.batch_id ?? reference.source_id}-${index}`}><h4>{reference.kind.replaceAll("_", " ")}</h4><dl className="facts compact"><dt>Source</dt><dd><code>{reference.source_id}</code></dd><dt>Source run</dt><dd><code>{reference.source_run_id}</code></dd>{reference.batch_id && <><dt>Batch ID</dt><dd><code>{reference.batch_id}</code></dd></>}{reference.source_record_id && <><dt>Source record</dt><dd><code>{reference.source_record_id}</code></dd></>}{reference.audit_id && <><dt>Matching metadata audit</dt><dd><code>{reference.audit_id}</code> · <a href={`/api/audit?subject_id=${encodeURIComponent(finding.data.subject.id)}`} target="_blank" rel="noreferrer">View prefix audit JSON</a></dd></>}</dl>{reference.record_id && <button className="text-button" onClick={() => setRawId(reference.record_id!)}>Load stored raw record</button>}</article>)}
        {rawId && <><button className="text-button" onClick={() => setRawId(null)}>Close raw record</button><RawRecord key={rawId} id={rawId} /></>}
      </section>
    </>}
  </aside>;
}

function RunResults({ run, scopes }: { run: SavedRun; scopes: Scope[] }) {
  const [scope, setScope] = useState("");
  const [state, setState] = useState("");
  const [rule, setRule] = useState("");
  const [severity, setSeverity] = useState("");
  const [offset, setOffset] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const selectedButton = useRef<HTMLButtonElement | null>(null);
  const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(offset) });
  if (scope) params.set("scope_id", scope);
  if (state) params.set("evidence_state", state);
  if (rule) params.set("rule_id", rule);
  if (severity) params.set("severity", severity);
  const findings = useApiResource<Page<Finding>>(`/api/runs/${encodeURIComponent(run.id)}/findings?${params}`, revision);
  function changePage(next: number) { setSelectedId(null); setOffset(next); }
  return <section className="run-results" aria-labelledby="run-heading">
    <div className="section-heading"><h3 id="run-heading">Saved calculation result</h3><span className="quiet">Synthetic · {run.rule_id}</span></div>
    <dl className="run-identity facts"><dt>Pinned run</dt><dd><code>{run.id}</code></dd><dt>Created at</dt><dd><time>{run.created_at}</time></dd><dt>Fixed demo clock</dt><dd><time>{run.demo_clock_at}</time></dd><dt>Ledger / rule version</dt><dd>{run.ledger_version} / {run.rule_version}</dd></dl>
    <p className="quiet run-help">All totals below come from this saved run across all scopes. Filters narrow the list only. New imports do not change this result.</p>
    <dl className="overview-counts"><div><dt>Evaluated</dt><dd>{run.overview.total}</dd></div>{(Object.keys(stateLabels) as EvidenceState[]).map((key) => <div key={key}><dt><EvidenceBadge state={key} /></dt><dd>{run.overview[key]}</dd></div>)}</dl>
    <details className="selected-batches"><summary>Selected source batches ({run.selected_batches.length})</summary><p className="quiet">These saved receipts identify the evidence selected for this run. Completeness and freshness are evaluated separately.</p>{!run.selected_batches.length && <p>No source batches were available.</p>}{run.selected_batches.map((batch) => <article className="inventory-record" key={batch.id}><h4>{batch.source_id}</h4><dl className="facts compact"><dt>Source run</dt><dd><code>{batch.source_run_id}</code></dd><dt>Batch ID</dt><dd><code>{batch.id}</code></dd><dt>Ingested at</dt><dd><time>{batch.ingested_at}</time></dd><dt>Import status</dt><dd>{batch.application_status}</dd><dt>Accepted / rejected / duplicate</dt><dd>{batch.accepted_rows} / {batch.rejected_rows} / {batch.duplicate_rows}</dd></dl><CoverageList coverage={batch.coverage} scopes={scopes} /></article>)}</details>
    <div className="filters result-filters"><label>Network scope<select value={scope} onChange={(event) => { setScope(event.target.value); changePage(0); }}><option value="">All network scopes</option>{scopes.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label><label>Evidence state<select value={state} onChange={(event) => { setState(event.target.value); changePage(0); }}><option value="">All evidence states</option>{(Object.keys(stateLabels) as EvidenceState[]).map((key) => <option value={key} key={key}>{stateLabels[key]}</option>)}</select></label></div>
    <div className="filters result-filters"><label>Rule<select value={rule} onChange={(event) => { setRule(event.target.value); changePage(0); }}><option value="">All rules</option>{[...new Set(run.findings.map((finding) => finding.rule_id))].sort().map((id) => <option key={id}>{id}</option>)}</select></label><label>Severity<select value={severity} onChange={(event) => { setSeverity(event.target.value); changePage(0); }}><option value="">All severities</option>{["critical", "high", "warning"].map((value) => <option key={value}>{value}</option>)}</select></label></div>
    <div className={`inventory-layout${selectedId ? " has-detail" : ""}`}>
      <section className="inventory-panel" aria-label="Findings in selected run" aria-busy={findings.status === "loading"}>
        {findings.status === "loading" && <p className="panel-message" role="status">Loading findings from this run…</p>}
        {findings.status === "error" && <ErrorNotice error={findings.error} retry={() => setRevision((value) => value + 1)} />}
        {findings.status === "ready" && <>
          {!findings.data.items.length && <p className="panel-message">No findings match these filters in this run.</p>}
          {!!findings.data.items.length && <div className="table-scroll" tabIndex={0} role="region" aria-label="Run findings"><table><caption className="sr-only">Saved results by rule and subject. Evidence state and rule severity are separate.</caption><thead><tr><th scope="col">Prefix / scope</th><th scope="col">Evidence state</th><th scope="col">Rule severity</th></tr></thead><tbody>{findings.data.items.map((finding) => <tr key={finding.id} data-selected={selectedId === finding.id}><td><button className="prefix-link mono" aria-expanded={selectedId === finding.id} aria-controls={selectedId === finding.id ? "finding-detail" : undefined} onClick={(event) => { selectedButton.current = event.currentTarget; setSelectedId(finding.id); }}>{finding.subject.cidr}<span className="sr-only"> in {finding.subject.scope_name}, open evidence</span></button><div className="table-secondary">{finding.subject.scope_name} · IPv{finding.subject.family}</div></td><td><EvidenceBadge state={finding.evidence_state} /><div className="table-secondary">{finding.explanation}</div></td><td>{finding.severity}<div className="table-secondary">{finding.rule_id}</div></td></tr>)}</tbody></table></div>}
          <Pagination page={findings.data} onChange={changePage} label="Finding pages" />
        </>}
      </section>
      {selectedId && <FindingDetail key={`${run.id}-${selectedId}`} runId={run.id} findingId={selectedId} scopes={scopes} onClose={() => { setSelectedId(null); selectedButton.current?.focus(); }} />}
    </div>
  </section>;
}

export default function FirstPath({ scopes }: { scopes: Scope[] }) {
  const [file, setFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<ApiError | null>(null);
  const [importResult, setImportResult] = useState<{ receipt: Receipt; replay: boolean } | null>(null);
  const [receiptId, setReceiptId] = useState<string | null>(null);
  const [importRevision, setImportRevision] = useState(0);
  const [runRevision, setRunRevision] = useState(0);
  const [run, setRun] = useState<SavedRun | null>(null);
  const [runBusy, setRunBusy] = useState<"computing" | "opening" | null>(null);
  const [runError, setRunError] = useState<ApiError | null>(null);
  const [newImport, setNewImport] = useState(false);
  const [reconcileAfterImport, setReconcileAfterImport] = useState(false);
  const uploadController = useRef<AbortController | null>(null);
  const runController = useRef<AbortController | null>(null);
  useEffect(() => () => { uploadController.current?.abort(); runController.current?.abort(); }, []);

  async function importFile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || importing) return;
    const controller = new AbortController();
    uploadController.current = controller;
    setImporting(true);
    setImportError(null);
    try {
      if (file.size > 10 * 1024 * 1024) throw new ApiError("Choose a JSON file no larger than 10 MiB.", "FILE_TOO_LARGE");
      const bytes = await file.arrayBuffer();
      if (controller.signal.aborted) return;
      let body: string;
      try { body = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(bytes); }
      catch { throw new ApiError("The selected file is not valid UTF-8. No upload was sent; save the source as UTF-8 JSON and try again.", "INVALID_ENCODING"); }
      try { JSON.parse(body); } catch { throw new ApiError("The selected file is not valid JSON. No upload was sent.", "INVALID_JSON"); }
      const result = await uploadSourceWithReconciliation(body, controller.signal, reconcileAfterImport);
      if (controller.signal.aborted) return;
      setImportResult(result);
      setReceiptId(result.receipt.id);
      setImportRevision((value) => value + 1);
      if (!result.replay) setNewImport(true);
    } catch (error) {
      if (!controller.signal.aborted) setImportError(asError(error));
    } finally { if (!controller.signal.aborted) setImporting(false); }
  }

  async function loadRun(id?: string) {
    if (runBusy) return;
    const controller = new AbortController();
    runController.current = controller;
    setRunBusy(id ? "opening" : "computing");
    setRunError(null);
    try {
      const result = id ? await request<SavedRun>(`/api/runs/${encodeURIComponent(id)}`, controller.signal) : await computeRun(controller.signal);
      if (controller.signal.aborted) return;
      setRun(result);
      if (!id) { setNewImport(false); setRunRevision((value) => value + 1); }
    } catch (error) {
      if (!controller.signal.aborted) setRunError(asError(error));
    } finally { if (!controller.signal.aborted) setRunBusy(null); }
  }

  return <div className="first-path">
    <div className="page-heading"><div><p className="eyebrow">Source evidence → saved calculation</p><h1>Source evidence and findings</h1><p className="intro">Import synthetic DHCP, routing and intended policy, then inspect saved calculations and findings.</p></div></div>
    <div className="evidence-banner"><strong>Synthetic inputs · Fixed demo clock</strong><span>Scope, policy and fresh complete coverage determine whether absence can be established. Missing evidence stays unknown.</span></div>
    <section className="path-step" aria-labelledby="import-heading"><div className="step-heading"><span className="step-number" aria-hidden="true">1</span><div><h2 id="import-heading">Import a source envelope</h2><p className="quiet">Choose a DHCP, routing or intended-policy JSON file. Intended-inventory uploads are staged and never overwrite the active ledger.</p></div></div>
      <form className="source-upload" onSubmit={(event) => { void importFile(event); }}><label className="field-label">Source JSON<input type="file" accept=".json,application/json" disabled={importing || runBusy !== null} onChange={(event) => { setFile(event.target.files?.[0] ?? null); setImportError(null); }} aria-describedby="source-help" /></label><label className="checkbox-field"><input type="checkbox" checked={reconcileAfterImport} disabled={importing || runBusy !== null} onChange={(event) => setReconcileAfterImport(event.target.checked)} /> Reconcile after this import</label><button disabled={!file || importing || runBusy !== null} type="submit">{importing ? "Importing…" : "Import source"}</button></form>
      <p className="filter-help" id="source-help">ipam-synthetic-v1 · Up to 10 MiB / 10,000 records · Expected-answer files are not rule inputs.</p>
      {importError && <><ErrorNotice error={importError} title="No new import receipt confirmed" /><p className="quiet">If the request timed out or lost its connection, it may have been saved. Reload saved imports before retrying; identical replay returns the original receipt.</p></>}
      {importResult && <div className={`notice import-result ${importResult.receipt.application_status}`} role="status"><h3>{importResult.replay ? "Identical replay — original receipt returned" : importResult.receipt.application_status === "partial" ? "Saved a partial import" : "Source import saved"}</h3><p><code>{importResult.receipt.source_id}</code> · {importResult.receipt.input_rows} input rows: {importResult.receipt.accepted_rows} accepted, {importResult.receipt.rejected_rows} rejected, {importResult.receipt.duplicate_rows} duplicate.</p><p>{importResult.replay ? "No new ingestion sequence was created." : reconcileAfterImport ? "Import committed; the separate reconciliation result is shown below." : "No calculation was triggered. Compute reconciliation when the intended inputs are ready."}</p>{importResult.receipt.reconciliation && <p><strong>Reconciliation:</strong> {importResult.receipt.reconciliation.status}{importResult.receipt.reconciliation.run_id && <> · run <code>{importResult.receipt.reconciliation.run_id}</code></>}{importResult.receipt.reconciliation.error && <> · {importResult.receipt.reconciliation.error.message}</>}</p>}{importError && <p>This is the last confirmed receipt, from before the failed request.</p>}<button className="text-button" onClick={() => setReceiptId(importResult.receipt.id)}>Open this receipt</button></div>}
      <ImportHistory revision={importRevision} selectedId={receiptId} onSelect={setReceiptId} refresh={() => setImportRevision((value) => value + 1)} />
      {receiptId && <ReceiptDetail key={receiptId} id={receiptId} scopes={scopes} onClose={() => setReceiptId(null)} />}
    </section>
    <SourceCatalog scopes={scopes} />
    <section className="path-step" aria-labelledby="compute-heading"><div className="step-heading"><span className="step-number" aria-hidden="true">2</span><div><h2 id="compute-heading">Compute and save reconciliation</h2><p className="quiet">The API saves a new run using the current intended ledger and selected source batches.</p></div></div>
      <div className="compute-actions"><button disabled={runBusy !== null || importing} onClick={() => { void loadRun(); }}>{runBusy === "computing" ? "Computing and saving…" : "Compute reconciliation"}</button><span className="quiet">Explicit trigger · Saved evidence · No network changes</span></div>
      {runBusy && <p role="status" className="loading-line">{runBusy === "computing" ? "Waiting for a saved calculation result…" : "Opening the saved calculation…"}{run && " The previous run remains below until this request succeeds."}</p>}
      {runError && <><ErrorNotice error={runError} title="No new calculation result confirmed" /><p className="run-warning" role="status">{run ? "The previous saved run remains displayed below." : "No calculation result is displayed."} A request that timed out may have saved a run; reload saved runs to inspect it.</p></>}
      {newImport && <p className="run-warning">A new import was saved. Existing runs remain unchanged; use Compute to include the currently selected source inputs.</p>}
      <RunHistory revision={runRevision} currentId={run?.id} busy={runBusy !== null || importing} onSelect={(id) => { void loadRun(id); }} refresh={() => setRunRevision((value) => value + 1)} />
      {!run && !runBusy && <div className="empty-state"><h3>No saved result selected</h3><p>Compute reconciliation or open a saved run. The browser does not calculate findings or infer healthy state from an empty list.</p></div>}
      {run && <RunResults key={run.id} run={run} scopes={scopes} />}
    </section>
  </div>;
}
