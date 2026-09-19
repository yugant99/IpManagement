import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { ApiError, loadScopes, request } from "./api";
import type { Health, Origin, Page, Prefix, PrefixDetail, Scope } from "./api";
import FirstPath from "./FirstPath";
import CapacityReports from "./CapacityReports";
import InventoryEditor from "./InventoryEditor";
import Workflow from "./Workflow";

type Resource<T> = { status: "loading" } | { status: "ready"; data: T } | { status: "error"; error: ApiError };
type Bootstrap =
  | { status: "loading" }
  | { status: "ready"; health: Health; scopes: Scope[] }
  | { status: "not-ready"; health: Health }
  | { status: "error"; error: ApiError };

const PAGE_SIZE = 25;
const emptyFilters = { scope: "", family: "", query: "" };
const displayCount = (value: string) => value.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
const asError = (error: unknown) => error instanceof ApiError ? error : new ApiError("The inventory response could not be read. Retry to request it again.", "INVALID_RESPONSE");

function ErrorState({ error, onRetry }: { error: ApiError; onRetry: () => void }) {
  return (
    <div className="notice error" role="alert">
      <h2>Inventory request failed</h2>
      <p>{error.message}</p>
      <p className="diagnostic"><code>{error.code}</code>{error.requestId && <> · Request <code>{error.requestId}</code></>}</p>
      <button className="secondary" onClick={onRetry}>Retry request</button>
    </div>
  );
}

function Readiness({ health }: { health: Health }) {
  return (
    <details className="readiness">
      <summary>Readiness details</summary>
      <dl className="facts compact">
        <dt>API process</dt><dd>{health.process_ready ? "Ready" : "Unavailable"}</dd>
        <dt>Database schema</dt><dd>{health.schema_ready ? "Ready" : "Not ready"}</dd>
        <dt>Initialized inventory</dt><dd>{health.data_ready ? "Ready" : "Not ready"}</dd>
        <dt>Compiled UI assets</dt><dd>{health.static_ready ? "Available" : "Not available to API"}</dd>
        <dt>Schema version</dt><dd>{health.schema_version ?? "Not initialized"}</dd>
        <dt>Contract</dt><dd><code>{health.contract_revision}</code></dd>
      </dl>
    </details>
  );
}

function OriginDetails({ origin }: { origin: Origin }) {
  return (
    <details className="provenance">
      <summary>Source references</summary>
      <p className="quiet">Synthetic intended state. These records do not establish current network use.</p>
      <dl className="facts compact">
        <dt>Source</dt><dd><code>{origin.source_id}</code></dd>
        <dt>Source run</dt><dd><code>{origin.source_run_id}</code></dd>
        <dt>Source record</dt><dd><code>{origin.source_record_id}</code></dd>
        <dt>Source timestamp</dt><dd><time dateTime={origin.observed_at}>{origin.observed_at}</time></dd>
        <dt>Ingested at</dt><dd><time dateTime={origin.ingested_at}>{origin.ingested_at}</time></dd>
      </dl>
    </details>
  );
}

function DetailSection({ title, children }: { title: string; children: ReactNode }) {
  return <section className="detail-section"><h3>{title}</h3>{children}</section>;
}

function PrefixPanel({ id, onClose, onSelect }: { id: string; onClose: () => void; onSelect: (id: string) => void }) {
  const [result, setResult] = useState<Resource<PrefixDetail>>({ status: "loading" });
  const [revision, setRevision] = useState(0);
  const heading = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    setResult({ status: "loading" });
    request<PrefixDetail>(`/api/prefixes/${encodeURIComponent(id)}`, controller.signal)
      .then((data) => { if (!controller.signal.aborted) setResult({ status: "ready", data }); })
      .catch((error: unknown) => { if (!controller.signal.aborted) setResult({ status: "error", error: asError(error) }); });
    return () => controller.abort();
  }, [id, revision]);

  useEffect(() => {
    heading.current?.focus({ preventScroll: true });
    if (window.matchMedia("(max-width: 1100px)").matches) {
      heading.current?.scrollIntoView({ block: "start" });
    }
  }, []);

  return (
    <aside id="prefix-detail" className="detail-panel" aria-labelledby="detail-heading" aria-busy={result.status === "loading"}>
      <div className="section-heading">
        <p className="eyebrow">Prefix detail</p>
        <button className="text-button" onClick={onClose}>Close detail</button>
      </div>
      <h2 id="detail-heading" ref={heading} tabIndex={-1} className="detail-title">{result.status === "ready" ? result.data.cidr : "Selected prefix"}</h2>
      {result.status === "loading" && <p role="status" className="loading-line">Loading stored prefix details…</p>}
      {result.status === "error" && <ErrorState error={result.error} onRetry={() => setRevision((value) => value + 1)} />}
      {result.status === "ready" && <PrefixContents prefix={result.data} onSelect={onSelect} />}
    </aside>
  );
}

