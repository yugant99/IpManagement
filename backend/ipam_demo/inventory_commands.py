"""Bounded intended-prefix writes and IPv6 delegation arithmetic.

The API owns the transaction. Original evidence is retained on edits; the
successful audit and intended-ledger revision commit with the prefix mutation.
"""

from datetime import datetime, timezone
from hashlib import sha256
from ipaddress import IPv6Network, ip_network
import json
import re
from uuid import UUID, uuid4

from .errors import AppError
from .inventory import prefix_detail, scope_payload
from .workflow import actors, audit_event, require_actor
from .rules import comparable_findings


_RESERVED = {
    "id", "scope_id", "scope_name", "family", "cidr", "network_hex", "prefix_length",
    "parent_id", "owner", "purpose", "tags", "custom_fields", "version", "origin",
    "address_count", "baseline_version", "pool_version", "source_id", "source_run_id",
    "source_record_id", "observed_at", "ingested_at", "synthetic", "domain", "region",
    "actor_id", "role", "permissions", "__proto__", "constructor", "prototype",
}


def _invalid(message, field):
    raise AppError("INVALID_INPUT", message, 422, {"field": field})


def _uuid(value, field):
    if not isinstance(value, str):
        _invalid(f"{field} must be a UUID.", field)
    try:
        return str(UUID(value))
    except ValueError:
        _invalid(f"{field} must be a UUID.", field)


def _text(value, field, maximum, *, required=False):
    if not isinstance(value, str) or len(value) > maximum or "\x00" in value:
        _invalid(f"{field} must be text of at most {maximum} characters.", field)
    value = value.strip()
    if required and not value:
        _invalid(f"{field} is required.", field)
    return value


def _network(value):
    if not isinstance(value, str) or "/" not in value or "%" in value:
        _invalid("cidr must be an explicit IPv4 or IPv6 network with a prefix length.", "cidr")
    try:
        return ip_network(value.strip(), strict=True)
    except ValueError:
        _invalid("cidr must be a valid network; host bits must be zero.", "cidr")


def _metadata(payload):
    owner = _text(payload.get("owner"), "owner", 120)
    purpose = _text(payload.get("purpose"), "purpose", 500)
    tags = payload.get("tags")
    if not isinstance(tags, list) or len(tags) > 20:
        _invalid("tags must contain at most 20 strings.", "tags")
    tags = [_text(tag, "tags", 80, required=True) for tag in tags]
    if len(set(tags)) != len(tags):
        _invalid("tags must be distinct.", "tags")
    fields = payload.get("custom_fields")
    if not isinstance(fields, dict) or len(fields) > 32:
        _invalid("custom_fields must be an object with at most 32 string fields.", "custom_fields")
    for key, value in fields.items():
        if (not isinstance(key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,63}", key)
                or key.casefold() in _RESERVED):
            _invalid("Custom field names must start with a letter and cannot replace reserved fields.", "custom_fields")
        if not isinstance(value, str) or len(value) > 500 or "\x00" in value:
            _invalid("Custom field values must be strings of at most 500 characters.", "custom_fields")
    return owner, purpose, tags, fields


def _payload(payload, *, create):
    shared = {"actor_id", "reason", "expected_baseline_version", "cidr", "owner", "purpose", "tags", "custom_fields"}
    allowed = shared | ({"scope_id", "parent_id", "expected_parent_version"} if create else {"expected_version"})
    if not isinstance(payload, dict) or set(payload) != allowed:
        _invalid("Supply exactly the documented editable fields and reviewed versions.", "body")
    actor_id = _text(payload["actor_id"], "actor_id", 80, required=True)
    require_actor(actor_id, "inventory_edit")
    reason = _text(payload["reason"], "reason", 500, required=True)
    for field in ("expected_baseline_version", "expected_parent_version" if create else "expected_version"):
        if type(payload[field]) is not int or payload[field] < 1:
            _invalid(f"{field} must be a positive integer.", field)
    return reason, _network(payload["cidr"]), _metadata(payload)


