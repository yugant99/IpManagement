"""Persist one immutable run of shared calculations and scoped evidence rules."""

from datetime import datetime, timezone
from ipaddress import ip_network
import json
from uuid import uuid4

from .errors import AppError
from .calculations import calculate_pools
from .evidence import selected_views as _selected_views, reference as _reference
from .rules import evaluate_rules
from .inventory_commands import link_correction_results

RULE_ID = "missing_expected_route"
RULE_VERSION = 1


def _instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def get_run(connection, run_id):
    row = connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (run_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "Saved reconciliation run does not exist.", 404)
    return json.loads(row["result_json"])


def create_run(connection):
    """Caller owns the run lock and one immediate transaction, including this insert."""
    meta = connection.execute("SELECT * FROM app_meta WHERE singleton=1").fetchone()
    clock_text = meta["demo_clock_at"]
    clock = _instant(clock_text)
    run_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    views, selected = _selected_views(connection)
    calculations = calculate_pools(connection, views, clock_text)
    findings, candidate_space = evaluate_rules(connection, views, calculations, run_id, clock_text)
    for row in connection.execute(
        "SELECT p.*, s.name AS scope_name FROM prefixes p JOIN scopes s ON s.id=p.scope_id "
        "ORDER BY p.scope_id, p.family, p.network_hex, p.prefix_length, p.id"
    ):
        subject = {key: row[key] for key in ("id", "scope_id", "scope_name", "family", "cidr", "version")}
        subject["origin"] = json.loads(row["origin"])
        policies = views["route_policy"].get(row["scope_id"], [])
        routes = views["routing"].get(row["scope_id"], [])
        references = [{"kind": "inventory", **{key: subject["origin"][key]
                       for key in ("source_id", "source_run_id", "source_record_id")}}]
        references.extend(_reference(view) for view in policies + routes)
        finding = {"id": str(uuid4()), "run_id": run_id, "rule_id": RULE_ID, "rule_version": RULE_VERSION,
                   "subject": subject, "severity": "high", "evidence_state": "unknown",
                   "explanation": "No intended route policy has been imported for this scope.",
                   "input_references": references,
                   "evaluated_window": {"kind": "instant", "start_at": clock_text, "end_at": clock_text,
                                        "interval_convention": "[start,end)"},
                   "limitations": ["Synthetic routing evidence; this does not measure traffic or prove safe reclamation.",
                                   "This rule requires one declared policy and routing source per scope."],
                   "proposed_action": "Import applicable intended policy and a fresh routing view, then compute a new run.",
                   "policy": None, "coverage": [view["coverage"] for view in routes]}
        findings.append(finding)
        if len(policies) > 1:
            finding["explanation"] = "Multiple policy sources declare this scope; intended-policy authority is unresolved."
            continue
        if not policies:
            continue
        policy_view = policies[0]
        policy_rows = []
        for record in policy_view["records"]:
            raw = json.loads(record["raw_json"])
            if record["status"] != "accepted" and isinstance(raw, dict) and raw.get("prefix_id") == row["id"]:
                references.append(_reference(policy_view, record))
            if record["status"] == "accepted":
                typed = json.loads(record["typed_json"])
                if typed["scope_id"] == row["scope_id"] and typed["prefix_id"] == row["id"]:
                    policy_rows.append(typed)
                    references.append(_reference(policy_view, record))
        coverage = policy_view["coverage"]
        if (not coverage["effective_complete"] or _instant(coverage["window_end_at"]) != clock
                or _instant(coverage["window_start_at"]) != clock):
            finding["explanation"] = "The latest policy snapshot is incomplete or inapplicable; older policy was not reused."
            continue
        if len(policy_rows) != 1:
            finding["explanation"] = "The latest policy snapshot has no unambiguous valid policy for this prefix; older policy was not reused."
            continue
        policy = policy_rows[0]
        finding["policy"] = policy
        if _instant(policy["effective_from_at"]) > clock:
            finding["explanation"] = "The intended route policy is not yet effective at this demo clock."
            continue
        if not policy["expects_announcement"]:
            finding.update(evidence_state="not_applicable", explanation="The explicit intended policy does not require an announcement for this prefix.",
                           proposed_action="No missing-route decision applies. This is not a claim of network health.")
            continue
        if len(routes) != 1:
            finding["explanation"] = ("No routing source has been imported for this scope." if not routes else
                                      "Multiple routing sources declare this scope; routing-view authority is unresolved.")
            continue
        route_view = routes[0]
        coverage = route_view["coverage"]
        end = _instant(coverage["window_end_at"])
        age = (clock - end).total_seconds()
        if _instant(coverage["window_start_at"]) > clock or not 0 <= age <= 300:
            finding["explanation"] = "The latest routing view is stale or outside the demo-clock window; a missing route cannot be established."
            continue
        network = ip_network(row["cidr"])
        matches = []
        for record in route_view["records"]:
            if record["status"] != "accepted":
                continue
            route = json.loads(record["typed_json"])
            if route["scope_id"] != row["scope_id"] or route["family"] != row["family"]:
                continue
            observed = ip_network(route["cidr"])
            if (_instant(route["observed_at"]) <= clock and _instant(route["valid_from_at"]) <= clock
                    < _instant(route["valid_until_at"]) and (observed == network or
                    (policy["route_match_policy"] == "covering" and network.subnet_of(observed)))):
                matches.append(record)
        if matches:
            references.extend(_reference(route_view, record) for record in matches)
            finding.update(evidence_state="healthy", explanation=f"An active same-scope IPv{row['family']} route satisfies the explicit {policy['route_match_policy']} policy at the demo clock.",
                           proposed_action="No missing-route discrepancy under this rule.")
            if not coverage["effective_complete"]:
                finding["limitations"].append("The source is incomplete; positive presence is usable, but this view cannot establish absence.")
        elif coverage["effective_complete"]:
            finding.update(evidence_state="anomalous", explanation=f"The fresh, complete scoped routing view contains no active route satisfying the explicit {policy['route_match_policy']} announcement policy.",
                           proposed_action="Investigate the intended announcement and routing evidence. No router change or reclamation is performed.")
        else:
            finding["explanation"] = "No matching positive route was accepted, but the latest routing view is incomplete; absence remains unknown."
    severity_order = {"critical": 0, "high": 1, "warning": 2}
    findings.sort(key=lambda finding: (severity_order[finding["severity"]], finding["rule_id"], finding["subject"]["scope_id"],
                                       finding["subject"]["cidr"], finding["id"]))
    overview = {state: sum(finding["evidence_state"] == state for finding in findings)
                for state in ("anomalous", "healthy", "unknown", "not_applicable")}
    overview["total"] = len(findings)
    result = {"id": run_id, "created_at": created_at, "demo_clock_at": clock_text,
              "ledger_version": meta["baseline_version"], "rule_id": "pool_watch", "rule_version": 1,
              "rule_ids": sorted({finding["rule_id"] for finding in findings}),
              "synthetic": True, "selected_batches": selected, "overview": overview, "findings": findings,
              "calculations": calculations, "candidate_space": candidate_space}
    connection.execute("INSERT INTO calculation_runs(id,created_at,demo_clock_at,result_json) VALUES (?,?,?,?)",
                       (run_id, created_at, clock_text, json.dumps(result, allow_nan=False)))
    link_correction_results(connection, result)
    return result
