import { useEffect, useState } from "react";
import { ApiError } from "./api";
import { actOnServiceNowIncident, loadServiceNowIncident } from "./workflowApi";
import type { ServiceNowIncidentView } from "./workflowApi";

function readableError(error: unknown): string {
  if (error instanceof ApiError) return `${error.message} (${error.code}${error.requestId ? `; request ${error.requestId}` : ""})`;
  return error instanceof Error ? error.message : "The request failed.";
}

function uncertain(error: unknown) {
  return !(error instanceof ApiError) || ["REQUEST_TIMEOUT", "CONNECTION_FAILED", "INVALID_RESPONSE", "INTERNAL_ERROR"].includes(error.code);
}

/** Opt-in external sandbox Incident for one simulated handoff. Separate from the simulated ticket outcome. */
export default function ServiceNowIncident({ handoffId, actorId, mayOperate, locked }: {
  handoffId: string; actorId: string; mayOperate: boolean; locked: boolean;
}) {
  const [view, setView] = useState<ServiceNowIncidentView | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  // Kept after an uncertain send so the exact retry replays instead of creating another Incident.
  const [sendKey, setSendKey] = useState<{ key: string; version: number } | null>(null);
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setView(null);
    loadServiceNowIncident(handoffId, controller.signal)
      .then(value => { if (!controller.signal.aborted) setView(value); })
      .catch((failure: unknown) => { if (!controller.signal.aborted) setError(`Sandbox Incident failed to load. ${readableError(failure)}`); });
    return () => controller.abort();
  }, [handoffId, revision]);

  useEffect(() => { setSendKey(null); setError(""); setMessage(""); }, [handoffId]);

  async function act(action: "send" | "lookup" | "refresh") {
    if (!view || busy) return;
    const exact = action === "send" ? sendKey ?? { key: crypto.randomUUID(), version: view.record?.version ?? 0 } : null;
    if (exact) setSendKey(exact);
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await actOnServiceNowIncident(handoffId, action, {
        actor_id: actorId, expected_version: exact?.version ?? view.record?.version ?? 0,
        ...(exact ? { idempotency_key: exact.key } : {}),
      }, new AbortController().signal);
      setView(result);
      setSendKey(null);
      setMessage(`Manual ${action} recorded. External state is shown below as observed.`);
    } catch (failure: unknown) {
      if (!(action === "send" && uncertain(failure))) setSendKey(null);
      setError(`Sandbox Incident ${action} failed. ${readableError(failure)}${action === "send" && uncertain(failure)
        ? " The send outcome is uncertain; retry the exact send (it replays without another POST) or reload and run a correlation lookup." : ""}`);
      setRevision(value => value + 1);
    } finally {
      setBusy(false);
    }
  }

  const record = view?.record ?? null;
  const disabled = locked || busy || !mayOperate || !view;
  return <div className="notice">
    <h3>External ServiceNow sandbox Incident{record ? ` · ${record.state}` : " · not sent"}</h3>
    {!view && !error && <p className="quiet">Loading sandbox Incident…</p>}
    {view && <>
      <p className="quiet">{view.label} Local request {view.source_request_state}; simulated handoff {view.simulated_handoff_state}; provisioning {view.provisioning_status.replace("_", " ")}. The external Incident never decides the local ledger or the simulated outcome.</p>
      <dl className="facts">
        <dt>Sandbox configuration</dt><dd>{view.configuration.status}{view.configuration.instance_host ? ` · ${view.configuration.instance_host}` : ""}
          {view.configuration.domain_allowed === false ? " · this domain is not the configured sandbox domain" : ""}
          {view.configuration.problems.length > 0 ? ` · check server variables: ${view.configuration.problems.join(", ")}` : ""}</dd>
        {record && <>
          <dt>External outcome</dt><dd>{record.state} · {record.state_reason} · send {record.send_count} · record v{record.version}</dd>
          <dt>Incident</dt><dd>{record.number ?? "none recorded"}{record.sys_id ? <> · <code>{record.sys_id}</code></> : ""}</dd>
          <dt>Assignment group / assignee</dt><dd>{record.assignment_group ? <code>{record.assignment_group}</code> : "none"} · {record.assigned_to ? <code>{record.assigned_to}</code> : "none"}
            {record.assignment_matches_configuration === true ? " · matches the configured Network team and test assignee" : ""}
            {record.assignment_matches_configuration === false ? " · differs from the configured Network team or test assignee" : ""}</dd>
          <dt>External state</dt><dd>{record.external_state ? `${record.external_state_label ?? "code"} (${record.external_state})` : "not observed"}{record.observed_at ? ` · observed ${record.observed_at}` : ""}</dd>
          <dt>Sent</dt><dd>{record.sent_at} to {record.instance_host}</dd>
          {record.duplicate_numbers.length > 0 && <><dt>Owner review</dt><dd>Matching Incidents {record.duplicate_numbers.join(", ")}. Resolve the duplicates in ServiceNow, then run a lookup.</dd></>}
          {record.last_error_code && <><dt>Last failure</dt><dd>{record.last_error_code} · {record.last_error_at}</dd></>}
        </>}
      </dl>
      {record?.state === "unknown" && <p>The send outcome is unknown. No new send is allowed until a manual correlation lookup finds no exact match.</p>}
      {record?.state === "failed" && <p>ServiceNow rejected the send. Run a correlation lookup before any new send.</p>}
      {message && <p role="status">{message}</p>}
      <fieldset disabled={disabled}><legend>Manual sandbox actions · no automatic retry</legend>
        <div className="pagination">
          <button disabled={disabled || (!view.send_allowed && !sendKey)} onClick={() => void act("send")}>{sendKey ? "Retry exact send" : "Send one sandbox Incident"}</button>
          <button className="secondary" disabled={disabled || !view.lookup_allowed} onClick={() => void act("lookup")}>Look up by correlation</button>
          <button className="secondary" disabled={disabled || !view.refresh_allowed} onClick={() => void act("refresh")}>Refresh external state</button>
        </div>
        {!view.send_allowed && view.send_block_reason && <p className="quiet">Send blocked: {view.send_block_reason}.</p>}
        {!view.lookup_allowed && view.lookup_block_reason && record && <p className="quiet">Lookup unavailable: {view.lookup_block_reason}.</p>}
      </fieldset>
      {!mayOperate && <p>An Operator must authenticate for sandbox Incident actions.</p>}
      {view.events.length > 0 && <details><summary>Sandbox Incident history ({view.events.length})</summary>
        <ul className="plain-list">{view.events.map((event, index) => <li key={`${event.occurred_at}-${index}`}>{event.action} · {event.outcome}{event.result ? ` · ${event.result}` : ""} · {event.occurred_at}</li>)}</ul>
      </details>}
    </>}
    {error && <p className="notice error" role="alert">{error}</p>}
  </div>;
}
