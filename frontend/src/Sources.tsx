import { useEffect, useState } from "react";
import { ApiError } from "./api";
import { loadEvidenceSources } from "./sourcesApi";
import type { EvidenceRow, EvidenceSources, IntegrationProfile, Mechanism, MechanismScope } from "./sourcesApi";

type Load = { data: EvidenceSources | null; error: ApiError | null; loading: boolean };
const asError = (error: unknown) => error instanceof ApiError ? error : new ApiError("The evidence-source response could not be read. Refresh to request it again.", "INVALID_RESPONSE");
const chipTone: Record<string, string> = { fresh: "good", complete: "good", stale: "warn", partial: "warn", not_applicable: "muted", unknown: "warn" };

function Chip({ value, label }: { value: string; label?: string }) {
  return <span className={`source-chip tone-${chipTone[value] ?? "muted"}`}>{label ?? value.replaceAll("_", " ")}</span>;
}

function EvidenceLine({ item }: { item: EvidenceRow }) {
  return <li className="source-evidence">
    <div className="source-chips"><Chip value={item.freshness} /><Chip value={item.completeness} /><Chip value={item.application_status === "partial" ? "partial" : "muted"} label={`import ${item.application_status}`} />{item.rejected_rows > 0 && <Chip value="partial" label={`${item.rejected_rows} rejected`} />}</div>
    <div className="table-secondary"><code>{item.source_id}</code> · run <code>{item.source_run_id}</code> · {item.authority} ({item.authority_status})</div>
    <div className="table-secondary">{item.receipt ? <>Ingested <time dateTime={item.receipt.ingested_at}>{item.receipt.ingested_at}</time> · {item.receipt.accepted_rows} of {item.receipt.input_rows} batch rows accepted</> : "Saved receipt not available in this domain"}</div>
    <div className="table-secondary">Coverage {item.window_start_at ?? "not recorded"}{item.window_end_at ? ` → ${item.window_end_at}` : ""} · {item.in_latest_run ? "used by the latest saved run" : "not in the latest saved run"}</div>
  </li>;
}

function ScopeRow({ mechanism, scope }: { mechanism: Mechanism; scope: MechanismScope }) {
  if (mechanism.implementation === "seeded_inventory") {
    return <li className={`source-scope scope-${scope.state}`}>
      <div className="source-scope-head"><strong>{scope.scope_name}</strong><Chip value={scope.state === "loaded" ? "complete" : "unknown"} label={scope.state === "loaded" ? "baseline loaded" : "no intended rows"} /></div>
      {scope.counts && <div className="table-secondary">{scope.counts.prefixes} prefixes · {scope.counts.pools} pools · {scope.counts.allocations} intended assignments</div>}
      {scope.origins?.map(origin => <div className="table-secondary" key={`${origin.source_id}-${origin.source_run_id}`}><code>{origin.source_id ?? "unrecorded source"}</code> · {origin.rows} rows{origin.latest_ingested_at && <> · loaded <time dateTime={origin.latest_ingested_at}>{origin.latest_ingested_at}</time></>}</div>)}
      {scope.evidence.length > 0 && <ul className="plain-list">{scope.evidence.map(item => <li key={item.batch_id} className="table-secondary">Intended route policy <code>{item.source_id}</code> · {item.completeness} · {item.in_latest_run ? "used by the latest saved run" : "not in the latest saved run"}</li>)}</ul>}
      {scope.route_policy && !scope.evidence.length && <div className="table-secondary">Intended route policy: {scope.route_policy.in_latest_run ? `selected by the latest saved run (${scope.route_policy.latest_run_effective_complete ? "complete" : "incomplete"} for this scope)` : "not shown for this scope"}</div>}
    </li>;
  }
  return <li className={`source-scope scope-${scope.state}`}>
    <div className="source-scope-head"><strong>{scope.scope_name}</strong>{scope.state === "missing" && <Chip value="unknown" label="no selected source" />}</div>
    {scope.state === "missing" ? <p className="table-secondary">No selected synthetic source for this scope can be shown in this domain. No telemetry does not prove no usage.</p>
      : <ul className="plain-list">{scope.evidence.map(item => <EvidenceLine key={`${item.batch_id}-${item.scope_id}`} item={item} />)}</ul>}
  </li>;
}

