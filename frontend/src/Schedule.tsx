import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { ApiError, request } from "./api";
import type { DemoActor } from "./workflowApi";
import { loadSchedule, runSchedule, saveSchedule } from "./scheduleApi";
import type { ManualScheduleRun, ScheduleError, ScheduleRunResult, ScheduleStatus } from "./scheduleApi";

const ATTEMPT_KEY = "ipam.schedule.manual-attempt.v1";
const REFRESH_MS = 30000;
type ConfigurationDraft = { enabled: boolean; interval: string; version: number };

function readableError(error: unknown): string {
  if (error instanceof ApiError) return `${error.message} (${error.code}${error.requestId ? `; request ${error.requestId}` : ""})`;
  return error instanceof Error ? error.message : "The request failed.";
}

function readAttempt(): { payload: ManualScheduleRun | null; error: string } {
  try {
    const raw = sessionStorage.getItem(ATTEMPT_KEY);
    if (raw === null) return { payload: null, error: "" };
    const value = JSON.parse(raw) as Partial<ManualScheduleRun> | null;
    if (!value || typeof value !== "object" || Object.keys(value).sort().join(",") !== "actor_id,idempotency_key,reason"
      || typeof value.actor_id !== "string" || !value.actor_id.trim()
      || typeof value.reason !== "string" || !value.reason.trim() || value.reason.length > 500
      || typeof value.idempotency_key !== "string" || !value.idempotency_key.trim()) {
      throw new Error("The saved Run now request is unreadable; it has been preserved for recovery.");
    }
    return { payload: value as ManualScheduleRun, error: "" };
  } catch (error) {
    return { payload: null, error: `Run now is blocked because its saved retry request cannot be read. ${readableError(error)}` };
  }
}

function draftFrom(status: ScheduleStatus): ConfigurationDraft {
  return { enabled: status.enabled, interval: String(status.interval_hours), version: status.config_version };
}

function TimeValue({ value, empty }: { value: string | null; empty: string }) {
  return value ? <time dateTime={value}>{value}</time> : <>{empty}</>;
}

function StatusError({ title, error }: { title: string; error: ScheduleError }) {
  return <div className="notice error" role="alert"><strong>{title}</strong><p>{error.message}</p><p className="diagnostic"><code>{error.code}</code></p>
    {error.details && <details><summary>Recorded details</summary><pre>{JSON.stringify(error.details, null, 2)}</pre></details>}
  </div>;
}

