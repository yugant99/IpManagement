"""Pinned run comparison and one stored report preset; no new calculations."""

import csv
from datetime import datetime, timezone
from hashlib import sha256
from io import StringIO
import json
from uuid import uuid4

from .errors import AppError
from .reconciliation import get_run
from .rules import comparable_findings
from .workflow import audit_event, require_actor

COLUMNS = ("run_id", "rule_id", "scope_id", "subject", "severity", "evidence_state", "explanation", "proposed_action")
FILTERS = {"scope_id", "rule_id", "severity", "evidence_state", "family"}


def _validate_filters(filters):
    if not isinstance(filters, dict) or set(filters) - FILTERS or any(
            not isinstance(value, str) or len(value) > 200 for value in filters.values()):
        raise AppError("INVALID_INPUT", "Use scope_id, rule_id, severity, evidence_state and family string filters.", 422)
    if "family" in filters and filters["family"] not in {"", "4", "6"}:
        raise AppError("INVALID_INPUT", "Address family must be 4, 6 or empty.", 422)


def filtered_findings(run, filters):
    _validate_filters(filters)
    return [finding for finding in run["findings"] if all(
        not value or (str(finding["subject"].get("family")) if key == "family" else
                      finding["subject"].get(key) if key == "scope_id" else finding.get(key)) == value
        for key, value in filters.items())]


def project_run(run, scope_ids, *, domain, source_pairs=()):
    """Return a separately identified selected-domain projection of one immutable run."""
    allowed = set(scope_ids)
    pairs = set(source_pairs)
    local_sources = {"local-inventory", "local-inventory-correction", "local-demo-workflow"}
    def safe_source(source_id, scope_id):
        return (source_id, scope_id) in pairs or source_id in local_sources
    findings = []
    for item in run.get("findings", []):
        scope_id = item.get("subject", {}).get("scope_id")
        if scope_id not in allowed:
            continue
        origin = item.get("subject", {}).get("origin") or {}
        if origin.get("source_id") and not safe_source(origin["source_id"], scope_id):
            continue
        references = item.get("input_references", [])
        if not isinstance(references, list) or any(
                not isinstance(ref, dict) or not safe_source(ref.get("source_id"), scope_id) for ref in references):
            continue
        coverage = item.get("coverage", [])
        if any(not isinstance(ref, dict) or not safe_source(ref.get("source_id"), scope_id)
               for ref in coverage):
            continue
        findings.append(item)
    calculations = []
    for metric in run.get("calculations", []):
        scope_id = metric.get("scope_id")
        if scope_id not in allowed:
            continue
        references = metric.get("input_references", [])
        if not isinstance(references, list) or any(
                not isinstance(ref, dict) or not safe_source(ref.get("source_id"), scope_id) for ref in references):
            continue
        coverage = metric.get("coverage", [])
        if any(not isinstance(ref, dict) or not safe_source(ref.get("source_id"), scope_id)
               for ref in coverage):
            continue
        calculations.append(metric)
    selected_batches = []
    for batch in run.get("selected_batches", []):
        coverage = [item for item in batch.get("coverage", []) if item.get("scope_id") in allowed
                    and safe_source(batch.get("source_id"), item.get("scope_id"))]
        if coverage:
            selected_batches.append({key: batch[key] for key in ("id", "source_id", "source_run_id", "source_kind")
                                     if key in batch} | {"coverage": coverage})
    candidate_space = run.get("candidate_space", {})
    by_scope = candidate_space.get("by_scope", {})
    overview = {state: sum(item.get("evidence_state") == state for item in findings)
                for state in ("anomalous", "healthy", "unknown", "not_applicable")}
    overview["total"] = len(findings)
    projection = {key: value for key, value in run.items() if key != "ledger_version"}
    candidate_space = run.get("candidate_space", {})
    if not isinstance(candidate_space, dict):
        candidate_space = {}
    by_scope = candidate_space.get("by_scope", [])
    if not isinstance(by_scope, list):
        by_scope = []
    scoped_candidate_space = {**candidate_space,
                              "by_scope": [item for item in by_scope
                                           if isinstance(item, dict) and item.get("scope_id") in allowed]}
    return {**projection, "findings": findings, "calculations": calculations,
            "selected_batches": selected_batches, "overview": overview,
            "rule_ids": sorted({item.get("rule_id") for item in findings if item.get("rule_id")}),
            "candidate_space": scoped_candidate_space,
            "projection": {"kind": "selected_domain", "domain": domain, "scope_ids": sorted(allowed),
                           "source_run_id": run.get("id")}}


def _filtered_calculations(run, filters):
    family = filters.get("family", "")
    scope_id = filters.get("scope_id", "")
    return [metric for metric in run.get("calculations", [])
            if (not family or str(metric.get("family")) == family)
            and (not scope_id or metric.get("scope_id") == scope_id)]


def compare_runs(connection, before_id, after_id):
    before, after = get_run(connection, before_id), get_run(connection, after_id)
    return compare_runs_from_results(before, after)