function MechanismTile({ mechanism, profile }: { mechanism: Mechanism; profile?: IntegrationProfile }) {
  const summary = mechanism.summary;
  return <article className={`source-tile status-${mechanism.status}`} aria-labelledby={`source-${mechanism.id}`}>
    <span className="source-status">{mechanism.status_label}</span>
    <h3 id={`source-${mechanism.id}`}>{mechanism.name}</h3>
    <p className="source-establishes">{mechanism.establishes}</p>
    {mechanism.implementation_note && <p className="source-note">{mechanism.implementation_note}</p>}
    {summary && mechanism.implementation === "seeded_inventory" && <p className="source-summary">{summary.loaded} of {summary.scopes} scopes loaded</p>}
    {summary && mechanism.implementation !== "seeded_inventory" && <p className="source-summary">{summary.scopes - (summary.missing ?? 0)} of {summary.scopes} scopes covered · {summary.fresh} fresh · {summary.stale} stale · {summary.complete} complete · {summary.partial} partial</p>}
    {mechanism.scopes.length > 0 && <details className="source-scopes"><summary>Per-scope evidence ({mechanism.scopes.length})</summary><ul className="plain-list">{mechanism.scopes.map(scope => <ScopeRow key={scope.scope_id} mechanism={mechanism} scope={scope} />)}</ul></details>}
    {mechanism.status === "not_connected" && <p className="source-unlocks"><span>Would unlock</span> {mechanism.unlocks}</p>}
    {profile && <p className="source-note">DEMO-ONLY sample integration profile: <strong>{profile.profile}</strong> ({profile.version}) — {profile.status}.</p>}
  </article>;
}

