"""Local-static reservation lifecycle; every mutation joins the caller's transaction."""

from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
import json
from uuid import UUID, uuid4

from . import workflow
from .errors import AppError


def _now():
    return datetime.now(timezone.utc)


def _stamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _text(value, field, maximum=500):
    return workflow._text(value, field, maximum)


def _version(value, field):
    return workflow._version(value, field)


def _uuid(value):
    try:
        return str(value if isinstance(value, UUID) else UUID(str(value)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404) from exc


def _duration(value):
    if value is None:
        return 24
    if type(value) is not int or not 1 <= value <= 168:
        raise AppError("INVALID_INPUT", "duration_hours must be a positive integer no greater than 168.", 422,
                       {"field": "duration_hours"})
    return value


def _context():
    context = workflow._access_context.get()
    if (context is None or context.selected_domain is None or context.selected_domain not in context.domains
            or context.is_evidence_coordinator):
        raise AppError("FORBIDDEN", "Select a permitted domain before accessing domain data.", 403)
    return context


def _resource(connection, reservation_id):
    row = connection.execute("SELECT * FROM reservations WHERE id=?", (reservation_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    workflow._require_scope_domain(connection, row["scope_id"])
    return row


def _pool_for(connection, pool_id, scope_id=None):
    workflow._require_pool_domain(connection, pool_id)
    pool, ranges, exclusions = workflow._pool(connection, pool_id)
    if scope_id is not None and pool["scope_id"] != scope_id:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    return pool, ranges, exclusions


def _reservation(row):
    return {key: row[key] for key in row.keys()}


def _history(connection, reservation_id):
    return [{**dict(row), "before": json.loads(row["before_json"]) if row["before_json"] else None,
             "after": json.loads(row["after_json"])}
            for row in connection.execute(
                "SELECT * FROM reservation_history WHERE reservation_id=? ORDER BY version", (reservation_id,))]


def get_reservation(connection, reservation_id):
    object_id = _uuid(reservation_id)
    row = _resource(connection, object_id)
    item = _reservation(row)
    item["history"] = _history(connection, object_id)
    item["synthetic"] = True
    return item


def list_reservations(connection):
    context = _context()
    rows = connection.execute(
        "SELECT r.* FROM reservations r JOIN scopes s ON s.id=r.scope_id WHERE s.domain=? "
        "ORDER BY r.created_at DESC,r.id DESC", (context.selected_domain,)).fetchall()
    result = []
    for row in rows:
        item = _reservation(row)
        item["synthetic"] = True
        result.append(item)
    return result


def list_release_requests(connection, reservation_id):
    object_id = _uuid(reservation_id)
    _resource(connection, object_id)
    return [_release_request_payload(row) for row in connection.execute(
        "SELECT * FROM reservation_release_requests WHERE reservation_id=? ORDER BY created_at,id", (object_id,))]


def get_release_request(connection, reservation_id, request_id):
    object_id, release_id = _uuid(reservation_id), _uuid(request_id)
    _resource(connection, object_id)
    row = connection.execute(
        "SELECT * FROM reservation_release_requests WHERE id=? AND reservation_id=?", (release_id, object_id)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    return _release_request_payload(row)


def _receipt(connection, context, action, key, digest):
    row = connection.execute(
        "SELECT * FROM tier_a_operation_receipts WHERE principal_id=? AND domain=? AND action=? AND idempotency_key=?",
        (context.principal_id, context.selected_domain, action, key)).fetchone()
    if row is None:
        return None
    if row["request_digest"] != digest:
        raise AppError("IDEMPOTENCY_CONFLICT", "This operation key already identifies a different payload.", 409)
    return json.loads(row["result_json"])


def _save_receipt(connection, context, action, key, digest, target_kind, target_id, result):
    connection.execute(
        "INSERT INTO tier_a_operation_receipts(id,principal_id,domain,action,idempotency_key,request_digest,"
        "target_kind,target_id,result_json,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (str(uuid4()), context.principal_id, context.selected_domain, action, key, digest,
         target_kind, target_id, workflow._json(result), workflow._now()))


def _operation_result(reservation, *, state=None):
    result = _reservation(reservation)
    if state is not None:
        result["operation_state"] = state
    result["synthetic"] = True
    return result


def create_reservation(connection, payload):
    allowed = {"actor_id", "idempotency_key", "pool_id", "candidate", "pool_version", "baseline_version",
               "owner_reference", "service_reference", "reason", "duration_hours"}
    workflow._payload(payload, allowed)
    actor = workflow.require_actor(payload.get("actor_id"), "inventory_edit")
    context = _context()
    key = _text(payload.get("idempotency_key"), "idempotency_key", 200)
    normalized = {"actor_id": actor["id"], "idempotency_key": key,
                  "pool_id": _text(payload.get("pool_id"), "pool_id", 200),
                  "candidate": _text(payload.get("candidate"), "candidate", 200),
                  "pool_version": _version(payload.get("pool_version"), "pool_version"),
                  "baseline_version": _version(payload.get("baseline_version"), "baseline_version"),
                  "owner_reference": _text(payload.get("owner_reference"), "owner_reference", 200),
                  "service_reference": _text(payload.get("service_reference"), "service_reference", 200),
                  "reason": _text(payload.get("reason"), "reason", 2000),
                  "duration_hours": _duration(payload.get("duration_hours"))}
    try:
        address = ip_address(normalized["candidate"])
        if address.version != 4:
            raise ValueError("IPv4 required")
        normalized["candidate"] = str(address)
    except ValueError as exc:
        raise AppError("INVALID_INPUT", "candidate must be an IPv4 address.", 422, {"field": "candidate"}) from exc
    digest = workflow._hash(normalized)
    replay = _receipt(connection, context, "reservation.create", key, digest)
    if replay is not None:
        return replay, True
    pool, ranges, exclusions = _pool_for(connection, normalized["pool_id"])
    meta = connection.execute("SELECT baseline_version,demo_clock_at FROM app_meta WHERE singleton=1").fetchone()
    if (pool["pool_version"] != normalized["pool_version"]
            or meta["baseline_version"] != normalized["baseline_version"]):
        raise AppError("STALE_REVIEW", "Pool or intended-ledger version changed. Refresh and review again.", 409)
    limitations = workflow._eligibility(connection, pool, ranges, exclusions, normalized["candidate"],
                                        meta["demo_clock_at"])
    now = _now()
    expires = now + timedelta(hours=normalized["duration_hours"])
    object_id = str(uuid4())
    after = {"state": "reserved", "version": 1, "expires_at": _stamp(expires),
             "owner_reference": normalized["owner_reference"], "service_reference": normalized["service_reference"]}
    connection.execute(
        "INSERT INTO reservations(id,scope_id,prefix_id,pool_id,family,address,address_hex,owner_reference,service_reference,"
        "created_by,reason,created_at,expires_at,version,policy_revision,state) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'reserved')",
        (object_id, pool["scope_id"], pool["prefix_id"], pool["id"], 4, normalized["candidate"],
         f"{int(address):032x}", normalized["owner_reference"], normalized["service_reference"], actor["id"],
         normalized["reason"], _stamp(now), _stamp(expires), 1, context.policy_revision))
    connection.execute(
        "INSERT INTO reservation_history(id,reservation_id,version,action,actor_id,occurred_at,reason,before_json,after_json) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (str(uuid4()), object_id, 1, "created", actor["id"], workflow._now(), normalized["reason"], None,
         workflow._json(after)))
    connection.execute("UPDATE pools SET pool_version=pool_version+1 WHERE id=?", (pool["id"],))
    connection.execute("UPDATE app_meta SET baseline_version=baseline_version+1 WHERE singleton=1")
    workflow.audit_event(connection, actor_id=actor["id"], action="reservation.create", outcome="succeeded",
                         reason=normalized["reason"], subject_id=object_id, scope_id=pool["scope_id"],
                         pool_id=pool["id"], address=normalized["candidate"],
                         details={"before": None, "after": after, "limitations": limitations,
                                  "pool_version": pool["pool_version"] + 1,
                                  "baseline_version": meta["baseline_version"] + 1,
                                  "capacity_history_version_changed": False})
    result = _operation_result(connection.execute("SELECT * FROM reservations WHERE id=?", (object_id,)).fetchone())
    _save_receipt(connection, context, "reservation.create", key, digest, "reservation", object_id, result)
    return result, False


def extend_reservation(connection, reservation_id, payload):
    workflow._payload(payload, {"actor_id", "idempotency_key", "expected_version", "expected_pool_version",
                                "expected_baseline_version", "duration_hours", "reason"})
    actor = workflow.require_actor(payload.get("actor_id"), "inventory_edit")
    context = _context()
    object_id = _uuid(reservation_id)
    current = _resource(connection, object_id)
    key = _text(payload.get("idempotency_key"), "idempotency_key", 200)
    normalized = {"actor_id": actor["id"], "idempotency_key": key, "reservation_id": object_id,
                  "expected_version": _version(payload.get("expected_version"), "expected_version"),
                  "expected_pool_version": _version(payload.get("expected_pool_version"), "expected_pool_version"),
                  "expected_baseline_version": _version(payload.get("expected_baseline_version"), "expected_baseline_version"),
                  "duration_hours": _duration(payload.get("duration_hours")),
                  "reason": _text(payload.get("reason"), "reason", 2000)}
    digest = workflow._hash(normalized)
    replay = _receipt(connection, context, "reservation.extend", key, digest)
    if replay is not None:
        return replay, True
    if current["state"] != "reserved":
        raise AppError("RESERVATION_TERMINAL", "Only a current reserved hold can be extended.", 409)
    pool, ranges, exclusions = _pool_for(connection, current["pool_id"], current["scope_id"])
    meta = connection.execute("SELECT baseline_version,demo_clock_at FROM app_meta WHERE singleton=1").fetchone()
    if (current["version"] != normalized["expected_version"] or pool["pool_version"] != normalized["expected_pool_version"]
            or meta["baseline_version"] != normalized["expected_baseline_version"]):
        raise AppError("STALE_REVIEW", "Reservation, pool, or intended-ledger version changed.", 409)
    limitations = workflow._eligibility(connection, pool, ranges, exclusions, current["address"],
                                        meta["demo_clock_at"], reservation_id=object_id)
    now = _now()
    expires = now + timedelta(hours=normalized["duration_hours"])
    next_version = current["version"] + 1
    before = {key: current[key] for key in ("state", "version", "expires_at")}
    after = {"state": "reserved", "version": next_version, "expires_at": _stamp(expires)}
    changed = connection.execute(
        "UPDATE reservations SET expires_at=?,version=? WHERE id=? AND state='reserved' AND version=?",
        (_stamp(expires), next_version, object_id, current["version"]))
    if changed.rowcount != 1:
        raise AppError("STALE_RESERVATION", "The reservation changed during extension.", 409)
    connection.execute(
        "INSERT INTO reservation_history(id,reservation_id,version,action,actor_id,occurred_at,reason,before_json,after_json) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (str(uuid4()), object_id, next_version, "extended", actor["id"], workflow._now(), normalized["reason"],
         workflow._json(before), workflow._json(after)))
    connection.execute("UPDATE pools SET pool_version=pool_version+1 WHERE id=?", (pool["id"],))
    connection.execute("UPDATE app_meta SET baseline_version=baseline_version+1 WHERE singleton=1")
    workflow.audit_event(connection, actor_id=actor["id"], action="reservation.extend", outcome="succeeded",
                         reason=normalized["reason"], subject_id=object_id, scope_id=current["scope_id"],
                         pool_id=pool["id"], address=current["address"],
                         details={"before": before, "after": after, "limitations": limitations,
                                  "pool_version": pool["pool_version"] + 1,
                                  "baseline_version": meta["baseline_version"] + 1,
                                  "capacity_history_version_changed": False})
    result = _operation_result(connection.execute("SELECT * FROM reservations WHERE id=?", (object_id,)).fetchone())
    _save_receipt(connection, context, "reservation.extend", key, digest, "reservation", object_id, result)
    return result, False


def _release_eligibility(connection, reservation):
    allocation = connection.execute(
        "SELECT id FROM allocations WHERE scope_id=? AND family=4 AND address=?",
        (reservation["scope_id"], reservation["address"])).fetchone()
    if allocation:
        raise AppError("RESERVATION_IN_USE", "An intended allocation exists for this reservation.", 409)
    pending_effect = connection.execute(
        "SELECT ti.id FROM ticket_intents ti JOIN allocation_requests ar ON ar.id=ti.source_request_id "
        "WHERE ar.reservation_id=? AND ti.state IN ('pending','routing_blocked','unknown') LIMIT 1",
        (reservation["id"],)).fetchone()
    if pending_effect:
        raise AppError("EXTERNAL_EFFECT_UNRESOLVED", "An applicable ticket simulation remains unresolved.", 409)


def create_release_request(connection, reservation_id, payload):
    workflow._payload(payload, {"actor_id", "idempotency_key", "expected_version", "expected_pool_version",
                                "expected_baseline_version", "reason"})
    actor = workflow.require_actor(payload.get("actor_id"), "inventory_edit")
    context = _context()
    object_id = _uuid(reservation_id)
    current = _resource(connection, object_id)
    key = _text(payload.get("idempotency_key"), "idempotency_key", 200)
    normalized = {"actor_id": actor["id"], "idempotency_key": key, "reservation_id": object_id,
                  "expected_version": _version(payload.get("expected_version"), "expected_version"),
                  "expected_pool_version": _version(payload.get("expected_pool_version"), "expected_pool_version"),
                  "expected_baseline_version": _version(payload.get("expected_baseline_version"), "expected_baseline_version"),
                  "reason": _text(payload.get("reason"), "reason", 2000)}
    digest = workflow._hash(normalized)
    replay = _receipt(connection, context, "reservation.release.decision", key, digest)
    if replay is not None:
        return replay, True
    old = connection.execute("SELECT * FROM reservation_release_requests WHERE requester_id=? AND idempotency_key=?",
                             (actor["id"], key)).fetchone()
    if old:
        if old["payload_digest"] != digest:
            raise AppError("IDEMPOTENCY_CONFLICT", "This operation key already identifies a different payload.", 409)
        return _release_request_payload(old), True
    if current["state"] != "reserved":
        raise AppError("RESERVATION_TERMINAL", "Only an unused active reservation can be proposed for release.", 409)
    pool, _, _ = _pool_for(connection, current["pool_id"], current["scope_id"])
    meta = connection.execute("SELECT baseline_version FROM app_meta WHERE singleton=1").fetchone()
    if (current["version"] != normalized["expected_version"] or pool["pool_version"] != normalized["expected_pool_version"]
            or meta["baseline_version"] != normalized["expected_baseline_version"]):
        raise AppError("STALE_REVIEW", "Reservation, pool, or intended-ledger version changed.", 409)
    _release_eligibility(connection, current)
    request_id = str(uuid4())
    connection.execute(
        "INSERT INTO reservation_release_requests(id,reservation_id,reservation_version,requester_id,idempotency_key,"
        "payload_digest,reason,expected_pool_version,expected_baseline_version,state,created_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,'pending',?)",
        (request_id, object_id, current["version"], actor["id"], key, digest, normalized["reason"],
         pool["pool_version"], meta["baseline_version"], workflow._now()))
    workflow.audit_event(connection, actor_id=actor["id"], action="reservation.release.propose", outcome="succeeded",
                         reason=normalized["reason"], subject_id=request_id, scope_id=current["scope_id"],
                         pool_id=current["pool_id"], address=current["address"],
                         details={"reservation_id": object_id, "reservation_version": current["version"],
                                  "pool_version": pool["pool_version"], "baseline_version": meta["baseline_version"],
                                  "reservation_state": "reserved"})
    result = _release_request_payload(connection.execute(
        "SELECT * FROM reservation_release_requests WHERE id=?", (request_id,)).fetchone())
    _save_receipt(connection, context, "reservation.release.decision", key, digest, "reservation_release_request",
                  request_id, result)
    return result, False


def _release_request_payload(row):
    return {key: row[key] for key in row.keys()} | {"synthetic": True}


def decide_release_request(connection, reservation_id, request_id, payload):
    workflow._payload(payload, {"actor_id", "idempotency_key", "action", "expected_version",
                                "expected_pool_version", "expected_baseline_version", "reason"})
    actor = workflow.require_actor(payload.get("actor_id"), "approve")
    context = _context()
    reservation_id, request_id = _uuid(reservation_id), _uuid(request_id)
    current = _resource(connection, reservation_id)
    request = connection.execute(
        "SELECT * FROM reservation_release_requests WHERE id=? AND reservation_id=?", (request_id, reservation_id)).fetchone()
    if request is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    if request["requester_id"] == actor["id"]:
        raise AppError("SELF_APPROVAL_FORBIDDEN", "A different permitted principal must decide this release.", 403)
    action = payload.get("action")
    if action not in ("approve", "reject"):
        raise AppError("INVALID_INPUT", "Use approve or reject.", 422, {"field": "action"})
    key = _text(payload.get("idempotency_key"), "idempotency_key", 200)
    normalized = {"actor_id": actor["id"], "idempotency_key": key, "reservation_id": reservation_id,
                  "request_id": request_id, "action": action,
                  "expected_version": _version(payload.get("expected_version"), "expected_version"),
                  "expected_pool_version": _version(payload.get("expected_pool_version"), "expected_pool_version"),
                  "expected_baseline_version": _version(payload.get("expected_baseline_version"), "expected_baseline_version"),
                  "reason": _text(payload.get("reason"), "reason", 2000)}
    digest = workflow._hash(normalized)
    replay = _receipt(connection, context, "reservation.release.decision", key, digest)
    if replay is not None:
        return replay, True
    if request["state"] != "pending":
        raise AppError("RELEASE_REQUEST_TERMINAL", "This release request already has an immutable decision.", 409)
    if current["state"] != "reserved":
        raise AppError("RESERVATION_TERMINAL", "This reservation is no longer active.", 409)
    pool, _, _ = _pool_for(connection, current["pool_id"], current["scope_id"])
    meta = connection.execute("SELECT baseline_version FROM app_meta WHERE singleton=1").fetchone()
    expected = (normalized["expected_version"], normalized["expected_pool_version"],
                normalized["expected_baseline_version"])
    reviewed = (request["reservation_version"], request["expected_pool_version"], request["expected_baseline_version"])
    live = (current["version"], pool["pool_version"], meta["baseline_version"])
    if expected != reviewed or live != reviewed:
        raise AppError("STALE_REVIEW", "Reservation, pool, or intended-ledger version changed since the release proposal.", 409)
    _release_eligibility(connection, current)
    now = workflow._now()
    next_version = current["version"]
    before = {key: current[key] for key in ("state", "version", "released_at")}
    after = {"state": "reserved", "version": current["version"]}
    if action == "approve":
        next_version += 1
        after = {"state": "released", "version": next_version, "released_at": now}
        changed = connection.execute(
            "UPDATE reservations SET state='released',version=?,released_at=? WHERE id=? AND state='reserved' AND version=?",
            (next_version, now, reservation_id, current["version"]))
        if changed.rowcount != 1:
            raise AppError("STALE_RESERVATION", "The reservation changed during release approval.", 409)
        connection.execute(
            "INSERT INTO reservation_history(id,reservation_id,version,action,actor_id,occurred_at,reason,before_json,after_json) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (str(uuid4()), reservation_id, next_version, "released", actor["id"], now, normalized["reason"],
             workflow._json(before), workflow._json(after)))
        connection.execute("UPDATE pools SET pool_version=pool_version+1 WHERE id=?", (pool["id"],))
        connection.execute("UPDATE app_meta SET baseline_version=baseline_version+1 WHERE singleton=1")
    changed = connection.execute(
        "UPDATE reservation_release_requests SET state=?,decided_at=?,approver_id=?,decision_reason=? "
        "WHERE id=? AND state='pending'",
        ("approved" if action == "approve" else "rejected", now, actor["id"], normalized["reason"], request_id))
    if changed.rowcount != 1:
        raise AppError("RELEASE_REQUEST_TERMINAL", "This release request already has an immutable decision.", 409)
    workflow.audit_event(connection, actor_id=actor["id"], action="reservation.release.decision", outcome="succeeded",
                         reason=normalized["reason"], subject_id=reservation_id, request_id=request_id,
                         scope_id=current["scope_id"], pool_id=current["pool_id"], address=current["address"],
                         details={"decision": action, "before": before, "after": after,
                                  "pool_version": pool["pool_version"] + (action == "approve"),
                                  "baseline_version": meta["baseline_version"] + (action == "approve"),
                                  "capacity_history_version_changed": False,
                                  "authority": "local_static_ledger"})
    result = _release_request_payload(connection.execute(
        "SELECT * FROM reservation_release_requests WHERE id=?", (request_id,)).fetchone())
    _save_receipt(connection, context, "reservation.release.decision", key, digest, "reservation_release_request",
                  request_id, result)
    return result, False
