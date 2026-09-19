"""Bounded Pool Watch rules over shared calculations and immutable evidence."""

from collections import defaultdict
from datetime import timedelta
from ipaddress import ip_address, ip_network
import json
from uuid import NAMESPACE_URL, uuid4, uuid5

from .calculations import assignable_intervals, stamp
from .evidence import eligible_current_view, instant, reference, typed_records
from .inventory import pools

RULE_VERSION = 1


def _finding(run_id, clock_text, rule, subject, references, coverage, severity="high"):
    return {"id": str(uuid4()), "run_id": run_id, "rule_id": rule, "rule_version": RULE_VERSION,
            "subject": subject, "severity": severity, "evidence_state": "unknown",
            "explanation": "Required scoped source evidence is unavailable.", "input_references": references,
            "evaluated_window": {"kind": "instant", "start_at": clock_text, "end_at": clock_text,
                                 "interval_convention": "[start,end)"}, "coverage": coverage, "policy": None,
            "limitations": ["Synthetic evidence only; an investigation candidate does not prove safe reclamation or unauthorized use."],
            "proposed_action": "Review source evidence and uncertainty before any external action."}


def _state(finding, state, explanation):
    finding.update(evidence_state=state, explanation=explanation)


def _source_reason(candidates, clock, kind):
    if len(candidates) != 1:
        return "No source declares this scope." if not candidates else "Multiple sources declare this scope; authority is ambiguous."
    if not eligible_current_view(candidates[0], clock, kind):
        return "The latest source is stale or outside the demo-clock window; older batches were not reused."
    return None


