import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { request } from "./api";
import type { Page, Scope } from "./api";
import type { Finding, RunSummary, SavedRun } from "./firstPathApi";

interface Metric {
  pool_id: string; scope_id: string; scope_name: string; cidr: string; name: string; capacity: string;
  current: { status: string; occupied_addresses: string | null; utilization_pct: number | null; reason?: string };
  p95: { status: string; occupied_addresses: string | null; utilization_pct: number | null; eligible_samples: number; required_samples: number; window_start_at: string; window_end_at: string; reason?: string };
  forecast: { status: string; days_to_full: number | null; estimated_full_at: string | null; slope_addresses_per_day: number | null; baseline_addresses: number | string | null; complete_days: number; reason?: string };
  history: { at: string; occupied_addresses: string | null }[];
  limitations: string[];
}
interface CapacityRun extends SavedRun { calculations?: Metric[]; candidate_space?: unknown }
interface Actor { id: string; name?: string; role: string; team: string }
interface Preset { name: string; run_id: string; filters: Record<string, string>; columns: string[]; revision: string }
interface Comparison { before_run_id: string; after_run_id: string; limitations: string[]; items: { subject: Finding["subject"]; rule_id: string; transition: string; before: Finding | null; after: Finding | null }[] }
const columns = ["run_id", "rule_id", "scope_id", "subject", "severity", "evidence_state", "explanation", "proposed_action"];

function History({ metric }: { metric: Metric }) {
  const capacity = Number(metric.capacity);
  if (!metric.history.length || !Number.isFinite(capacity) || capacity <= 0) return <p>No eligible history available.</p>;
  // Render the saved values only. Gaps break the path instead of becoming zero.
  let open = false;
  const path = metric.history.map((sample, index) => {
    if (sample.occupied_addresses === null) { open = false; return ""; }
    const x = 30 + index * 660 / Math.max(1, metric.history.length - 1);
    const y = 150 - Number(sample.occupied_addresses) * 130 / capacity;
    const segment = `${open ? "L" : "M"}${x},${y}`;
    open = true;
    return segment;
  }).join(" ");
  return <figure className="capacity-history"><svg viewBox="0 0 720 185" role="img" aria-label={`Saved hourly occupied addresses for ${metric.name}; gaps mean unknown`}>
    <line x1="30" y1="20" x2="690" y2="20" stroke="currentColor" opacity=".15" />
    <line x1="30" y1="150" x2="690" y2="150" stroke="currentColor" opacity=".25" />
    <path d={path} fill="none" stroke="currentColor" strokeWidth="2" />
    <text x="30" y="175">Window start</text><text x="570" y="175">Last hourly sample</text>
  </svg><figcaption>Saved hourly lease occupancy; {metric.p95.eligible_samples} / {metric.p95.required_samples} eligible samples. Gaps are unknown. Top line is configured capacity.</figcaption></figure>;
}