def compare_runs_from_results(before, after):
    before_id, after_id = before["id"], after["id"]
    if before_id == after_id or before["created_at"] > after["created_at"]:
        raise AppError("INVALID_INPUT", "Select two different runs in chronological order.", 422)
    def indexed(run):
        return {(item["rule_id"], item["subject"]["scope_id"], item["subject"]["id"]): item
                for item in run["findings"]}
    left, right = indexed(before), indexed(after)
    changes = []
    for key in sorted(left.keys() | right.keys()):
        old, new = left.get(key), right.get(key)
        old_state, new_state = (old or {}).get("evidence_state"), (new or {}).get("evidence_state")
        transition = "unchanged" if old_state == new_state else "changed"
        if old_state == "anomalous":
            transition = "resolution_unknown" if not comparable_findings(old, new) else (
                "resolved_by_evidence" if new_state == "healthy" else (
                    "still_anomalous" if new_state == "anomalous" else "resolution_unknown"))
        elif new_state == "anomalous":
            transition = "new_anomaly"
        changes.append({"rule_id": key[0], "scope_id": key[1], "subject_id": key[2],
                        "subject": (new or old)["subject"], "before": old, "after": new,
                        "transition": transition})
    return {"before_run_id": before_id, "after_run_id": after_id,
            "before_clock": before["demo_clock_at"], "after_clock": after["demo_clock_at"],
            "synthetic": True, "items": changes,
            "limitations": ["Missing, unknown or not-applicable outcomes never resolve an earlier anomaly.",
                            "Evidence changes are not proof of external remediation."]}


def get_preset(connection, domain):
    row = connection.execute("SELECT * FROM report_presets WHERE domain=? ORDER BY updated_at DESC,id LIMIT 1",
                             (domain,)).fetchone()
    if row is None:
        return None
    preset = {"name": row["name"], "run_id": row["run_id"], "filters": json.loads(row["filters_json"]),
              "columns": json.loads(row["columns_json"]), "updated_at": row["updated_at"], "actor_id": row["actor_id"]}
    preset["revision"] = sha256(json.dumps(preset, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return preset


def save_preset(connection, payload, domain):
    if not isinstance(payload, dict) or set(payload) - {"actor_id", "reason", "name", "run_id", "filters", "columns"}:
        raise AppError("INVALID_INPUT", "Invalid report preset fields.", 422)
    actor = require_actor(payload.get("actor_id"), "inventory_edit")
    name, reason, run_id = payload.get("name"), payload.get("reason"), payload.get("run_id")
    if not all(isinstance(value, str) and value.strip() and len(value) <= 200 for value in (name, reason, run_id)):
        raise AppError("INVALID_INPUT", "Name, reason and a saved run ID are required (maximum 200 characters).", 422)
    run = get_run(connection, run_id)
    filters, columns = payload.get("filters", {}), payload.get("columns", list(COLUMNS))
    filtered_findings(run, filters)
    if (not isinstance(columns, list) or not columns or not all(isinstance(column, str) and column in COLUMNS for column in columns)
            or len(set(columns)) != len(columns)):
        raise AppError("INVALID_INPUT", "Choose distinct supported report columns.", 422, {"columns": list(COLUMNS)})
    before = get_preset(connection, domain)
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    connection.execute("INSERT INTO report_presets(id,domain,name,run_id,filters_json,columns_json,version,created_at,updated_at,actor_id) "
                       "VALUES (?,?,?,?,?,?,1,?,?,?) ON CONFLICT(domain,name) DO UPDATE SET "
                       "run_id=excluded.run_id,filters_json=excluded.filters_json,columns_json=excluded.columns_json,"
                       "version=report_presets.version+1,updated_at=excluded.updated_at,actor_id=excluded.actor_id",
                       (str(uuid4()), domain, name.strip(), run_id, json.dumps(filters),
                        json.dumps(columns), now, now, actor["id"]))
    after = get_preset(connection, domain)
    audit_event(connection, actor_id=actor["id"], action="report_preset_saved", outcome="success", reason=reason,
                subject_id=run_id, details={"before": before, "after": after})
    return after


def export_run(connection, run_id, filters):
    run = get_run(connection, run_id)
    findings = filtered_findings(run, filters)
    return {**run, "findings": findings, "filters": filters, "exported_findings": len(findings),
            "overview_scope": "Overview retains full saved-run totals; exported_findings is the filtered count.",
            "calculations": _filtered_calculations(run, filters)}


def csv_text(columns, rows):
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        values = []
        for key in columns:
            value = row.get(key, "")
            text = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value if value is not None else "")
            # Keep untrusted source/metadata text inert in spreadsheet applications.
            values.append("'" + text if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else text)
        writer.writerow(values)
    return output.getvalue()


def preset_csv(connection, expected_revision, domain, scope_ids, source_pairs=()):
    preset = get_preset(connection, domain)
    if preset is None:
        raise AppError("NOT_FOUND", "Save the report preset before exporting it.", 404)
    if preset["revision"] != expected_revision:
        raise AppError("STALE_REPORT_PRESET", "The saved preset changed. Reload the saved preset, review its run, filters and columns, then export again.", 409)
    scope_filter = preset.get("filters", {}).get("scope_id")
    if scope_filter and scope_filter not in set(scope_ids):
        raise AppError("NOT_FOUND", "Saved report preset was not found.", 404)
    run = project_run(get_run(connection, preset["run_id"]), scope_ids, domain=domain, source_pairs=source_pairs)
    if not run["selected_batches"] and not run["findings"] and not run["calculations"]:
        raise AppError("NOT_FOUND", "Saved report preset was not found.", 404)
    rows = [{**finding, "scope_id": finding["subject"]["scope_id"], "subject": finding["subject"]["cidr"]}
            for finding in filtered_findings(run, preset["filters"])]
    return {**preset, "projection": run["projection"]}, csv_text(preset["columns"], rows)
