import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, currentContext, hasRole } from "./api";
import type { Prefix, Scope } from "./api";
import { createChildPrefix, loadChildPreview, loadEditContext, loadScopedPrefixes, updatePrefix } from "./inventoryCommandsApi";
import type { ChildPreview, EditContext, EditablePrefix, PrefixMutation } from "./inventoryCommandsApi";

type Resource<T> = { status: "loading" } | { status: "ready"; data: T } | { status: "error"; error: ApiError };
const asError = (error: unknown) => error instanceof ApiError ? error : new ApiError("The inventory response could not be read. Reload saved inventory before retrying.", "INVALID_RESPONSE");
const displayCount = (value: string) => value.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

function ErrorNotice({ error }: { error: ApiError }) {
  return <div className="notice error" role="alert"><p>{error.message}</p><p className="diagnostic"><code>{error.code}</code>{error.requestId && <> · Request <code>{error.requestId}</code></>}</p></div>;
}

function PrefixCommandForm({ context, onSaved }: { context: EditContext; onSaved: (result: PrefixMutation) => void }) {
  const { prefix, scope } = context;
  const [mode, setMode] = useState<"child" | "edit">("child");
  const actorId = currentContext().principal_id;
  const [cidr, setCidr] = useState("");
  const [owner, setOwner] = useState("");
  const [purpose, setPurpose] = useState("");
  const [tags, setTags] = useState("");
  const [fields, setFields] = useState<[string, string][]>([]);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<ApiError | null>(null);
  const [busy, setBusy] = useState(false);
  const [previewBusy, setPreviewBusy] = useState(false);
  const [preview, setPreview] = useState<ChildPreview | null>(null);
  const [previewError, setPreviewError] = useState<ApiError | null>(null);
  const [selectedPreview, setSelectedPreview] = useState<ChildPreview | null>(null);
  const parentLength = Number(prefix.cidr.split("/")[1]);
  const [childLength, setChildLength] = useState(String(Math.min(128, Math.max(64, parentLength + 1))));
  const operation = useRef<AbortController | null>(null);
  const previewOperation = useRef<AbortController | null>(null);
  const populated = Boolean(context.children_count || prefix.pools.length || prefix.allocations.length);
  const structuralChange = mode === "child" || cidr.trim() !== prefix.cidr;
  const affectedPools = context.history_impact?.structural;

  useEffect(() => () => { operation.current?.abort(); previewOperation.current?.abort(); }, []);

  function chooseMode(next: "child" | "edit") {
    setMode(next);
    setCidr(next === "edit" ? prefix.cidr : "");
    setOwner(next === "edit" ? prefix.owner : "");
    setPurpose(next === "edit" ? prefix.purpose : "");
    setTags(next === "edit" ? prefix.tags.join(", ") : "");
    setFields(next === "edit" ? Object.entries(prefix.custom_fields) : []);
    setSelectedPreview(null);
    setError(null);
  }

  async function previewChildren() {
    previewOperation.current?.abort();
    const controller = new AbortController();
    previewOperation.current = controller;
    setPreviewBusy(true);
    setPreview(null);
    setPreviewError(null);
    try {
      const value = await loadChildPreview(prefix.id, Number(childLength), controller.signal);
      if (!controller.signal.aborted) setPreview(value);
    } catch (failure) {
      if (!controller.signal.aborted) setPreviewError(asError(failure));
    } finally {
      if (!controller.signal.aborted) setPreviewBusy(false);
    }
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    if (structuralChange && !affectedPools) {
      setError(new ApiError("History impact is unavailable. Reload saved inventory before changing prefix structure.", "INCOMPLETE_RESPONSE"));
      return;
    }
    const names = fields.map(([key]) => key.trim());
    if (new Set(names).size !== names.length || names.some((key) => !key)) {
      setError(new ApiError("Custom field names must be distinct and nonempty.", "INVALID_INPUT"));
      return;
    }
    const controller = new AbortController();
    operation.current = controller;
    setBusy(true);
    setError(null);
    const reviewed = mode === "child" ? selectedPreview : null;
    const payload: EditablePrefix = {
      actor_id: actorId, reason, cidr, owner, purpose,
      tags: tags.trim() ? tags.split(",").map((tag) => tag.trim()) : [],
      custom_fields: Object.fromEntries(fields.map(([key, value]) => [key.trim(), value])),
      expected_baseline_version: reviewed?.baseline_version ?? context.baseline_version,
    };
    try {
      const result = mode === "child"
        ? await createChildPrefix({ ...payload, scope_id: prefix.scope_id, parent_id: prefix.id, expected_parent_version: reviewed?.parent_version ?? prefix.version }, controller.signal)
        : await updatePrefix(prefix.id, { ...payload, expected_version: prefix.version }, controller.signal);
      if (!controller.signal.aborted) onSaved(result);
    } catch (failure) {
      if (!controller.signal.aborted) setError(asError(failure));
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  }

  return <div className="detail-section">
    <h3>{prefix.cidr} · {scope.region}</h3>
    <dl className="facts compact"><dt>Domain / region</dt><dd>{scope.domain} / {scope.region}</dd><dt>Scoped namespace</dt><dd>{scope.namespace}</dd><dt>Scope ID</dt><dd><code>{scope.id}</code></dd><dt>Reviewed versions</dt><dd>Prefix {prefix.version} · Intended ledger {context.baseline_version}</dd><dt>Existing dependents</dt><dd>{context.children_count} direct children · {prefix.pools.length} attached pools · {prefix.allocations.length} direct allocations</dd></dl>
    <div className="compute-actions"><button type="button" className={mode === "child" ? "" : "secondary"} disabled={busy} onClick={() => chooseMode("child")}>Create child prefix</button><button type="button" className={mode === "edit" ? "" : "secondary"} disabled={busy} onClick={() => chooseMode("edit")}>Edit selected prefix</button></div>
    {mode === "child" && prefix.family === 6 && <section className="inventory-record" aria-busy={previewBusy}>
      <h4>IPv6 child-prefix planning</h4>
      <p className="quiet">Capacity counts child prefixes in this regional parent. Existing overlapping prefixes block a slot. This preview does not reserve space or measure host availability.</p>
      <div className="compute-actions"><label className="field-label">Child prefix length<input type="number" min={parentLength + 1} max={128} value={childLength} onChange={(event) => { setChildLength(event.target.value); setPreview(null); }} disabled={previewBusy || busy} /></label><button type="button" className="secondary" onClick={() => { void previewChildren(); }} disabled={previewBusy || busy || parentLength === 128}>{previewBusy ? "Loading preview…" : "Preview first free children"}</button></div>
      {previewError && <ErrorNotice error={previewError} />}
      {preview && <><dl className="facts compact"><dt>Total /{preview.prefix_length} slots</dt><dd className="mono">{displayCount(preview.total_children)}</dd><dt>Blocked by inventory</dt><dd className="mono">{displayCount(preview.blocked_children)}</dd><dt>Free prefix slots</dt><dd className="mono">{displayCount(preview.free_children)}</dd><dt>Preview ledger version</dt><dd>{preview.baseline_version}</dd></dl>
        {preview.items.length ? <ul className="plain-list">{preview.items.map((item) => <li key={item}><button type="button" className="text-button mono" disabled={busy} onClick={() => { setCidr(item); setSelectedPreview(preview); }}>{item}{cidr === item && selectedPreview === preview ? " · Selected" : " · Select"}</button></li>)}</ul> : <p>No free child-prefix slots at this length.</p>}
        <p className="quiet">Showing at most {preview.limit} candidates. Select one and save the child below to persist the regional assignment.</p></>}
    </section>}
    <form onSubmit={(event) => { void save(event); }}>
      <fieldset disabled={busy} className="inventory-form"><legend>{mode === "child" ? "New intended child" : "Edit intended prefix"}</legend>
        <p className="quiet">Authenticated principal: {actorId}. Inventory editing requires the Operator role.</p>
        <label className="field-label">{mode === "child" ? "Child CIDR" : "Prefix CIDR"}<input required maxLength={80} value={cidr} disabled={mode === "edit" && populated} placeholder={prefix.family === 6 ? "2001:db8:100:1::/64" : "10.40.0.0/26"} onChange={(event) => { setCidr(event.target.value); setSelectedPreview(null); }} /></label>
        {mode === "edit" && populated && <p className="quiet">Bounds are locked because this prefix has children, allocations or an attached pool. Metadata can still be edited.</p>}
        {mode === "child" && <p className="quiet">Parent: {prefix.cidr} in {scope.name}. The API requires strict containment and rejects unrelated overlaps.</p>}
        <label className="field-label">Owner<input maxLength={120} value={owner} onChange={(event) => setOwner(event.target.value)} /></label>
        <label className="field-label">Purpose<input maxLength={500} value={purpose} onChange={(event) => setPurpose(event.target.value)} /></label>
        <label className="field-label">Tags, separated by commas<input maxLength={1600} value={tags} onChange={(event) => setTags(event.target.value)} /></label>
        <h4>Extra string metadata</h4>
        <p className="quiet">Names start with a letter and may contain letters, numbers, dots, underscores or hyphens. Identity, version and source fields are reserved.</p>
        {fields.map(([key, value], index) => <div className="compute-actions" key={index}>
          <label className="field-label">Field name {index + 1}<input required maxLength={64} value={key} onChange={(event) => setFields((current) => current.map((entry, position) => position === index ? [event.target.value, entry[1]] : entry))} /></label>
          <label className="field-label">Field value {index + 1}<input maxLength={500} value={value} onChange={(event) => setFields((current) => current.map((entry, position) => position === index ? [entry[0], event.target.value] : entry))} /></label>
          <button type="button" className="secondary" onClick={() => setFields((current) => current.filter((_, position) => position !== index))}>Remove field {index + 1}</button>
        </div>)}
        <button type="button" className="secondary" disabled={fields.length >= 32} onClick={() => setFields((current) => [...current, ["", ""]])}>Add metadata field</button>
        <label className="field-label">Reason for this change<input required maxLength={500} value={reason} onChange={(event) => setReason(event.target.value)} /></label>
        <div className={structuralChange ? "run-warning" : "quiet"} role="status">
          {!structuralChange ? <p>Changing only owner, purpose, tags or custom metadata preserves eligible historical p95 and forecast. Existing evidence requirements still apply.</p> : !affectedPools ?
            <p>The server did not provide the affected-pool review. Reload saved inventory before creating a child or changing prefix bounds. Metadata corrections remain available.</p> : affectedPools.length > 0 ? <>
              <p>{mode === "child" ? "Creating this child changes relevant prefix structure and invalidates" : "If the submitted CIDR changes prefix bounds, it invalidates"} historical p95 and forecast eligibility for these pools on this prefix or its ancestors:</p>
              <ul>{affectedPools.map((pool) => <li key={pool.pool_id}>{pool.name} · <code>{pool.cidr}</code></li>)}</ul>
              <p>Current occupancy may remain available, and positive lease evidence can still show activity. Previously saved runs remain unchanged.</p>
            </> : <p>The server lists no affected pools for {mode === "child" ? "this child creation" : "a bounds change to this prefix"} at the reviewed inventory version. Previously saved runs remain unchanged.</p>}
        </div>
        <button type="submit" disabled={!hasRole("Operator") || !cidr.trim() || (structuralChange && !affectedPools)}>{busy ? "Saving intended inventory…" : mode === "child" ? "Save child prefix" : "Save prefix changes"}</button>
      </fieldset>
    </form>
    {error && <><ErrorNotice error={error} /><p className="run-warning">No write is confirmed by this response. Reload saved inventory before retrying; a timed-out request may have committed. Stale changes require a new review.</p></>}
    <details className="provenance"><summary>Original source reference</summary><p>Edits preserve the original source record; the saved audit records the local change.</p><dl className="facts compact"><dt>Source</dt><dd><code>{prefix.origin.source_id}</code></dd><dt>Source run</dt><dd><code>{prefix.origin.source_run_id}</code></dd><dt>Source record</dt><dd><code>{prefix.origin.source_record_id}</code></dd></dl></details>
  </div>;
}

export default function InventoryEditor({ scopes, onChanged }: { scopes: Scope[]; onChanged?: () => void }) {
  const [scopeId, setScopeId] = useState(scopes[0]?.id ?? "");
  const [prefixId, setPrefixId] = useState("");
  const [prefixes, setPrefixes] = useState<Resource<Prefix[]>>({ status: "loading" });
  const [context, setContext] = useState<Resource<EditContext>>({ status: "loading" });
  const [revision, setRevision] = useState(0);
  const [saved, setSaved] = useState<PrefixMutation | null>(null);
  const selectedScope = scopes.find((scope) => scope.id === scopeId);
  const domain = selectedScope?.domain ?? "";
  const region = selectedScope?.region ?? "";
  const regions = [...new Set(scopes.filter((scope) => scope.domain === domain).map((scope) => scope.region))];

  useEffect(() => {
    const controller = new AbortController();
    setPrefixes({ status: "loading" });
    if (scopeId) loadScopedPrefixes(scopeId, controller.signal)
      .then((data) => { if (!controller.signal.aborted) { setPrefixes({ status: "ready", data }); setPrefixId((current) => data.some((prefix) => prefix.id === current) ? current : data[0]?.id ?? ""); } })
      .catch((error: unknown) => { if (!controller.signal.aborted) setPrefixes({ status: "error", error: asError(error) }); });
    else setPrefixes({ status: "ready", data: [] });
    return () => controller.abort();
  }, [scopeId, revision]);

  useEffect(() => {
    const controller = new AbortController();
    setContext({ status: "loading" });
    if (prefixId) loadEditContext(prefixId, controller.signal)
      .then((data) => { if (!controller.signal.aborted) setContext({ status: "ready", data }); })
      .catch((error: unknown) => { if (!controller.signal.aborted) setContext({ status: "error", error: asError(error) }); });
    return () => controller.abort();
  }, [prefixId, revision]);

  function changeScope(id: string) { setScopeId(id); setPrefixId(""); setSaved(null); }

  return <section className="panel" aria-labelledby="inventory-editor-heading">
    <div className="section-heading"><div><p className="eyebrow">Local intended inventory</p><h2 id="inventory-editor-heading">Prefix editing and IPv6 planning</h2><p className="quiet">Edit intended prefixes with server validation and audit.</p></div><button className="secondary" onClick={() => setRevision((value) => value + 1)}>Reload saved inventory</button></div>
    <div className="filters">
      <span className="filter-help">Selected domain: {currentContext().selected_domain}</span>
      <label className="field-label">Region<select value={region} onChange={(event) => changeScope(scopes.find((scope) => scope.domain === domain && scope.region === event.target.value)?.id ?? "")}>{regions.map((value) => <option key={value} value={value}>{value}</option>)}</select></label>
      <label className="field-label">Network scope<select value={scopeId} onChange={(event) => changeScope(event.target.value)}>{scopes.filter((scope) => scope.domain === domain && scope.region === region).map((scope) => <option key={scope.id} value={scope.id}>{scope.name} · {scope.namespace}</option>)}</select></label>
    </div>
    {saved && <div className="notice" role="status"><h3>Intended prefix saved</h3><p><code>{saved.prefix.cidr}</code> · Prefix version {saved.prefix.version} · Ledger version {saved.baseline_version}</p><p>Audit record <code>{saved.audit_id}</code>. Saved calculations retain their original ledger version until a new run is computed.</p></div>}
    {prefixes.status === "loading" && <p role="status" className="loading-line">Loading this scope's intended prefixes…</p>}
    {prefixes.status === "error" && <ErrorNotice error={prefixes.error} />}
    {!hasRole("Operator") && <p className="notice">Prefix editing is available to domain Operators.</p>}
    {prefixes.status === "ready" && <>{!prefixes.data.length ? <p>No intended prefixes exist in this scope. Child creation requires an existing parent.</p> : <label className="field-label">Selected prefix / child parent<select value={prefixId} onChange={(event) => { setPrefixId(event.target.value); setSaved(null); }}>{prefixes.data.map((prefix) => <option key={prefix.id} value={prefix.id}>{prefix.cidr} · {prefix.owner || "Owner unspecified"}</option>)}</select></label>}</>}
    {prefixId && context.status === "loading" && <p role="status">Loading the prefix and current intended-ledger revision…</p>}
    {prefixId && context.status === "error" && <ErrorNotice error={context.error} />}
    {prefixId && context.status === "ready" && context.data.prefix.id === prefixId && context.data.scope.id === scopeId && hasRole("Operator") && <PrefixCommandForm key={`${prefixId}:${revision}:${context.data.baseline_version}`} context={context.data} onSaved={(result) => { setSaved(result); setPrefixId(result.prefix.id); setRevision((value) => value + 1); onChanged?.(); }} />}
  </section>;
}