def _prefix(connection, object_id):
    object_id = _uuid(object_id, "prefix_id")
    row = connection.execute("SELECT * FROM prefixes WHERE id=?", (object_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "No prefix exists with that ID.", 404)
    return row


def _baseline(connection):
    return connection.execute("SELECT baseline_version FROM app_meta WHERE singleton=1").fetchone()[0]


def _reviewed(connection, prefix, payload, version_field):
    baseline = _baseline(connection)
    if payload["expected_baseline_version"] != baseline or payload[version_field] != prefix["version"]:
        raise AppError("STALE_INVENTORY", "Inventory changed after review. Reload the prefix and review the change again.", 409,
                       {"baseline_version": baseline, "prefix_version": prefix["version"]})


def _ancestors(connection, prefix):
    result = set()
    parent_id = prefix["parent_id"]
    while parent_id:
        if parent_id in result or parent_id == prefix["id"]:
            raise AppError("INVALID_HIERARCHY", "Stored prefix ancestry contains a cycle.", 409)
        result.add(parent_id)
        row = _prefix(connection, parent_id)
        if row["scope_id"] != prefix["scope_id"] or row["family"] != prefix["family"]:
            raise AppError("INVALID_HIERARCHY", "Stored prefix ancestry crosses a scope or family.", 409)
        parent_id = row["parent_id"]
    return result


def _validate_position(connection, scope_id, network, parent, *, editing_id=None):
    scope = connection.execute("SELECT * FROM scopes WHERE id=?", (scope_id,)).fetchone()
    if scope is None:
        raise AppError("NOT_FOUND", "The selected network scope does not exist.", 404)
    if not any(network.version == boundary.version and network.subnet_of(boundary)
               for boundary in map(ip_network, json.loads(scope["managed_cidrs"]))):
        raise AppError("OUTSIDE_MANAGED_SCOPE", "The prefix must remain inside this scope's declared managed perimeter.", 422)
    ancestors = set()
    if parent is not None:
        parent_network = ip_network(parent["cidr"])
        if (parent["scope_id"] != scope_id or parent_network.version != network.version
                or network.prefixlen <= parent_network.prefixlen or not network.subnet_of(parent_network)):
            raise AppError("INVALID_PARENT", "The parent must strictly contain its child in the same scope and family.", 422)
        ancestors = _ancestors(connection, parent) | {parent["id"]}
    for row in connection.execute("SELECT * FROM prefixes WHERE scope_id=? AND family=?", (scope_id, network.version)):
        if row["id"] == editing_id:
            continue
        other = ip_network(row["cidr"])
        if not network.overlaps(other):
            continue
        if row["id"] in ancestors and network != other and network.subnet_of(other):
            continue
        raise AppError("PREFIX_OVERLAP", "This prefix overlaps inventory outside its declared ancestry.", 409,
                       {"conflicting_prefix_id": row["id"], "conflicting_cidr": row["cidr"]})


def _bump_ledger(connection, affected_prefix_ids):
    connection.execute("UPDATE app_meta SET baseline_version=baseline_version+1 WHERE singleton=1")
    for prefix_id in affected_prefix_ids:
        connection.execute("UPDATE pools SET pool_version=pool_version+1 WHERE prefix_id=?", (prefix_id,))
    return _baseline(connection)


def edit_context(connection, prefix_id):
    prefix = prefix_detail(connection, _prefix(connection, prefix_id)["id"])
    scope = connection.execute("SELECT * FROM scopes WHERE id=?", (prefix["scope_id"],)).fetchone()
    return {"prefix": prefix, "scope": scope_payload(scope), "baseline_version": _baseline(connection),
            "children_count": connection.execute("SELECT COUNT(*) FROM prefixes WHERE parent_id=?", (prefix["id"],)).fetchone()[0]}


def create_child(connection, payload):
    reason, network, (owner, purpose, tags, fields) = _payload(payload, create=True)
    scope_id = _uuid(payload["scope_id"], "scope_id")
    parent = _prefix(connection, _uuid(payload["parent_id"], "parent_id"))
    _reviewed(connection, parent, payload, "expected_parent_version")
    _validate_position(connection, scope_id, network, parent)
    prefix_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    clock = connection.execute("SELECT demo_clock_at FROM app_meta WHERE singleton=1").fetchone()[0]
    origin = {"source_id": "local-inventory", "source_run_id": str(uuid4()), "source_record_id": prefix_id,
              "observed_at": clock, "ingested_at": now, "synthetic": True}
    connection.execute(
        "INSERT INTO prefixes (id,scope_id,family,cidr,network_hex,prefix_length,parent_id,owner,purpose,tags,custom_fields,version,origin) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (prefix_id, scope_id, network.version, str(network), f"{int(network.network_address):032x}", network.prefixlen,
         parent["id"], owner, purpose, json.dumps(tags), json.dumps(fields, sort_keys=True), 1, json.dumps(origin)),
    )
    connection.execute("UPDATE prefixes SET version=version+1 WHERE id=?", (parent["id"],))
    baseline = _bump_ledger(connection, _ancestors(connection, parent) | {parent["id"]})
    result = prefix_detail(connection, prefix_id)
    audit = audit_event(connection, actor_id=payload["actor_id"], action="prefix_created", outcome="success", reason=reason,
                        subject_id=prefix_id, scope_id=scope_id,
                        details={"before": None, "after": result, "baseline_version_before": payload["expected_baseline_version"],
                                 "baseline_version": baseline, "parent_version_before": parent["version"],
                                 "parent_version_after": parent["version"] + 1})
    return {"prefix": result, "baseline_version": baseline, "audit_id": audit["id"]}


