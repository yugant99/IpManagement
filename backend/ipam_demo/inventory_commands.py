"""Bounded intended-prefix writes and IPv6 delegation arithmetic.

The API owns the transaction. Original evidence is retained on edits; the
successful audit and intended-ledger revision commit with the prefix mutation.
"""

from datetime import datetime, timezone
from ipaddress import IPv6Network, ip_network
import json
import re
from uuid import UUID, uuid4

from .errors import AppError
from .inventory import prefix_detail, scope_payload
from .workflow import audit_event, require_actor


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


def _bump_ledger(connection, affected_prefix_ids, *, structural=False):
    connection.execute("UPDATE app_meta SET baseline_version=baseline_version+1 WHERE singleton=1")
    for prefix_id in affected_prefix_ids:
        connection.execute("UPDATE pools SET pool_version=pool_version+1 WHERE prefix_id=?", (prefix_id,))
        if structural:
            connection.execute("UPDATE pools SET capacity_history_version=capacity_history_version+1 WHERE prefix_id=?", (prefix_id,))
    return _baseline(connection)


def edit_context(connection, prefix_id):
    prefix = prefix_detail(connection, _prefix(connection, prefix_id)["id"])
    scope = connection.execute("SELECT * FROM scopes WHERE id=?", (prefix["scope_id"],)).fetchone()
    affected_ids = _ancestors(connection, prefix) | {prefix["id"]}
    affected_pools = [{"pool_id": row["id"], "name": row["name"], "cidr": row["cidr"]}
                      for row in connection.execute(
                          "SELECT p.id,p.name,p.prefix_id,n.cidr FROM pools p JOIN prefixes n ON n.id=p.prefix_id "
                          "WHERE p.family=4 AND p.management_mode='dhcp' ORDER BY p.id")
                      if row["prefix_id"] in affected_ids]
    return {"prefix": prefix, "scope": scope_payload(scope), "baseline_version": _baseline(connection),
            "history_impact": {"metadata": [], "structural": affected_pools},
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
    baseline = _bump_ledger(connection, _ancestors(connection, parent) | {parent["id"]}, structural=True)
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
    baseline = _bump_ledger(connection, _ancestors(connection, prefix) | {prefix["id"]}, structural=changed_bounds)
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