function PrefixContents({ prefix, onSelect }: { prefix: PrefixDetail; onSelect: (id: string) => void }) {
  return (
    <>
      <p className="detail-subtitle">{prefix.scope_name} · IPv{prefix.family} · Synthetic intended state</p>
      <DetailSection title="Intended inventory">
        <dl className="facts">
          <dt>Owner</dt><dd>{prefix.owner || "Not specified"}</dd>
          <dt>Purpose</dt><dd>{prefix.purpose || "Not specified"}</dd>
          <dt>Scope ID</dt><dd><code>{prefix.scope_id}</code></dd>
          <dt>Prefix ID</dt><dd><code>{prefix.id}</code></dd>
          <dt>Version</dt><dd>{prefix.version}</dd>
          <dt>Address-space size</dt><dd className="mono">{displayCount(prefix.address_count)} addresses</dd>
          <dt>Parent prefix</dt><dd>{prefix.parent_id ? <button className="text-button mono" onClick={() => onSelect(prefix.parent_id!)}>Open parent <span className="sr-only">{prefix.parent_id}</span></button> : "None recorded"}</dd>
          <dt>Tags</dt><dd>{prefix.tags.length ? <span className="tags">{prefix.tags.map((tag) => <span className="tag" key={tag}>{tag}</span>)}</span> : "None recorded"}</dd>
        </dl>
        <OriginDetails origin={prefix.origin} />
      </DetailSection>
      <DetailSection title="Custom metadata">
        {Object.keys(prefix.custom_fields).length ? <dl className="facts">{Object.entries(prefix.custom_fields).map(([key, value]) => <div className="fact-pair" key={key}><dt>{key}</dt><dd>{value || "Empty value"}</dd></div>)}</dl> : <p className="quiet">No custom metadata recorded.</p>}
      </DetailSection>
      <DetailSection title={`Pools (${prefix.pools.length})`}>
        <p className="quiet">Directly attached pools. Capacity describes configured ranges after exclusions, not unused space.</p>
        {!prefix.pools.length && <p>No pools attached to this prefix.</p>}
        {prefix.pools.map((pool) => (
          <article className="inventory-record" key={pool.id}>
            <h4>{pool.name}</h4>
            <dl className="facts compact">
              <dt>Management</dt><dd>{pool.management_mode === "dhcp" ? "DHCP" : "Static"}</dd>
              <dt>Authority</dt><dd>{pool.allocation_authority === "local" ? "Local intended ledger" : "External"}</dd>
              <dt>Configured capacity</dt><dd className="mono">{displayCount(pool.capacity)} addresses</dd>
              <dt>Version</dt><dd>{pool.pool_version}</dd>
              <dt>Pool ID</dt><dd><code>{pool.id}</code></dd>
              <dt>Ranges</dt><dd>{pool.ranges.length ? <ul className="plain-list">{pool.ranges.map((range) => <li className="mono" key={`${range.start}-${range.end}`}>{range.start} – {range.end}</li>)}</ul> : "None recorded"}</dd>
              <dt>Exclusions</dt><dd>{pool.exclusions.length ? <ul className="plain-list">{pool.exclusions.map((range) => <li className="mono" key={`${range.start}-${range.end}`}>{range.start} – {range.end}</li>)}</ul> : "None recorded"}</dd>
            </dl>
            <OriginDetails origin={pool.origin} />
          </article>
        ))}
      </DetailSection>
      <DetailSection title={`Intended IP assignments (${prefix.allocations.length})`}>
        <p className="quiet">Direct assignments to this prefix. Child-prefix assignments are shown in their own details.</p>
        {!prefix.allocations.length && <p>No intended IP assignments recorded for this prefix.</p>}
        {prefix.allocations.map((allocation) => (
          <article className="inventory-record" key={allocation.id}>
            <h4 className="mono">{allocation.address}</h4>
            <dl className="facts compact">
              <dt>Owner</dt><dd>{allocation.owner || "Not specified"}</dd>
              <dt>Purpose</dt><dd>{allocation.purpose || "Not specified"}</dd>
              <dt>Pool</dt><dd>{allocation.pool_id ? prefix.pools.find((pool) => pool.id === allocation.pool_id)?.name ?? allocation.pool_id : "No pool association"}</dd>
              <dt>Assignment ID</dt><dd><code>{allocation.id}</code></dd>
            </dl>
            <OriginDetails origin={allocation.origin} />
          </article>
        ))}
      </DetailSection>
    </>
  );
}