def edit_prefix(connection, prefix_id, payload):
    reason, network, (owner, purpose, tags, fields) = _payload(payload, create=False)
    prefix = _prefix(connection, prefix_id)
    _reviewed(connection, prefix, payload, "expected_version")
    if network.version != prefix["family"]:
        raise AppError("FAMILY_IMMUTABLE", "A prefix cannot change address family.", 422)
    before = prefix_detail(connection, prefix["id"])
    changed_bounds = str(network) != prefix["cidr"]
    if changed_bounds:
        children = connection.execute("SELECT COUNT(*) FROM prefixes WHERE parent_id=?", (prefix["id"],)).fetchone()[0]
        if children or before["allocations"] or before["pools"]:
            raise AppError("PREFIX_NOT_EMPTY", "Bounds edits require a prefix with no children, allocations or attached pools.", 409,
                           {"children": children, "allocations": len(before["allocations"]), "pools": len(before["pools"])})
        parent = _prefix(connection, prefix["parent_id"]) if prefix["parent_id"] else None
        _validate_position(connection, prefix["scope_id"], network, parent, editing_id=prefix["id"])
    if (not changed_bounds and owner == before["owner"] and purpose == before["purpose"]
            and tags == before["tags"] and fields == before["custom_fields"]):
        raise AppError("NO_CHANGE", "No inventory fields changed.", 409)
    connection.execute(
        "UPDATE prefixes SET cidr=?,network_hex=?,prefix_length=?,owner=?,purpose=?,tags=?,custom_fields=?,version=version+1 WHERE id=?",
        (str(network), f"{int(network.network_address):032x}", network.prefixlen, owner, purpose,
         json.dumps(tags), json.dumps(fields, sort_keys=True), prefix["id"]),
    )
    baseline = _bump_ledger(connection, _ancestors(connection, prefix) | {prefix["id"]})
    result = prefix_detail(connection, prefix["id"])
    audit = audit_event(connection, actor_id=payload["actor_id"], action="prefix_edited", outcome="success", reason=reason,
                        subject_id=prefix["id"], scope_id=prefix["scope_id"],
                        details={"before": before, "after": result,
                                 "baseline_version_before": payload["expected_baseline_version"], "baseline_version": baseline})
    return {"prefix": result, "baseline_version": baseline, "audit_id": audit["id"]}