export default function CapacityReports({ scopes }: { scopes: Scope[] }) {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [runTotal, setRunTotal] = useState(0);
  const [run, setRun] = useState<CapacityRun | null>(null);
  const [actors, setActors] = useState<Actor[]>([]);
  const [actor, setActor] = useState("demo-requester");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [filters, setFilters] = useState({ scope_id: "", rule_id: "", severity: "", evidence_state: "" });
  const [before, setBefore] = useState("");
  const [after, setAfter] = useState("");
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [preset, setPreset] = useState<Preset | null>(null);
  const [name, setName] = useState("Reconciliation review");
  const [reason, setReason] = useState("");
  const [selectedColumns, setSelectedColumns] = useState(columns);

  async function loadRuns(append = false) {
    setBusy(true); setError("");
    try {
      const data = await request<Page<RunSummary>>(`/api/runs?limit=50&offset=${append ? runs.length : 0}`, new AbortController().signal);
      setRuns(append ? [...runs, ...data.items] : data.items); setRunTotal(data.total);
    } catch (error) { setError(error instanceof Error ? error.message : "Could not load saved runs."); }
    finally { setBusy(false); }
  }
  useEffect(() => {
    const controller = new AbortController();
    Promise.all([request<Page<RunSummary>>("/api/runs?limit=50", controller.signal), request<Actor[]>("/api/actors", controller.signal), request<Preset | null>("/api/report-preset", controller.signal)])
      .then(([page, identities, saved]) => { if (!controller.signal.aborted) { setRuns(page.items); setRunTotal(page.total); setActors(identities); setPreset(saved); } })
      .catch((error: unknown) => { if (!controller.signal.aborted) setError(error instanceof Error ? error.message : "Could not load reporting data."); });
    return () => controller.abort();
  }, []);
  async function selectRun(id: string) {
    setBusy(true); setError(""); setNotice("");
    try { setRun(await request<CapacityRun>(`/api/runs/${id}`, new AbortController().signal)); }
    catch (error) { setError(error instanceof Error ? error.message : "Could not load this run."); }
    finally { setBusy(false); }
  }
  async function compare() {
    setBusy(true); setError("");
    try { setComparison(await request<Comparison>(`/api/run-comparison?before_run_id=${before}&after_run_id=${after}`, new AbortController().signal)); }
    catch (error) { setError(error instanceof Error ? error.message : "Comparison failed."); }
    finally { setBusy(false); }
  }
  async function savePreset(event: FormEvent) {
    event.preventDefault(); if (!run) return;
    setBusy(true); setError(""); setNotice("");
    try {
      const saved = await request<Preset>("/api/report-preset", new AbortController().signal, false, { method: "POST", body: JSON.stringify({ actor_id: actor, reason, name, run_id: run.id, filters, columns: selectedColumns }) });
      setPreset(saved); setNotice("Report preset saved with this run, filters and columns.");
    } catch (error) { setError(error instanceof Error ? error.message : "Preset save failed."); }
    finally { setBusy(false); }
  }
  async function reloadPreset() {
    setBusy(true); setError(""); setNotice("");
    try {
      setPreset(await request<Preset | null>("/api/report-preset", new AbortController().signal));
      setNotice("Saved preset reloaded. Review its run, filters and columns before exporting.");
    } catch (error) { setError(error instanceof Error ? error.message : "Could not reload the saved preset."); }
    finally { setBusy(false); }
  }
  async function downloadPreset() {
    if (!preset) return;
    setBusy(true); setError(""); setNotice("");
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(`/api/report-preset/export?revision=${preset.revision}`, {
        signal: controller.signal, headers: { Accept: "text/csv" },
      });
      if (!response.ok) {
        const body = response.headers.get("content-type")?.includes("application/json") ? await response.json() : null;
        throw new Error(body?.error?.message ?? `Export failed (HTTP ${response.status}).`);
      }
      if (!response.headers.get("content-type")?.includes("text/csv") || response.headers.get("X-Preset-Revision") !== preset.revision) {
        throw new Error("The export did not match the displayed preset. Reload the saved preset and retry.");
      }
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url; link.download = "ipam-findings.csv";
      document.body.appendChild(link); link.click(); link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setNotice("CSV download requested for the displayed preset.");
    } catch (error) {
      setError(controller.signal.aborted ? "Export timed out after 12 seconds. Retry the displayed preset." : error instanceof Error ? error.message : "Could not download the saved preset.");
    } finally { window.clearTimeout(timeout); setBusy(false); }
  }
  const visibleMetrics = (run?.calculations ?? []).filter((metric) => !filters.scope_id || metric.scope_id === filters.scope_id);
  const exportParams = new URLSearchParams(Object.entries(filters).filter(([, value]) => value));
  return <section aria-labelledby="capacity-heading">
    <div className="page-heading"><div><p className="eyebrow">Saved calculations</p><h1 id="capacity-heading">Capacity and reports</h1><p className="intro">Inspect saved occupancy, compare two runs, and export the evidence you reviewed.</p></div><button className="secondary" disabled={busy} onClick={() => { void loadRuns(); }}>Reload run list</button></div>
    <div className="evidence-banner"><strong>Synthetic lease occupancy</strong><span>Hourly samples approximate the source history. Lease counts do not measure traffic, and candidate space is not proven reclaimable.</span></div>
    {error && <div className="notice error" role="alert"><p>{error}</p><p>Previously loaded results remain pinned to their displayed IDs and times.</p></div>}
    {notice && <p className="notice" role="status">{notice}</p>}
    <label className="report-run-select">Saved run<select disabled={busy} value={run?.id ?? ""} onChange={(event) => { if (event.target.value) void selectRun(event.target.value); }}><option value="">Select a saved run</option>{runs.map((item) => <option key={item.id} value={item.id}>{item.created_at} · {item.id}</option>)}</select></label>
    {runs.length < runTotal && <button className="text-button" disabled={busy} onClick={() => { void loadRuns(true); }}>Load older runs ({runs.length} of {runTotal})</button>}
    {!runs.length && <p className="notice">No runs loaded. Import sources and compute a run in Source evidence, then reload this list.</p>}
    {run && <>
      <dl className="facts run-identity"><dt>Pinned run</dt><dd><code>{run.id}</code></dd><dt>Saved at</dt><dd>{run.created_at}</dd><dt>Demo clock</dt><dd>{run.demo_clock_at}</dd><dt>Ledger revision</dt><dd>{run.ledger_version}</dd></dl>
      <div className="filters"><label>Scope<select value={filters.scope_id} onChange={(event) => setFilters({ ...filters, scope_id: event.target.value })}><option value="">All scopes</option>{scopes.map((scope) => <option key={scope.id} value={scope.id}>{scope.name} · {scope.domain}</option>)}</select></label>
        <label>Report rule<select value={filters.rule_id} onChange={(event) => setFilters({ ...filters, rule_id: event.target.value })}><option value="">All rules</option>{[...new Set(run.findings.map((finding) => finding.rule_id))].sort().map((id) => <option key={id}>{id}</option>)}</select></label>
        <label>Report evidence state<select value={filters.evidence_state} onChange={(event) => setFilters({ ...filters, evidence_state: event.target.value })}><option value="">All states</option>{["anomalous", "healthy", "unknown", "not_applicable"].map((state) => <option key={state}>{state}</option>)}</select></label>
        <label>Report severity<select value={filters.severity} onChange={(event) => setFilters({ ...filters, severity: event.target.value })}><option value="">All severities</option>{["critical", "high", "warning"].map((severity) => <option key={severity}>{severity}</option>)}</select></label>
      </div>
      <p className="quiet">Scope filters capacity and exported findings. Rule, state and severity filter report findings only.</p>
      {!visibleMetrics.length && <p className="notice">This saved run has no capacity results for the selected scope. Older Stage 2 runs retain their original findings.</p>}
      {visibleMetrics.map((metric) => <article className="inventory-panel capacity-card" key={metric.pool_id}><h2>{metric.name}</h2><p>{metric.scope_name} · <code>{metric.cidr}</code> · capacity {metric.capacity} assignable addresses</p>
        <dl className="facts"><dt>Current occupancy</dt><dd>{metric.current.occupied_addresses ?? "Unknown"} · {metric.current.status}{metric.current.utilization_pct !== null && ` · ${metric.current.utilization_pct.toFixed(1)}%`} {metric.current.reason}</dd>
          <dt>30-day p95</dt><dd>{metric.p95.occupied_addresses ?? "Unknown"} · {metric.p95.status}{metric.p95.utilization_pct !== null && ` · ${metric.p95.utilization_pct.toFixed(1)}%`} {metric.p95.reason}</dd>
          <dt>History window</dt><dd>{metric.p95.window_start_at} → {metric.p95.window_end_at} (exclusive end)</dd>
          <dt>Forecast</dt><dd>{metric.forecast.status.replaceAll("_", " ")}{metric.forecast.days_to_full !== null && ` · ${metric.forecast.days_to_full.toFixed(1)} days to capacity`}{metric.forecast.estimated_full_at && ` · ${metric.forecast.estimated_full_at}`}. {metric.forecast.reason}</dd>
          <dt>Fit basis</dt><dd>{metric.forecast.complete_days} complete days · slope {metric.forecast.slope_addresses_per_day?.toFixed(3) ?? "unavailable"} addresses/day · latest daily p95 {metric.forecast.baseline_addresses ?? "unavailable"}</dd></dl>
        <History metric={metric} /><details><summary>Saved calculation and evidence</summary><pre className="json-value">{JSON.stringify(metric, null, 2)}</pre></details><ul>{metric.limitations.map((text, index) => <li key={index}>{text}</li>)}</ul>
      </article>)}
      {run.candidate_space !== undefined && <details className="inventory-panel"><summary>Addresses in candidate pools, by scope</summary><pre className="json-value">{JSON.stringify(run.candidate_space, null, 2)}</pre><p>This is candidate pool space, not released or proven recoverable addresses.</p></details>}
      <p><a href={`/api/runs/${run.id}/export?${exportParams}`}>Export pinned findings and calculations (JSON)</a></p>
      <form className="inventory-panel report-preset" onSubmit={(event) => { void savePreset(event); }}><h2>One report preset</h2><div className="filters"><label>Demo actor<select value={actor} onChange={(event) => setActor(event.target.value)}>{actors.map((item) => <option key={item.id} value={item.id}>{item.id} · {item.team}</option>)}</select></label><label>Name<input maxLength={200} required value={name} onChange={(event) => setName(event.target.value)} /></label><label>Reason<input maxLength={200} required value={reason} onChange={(event) => setReason(event.target.value)} /></label></div><fieldset><legend>CSV columns</legend><div className="column-options">{columns.map((column) => <label key={column}><input type="checkbox" checked={selectedColumns.includes(column)} onChange={(event) => setSelectedColumns(event.target.checked ? [...selectedColumns, column] : selectedColumns.filter((value) => value !== column))} />{column}</label>)}</div></fieldset><button disabled={busy || !selectedColumns.length}>Save current run and filters</button></form>
    </>}
    {preset && <div className="notice"><strong>Saved preset: {preset.name}</strong><p>Pinned run <code>{preset.run_id}</code>; filters <code>{JSON.stringify(preset.filters)}</code></p><p>Columns: {preset.columns.join(", ")}</p><button disabled={busy} onClick={() => { void downloadPreset(); }}>Export displayed preset (CSV)</button> <button className="secondary" disabled={busy} onClick={() => { void reloadPreset(); }}>Reload saved preset</button></div>}
    <section className="path-step"><h2>Compare two runs</h2><div className="filters"><label>Earlier run<select value={before} onChange={(event) => setBefore(event.target.value)}><option value="">Select earlier run</option>{runs.map((item) => <option key={item.id} value={item.id}>{item.created_at} · {item.id}</option>)}</select></label><label>Later run<select value={after} onChange={(event) => setAfter(event.target.value)}><option value="">Select later run</option>{runs.map((item) => <option key={item.id} value={item.id}>{item.created_at} · {item.id}</option>)}</select></label><button disabled={busy || !before || !after || before === after} onClick={() => { void compare(); }}>Compare saved evidence</button></div>
      {comparison && <><p>Compared <code>{comparison.before_run_id}</code> → <code>{comparison.after_run_id}</code></p><ul>{comparison.limitations.map((text) => <li key={text}>{text}</li>)}</ul><div className="table-scroll"><table><thead><tr><th>Subject / rule</th><th>Earlier</th><th>Later</th><th>Transition</th></tr></thead><tbody>{comparison.items.map((item) => <tr key={`${item.rule_id}-${item.subject.scope_id}-${item.subject.id}`}><td>{item.subject.scope_name} · {item.subject.cidr}<div className="quiet">{item.rule_id}</div></td><td>{item.before?.evidence_state ?? "Not evaluated"}</td><td>{item.after?.evidence_state ?? "Not evaluated"}</td><td>{item.transition.replaceAll("_", " ")}</td></tr>)}</tbody></table></div></>}
    </section>
  </section>;
}