export default function Sources({ active, onNavigate }: { active: boolean; onNavigate: (view: "inventory" | "first-path") => void }) {
  const [state, setState] = useState<Load>({ data: null, error: null, loading: true });
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    setState(current => ({ ...current, loading: true }));
    loadEvidenceSources(controller.signal)
      .then(data => { if (!controller.signal.aborted) setState({ data, error: null, loading: false }); })
      .catch((error: unknown) => { if (!controller.signal.aborted) setState(current => ({ data: current.data, error: asError(error), loading: false })); });
    return () => controller.abort();
  }, [active, revision]);

  const data = state.data;
  const count = (status: string) => data?.mechanisms.filter(item => item.status === status).length ?? 0;
  const run = data?.latest_run;
  const evidenced = count("loaded_synthetic_baseline") + count("imported_synthetic_evidence");
  const functionsPresent = data?.functions.available_now.filter(item => item.evidence_present).length ?? 0;
  const supporting = (data?.mechanisms ?? []).filter(item => item.implementation === "synthetic_dhcp_import" || item.implementation === "synthetic_routing_import").map(item => {
    const rows = item.scopes.flatMap(scope => scope.evidence);
    const ingested = rows.map(row => row.receipt?.ingested_at).filter((value): value is string => Boolean(value)).sort();
    return { id: item.id, label: item.implementation === "synthetic_dhcp_import" ? "Synthetic DHCP imports" : "Synthetic routing observations",
      status: item.status_label, rows: rows.length, latest: ingested[ingested.length - 1] };
  });

  return <div className="sources" aria-busy={state.loading}>
    <div className="page-heading">
      <div><p className="eyebrow">Dodona IPAM · domain {data?.domain ?? "selected"} · synthetic demo data</p><h1>Evidence sources</h1>
        <p className="intro">Dodona IPAM can be configured around up to twelve evidence mechanisms. It also works with fewer feeds, with correspondingly fewer evidence-backed functions.</p>
        {data && <p className="intro sources-now" role="status">In this domain, {evidenced} of {data.mechanisms.length} mechanisms have synthetic evidence ({count("loaded_synthetic_baseline")} loaded synthetic baseline, {count("imported_synthetic_evidence")} imported synthetic evidence); {count("not_connected")} not connected{count("no_permitted_evidence") > 0 && `; ${count("no_permitted_evidence")} with no permitted rows`}. {functionsPresent} of {data.functions.available_now.length} functions have their required sources present. No operator system is connected.</p>}</div>
      <button className="secondary" onClick={() => setRevision(value => value + 1)} disabled={state.loading}>{state.loading ? "Refreshing…" : "Refresh sources"}</button>
    </div>
    {state.error && <div className="notice error" role="alert"><h2>Evidence sources unavailable</h2><p>{state.error.message}</p><p className="diagnostic"><code>{state.error.code}</code>{state.error.requestId && <> · Request <code>{state.error.requestId}</code></>}</p>{data && <p>The last loaded overview remains below.</p>}<button className="secondary" onClick={() => setRevision(value => value + 1)}>Retry request</button></div>}
    {!data && state.loading && <div className="notice loading-line" role="status">Loading evidence sources…</div>}
    {data && <>
      <section className="sources-strip" aria-label="Evidence source status">
        <div className="strip-count status-loaded_synthetic_baseline"><span>{count("loaded_synthetic_baseline")}</span>Loaded synthetic baseline</div>
        <div className="strip-count status-imported_synthetic_evidence"><span>{count("imported_synthetic_evidence")}</span>Imported synthetic evidence</div>
        <div className="strip-count status-not_connected"><span>{count("not_connected")}</span>Not connected</div>
        {count("no_permitted_evidence") > 0 && <div className="strip-count status-no_permitted_evidence"><span>{count("no_permitted_evidence")}</span>No permitted rows in this domain</div>}
        <div className="strip-run">
          <p className="eyebrow">Latest saved run</p>
          {run ? <>
            <code>{run.id}</code>
            <p className="table-secondary">Created <time dateTime={run.created_at}>{run.created_at}</time> · demo clock <time dateTime={run.demo_clock_at}>{run.demo_clock_at}</time></p>
            <p className="strip-run-counts"><strong>{run.overview.anomalous}</strong> anomalous · {run.overview.healthy} healthy · {run.overview.unknown} unknown · {run.overview.not_applicable} not applicable</p>
            <button className="text-button" onClick={() => onNavigate("first-path")}>Open reconciliation</button>
          </> : <p className="table-secondary">No saved run is available for this domain yet.</p>}
        </div>
      </section>
      <p className="filter-help">Evaluated at the seeded demo clock <time>{data.evaluated_at ?? "not set"}</time>. Freshness and completeness are shown per source and scope.</p>

      <div className="source-planes">
        {data.planes.map(plane => <section className="source-plane" key={plane.id} aria-labelledby={`plane-${plane.id}`}>
          <div className="source-plane-head"><h2 id={`plane-${plane.id}`}>{plane.name}</h2><p className="quiet">{plane.question}</p></div>
          <div className="source-tiles">{data.mechanisms.filter(item => item.plane === plane.id).map(item =>
            <MechanismTile key={item.id} mechanism={item} profile={data.integration_profiles.find(profile => profile.mechanism_id === item.id)} />)}</div>
        </section>)}
      </div>

      <section className="source-functions" aria-labelledby="source-functions-heading">
        <h2 id="source-functions-heading">What this evidence supports</h2>
        <div className="source-functions-grid">
          <div><h3>Checks and source requirements</h3><ul className="plain-list">{data.functions.available_now.map(item => <li key={item.id} className="source-function">
            <Chip value={item.evidence_present ? "complete" : "unknown"} label={item.evidence_present ? "sources present" : "sources missing"} /> <strong>{item.name}</strong>
            <div className="table-secondary">Rules {item.rule_ids.join(", ")} · needs {item.requires.map(id => data.mechanisms.find(mechanism => mechanism.id === id)?.name ?? id).join(" + ")}{item.requires_route_policy && " + intended route policy"}</div>
            {item.route_policy_scopes && <div className="table-secondary">Intended route policy present for {item.route_policy_scopes.present} of {item.route_policy_scopes.scopes} scopes</div>}
          </li>)}</ul><button className="text-button" onClick={() => onNavigate("inventory")}>Open inventory</button></div>
          <div><h3>Next unlocks</h3><ul className="plain-list">{data.functions.next_unlocks.map(item => <li key={item.mechanism_id} className="source-function"><strong>{item.name}</strong><div className="table-secondary">{item.unlocks}</div></li>)}</ul></div>
        </div>
      </section>

      {data.integration_profiles.map(profile => <section className="source-profile" key={profile.id} aria-labelledby={`profile-${profile.id}`}>
        <div className="section-heading"><div><p className="eyebrow">Sample profile · not a live integration</p><h2 id={`profile-${profile.id}`}>EMS integration profile</h2></div><span className="source-status demo-only">DEMO-ONLY · no endpoint connected</span></div>
        <dl className="facts">
          <dt>Profile</dt><dd>{profile.profile}</dd>
          <dt>Version</dt><dd><code>{profile.version}</code></dd>
          <dt>Managed system</dt><dd>{profile.managed_system}</dd>
          <dt>Proposed interface</dt><dd>{profile.proposed_interface}</dd>
          <dt>Status</dt><dd>{profile.status}</dd>
          <dt>Last live read</dt><dd>{profile.last_live_read}</dd>
        </dl>
        <p className="quiet">{profile.note}</p>
        <div className="source-supporting">
          <h3>Supporting demo evidence</h3>
          <p className="quiet">From this demo's synthetic DHCP and routing pipeline, not from this profile. No EMS or CMTS data was acquired or used in any calculation.</p>
          <ul className="plain-list">
            {supporting.map(item => <li key={item.id}><strong>{item.label}</strong> · {item.status} · {item.rows} selected source/scope rows{item.latest ? <> · latest ingest <time dateTime={item.latest}>{item.latest}</time></> : " · no permitted receipt"}</li>)}
            <li><strong>Latest saved run</strong> · {run ? <>demo clock <time dateTime={run.demo_clock_at}>{run.demo_clock_at}</time> · <code>{run.id}</code></> : "none in this domain"}</li>
          </ul>
        </div>
      </section>)}

      <ul className="limitation-list">{data.limitations.map((item, index) => <li key={index}>{item}</li>)}</ul>
    </>}
  </div>;
}