def preview_children(connection, parent_id, prefix_length, limit=10):
    parent = _prefix(connection, parent_id)
    network = ip_network(parent["cidr"])
    if network.version != 6:
        raise AppError("IPV6_REQUIRED", "Child-prefix planning is bounded to IPv6 parents.", 422)
    if type(prefix_length) is not int or not network.prefixlen < prefix_length <= 128:
        _invalid("Choose a child prefix length longer than its parent and no longer than 128.", "prefix_length")
    if type(limit) is not int or not 1 <= limit <= 20:
        _invalid("Preview limit must be between 1 and 20.", "limit")
    total = 1 << (prefix_length - network.prefixlen)
    step = 1 << (128 - prefix_length)
    start = int(network.network_address)
    ancestors = _ancestors(connection, parent) | {parent["id"]}
    blocked = []
    for row in connection.execute("SELECT * FROM prefixes WHERE scope_id=? AND family=6", (parent["scope_id"],)):
        if row["id"] in ancestors:
            continue
        other = ip_network(row["cidr"])
        if network.overlaps(other):
            first = max(start, int(other.network_address))
            last = min(int(network.broadcast_address), int(other.broadcast_address))
            blocked.append(((first - start) // step, (last - start) // step))
    # Merge occupied child-index ranges. Work scales with stored prefixes and
    # the preview limit, even when the requested capacity is larger than 2^53.
    merged = []
    for first, last in sorted(blocked):
        if merged and first <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(last, merged[-1][1]))
        else:
            merged.append((first, last))
    items = []
    cursor = 0
    for first, last in [*merged, (total, total)]:
        while cursor < first and len(items) < limit:
            items.append(str(IPv6Network((start + cursor * step, prefix_length))))
            cursor += 1
        cursor = max(cursor, last + 1)
        if len(items) == limit:
            break
    used = sum(last - first + 1 for first, last in merged)
    return {"parent_id": parent["id"], "parent_cidr": parent["cidr"], "parent_version": parent["version"],
            "scope_id": parent["scope_id"], "baseline_version": _baseline(connection), "prefix_length": prefix_length,
            "total_children": str(total), "blocked_children": str(used), "free_children": str(total - used),
            "items": items, "limit": limit, "synthetic": True}


def _saved_finding(connection, run_id, finding_id):
    row = connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (run_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "The saved reconciliation run does not exist.", 404)
    run = json.loads(row["result_json"])
    finding = next((item for item in run["findings"] if item["id"] == finding_id), None)
    if finding is None:
        raise AppError("NOT_FOUND", "The finding does not belong to the selected saved run.", 404)
    return run, finding


def correction_context(connection, run_id, finding_id):
    _, finding = _saved_finding(connection, run_id, finding_id)
    if (finding["rule_id"] not in ("ghost_scope", "unregistered_managed_route")
            or finding["evidence_state"] != "anomalous" or finding["subject"].get("kind") != "managed_perimeter"):
        raise AppError("CORRECTION_NOT_SUPPORTED", "Select an anomalous ghost-scope or unregistered-route finding for top-level registration.", 422)
    scope = connection.execute("SELECT * FROM scopes WHERE id=?", (finding["subject"]["scope_id"],)).fetchone()
    if scope is None:
        raise AppError("NOT_FOUND", "The finding's intended network scope no longer exists.", 404)
    return {"source_run_id": run_id, "source_finding": finding, "scope": scope_payload(scope),
            "baseline_version": _baseline(connection), "actors": actors(), "synthetic": True,
            "limitations": ["Propose one top-level prefix inside the existing managed perimeter; pending proposals do not change inventory.",
                            "Independent approval changes local intended inventory only. Reconcile afterward to inspect every remaining discrepancy.",
                            "Registration does not create intended route policy or establish external authorization."]}


def _correction_position(connection, payload):
    context = correction_context(connection, payload["source_run_id"], payload["source_finding_id"])
    finding = context["source_finding"]
    network = _network(payload["cidr"])
    boundary = ip_network(finding["subject"]["cidr"])
    if (payload["scope_id"] != finding["subject"]["scope_id"] or network.version != boundary.version
            or not network.subnet_of(boundary)):
        raise AppError("CORRECTION_SCOPE_MISMATCH", "The prefix must belong to the finding's scope, family and managed perimeter.", 422)
    observations = [ip_network(item["cidr"]) if "cidr" in item else ip_network(item["address"])
                    for item in finding.get("observations", [])]
    if not any(item.version == network.version and item.subnet_of(network) for item in observations):
        raise AppError("CORRECTION_TARGET_MISMATCH", "The proposed prefix must register at least one discrepancy in the reviewed finding.", 422)
    if payload["expected_baseline_version"] != context["baseline_version"]:
        raise AppError("STALE_INVENTORY", "Inventory changed after review. Reload and submit a new reviewed proposal.", 409,
                       {"baseline_version": context["baseline_version"]})
    _validate_position(connection, payload["scope_id"], network, None)
    return network


def _correction_result(source, run):
    if run is None:
        return None, "pending_reconciliation"
    finding = next((item for item in run["findings"] if item["rule_id"] == source["rule_id"]
                    and item["subject"]["scope_id"] == source["subject"]["scope_id"]
                    and item["subject"]["family"] == source["subject"]["family"]
                    and item["subject"]["id"] == source["subject"]["id"]), None)
    if not comparable_findings(source, finding):
        return finding, "resolution_unknown"
    return finding, {"healthy": "resolved_by_evidence", "anomalous": "still_anomalous"}.get(
        finding["evidence_state"], "resolution_unknown")


def get_correction(connection, object_id):
    row = connection.execute("SELECT * FROM correction_requests WHERE id=?", (object_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "No inventory correction exists with that ID.", 404)
    item = dict(row)
    item["payload"] = json.loads(item.pop("payload_json"))
    item.pop("payload_hash")
    item.pop("decision_hash")
    _, source = _saved_finding(connection, item["source_run_id"], item["source_finding_id"])
    item.update(source_finding=source, result_finding=None, latest_finding=None, latest_run_id=None,
                resolution_state="not_approved", latest_resolution_state="not_approved",
                local_outcome="registered" if item["state"] == "approved" else "unchanged", synthetic=True)
    if item["state"] == "approved":
        saved = connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (item["result_run_id"],)).fetchone()
        first = json.loads(saved[0]) if saved else None
        item["result_finding"], item["resolution_state"] = _correction_result(source, first)
        saved = connection.execute("SELECT result_json FROM calculation_runs ORDER BY rowid DESC LIMIT 1").fetchone()
        latest = json.loads(saved[0]) if saved else None
        if latest and latest["ledger_version"] < item["approved_baseline_version"]:
            latest = None
        item["latest_run_id"] = latest["id"] if latest else None
        item["latest_finding"], item["latest_resolution_state"] = _correction_result(source, latest)
    return item


def list_corrections(connection):
    return [get_correction(connection, row["id"]) for row in connection.execute(
        "SELECT id FROM correction_requests ORDER BY created_at DESC,id DESC")]


def create_correction(connection, payload):
    allowed = {"actor_id", "idempotency_key", "scope_id", "cidr", "owner", "purpose", "reason",
               "expected_baseline_version", "source_run_id", "source_finding_id"}
    if not isinstance(payload, dict) or set(payload) != allowed:
        _invalid("Supply exactly the documented correction fields and reviewed inventory version.", "body")
    actor = require_actor(payload["actor_id"], "request")
    normalized = {"actor_id": actor["id"], "cidr": str(_network(payload["cidr"]))}
    for field, limit in (("idempotency_key", 200), ("owner", 120), ("purpose", 500), ("reason", 500)):
        normalized[field] = _text(payload[field], field, limit, required=True)
    for field in ("scope_id", "source_run_id", "source_finding_id"):
        normalized[field] = _uuid(payload[field], field)
    if type(payload["expected_baseline_version"]) is not int or payload["expected_baseline_version"] < 1:
        _invalid("expected_baseline_version must be a positive integer.", "expected_baseline_version")
    normalized["expected_baseline_version"] = payload["expected_baseline_version"]
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    digest = sha256(encoded.encode("utf-8")).hexdigest()
    previous = connection.execute("SELECT * FROM correction_requests WHERE actor_id=? AND idempotency_key=?",
                                  (actor["id"], normalized["idempotency_key"])).fetchone()
    if previous:
        if previous["payload_hash"] != digest:
            raise AppError("IDEMPOTENCY_CONFLICT", "This correction key already identifies a different proposal.", 409)
        return get_correction(connection, previous["id"]), True
    _correction_position(connection, normalized)
    object_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    connection.execute(
        "INSERT INTO correction_requests(id,actor_id,idempotency_key,payload_hash,payload_json,scope_id,source_run_id,"
        "source_finding_id,baseline_version,state,created_at) VALUES (?,?,?,?,?,?,?,?,?,'pending',?)",
        (object_id, actor["id"], normalized["idempotency_key"], digest, encoded, normalized["scope_id"],
         normalized["source_run_id"], normalized["source_finding_id"], normalized["expected_baseline_version"], now))
    audit_event(connection, actor_id=actor["id"], action="correction.proposed", outcome="succeeded", reason=normalized["reason"],
                request_id=object_id, subject_id=object_id, scope_id=normalized["scope_id"],
                details={"before": None, "after": {"state": "pending", "proposal": normalized}})
    return get_correction(connection, object_id), False


def decide_correction(connection, object_id, payload):
    if not isinstance(payload, dict) or set(payload) != {"actor_id", "action", "reason"}:
        _invalid("Supply actor_id, action and reason for the correction decision.", "body")
    actor = require_actor(payload["actor_id"], "approve")
    action = payload["action"]
    if action not in ("approve", "reject"):
        _invalid("Use approve or reject for a correction decision.", "action")
    reason = _text(payload["reason"], "reason", 500, required=True)
    row = connection.execute("SELECT * FROM correction_requests WHERE id=?", (object_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "No inventory correction exists with that ID.", 404)
    if row["actor_id"] == actor["id"]:
        raise AppError("SELF_APPROVAL", "A different authorized actor must review this correction.", 403)
    digest = sha256(json.dumps({"actor_id": actor["id"], "action": action, "reason": reason},
                              sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if row["state"] != "pending":
        if row["decision_hash"] == digest:
            return get_correction(connection, object_id), True
        raise AppError("DECISION_CONFLICT", "This correction already has an immutable decision.", 409)
    proposed = json.loads(row["payload_json"])
    prefix_id, baseline, registered = None, None, None
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    if action == "approve":
        require_actor(actor["id"], "inventory_edit")
        network = _correction_position(connection, proposed)
        prefix_id = str(uuid4())
        clock = connection.execute("SELECT demo_clock_at FROM app_meta WHERE singleton=1").fetchone()[0]
        origin = {"source_id": "local-inventory-correction", "source_run_id": object_id, "source_record_id": prefix_id,
                  "observed_at": clock, "ingested_at": now, "synthetic": True}
        connection.execute(
            "INSERT INTO prefixes(id,scope_id,family,cidr,network_hex,prefix_length,parent_id,owner,purpose,tags,custom_fields,version,origin) "
            "VALUES (?,?,?,?,?,?,NULL,?,?,'[]','{}',1,?)",
            (prefix_id, proposed["scope_id"], network.version, str(network), f"{int(network.network_address):032x}",
             network.prefixlen, proposed["owner"], proposed["purpose"], json.dumps(origin)))
        baseline = _bump_ledger(connection, set())
        registered = prefix_detail(connection, prefix_id)
    state = "approved" if action == "approve" else "rejected"
    connection.execute(
        "UPDATE correction_requests SET state=?,prefix_id=?,decided_at=?,decision_actor_id=?,decision_hash=?,decision_reason=?,"
        "approved_baseline_version=? WHERE id=?", (state, prefix_id, now, actor["id"], digest, reason, baseline, object_id))
    audit_event(connection, actor_id=actor["id"], action=f"correction.{action}", outcome="succeeded", reason=reason,
                request_id=object_id, subject_id=prefix_id or object_id, scope_id=row["scope_id"],
                details={"before": {"state": "pending", "prefix": None, "baseline_version": _baseline(connection) if baseline is None else baseline - 1},
                         "after": {"state": state, "prefix": registered, "baseline_version": _baseline(connection)},
                         "source_run_id": row["source_run_id"], "source_finding_id": row["source_finding_id"]})
    return get_correction(connection, object_id), False


def link_correction_results(connection, run):
    """Link first post-approval run without treating approval as evidence resolution."""
    connection.execute("UPDATE correction_requests SET result_run_id=? WHERE state='approved' AND result_run_id IS NULL "
                       "AND approved_baseline_version<=?", (run["id"], run["ledger_version"]))