def evaluate_rules(connection, views, calculations, run_id, clock_text):
    clock = instant(clock_text)
    window_start = clock - timedelta(days=30)
    findings, candidate_intervals = [], defaultdict(list)
    pool_rows = {pool["id"]: pool for pool in pools(connection)}
    prefixes = [dict(row) for row in connection.execute(
        "SELECT p.*,s.name AS scope_name FROM prefixes p JOIN scopes s ON s.id=p.scope_id")]
    by_id = {prefix["id"]: prefix for prefix in prefixes}
    for metric in calculations:
        prefix = by_id[metric["prefix_id"]]
        subject = {key: prefix[key] for key in ("id", "scope_id", "scope_name", "family", "cidr", "version")}
        subject.update(id=metric["pool_id"], prefix_id=prefix["id"], pool_id=metric["pool_id"],
                       kind="pool", origin=json.loads(prefix["origin"]))
        p95, forecast = metric["p95"], metric["forecast"]
        pressure = _finding(run_id, clock_text, "pool_pressure", subject, list(metric["input_references"]), metric["coverage"])
        oversized = _finding(run_id, clock_text, "oversized_pool", subject, list(metric["input_references"]), metric["coverage"], "warning")
        zombie = _finding(run_id, clock_text, "zombie_candidate", subject, list(metric["input_references"]), metric["coverage"], "warning")
        out_of_range = _finding(run_id, clock_text, "pool_assignment_discrepancy", subject,
                                list(metric["input_references"]), metric["coverage"])
        out_of_range["observations"] = metric["out_of_range_observations"]
        for finding in (pressure, oversized, zombie, out_of_range):
            finding["calculation_pool_id"] = metric["pool_id"]
        for finding in (pressure, oversized, zombie):
            finding["evaluated_window"].update(kind="interval", start_at=stamp(window_start))
        findings.extend((pressure, oversized, zombie, out_of_range))
        if metric["management_mode"] != "dhcp" or metric["family"] != 4:
            for finding in (pressure, oversized, zombie, out_of_range):
                _state(finding, "not_applicable", "This rule is limited to DHCP-managed IPv4 pools.")
            continue
        if out_of_range["observations"]:
            _state(out_of_range, "anomalous", "Fresh current DHCP claims lie inside this pool's intended prefix but outside its assignable ranges or within exclusions; they do not change the capacity denominator.")
        elif metric["current"]["status"] == "available":
            _state(out_of_range, "healthy", "The complete fresh view has no current DHCP claims outside this pool's assignable ranges within its prefix.")
        else:
            out_of_range["explanation"] = "No positive out-of-range claim is accepted; complete fresh unambiguous evidence and valid capacity are required for a healthy control."
        p95_warning = p95["utilization_pct"] >= 80 if p95["status"] == "available" else None
        forecast_warning = (forecast["days_to_full"] < 60 if forecast["status"] in ("available", "beyond_horizon", "exhausted")
                            else False if forecast["status"] == "no_positive_growth" else None)
        pressure["policy"] = {"p95_at_least_pct": 80, "forecast_below_days": 60,
                              "p95_branch": p95_warning, "forecast_branch": forecast_warning, "operator": "OR"}
        if p95_warning is True or forecast_warning is True:
            _state(pressure, "anomalous", "Shared p95 occupancy is at least 80% or the eligible shared forecast is below 60 days to full.")
        elif p95_warning is False and forecast_warning is False:
            _state(pressure, "healthy", "Both eligible pressure branches are false: p95 is below 80% and forecast does not warn below 60 days.")
        else:
            pressure["explanation"] = "No pressure branch is known true, and at least one branch lacks eligible evidence."
        oversized["policy"] = {"p95_below_pct": 50, "required_samples": 720}
        if p95["status"] == "available":
            low = p95["utilization_pct"] < 50
            _state(oversized, "anomalous" if low else "healthy",
                   "Complete 30-day p95 occupancy is below 50%; review this candidate pool." if low else
                   "Complete 30-day p95 occupancy is at least 50%; the oversized rule does not apply.")
        else:
            oversized["explanation"] = "All 720 eligible hourly samples are required; missing samples are never filled with zero."
        overlap = metric["lease_overlap_30d"]
        if overlap is True:
            _state(zombie, "healthy", "An assignable lease overlaps the 30-day window; this is not a zero-lease candidate.")
        elif overlap is None:
            zombie["explanation"] = "A complete, consistent 30-day DHCP interval is required to establish zero lease overlap."
        else:
            routes = views["routing"].get(metric["scope_id"], [])
            zombie["input_references"].extend(reference(view) for view in routes)
            zombie["coverage"] = list(zombie["coverage"]) + [view["coverage"] for view in routes]
            reason = _source_reason(routes, clock, "routing")
            if reason:
                zombie["explanation"] = reason
            else:
                match_policy = "exact"
                policies = views["route_policy"].get(metric["scope_id"], [])
                if len(policies) == 1:
                    policy_view = policies[0]
                    cov = policy_view["coverage"]
                    if (cov["effective_complete"] and instant(cov["window_start_at"]) == clock
                            and instant(cov["window_end_at"]) == clock):
                        for record, policy in typed_records(policy_view):
                            if policy["prefix_id"] == prefix["id"] and instant(policy["effective_from_at"]) <= clock:
                                match_policy = policy["route_match_policy"]
                                zombie["input_references"].append(reference(policy_view, record))
                matches = []
                network = ip_network(metric["cidr"])
                for record, route in typed_records(routes[0]):
                    observed = ip_network(route["cidr"])
                    if (route["family"] == metric["family"] and instant(route["observed_at"]) <= clock
                            and instant(route["valid_from_at"]) <= clock < instant(route["valid_until_at"])
                            and (observed == network or (match_policy == "covering" and network.subnet_of(observed)))):
                        matches.append(record)
                zombie["policy"] = {"route_match_policy": match_policy, "zero_lease_days": 30}
                if matches:
                    zombie["input_references"].extend(reference(routes[0], record) for record in matches)
                    _state(zombie, "anomalous", "This intended DHCP pool is currently announced and has complete 30-day coverage without lease overlap; investigate only.")
                elif routes[0]["coverage"]["effective_complete"]:
                    _state(zombie, "healthy", "Complete fresh routing evidence has no applicable current announcement; the zombie conjunction is false.")
                else:
                    zombie["explanation"] = "No positive route is accepted and the current route view is incomplete."
        if any(finding["evidence_state"] == "anomalous" for finding in (oversized, zombie)):
            candidate_intervals[metric["scope_id"]].extend(assignable_intervals(pool_rows[metric["pool_id"]], metric["cidr"]))

    meta = connection.execute("SELECT * FROM app_meta WHERE singleton=1").fetchone()
    seed = json.loads(meta["seed_envelope"])
    for scope in connection.execute("SELECT * FROM scopes ORDER BY id"):
        origin_record = next((row for row in seed["scopes"] if row["id"] == scope["id"]), None)
        origin = {"source_id": seed["source_id"], "source_run_id": seed["source_run_id"],
                  "source_record_id": origin_record["source_record_id"] if origin_record else scope["id"],
                  "observed_at": clock_text, "ingested_at": meta["seeded_at"], "synthetic": True}
        intended = [ip_network(prefix["cidr"]) for prefix in prefixes if prefix["scope_id"] == scope["id"]]
        for cidr in json.loads(scope["managed_cidrs"]):
            boundary = ip_network(cidr)
            subject = {"id": str(uuid5(NAMESPACE_URL, f"ipam-perimeter/{scope['id']}/{cidr}")),
                       "scope_id": scope["id"], "scope_name": scope["name"], "family": boundary.version,
                       "cidr": cidr, "version": 1, "kind": "managed_perimeter", "origin": origin}
            for kind, rule in (("dhcp", "ghost_scope"), ("routing", "unregistered_managed_route"), ("dhcp", "assignment_conflict")):
                candidates = views[kind].get(scope["id"], [])
                finding = _finding(run_id, clock_text, rule, subject, [reference(view) for view in candidates],
                                   [view["coverage"] for view in candidates], "critical" if rule == "assignment_conflict" else "high")
                finding["observations"] = []
                findings.append(finding)
                reason = _source_reason(candidates, clock, kind)
                if reason:
                    finding["explanation"] = reason
                    continue
                view = candidates[0]
                evidence_rows = []
                for record, typed in typed_records(view):
                    if typed["family"] != boundary.version or instant(typed["observed_at"]) > clock:
                        continue
                    observed = (ip_network(typed["cidr"]) if kind == "routing" else
                                ip_network(typed["address"] + ("/32" if boundary.version == 4 else "/128")))
                    if not observed.subnet_of(boundary):
                        continue
                    left = instant(typed["valid_from_at"] if kind == "routing" else typed["lease_start_at"])
                    right = instant(typed["valid_until_at"] if kind == "routing" else typed["lease_end_at"])
                    if rule == "assignment_conflict":
                        if left <= clock and right > max(window_start, instant(view["coverage"]["window_start_at"])):
                            evidence_rows.append((record, typed, left, right))
                    elif left <= clock < right:
                        registered = any(network.version == observed.version and observed.subnet_of(network) for network in intended)
                        if not registered:
                            finding["observations"].append({"address" if kind == "dhcp" else "cidr": typed["address"] if kind == "dhcp" else typed["cidr"],
                                                            "input_reference": reference(view, record)})
                            finding["input_references"].append(reference(view, record))
                if rule == "assignment_conflict":
                    finding["evaluated_window"].update(kind="interval_and_current_snapshot", start_at=stamp(window_start))
                    grouped = defaultdict(list)
                    for record, typed, left, right in evidence_rows:
                        grouped[typed["address"]].append((record, typed, left, right))
                    for address, claims in grouped.items():
                        for index, (record, typed, left, right) in enumerate(claims):
                            for other_record, other, other_left, other_right in claims[index + 1:]:
                                overlap_start = max(left, other_left, window_start, instant(view["coverage"]["window_start_at"]))
                                overlap_end = min(right, other_right)
                                historical_overlap = overlap_start < min(overlap_end, clock, instant(view["coverage"]["window_end_at"]))
                                current_overlap = overlap_start <= clock < overlap_end
                                if typed["client_id"] != other["client_id"] and (historical_overlap or current_overlap):
                                    finding["observations"].append({"address": address,
                                        "clients": [typed["client_id"], other["client_id"]],
                                        "overlap_start_at": stamp(overlap_start), "overlap_end_at": stamp(overlap_end),
                                        "input_references": [reference(view, record), reference(view, other_record)]})
                                    finding["input_references"].extend((reference(view, record), reference(view, other_record)))
                    finding["limitations"].append("Conflicts compare incompatible DHCP client IDs; owner metadata is not a mapped subscriber identity. Sequential and cross-scope reuse do not conflict.")
                if finding["observations"]:
                    _state(finding, "anomalous", {"ghost_scope": "Fresh current DHCP usage lies inside the declared managed perimeter and outside all same-scope intended prefixes.",
                           "unregistered_managed_route": "A fresh active managed announcement lies outside all same-scope intended prefixes.",
                           "assignment_conflict": "Different DHCP clients claim the same scoped address during overlapping half-open validity intervals."}[rule])
                    if not view["coverage"]["effective_complete"]:
                        finding["limitations"].append("Coverage is incomplete; accepted positive evidence supports this finding but cannot establish absence elsewhere.")
                elif view["coverage"]["effective_complete"]:
                    _state(finding, "healthy", "The complete fresh scoped view contains no eligible discrepancy under this rule.")
                else:
                    finding["explanation"] = "No positive discrepancy is accepted, but incomplete coverage cannot establish a healthy absence control."

    candidate_space = []
    for scope_id, intervals in sorted(candidate_intervals.items()):
        merged = []
        for start, end in sorted(intervals):
            if merged and start <= merged[-1][1] + 1:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        candidate_space.append({"scope_id": scope_id, "family": 4,
                                "addresses_in_candidate_pools": str(sum(end - start + 1 for start, end in merged)),
                                "intervals": [{"start": str(ip_address(start)), "end": str(ip_address(end))} for start, end in merged]})
    return findings, {"by_scope": candidate_space, "released_addresses": "0",
                      "label": "Distinct assignable IPv4 addresses in candidate pools; not proven recoverable or released space."}
