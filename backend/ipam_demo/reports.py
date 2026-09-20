"""Pinned run comparison and one stored report preset; no new calculations."""

import csv
from datetime import datetime, timezone
from hashlib import sha256
from io import StringIO
import json

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


def _filtered_calculations(run, filters):
    family = filters.get("family", "")
    scope_id = filters.get("scope_id", "")
    return [metric for metric in run.get("calculations", [])
            if (not family or str(metric.get("family")) == family)
            and (not scope_id or metric.get("scope_id") == scope_id)]


def summarize_run(run, filters):
    """Summarize only the selected immutable run; never consult current state."""
    findings = filtered_findings(run, filters)
    affected_scopes = {finding["subject"]["scope_id"] for finding in findings
                       if finding["evidence_state"] in {"anomalous", "unknown"}}
    pressure_subjects = {(finding["subject"]["scope_id"], finding["subject"]["id"])
                         for finding in findings
                         if finding["rule_id"] == "pool_pressure" and finding["evidence_state"] == "anomalous"}
    return {
        "run_id": run["id"],
        "saved_at": run["created_at"],
        "demo_clock_at": run["demo_clock_at"],
        "filters": filters,
        "anomalous_findings": sum(item["evidence_state"] == "anomalous" for item in findings),
        "unknown_findings": sum(item["evidence_state"] == "unknown" for item in findings),
        "affected_scopes": len(affected_scopes),
        "pressure_pools": len(pressure_subjects),
        "limitations": ["Counts are from this saved run and selected filters only; no live or latest exception state is included.",
                        "Pressure pools count unique saved pool_pressure subjects with anomalous evidence; this is not a traffic or reclaimability claim."],
    }


def compare_runs(connection, before_id, after_id):
    before, after = get_run(connection, before_id), get_run(connection, after_id)
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


def get_preset(connection):
    row = connection.execute("SELECT * FROM report_preset WHERE singleton=1").fetchone()
    if row is None:
        return None
    preset = {"name": row["name"], "run_id": row["run_id"], "filters": json.loads(row["filters_json"]),
              "columns": json.loads(row["columns_json"]), "updated_at": row["updated_at"], "actor_id": row["actor_id"]}
    preset["revision"] = sha256(json.dumps(preset, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return preset


def save_preset(connection, payload):
    if not isinstance(payload, dict) or set(payload) - {"actor_id", "reason", "name", "run_id", "filters", "columns"}:
        raise AppError("INVALID_INPUT", "Invalid report preset fields.", 422)
    actor = require_actor(payload.get("actor_id"), "request")
    name, reason, run_id = payload.get("name"), payload.get("reason"), payload.get("run_id")
    if not all(isinstance(value, str) and value.strip() and len(value) <= 200 for value in (name, reason, run_id)):
        raise AppError("INVALID_INPUT", "Name, reason and a saved run ID are required (maximum 200 characters).", 422)
    run = get_run(connection, run_id)
    filters, columns = payload.get("filters", {}), payload.get("columns", list(COLUMNS))
    filtered_findings(run, filters)
    if (not isinstance(columns, list) or not columns or not all(isinstance(column, str) and column in COLUMNS for column in columns)
            or len(set(columns)) != len(columns)):
        raise AppError("INVALID_INPUT", "Choose distinct supported report columns.", 422, {"columns": list(COLUMNS)})
    before = get_preset(connection)
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    connection.execute("INSERT INTO report_preset VALUES(1,?,?,?,?,?,?) ON CONFLICT(singleton) DO UPDATE SET "
                       "name=excluded.name,run_id=excluded.run_id,filters_json=excluded.filters_json,columns_json=excluded.columns_json,"
                       "updated_at=excluded.updated_at,actor_id=excluded.actor_id",
                       (name.strip(), run_id, json.dumps(filters), json.dumps(columns), now, actor["id"]))
    audit_event(connection, actor_id=actor["id"], action="report_preset_saved", outcome="success", reason=reason,
                subject_id=run_id, details={"before": before, "after": get_preset(connection)})
    return get_preset(connection)


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


def preset_csv(connection, expected_revision):
    preset = get_preset(connection)
    if preset is None:
        raise AppError("NOT_FOUND", "Save the report preset before exporting it.", 404)
    if preset["revision"] != expected_revision:
        raise AppError("STALE_REPORT_PRESET", "The saved preset changed. Reload the saved preset, review its run, filters and columns, then export again.", 409)
    run = get_run(connection, preset["run_id"])
    rows = [{**finding, "scope_id": finding["subject"]["scope_id"], "subject": finding["subject"]["cidr"]}
            for finding in filtered_findings(run, preset["filters"])]
    return preset, csv_text(preset["columns"], rows)