export default function Schedule() {
  const [restored] = useState(readAttempt);
  const [attempt, setAttempt] = useState<ManualScheduleRun | null>(restored.payload);
  const [storageError, setStorageError] = useState(restored.error);
  const [status, setStatus] = useState<ScheduleStatus | null>(null);
  const [draft, setDraft] = useState<ConfigurationDraft | null>(null);
  const [actors, setActors] = useState<DemoActor[]>([]);
  const [actorId, setActorId] = useState(restored.payload?.actor_id ?? "");
  const [configReason, setConfigReason] = useState("");
  const [runReason, setRunReason] = useState(restored.payload?.reason ?? "");
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<"configuration" | "run" | null>(null);
  const [refreshError, setRefreshError] = useState("");
  const [actorError, setActorError] = useState("");
  const [actionError, setActionError] = useState("");
  const [message, setMessage] = useState("");
  const [result, setResult] = useState<ScheduleRunResult | null>(null);
  const operation = useRef<AbortController | null>(null);

  useEffect(() => () => operation.current?.abort(), []);

  useEffect(() => {
    const controller = new AbortController();
    let timer: number | undefined;
    async function refresh() {
      setLoading(true);
      try {
        const current = await loadSchedule(controller.signal);
        if (controller.signal.aborted) return;
        setStatus(current); setDraft(previous => previous ?? draftFrom(current)); setRefreshError("");
      } catch (error) {
        if (!controller.signal.aborted) setRefreshError(`Schedule refresh failed. Previously displayed status may be stale. ${readableError(error)}`);
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
          timer = window.setTimeout(() => { void refresh(); }, REFRESH_MS);
        }
      }
    }
    void refresh();
    return () => { controller.abort(); window.clearTimeout(timer); };
  }, [revision]);

  useEffect(() => {
    const controller = new AbortController();
    request<DemoActor[]>("/api/actors", controller.signal).then(items => {
      if (controller.signal.aborted) return;
      setActors(items); setActorError("");
      setActorId(previous => previous || items.find(item => item.permissions.includes("inventory_edit"))?.id || "");
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) setActorError(`Demo actors could not be loaded. ${readableError(error)}`);
    });
    return () => controller.abort();
  }, [revision]);

  const mayEdit = actors.find(actor => actor.id === actorId)?.permissions.includes("inventory_edit") ?? false;
  const configChanged = !!status && !!draft && status.config_version !== draft.version;

  async function configure(event: FormEvent) {
    event.preventDefault();
    if (operation.current || !draft || !mayEdit) return;
    const interval = Number(draft.interval);
    if (!Number.isInteger(interval) || interval < 1 || interval > 168 || !configReason.trim()) {
      setActionError("Enter a whole interval from 1 to 168 hours and a reason for the change."); return;
    }
    const controller = new AbortController();
    operation.current = controller; setBusy("configuration"); setActionError(""); setMessage("");
    try {
      const current = await saveSchedule({ actor_id: actorId, reason: configReason,
        expected_config_version: draft.version, enabled: draft.enabled, interval_hours: interval }, controller.signal);
      if (controller.signal.aborted) return;
      setStatus(current); setDraft(draftFrom(current)); setConfigReason("");
      setMessage(`Schedule configuration ${current.config_version} saved: ${current.enabled ? "enabled" : "disabled"}, every ${current.interval_hours} wall-clock hours.`);
    } catch (error) {
      if (!controller.signal.aborted) setActionError(`Configuration save is not confirmed. Refresh and review the saved configuration before retrying. ${readableError(error)}`);
    } finally {
      operation.current = null;
      if (!controller.signal.aborted) { setBusy(null); setRevision(value => value + 1); }
    }
  }

  function retryStorage() {
    const saved = readAttempt();
    setStorageError(saved.error);
    if (saved.payload) {
      setAttempt(saved.payload); setActorId(saved.payload.actor_id); setRunReason(saved.payload.reason);
    }
  }

  async function runNow(event: FormEvent) {
    event.preventDefault();
    if (operation.current || storageError) return;
    if (!attempt && (!mayEdit || !status?.eligibility.eligible || status.in_progress || !runReason.trim())) return;
    let payload = attempt;
    try {
      payload ??= { actor_id: actorId, reason: runReason, idempotency_key: crypto.randomUUID() };
      const saved = readAttempt();
      if (saved.error) throw new Error(saved.error);
      if (saved.payload && JSON.stringify(saved.payload) !== JSON.stringify(payload)) {
        throw new Error("A different Run now request is already saved in this tab. Reload its saved request before retrying.");
      }
      const serialized = JSON.stringify(payload);
      sessionStorage.setItem(ATTEMPT_KEY, serialized);
      if (sessionStorage.getItem(ATTEMPT_KEY) !== serialized) throw new Error("The retry request could not be saved.");
    } catch (error) {
      if (payload) setAttempt(payload);
      setStorageError(`No run was submitted. Run now requires a saved retry request in this tab. ${readableError(error)}`); return;
    }
    setAttempt(payload);
    const controller = new AbortController();
    operation.current = controller; setBusy("run"); setActionError(""); setMessage(""); setResult(null);
    try {
      const completed = await runSchedule(payload, controller.signal);
      if (controller.signal.aborted) return;
      setResult(completed);
      try {
        sessionStorage.removeItem(ATTEMPT_KEY);
        if (sessionStorage.getItem(ATTEMPT_KEY) !== null) throw new Error("The completed retry request remains saved.");
        setAttempt(null); setRunReason("");
      } catch (error) {
        setStorageError(`This run is confirmed below, but its saved retry request could not be cleared. A new operation is blocked. ${readableError(error)}`);
      }
    } catch (error) {
      if (!controller.signal.aborted) setActionError(`No saved result is confirmed by this response. Retry retains the exact actor, reason and operation key. ${readableError(error)}`);
    } finally {
      operation.current = null;
      if (!controller.signal.aborted) { setBusy(null); setRevision(value => value + 1); }
    }
  }

  return <section aria-labelledby="schedule-heading">
    <div className="page-heading"><div><p className="eyebrow">Evolving synthetic observations</p><h1 id="schedule-heading">Acquisition schedule</h1>
      <p className="intro">Advance the synthetic feed, import its observations and save a reconciliation result in one operation.</p></div>
      <button type="button" className="secondary" disabled={loading || !!busy} onClick={() => setRevision(value => value + 1)}>Refresh status</button></div>
    <div className="evidence-banner"><strong>Synthetic acquisition</strong><span>Wall time controls the schedule. Each committed cycle advances scenario time by six hours, regardless of the schedule interval. No live network discovery occurs.</span></div>
    {refreshError && <div className="notice error" role="alert">{refreshError}</div>}
    {actorError && <div className="notice error" role="alert">{actorError}</div>}
    {actionError && <div className="notice error" role="alert">{actionError}</div>}
    {message && <div className="notice" role="status">{message}</div>}
    {loading && !status && <p role="status">Loading the saved schedule…</p>}

    {status && <section className="inventory-panel" aria-labelledby="schedule-status-heading">
      <div className="section-heading"><h2 id="schedule-status-heading">Saved schedule and latest cycle</h2><span>{loading ? "Refreshing…" : "Refreshes every 30 seconds while open"}</span></div>
      <div className="detail-section"><dl className="facts">
        <dt>Automatic schedule</dt><dd>{status.enabled ? "Enabled" : "Disabled"} · every {status.interval_hours} wall-clock hours · configuration {status.config_version}</dd>
        <dt>Next due · wall time</dt><dd><TimeValue value={status.next_due_at} empty="No automatic attempt scheduled" /></dd>
        <dt>Last attempt · wall time</dt><dd><TimeValue value={status.last_attempt_at} empty="No recorded attempt" /></dd>
        <dt>Last success · wall time</dt><dd><TimeValue value={status.last_success_at} empty="No committed cycle recorded" /></dd>
        <dt>Last outcome</dt><dd>{status.last_outcome ?? "No recorded outcome"}{status.in_progress && " · acquisition or reconciliation in progress"}</dd>
        <dt>Scenario time</dt><dd><TimeValue value={status.demo_clock_at} empty="Unavailable" /></dd>
        <dt>Feed / cycle</dt><dd><code>{status.feed_version}</code> · cycle {status.cycle_index}<div><code>{status.cycle_id ?? "No advancing cycle recorded"}</code></div></dd>
        <dt>Saved run ID</dt><dd>{status.run_id ? <code>{status.run_id}</code> : "No acquisition run recorded"}</dd>
      </dl></div>
      {status.last_outcome === "partial" && <p className="run-warning">The last cycle committed with intentionally incomplete synthetic evidence. Inspect its saved run for partial and unknown results.</p>}
      {status.last_outcome === "busy" && <p className="run-warning">The last attempt was busy. It did not establish a new completed cycle; automatic retry uses the next due wall time.</p>}
      {status.last_outcome === "failed" && <p className="run-warning">The last attempt failed. The cycle and saved run shown above remain the previously committed result.</p>}
      {status.in_progress && <p className="panel-message" role="status">An operation is in progress. Status will refresh; a busy response is not a successful cycle.</p>}
      {!status.eligibility.eligible && <p className="run-warning">New acquisition is unavailable. Resolve the eligibility reason below before enabling the schedule or starting a new cycle.</p>}
      {status.eligibility.error && <StatusError title="Acquisition eligibility" error={status.eligibility.error} />}
      {status.last_error && <StatusError title="Last acquisition error" error={status.last_error} />}
      {status.timer_error && <StatusError title="Automatic timer error" error={status.timer_error} />}
    </section>}

    <section className="path-step" aria-labelledby="schedule-controls-heading"><h2 id="schedule-controls-heading">Schedule controls</h2>
      <div className="filters"><label>Named demo actor<select value={actorId} disabled={!!busy || !!attempt} onChange={event => setActorId(event.target.value)}>
        <option value="">Select an actor</option>{actors.map(actor => <option key={actor.id} value={actor.id}>{actor.name} · {actor.role} · {actor.team}</option>)}
      </select></label></div>
      <p className="filter-help">The server checks inventory editing permission. These are fixed demo identities, not a sign-in system.{!mayEdit && " Select an actor with inventory editing permission to change the schedule or start a new run."}</p>
      {draft && status && <form onSubmit={event => void configure(event)}>
        <fieldset className="inventory-form" disabled={!!busy || !mayEdit}><legend>Automatic acquisition</legend>
          <label className="field-label">Schedule state<select value={draft.enabled ? "enabled" : "disabled"} onChange={event => setDraft({ ...draft, enabled: event.target.value === "enabled" })}>
            <option value="disabled">Disabled</option><option value="enabled" disabled={!status.eligibility.eligible}>Enabled</option></select></label>
          <label className="field-label">Wall-clock interval in hours<input type="number" min={1} max={168} step={1} required value={draft.interval} onChange={event => setDraft({ ...draft, interval: event.target.value })} /></label>
          <label className="field-label">Configuration reason<input required maxLength={500} value={configReason} onChange={event => setConfigReason(event.target.value)} /></label>
          <p className="quiet">Default interval: six hours. This form reviews configuration {draft.version}. Saving does not advance scenario time.</p>
          {configChanged && <p className="run-warning" role="status">Configuration changed to version {status.config_version} after this form was loaded. Review the current saved settings before submitting.</p>}
          <div className="compute-actions"><button type="submit" disabled={configChanged || !configReason.trim() || (draft.enabled && !status.eligibility.eligible)}>{busy === "configuration" ? "Saving configuration…" : "Save schedule"}</button>
            <button type="button" className="secondary" disabled={loading || !!refreshError} onClick={() => { setDraft(draftFrom(status)); setConfigReason(""); setMessage("Form reloaded from the displayed saved configuration. Review before saving."); }}>Load saved settings into form</button></div>
        </fieldset>
      </form>}
    </section>

    <section className="path-step" aria-labelledby="schedule-run-heading"><h2 id="schedule-run-heading">Run now</h2>
      <p>An eligible manual run can advance the feed even while the automatic schedule is disabled. The reviewed feed ends at cycle 1460; exhaustion is reported visibly and never rewinds the cursor.</p>
      {storageError && <div className="notice error" role="alert"><p>{storageError}</p><button type="button" className="secondary" disabled={!!busy} onClick={retryStorage}>Reload saved retry request</button></div>}
      {attempt && <div className="notice" role="status"><strong>Run now request retained</strong><p>A new operation is blocked until this request returns a confirmed result. Retry sends the same request and can recover an earlier commit without advancing again.</p>
        <dl className="facts"><dt>Actor</dt><dd><code>{attempt.actor_id}</code></dd><dt>Reason</dt><dd>{attempt.reason}</dd><dt>Operation key</dt><dd><code>{attempt.idempotency_key}</code></dd></dl>
        <p className="quiet">The request is stored before submission so it can survive reloads in this tab. Storage errors block submission. Keep this tab open until the request is resolved.</p></div>}
      <form onSubmit={event => void runNow(event)}><div className="compute-actions">
        <label className="field-label">Run reason<input required maxLength={500} disabled={!!busy || !!attempt} value={attempt?.reason ?? runReason} onChange={event => setRunReason(event.target.value)} /></label>
        <button type="submit" disabled={!!busy || !!storageError || (!attempt && (loading || !!refreshError || !mayEdit || !status?.eligibility.eligible || !!status.in_progress || !runReason.trim()))}>
          {busy === "run" ? "Waiting for saved result…" : attempt ? "Retry exact Run now request" : "Run now"}</button>
      </div></form>
      {result && <div className={result.outcome === "partial" ? "notice run-warning" : "notice"} role="status"><h3>{result.replay ? "Saved operation recovered" : "Cycle committed"} · {result.outcome}</h3>
        <p>{result.replay ? "This response replays the earlier committed result; it did not advance the feed again." : "The server confirmed this cycle and its saved reconciliation result."}</p>
        {result.outcome === "partial" && <p>This committed cycle contains incomplete synthetic evidence. Its findings may be partial or unknown.</p>}
        <dl className="facts"><dt>Completed · wall time</dt><dd><TimeValue value={result.completed_at} empty="Unavailable" /></dd><dt>Scenario time</dt><dd><TimeValue value={result.demo_clock_at} empty="Unavailable" /></dd>
          <dt>Feed / cycle</dt><dd><code>{result.feed_version}</code> · {result.cycle_index} · <code>{result.cycle_id}</code></dd><dt>Saved run ID</dt><dd><code>{result.run_id}</code></dd><dt>Operation ID</dt><dd><code>{result.operation_id}</code></dd></dl>
      </div>}
    </section>
  </section>;
}