export default function App() {
  const [view, setView] = useState<"inventory" | "first-path" | "planning" | "capacity" | "workflow">("inventory");
  const [bootstrap, setBootstrap] = useState<Bootstrap>({ status: "loading" });
  const [evidenceScopes, setEvidenceScopes] = useState<Scope[] | null>(null);
  const [revision, setRevision] = useState(0);
  const [inventory, setInventory] = useState<Resource<Page<Prefix>>>({ status: "loading" });
  const [listRevision, setListRevision] = useState(0);
  const [filters, setFilters] = useState(emptyFilters);
  const [queryInput, setQueryInput] = useState("");
  const [offset, setOffset] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selectedButton = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setBootstrap({ status: "loading" });
    async function load() {
      try {
        const health = await request<Health>("/healthz", controller.signal, true);
        if (controller.signal.aborted) return;
        if (health.status !== "ready") {
          setBootstrap({ status: "not-ready", health });
          return;
        }
        const scopes = await loadScopes(controller.signal);
        if (!controller.signal.aborted) {
          setEvidenceScopes(scopes);
          setBootstrap({ status: "ready", health, scopes });
        }
      } catch (error) {
        if (!controller.signal.aborted) setBootstrap({ status: "error", error: asError(error) });
      }
    }
    void load();
    return () => controller.abort();
  }, [revision]);

  useEffect(() => {
    if (bootstrap.status !== "ready") return;
    const controller = new AbortController();
    const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(offset) });
    if (filters.scope) params.set("scope_id", filters.scope);
    if (filters.family) params.set("family", filters.family);
    if (filters.query) params.set("q", filters.query);
    setInventory({ status: "loading" });
    request<Page<Prefix>>(`/api/prefixes?${params}`, controller.signal)
      .then((data) => { if (!controller.signal.aborted) setInventory({ status: "ready", data }); })
      .catch((error: unknown) => { if (!controller.signal.aborted) setInventory({ status: "error", error: asError(error) }); });
    return () => controller.abort();
  }, [bootstrap, filters, offset, listRevision]);

  function refresh() {
    setSelectedId(null);
    setOffset(0);
    setInventory({ status: "loading" });
    setBootstrap({ status: "loading" });
    setRevision((value) => value + 1);
  }

  function updateFilters(next: typeof emptyFilters) {
    setSelectedId(null);
    setOffset(0);
    setInventory({ status: "loading" });
    setFilters(next);
  }

  function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    updateFilters({ ...filters, query: queryInput.trim() });
  }

  function clearFilters() {
    setQueryInput("");
    updateFilters(emptyFilters);
  }

  function changePage(next: number) {
    setSelectedId(null);
    setInventory({ status: "loading" });
    setOffset(next);
  }

  const activeScope = bootstrap.status === "ready" ? bootstrap.scopes.find((scope) => scope.id === filters.scope) : undefined;
  const hasFilters = Boolean(filters.scope || filters.family || filters.query);
  const health = bootstrap.status === "ready" || bootstrap.status === "not-ready" ? bootstrap.health : null;

  return (
    <>
      <a className="skip-link" href="#inventory-main">Skip to main content</a>
      <header className="app-header">
        <div className="brand"><span className="brand-mark" aria-hidden="true">IP</span><span>IP inventory</span><span className="demo-label">Synthetic demo</span></div>
        <span className="header-context">Scoped inventory · Evidence · Decisions</span>
      </header>
      <main id="inventory-main">
        <nav className="view-navigation" aria-label="Inventory views">
          <button className="secondary" aria-current={view === "inventory" ? "page" : undefined} onClick={() => setView("inventory")}>Intended inventory</button>
          <button className="secondary" aria-current={view === "first-path" ? "page" : undefined} onClick={() => setView("first-path")}>Source evidence</button>
          <button className="secondary" aria-current={view === "planning" ? "page" : undefined} onClick={() => setView("planning")}>Prefix planning</button>
          <button className="secondary" aria-current={view === "capacity" ? "page" : undefined} onClick={() => setView("capacity")}>Capacity and reports</button>
          <button className="secondary" aria-current={view === "workflow" ? "page" : undefined} onClick={() => setView("workflow")}>Requests and exceptions</button>
        </nav>
        <div hidden={view !== "inventory"}>
        <div className="page-heading">
          <div><p className="eyebrow">Intended network state</p><h1>Scoped inventory</h1><p className="intro">Browse IPv4 and IPv6 prefixes, their owners, and intended assignments.</p></div>
          <button className="secondary" onClick={refresh} disabled={bootstrap.status === "loading"}>Refresh inventory</button>
        </div>
        <div className="evidence-banner"><strong>Synthetic intended inventory</strong><span>Data comes from the local inventory API. No live discovery, traffic measurements, or current-use evidence is included.</span></div>
        </div>

        {bootstrap.status === "loading" && <div className="notice loading-line" role="status">Checking API readiness and loading network scopes…</div>}
        {bootstrap.status === "error" && <ErrorState error={bootstrap.error} onRetry={refresh} />}
        {bootstrap.status === "not-ready" && (
          <section className="notice setup" role="status">
            <p className="eyebrow">{bootstrap.health.status === "setup_needed" ? "Setup required" : "Inventory unavailable"}</p>
            <h2>{bootstrap.health.status === "setup_needed" ? "Initialize the synthetic inventory" : "The inventory store is not ready"}</h2>
            <p>{bootstrap.health.reason ?? "The API has not reported initialized inventory."}</p>
            {bootstrap.health.status === "setup_needed" && <><p>From the installed backend environment, use the same data directory as the server and run:</p><pre><code>python -m ipam_demo seed --scenario baseline</code></pre><p className="quiet">Setup is explicit. This page does not create or overwrite records.</p></>}
            {bootstrap.health.code && <p className="diagnostic"><code>{bootstrap.health.code}</code></p>}
            <button onClick={refresh}>Check readiness again</button>
          </section>
        )}

        {bootstrap.status === "ready" && (
          <div hidden={view !== "inventory"}>
            <form className="filters" onSubmit={search} aria-label="Filter intended prefixes">
              <label>Network scope<select value={filters.scope} onChange={(event) => updateFilters({ ...filters, scope: event.target.value })}><option value="">All network scopes</option>{bootstrap.scopes.map((scope) => <option value={scope.id} key={scope.id}>{scope.name} · {scope.namespace}</option>)}</select></label>
              <label>Address family<select value={filters.family} onChange={(event) => updateFilters({ ...filters, family: event.target.value })}><option value="">IPv4 and IPv6</option><option value="4">IPv4</option><option value="6">IPv6</option></select></label>
              <label className="search-field">Prefix, IP, owner, purpose or tag<input type="search" placeholder="Search inventory" value={queryInput} onChange={(event) => setQueryInput(event.target.value)} aria-describedby="search-help" /></label>
              <button type="submit">Search</button>
              {hasFilters && <button className="text-button" type="button" onClick={clearFilters}>Clear filters</button>}
            </form>
            <p className="filter-help" id="search-help">IP search returns containing prefixes; CIDR search returns intersecting prefixes. Matching is scoped.</p>
            {activeScope ? <div className="scope-context"><strong>{activeScope.name}</strong><span>Namespace: <code>{activeScope.namespace}</code></span><span>Domain: {activeScope.domain}</span><span>Region: {activeScope.region}</span><span className="scope-perimeter">Managed space: {activeScope.managed_cidrs.map((cidr, index) => <span key={cidr}>{index > 0 && ", "}<code>{cidr}</code></span>)}</span></div> : <p className="scope-context">The same private address may be valid in separate network scopes. Scope identifies the isolated network; it does not establish tenant security.</p>}
            {filters.query && <p className="applied-query">Applied search: <strong>{filters.query}</strong></p>}
            <div className={`inventory-layout${selectedId ? " has-detail" : ""}`}>
              <section className="inventory-panel" aria-labelledby="prefix-list-heading" aria-busy={inventory.status === "loading"}>
                <div className="section-heading"><h2 id="prefix-list-heading">Prefixes</h2><span className="quiet" role="status">{inventory.status === "ready" ? `${inventory.data.total} matching ${inventory.data.total === 1 ? "prefix" : "prefixes"}` : inventory.status === "loading" ? "Loading…" : "Request failed"}</span></div>
                {inventory.status === "loading" && <div className="table-loading" role="status"><span>Loading intended prefixes…</span><div className="skeleton-line" /><div className="skeleton-line" /><div className="skeleton-line" /></div>}
                {inventory.status === "error" && <ErrorState error={inventory.error} onRetry={inventory.error.code === "SETUP_NEEDED" ? refresh : () => setListRevision((value) => value + 1)} />}
                {inventory.status === "ready" && inventory.data.items.length === 0 && <div className="empty-state"><h3>{hasFilters ? "No prefixes match these filters" : "No prefixes on this page"}</h3><p>{hasFilters ? "Try a different scope, address family, or search." : "The API returned no prefixes for this page."}</p>{hasFilters ? <button className="secondary" onClick={clearFilters}>Clear filters</button> : <button className="secondary" onClick={refresh}>Reload inventory</button>}</div>}
                {inventory.status === "ready" && inventory.data.items.length > 0 && (
                  <>
                    <div className="table-scroll" tabIndex={0} role="region" aria-label="Prefix inventory table">
                      <table><caption className="sr-only">Synthetic intended prefixes. Open a prefix to view its stored details.</caption><thead><tr><th scope="col">Prefix / scope</th><th scope="col">Owner / purpose</th><th scope="col">Tags</th></tr></thead><tbody>{inventory.data.items.map((prefix) => <tr key={prefix.id} data-selected={selectedId === prefix.id}><td><button className="prefix-link mono" onClick={(event) => { selectedButton.current = event.currentTarget; setSelectedId(prefix.id); }} aria-expanded={selectedId === prefix.id} aria-controls={selectedId === prefix.id ? "prefix-detail" : undefined}>{prefix.cidr}<span className="sr-only"> in {prefix.scope_name}, open details</span></button><div className="table-secondary">{prefix.scope_name}<span className="family-label">IPv{prefix.family}</span></div></td><td><span className="owner">{prefix.owner || "Not specified"}</span><div className="table-secondary">{prefix.purpose || "No purpose recorded"}</div></td><td>{prefix.tags.length ? <span className="tags">{prefix.tags.map((tag) => <span className="tag" key={tag}>{tag}</span>)}</span> : <span className="quiet">None</span>}</td></tr>)}</tbody></table>
                    </div>
                    <nav className="pagination" aria-label="Inventory pages"><span className="quiet">{inventory.data.offset + 1}–{inventory.data.offset + inventory.data.items.length} of {inventory.data.total}</span><div><button className="secondary" disabled={offset === 0} onClick={() => changePage(Math.max(0, offset - PAGE_SIZE))}>Previous</button><button className="secondary" disabled={offset + inventory.data.items.length >= inventory.data.total} onClick={() => changePage(offset + PAGE_SIZE)}>Next</button></div></nav>
                  </>
                )}
              </section>
              {selectedId && <PrefixPanel key={selectedId} id={selectedId} onSelect={setSelectedId} onClose={() => { setSelectedId(null); selectedButton.current?.focus(); }} />}
            </div>
          </div>
        )}
        {evidenceScopes && <div hidden={view !== "first-path"}><FirstPath scopes={evidenceScopes} /></div>}
        {/* Preserve unresolved workflow retries after initial readiness, including refresh failures. */}
        {evidenceScopes && <div hidden={view !== "workflow" || bootstrap.status !== "ready"}><Workflow /></div>}
        {bootstrap.status === "ready" && <>
          <div hidden={view !== "planning"}><InventoryEditor scopes={bootstrap.scopes} onChanged={() => { setListRevision((value) => value + 1); setSelectedId(null); }} /></div>
          <div hidden={view !== "capacity"}><CapacityReports scopes={bootstrap.scopes} /></div>
        </>}
        {health && <Readiness health={health} />}
        <footer className="page-footer">Synthetic inventory and evidence · Saved calculations are pinned to their run · Data and readiness are reported by the API</footer>
      </main>
    </>
  );
}
