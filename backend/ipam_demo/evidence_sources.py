"""Static evidence-mechanism manifest joined to existing selected-domain projections.

No calculation happens here. Per-scope evidence rows are the source catalog's
selected rows, batch counts come from authorized saved receipts, and run totals
come from the saved-run projection. The caller authorizes and scopes every input.
"""

from importlib.resources import files
import json

STATUS_LABELS = {
    "loaded_synthetic_baseline": "Loaded synthetic baseline",
    "imported_synthetic_evidence": "Imported synthetic evidence",
    "no_permitted_evidence": "No permitted synthetic rows in this domain",
    "not_connected": "Not connected",
}
_CATALOG_KINDS = {"synthetic_dhcp_import": "dhcp", "synthetic_routing_import": "routing"}
_INVENTORY_GROUPS = ("prefixes", "pools", "allocations")
_PRESENT = {"loaded_synthetic_baseline", "imported_synthetic_evidence"}


def manifest() -> dict:
    return json.loads(files("ipam_demo").joinpath("data/evidence_sources.json").read_text(encoding="utf-8"))


def overview(*, domain, evaluated_at, scopes, inventory_rows, catalog_rows, receipts, latest_run) -> dict:
    """Assemble the overview from inputs already restricted to ``domain``."""
    data = manifest()
    run = _run_summary(latest_run, set(receipts))
    run_batches = set(run["selected_batch_ids"]) if run else set()

    def evidence_row(item):
        receipt = receipts.get(item["batch_id"])
        return {**item, "in_latest_run": item["batch_id"] in run_batches,
                "receipt": {"grain": "batch", "ingested_at": receipt["ingested_at"],
                            "input_rows": receipt["input_rows"], "accepted_rows": receipt["accepted_rows"]}
                if receipt else None}

    def scoped(kind, scope):
        return [evidence_row(item) for item in catalog_rows
                if item["source_kind"] == kind and item["scope_id"] == scope["id"]]

    policy = _route_policy_presence(scopes, catalog_rows, latest_run)
    mechanisms = []
    for mechanism in data["mechanisms"]:
        implementation = mechanism["implementation"]
        result = {**mechanism, "scopes": [], "summary": None}
        if implementation == "seeded_inventory":
            rows = [{**_baseline_scope(scope, inventory_rows, scoped("route_policy", scope)),
                     "route_policy": policy[scope["id"]]} for scope in scopes]
            loaded = sum(row["state"] == "loaded" for row in rows)
            result.update(status="loaded_synthetic_baseline" if loaded else "no_permitted_evidence", scopes=rows,
                          summary={"scopes": len(rows), "loaded": loaded, "empty": len(rows) - loaded})
        elif implementation in _CATALOG_KINDS:
            rows = []
            for scope in scopes:
                evidence = scoped(_CATALOG_KINDS[implementation], scope)
                rows.append({"scope_id": scope["id"], "scope_name": scope["name"],
                             "state": "selected" if evidence else "missing", "evidence": evidence})
            selected = [item for row in rows for item in row["evidence"]]
            result.update(status="imported_synthetic_evidence" if selected else "no_permitted_evidence", scopes=rows,
                          summary={"scopes": len(rows), "missing": sum(row["state"] == "missing" for row in rows),
                                   **{key: sum(item["freshness"] == key for item in selected) for key in ("fresh", "stale")},
                                   **{key: sum(item["completeness"] == key for item in selected)
                                      for key in ("complete", "partial")}})
        else:
            result["status"] = "not_connected"
        result["status_label"] = STATUS_LABELS[result["status"]]
        mechanisms.append(result)

    status = {item["id"]: item["status"] for item in mechanisms}
    policy_present = sum(value["catalog_selected"] or value["in_latest_run"] for value in policy.values())
    functions = []
    for item in data["functions"]:
        # Source presence only; per-scope freshness and completeness still govern each finding.
        entry = {**item, "evidence_basis": "source_presence",
                 "evidence_present": all(status[required] in _PRESENT for required in item["requires"])}
        if item.get("requires_route_policy"):
            entry["route_policy_scopes"] = {"present": policy_present, "scopes": len(scopes)}
            entry["evidence_present"] = entry["evidence_present"] and policy_present > 0
        functions.append(entry)
    next_unlocks = [{"mechanism_id": item["id"], "name": item["name"], "plane": item["plane"], "unlocks": item["unlocks"]}
                    for item in mechanisms if item["status"] == "not_connected"]
    return {"domain": domain, "evaluated_at": evaluated_at, "synthetic": True,
            "manifest_version": data["manifest_version"], "planes": data["planes"], "mechanisms": mechanisms,
            "functions": {"available_now": functions, "next_unlocks": next_unlocks},
            "integration_profiles": data["integration_profiles"], "latest_run": run,
            "limitations": data["limitations"]}


def _baseline_scope(scope, inventory_rows, policy):
    counts, origins = {}, {}
    for group in _INVENTORY_GROUPS:
        rows = [item for item in inventory_rows[group] if item["scope_id"] == scope["id"]]
        counts[group] = len(rows)
        for item in rows:
            origin = item.get("origin") or {}
            key = (origin.get("source_id"), origin.get("source_run_id"))
            entry = origins.setdefault(key, {"source_id": key[0], "source_run_id": key[1],
                                             "rows": 0, "latest_ingested_at": None})
            entry["rows"] += 1
            ingested = origin.get("ingested_at")
            if ingested and (entry["latest_ingested_at"] is None or ingested > entry["latest_ingested_at"]):
                entry["latest_ingested_at"] = ingested
    # Intended inventory has no source-catalog receipt; its status is derived from loaded rows only.
    return {"scope_id": scope["id"], "scope_name": scope["name"],
            "state": "loaded" if counts["prefixes"] else "empty", "counts": counts,
            "origins": sorted(origins.values(), key=lambda value: (str(value["source_id"]), str(value["source_run_id"]))),
            "evidence": policy}


def _route_policy_presence(scopes, catalog_rows, latest_run):
    """Per-scope intended-policy presence from openable catalog rows and the domain-projected saved run.

    The run projection already limits coverage to this domain's scopes, so a mixed-domain
    policy batch contributes scope-local coverage only, never batch-wide counts.
    """
    catalog = {item["scope_id"] for item in catalog_rows if item["source_kind"] == "route_policy"}
    in_run = {}
    for batch in (latest_run or {}).get("selected_batches", []):
        if batch.get("source_kind") != "route_policy":
            continue
        for coverage in batch.get("coverage", []):
            scope_id = coverage.get("scope_id")
            in_run[scope_id] = in_run.get(scope_id, True) and bool(coverage.get("effective_complete"))
    return {scope["id"]: {"catalog_selected": scope["id"] in catalog, "in_latest_run": scope["id"] in in_run,
                          "latest_run_effective_complete": in_run.get(scope["id"])} for scope in scopes}


def _run_summary(run, openable):
    if run is None:
        return None
    # Only batch IDs this domain can open; mixed-domain batches are omitted here.
    return {"id": run["id"], "created_at": run["created_at"], "demo_clock_at": run["demo_clock_at"],
            "rule_id": run.get("rule_id"), "rule_version": run.get("rule_version"),
            "overview": run["overview"],
            "selected_batch_ids": [batch["id"] for batch in run["selected_batches"] if batch["id"] in openable],
            "projection": run["projection"]}
