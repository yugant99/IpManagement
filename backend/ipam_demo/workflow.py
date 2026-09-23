"""Fixed synthetic actors, exact-candidate allocation and a separate exception queue.

Mutations use the caller's BEGIN IMMEDIATE transaction. This module never commits;
the API records failed attempts in a fresh transaction after rollback.
"""

from datetime import datetime, timezone
from contextvars import ContextVar
from hashlib import sha256
from ipaddress import ip_address, ip_network
import json
from uuid import UUID, uuid4

from .errors import AppError
from . import access
from .evidence import active_dhcp_claims
from .inventory import pool_payload
from .rules import comparable_findings, discrepancy_keys
from .seed import _ranges

STATIC_POOL_ID = "8821c420-18ea-4caa-9d97-83a331c0c002"
_access_context = ContextVar("ipam_access_context", default=None)


def bind_access_context(context):
    """Bind this request's freshly authenticated principal for existing domain helpers."""
    return _access_context.set(context)


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value):
    return sha256(_json(value).encode("utf-8")).hexdigest()


def actors():
    context = _access_context.get()
    if context is None:
        return []
    permissions = []
    if "requester" in context.roles:
        permissions.append("request")
    if "approver" in context.roles:
        permissions.append("approve")
    if "operator" in context.roles:
        permissions.extend(("inventory_edit", "exception"))
    role = "coordinator" if context.is_evidence_coordinator else ",".join(
        role for role in context.roles if role != "viewer") or "viewer"
    return [{"id": context.principal_id, "name": context.principal_id,
             "role": role,
             "team": None, "permissions": permissions}]


def require_actor(actor_id, permission=None):
    context = _access_context.get()
    if context is None:
        raise AppError("AUTHENTICATION_REQUIRED", "A valid bearer credential is required.", 401)
    access.require_actor_match(context, actor_id)
    roles = {"request": "requester", "approve": "approver",
             "inventory_edit": "operator", "exception": "operator"}
    if permission:
        role = roles.get(permission)
        if role is None:
            raise AppError("FORBIDDEN", "The current principal is not permitted to perform this operation.", 403)
        access.require_role(context, role)
    return actors()[0]


def _text(value, field, maximum=500):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise AppError("INVALID_INPUT", f"{field} must be nonempty text, at most {maximum} characters.", 422,
                       {"field": field})
    return value.strip()


def _version(value, field):
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise AppError("INVALID_INPUT", f"{field} must be a positive integer.", 422, {"field": field})
    return value


def _payload(payload, allowed):
    if not isinstance(payload, dict) or set(payload) - set(allowed):
        raise AppError("INVALID_INPUT", "Payload must be an object with only the documented fields.", 422)


def audit_event(connection, *, actor_id, action, outcome, reason, request_id=None,
                subject_id=None, scope_id=None, pool_id=None, address=None, details=None):
    """Shared inventory/workflow audit, atomic with a successful local mutation."""
    context = _access_context.get()
    actor = actors()[0] if context is not None and actor_id == context.principal_id else None
    if actor_id == "system" and outcome != "failed" and context is not None and context.is_evidence_coordinator:
        actor = {"role": "system"}
    if actor is None and outcome != "failed":
        raise AppError("FORBIDDEN", "A successful mutation needs the authenticated principal.", 403)
    item = {"id": str(uuid4()), "created_at": _now(),
            "actor_id": (actor_id if actor is not None else "unknown"),
            "actor_role": actor["role"] if actor else "unknown", "action": action,
            "outcome": outcome, "reason": _text(reason, "reason", 2000), "request_id": request_id,
            "subject_id": subject_id, "scope_id": scope_id, "pool_id": pool_id,
            "address": address, "details": details or {}}
    connection.execute(
        "INSERT INTO audit_events(id,created_at,actor_id,actor_role,action,outcome,reason,request_id,"
        "subject_id,scope_id,pool_id,address,details_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (*[item[key] for key in ("id", "created_at", "actor_id", "actor_role", "action", "outcome", "reason",
                                "request_id", "subject_id", "scope_id", "pool_id", "address")],
         _json(item["details"])))
    return item


def list_audit(connection, request_id=None, subject_id=None):
    items = []
    for row in connection.execute("SELECT * FROM audit_events ORDER BY created_at DESC, id DESC"):
        if request_id and row["request_id"] != request_id:
            continue
        if subject_id and row["subject_id"] != subject_id:
            continue
        item = dict(row)
        item["details"] = json.loads(item.pop("details_json"))
        items.append(item)
    return items


def _pool(connection, object_id=STATIC_POOL_ID):
    if object_id != STATIC_POOL_ID:
        raise AppError("POOL_NOT_AUTHORIZED", "Only the designated North static IPv4 pool supports this flow.", 422)
    row = connection.execute(
        "SELECT p.*, n.cidr FROM pools p JOIN prefixes n ON n.id=p.prefix_id WHERE p.id=?", (object_id,)
    ).fetchone()
    if row is None:
        raise AppError("POOL_UNAVAILABLE", "The designated static pool is absent from the intended ledger.", 409)
    pool = dict(row)
    if pool["family"] != 4 or pool["management_mode"] != "static" or pool["allocation_authority"] != "local":
        raise AppError("POOL_NOT_AUTHORIZED", "The designated pool must retain authoritative local static IPv4 policy.", 409)
    try:
        network = ip_network(pool["cidr"])
        ranges = _ranges(json.loads(pool["ranges"]), network)
        exclusions = _ranges(json.loads(pool["exclusions"]), network)
        if not ranges or any(not any(a <= x <= y <= b for a, b in ranges) for x, y in exclusions):
            raise ValueError("Exclusions must be inside the configured ranges")
        if sum(b - a + 1 for a, b in ranges) <= sum(b - a + 1 for a, b in exclusions):
            raise ValueError("Assignable capacity must be positive")
    except (ValueError, KeyError, TypeError) as exc:
        raise AppError("INVALID_CAPACITY", "The designated pool has invalid ranges or exclusions; allocation is blocked.",
                       409, {"reason": str(exc)}) from exc
    return pool, ranges, exclusions


def _eligibility(connection, pool, ranges, exclusions, candidate, clock, *, reservation_id=None):
    address = ip_address(candidate)
    if address.version != 4 or not any(a <= int(address) <= b for a, b in ranges):
        raise AppError("CANDIDATE_OUTSIDE_POOL", "The exact candidate is outside the pool's assignable ranges.", 409)
    if any(a <= int(address) <= b for a, b in exclusions):
        raise AppError("CANDIDATE_EXCLUDED", "The exact candidate is excluded by pool policy.", 409)
    held = connection.execute(
        "SELECT id FROM reservations WHERE scope_id=? AND family=4 AND address=? AND state='reserved'",
        (pool["scope_id"], candidate)).fetchone()
    if held and held["id"] != reservation_id:
        raise AppError("CANDIDATE_RESERVED", "The exact candidate is held by an active reservation.", 409)
    allocation = connection.execute(
        "SELECT id FROM allocations WHERE scope_id=? AND family=4 AND address=?", (pool["scope_id"], candidate)
    ).fetchone()
    if allocation:
        raise AppError("CANDIDATE_OCCUPIED", "The exact candidate already has an intended allocation in this scope.",
                       409, {"allocation_id": allocation["id"]})
    evidence = active_dhcp_claims(connection, pool["scope_id"], 4, candidate, clock)
    if evidence["claims"]:
        raise AppError("CANDIDATE_OBSERVED", "Current eligible DHCP evidence contradicts allocation of this candidate.",
                       409, {"evidence": "eligible_dhcp_observation"})
    return evidence.get("unknown_reasons", [])


def _require_scope_domain(connection, scope_id):
    context = _access_context.get()
    if (context is None or context.selected_domain is None or context.selected_domain not in context.domains
            or context.is_evidence_coordinator):
        raise AppError("FORBIDDEN", "Select a permitted domain before accessing domain data.", 403)
    row = connection.execute("SELECT domain FROM scopes WHERE id=?", (scope_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    access.require_domain_access(context, row["domain"])


def _require_pool_domain(connection, pool_id):
    context = _access_context.get()
    if (context is None or context.selected_domain is None or context.selected_domain not in context.domains
            or context.is_evidence_coordinator):
        raise AppError("FORBIDDEN", "Select a permitted domain before accessing domain data.", 403)
    row = connection.execute(
        "SELECT s.domain FROM pools p JOIN scopes s ON s.id=p.scope_id WHERE p.id=?", (pool_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    access.require_domain_access(context, row["domain"])


def _matching_reservation(connection, reservation_id, pool, normalized):
    row = connection.execute(
        "SELECT r.* FROM reservations r WHERE r.id=?", (reservation_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    _require_scope_domain(connection, row["scope_id"])
    if (row["state"] != "reserved" or row["scope_id"] != pool["scope_id"] or row["pool_id"] != pool["id"]
            or row["family"] != 4 or row["address"] != normalized["candidate"]
            or row["owner_reference"] != normalized["owner"]
            or row["service_reference"] != normalized["service_reference"]):
        raise AppError("RESERVATION_MISMATCH", "The current reservation does not match this allocation request.", 409)
    return row


def workflow_status(connection):
    pool, _, _ = _pool(connection)
    meta = connection.execute("SELECT baseline_version,demo_clock_at FROM app_meta WHERE singleton=1").fetchone()
    return {"actors": actors(), "pool": pool_payload(pool), "baseline_version": meta["baseline_version"],
            "demo_clock_at": meta["demo_clock_at"], "synthetic": True,
            "limitations": ["The local static ledger is authoritative only inside this demo.",
                            "Pending requests do not reserve addresses. Approval rechecks the exact candidate and versions.",
                            "Local approval changes only the local ledger.",
                            "Ticket delivery is a separate simulated handoff.",
                            "External provisioning is unsupported and not requested; stored legacy "
                            "downstream status remains historical."]}


def _request_payload(row):
    item = dict(row)
    item["payload"] = json.loads(item.pop("payload_json"))
    item.pop("payload_hash")
    item.pop("decision_hash")
    item["synthetic"] = True
    item["local_outcome"] = "allocated" if item["state"] == "approved" else "unchanged"
    return item


def get_request(connection, object_id):
    row = connection.execute("SELECT * FROM allocation_requests WHERE id=?", (object_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "No allocation request exists with that ID.", 404)
    return _request_payload(row)


def list_requests(connection):
    return [_request_payload(row) for row in connection.execute(
        "SELECT * FROM allocation_requests ORDER BY created_at DESC,id DESC")]


def create_request(connection, payload, *, configuration):
    """Create a request and, for a new row only, its one simulated handoff intent.

    ``configuration`` is the reviewed configuration already bound by the caller's
    write boundary; it supplies routing. Replays never backfill an intent.
    """
    _payload(payload, ("actor_id", "idempotency_key", "pool_id", "candidate", "pool_version", "baseline_version",
                       "owner", "purpose", "reason", "supersedes_request_id", "reservation_id",
                       "service_reference", "reservation_version"))
    actor = require_actor(payload.get("actor_id"), "request")
    normalized = {key: _text(payload.get(key), key, 200 if key != "reason" else 500)
                  for key in ("idempotency_key", "pool_id", "candidate", "owner", "purpose", "reason")}
    normalized["actor_id"] = actor["id"]
    for key in ("pool_version", "baseline_version"):
        normalized[key] = _version(payload.get(key), key)
    reservation_id = payload.get("reservation_id")
    if reservation_id is not None:
        try:
            reservation_id = str(UUID(reservation_id))
        except (ValueError, TypeError, AttributeError) as exc:
            raise AppError("INVALID_INPUT", "reservation_id must be a UUID.", 422, {"field": "reservation_id"}) from exc
        normalized["reservation_id"] = reservation_id
        normalized["service_reference"] = _text(payload.get("service_reference"), "service_reference", 200)
        normalized["reservation_version"] = _version(payload.get("reservation_version"), "reservation_version")
    elif any(key in payload for key in ("service_reference", "reservation_version")):
        raise AppError("INVALID_INPUT", "service_reference and reservation_version require reservation_id.", 422)
    try:
        address = ip_address(normalized["candidate"])
        if address.version != 4:
            raise ValueError("IPv4 is required")
        normalized["candidate"] = str(address)
        previous = payload.get("supersedes_request_id")
        normalized["supersedes_request_id"] = str(UUID(previous)) if previous is not None else None
    except (ValueError, TypeError, AttributeError) as exc:
        raise AppError("INVALID_INPUT", "Candidate must be IPv4 and supersedes_request_id must be a UUID.", 422) from exc
    digest = _hash(normalized)
    old = connection.execute("SELECT * FROM allocation_requests WHERE actor_id=? AND idempotency_key=?",
                             (actor["id"], normalized["idempotency_key"])).fetchone()
    if old:
        _require_scope_domain(connection, old["scope_id"])
        if old["payload_hash"] != digest:
            raise AppError("IDEMPOTENCY_CONFLICT", "This creation key already identifies a different payload.", 409)
        return _request_payload(old), True
    if normalized["supersedes_request_id"]:
        previous_row = connection.execute("SELECT * FROM allocation_requests WHERE id=?",
                                          (normalized["supersedes_request_id"],)).fetchone()
        if previous_row is None:
            get_request(connection, normalized["supersedes_request_id"])
        _require_scope_domain(connection, previous_row["scope_id"])
        previous = _request_payload(previous_row)
        if previous["actor_id"] != actor["id"]:
            raise AppError("FORBIDDEN", "A renewed review may supersede only your own request.", 403)
    _require_pool_domain(connection, normalized["pool_id"])
    pool, ranges, exclusions = _pool(connection, normalized["pool_id"])
    if reservation_id:
        reservation = _matching_reservation(connection, reservation_id, pool, normalized)
        if reservation["version"] != normalized["reservation_version"]:
            raise AppError("STALE_RESERVATION", "The reservation changed; refresh it before requesting conversion.", 409)
    meta = connection.execute("SELECT baseline_version,demo_clock_at FROM app_meta WHERE singleton=1").fetchone()
    if (pool["pool_version"] != normalized["pool_version"]
            or meta["baseline_version"] != normalized["baseline_version"]):
        raise AppError("STALE_REVIEW", "Pool or intended-ledger version changed. Refresh and create a new review.", 409)
    limitations = _eligibility(connection, pool, ranges, exclusions, normalized["candidate"], meta["demo_clock_at"],
                               reservation_id=reservation_id)
    object_id, created_at = str(uuid4()), _now()
    connection.execute(
        "INSERT INTO allocation_requests(id,actor_id,idempotency_key,payload_hash,payload_json,pool_id,scope_id,"
        "candidate,pool_version,baseline_version,state,created_at,reservation_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (object_id, actor["id"], normalized["idempotency_key"], digest, _json(normalized), pool["id"], pool["scope_id"],
         normalized["candidate"], pool["pool_version"], meta["baseline_version"], "pending", created_at, reservation_id))
    audit_event(connection, actor_id=actor["id"], action="allocation.request", outcome="succeeded",
                reason=normalized["reason"], request_id=object_id, subject_id=object_id, scope_id=pool["scope_id"],
                pool_id=pool["id"], address=normalized["candidate"],
                details={"before": None, "after": {"state": "pending"}, "pool_version": pool["pool_version"],
                         "baseline_version": meta["baseline_version"], "limitations": limitations,
                         "authority": "local_static_ledger", "reserved": bool(reservation_id),
                         "reservation_id": reservation_id})
    # Imported here because ticket_handoff depends on this module's helpers.
    from . import ticket_handoff
    ticket_handoff.create_intent(connection, object_id, context=_access_context.get(), configuration=configuration)
    return get_request(connection, object_id), False


def decide_request(connection, object_id, payload):
    _payload(payload, ("actor_id", "action", "reason", "simulate_failure"))
    actor = require_actor(payload.get("actor_id"), "approve")
    action = payload.get("action")
    if action not in ("approve", "reject") or not isinstance(payload.get("simulate_failure", False), bool):
        raise AppError("INVALID_INPUT", "Use approve or reject and a boolean simulate_failure flag.", 422)
    reason = _text(payload.get("reason"), "reason")
    simulation = payload.get("simulate_failure", False)
    if action == "reject" and simulation:
        raise AppError("INVALID_INPUT", "Provisioning simulation is available only for approval.", 422)
    digest = _hash({"actor_id": actor["id"], "action": action, "reason": reason, "simulate_failure": simulation})
    row = connection.execute("SELECT * FROM allocation_requests WHERE id=?", (object_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "No allocation request exists with that ID.", 404)
    _require_scope_domain(connection, row["scope_id"])
    # Intent-backed requests keep the local decision independent of the ticket handoff.
    # Legacy rows without an intent retain their historical simulated downstream status.
    tracked = connection.execute(
        "SELECT 1 FROM ticket_intents WHERE source_request_id=? AND action='allocation.request'",
        (object_id,)).fetchone() is not None
    if tracked and simulation:
        raise AppError("SIMULATION_UNSUPPORTED", "This request uses the separate simulated ticket handoff; "
                       "local decisions do not simulate delivery or provisioning.", 422, {"field": "simulate_failure"})
    if row["actor_id"] == actor["id"]:
        raise AppError("SELF_APPROVAL_FORBIDDEN", "A request needs a different permitted decision actor.", 403)
    if row["state"] != "pending":
        if row["decision_hash"] == digest:
            return _request_payload(row), True
        raise AppError("REQUEST_TERMINAL", "This request is immutable. Fetch its result or create a renewed review.", 409)
    stored = _request_payload(row)
    before = {"state": "pending", "pool_version": row["pool_version"], "baseline_version": row["baseline_version"]}
    allocation_id, downstream, limitations = None, "not_requested", []
    after = {"state": "rejected"}
    reservation = None
    before_reservation = after_reservation = None
    if action == "approve":
        _require_pool_domain(connection, row["pool_id"])
        pool, ranges, exclusions = _pool(connection, row["pool_id"])
        meta = connection.execute("SELECT baseline_version,demo_clock_at FROM app_meta WHERE singleton=1").fetchone()
        if pool["pool_version"] != row["pool_version"] or meta["baseline_version"] != row["baseline_version"]:
            raise AppError("STALE_REVIEW", "Reviewed pool or intended-ledger version changed; no address was allocated.", 409,
                           {"reviewed_pool_version": row["pool_version"], "current_pool_version": pool["pool_version"],
                            "reviewed_baseline_version": row["baseline_version"], "current_baseline_version": meta["baseline_version"]})
        stored_payload = stored["payload"]
        if row["reservation_id"] is not None:
            if (stored_payload.get("reservation_id") != row["reservation_id"]
                    or "service_reference" not in stored_payload or "reservation_version" not in stored_payload):
                raise AppError("RESERVATION_MISMATCH", "The saved allocation request has incomplete reservation identity.", 409)
            reservation = _matching_reservation(connection, row["reservation_id"], pool, stored_payload)
            if reservation["version"] != stored_payload["reservation_version"]:
                raise AppError("STALE_RESERVATION", "The reservation changed; renewed review is required.", 409)
        elif any(key in stored_payload for key in ("service_reference", "reservation_version")):
            raise AppError("RESERVATION_MISMATCH", "The saved allocation request has incomplete reservation identity.", 409)
        limitations = _eligibility(connection, pool, ranges, exclusions, row["candidate"], meta["demo_clock_at"],
                                   reservation_id=row["reservation_id"])
        allocation_id = str(uuid4())
        origin = {"source_id": "local-demo-workflow", "source_run_id": object_id, "source_record_id": allocation_id,
                  "observed_at": meta["demo_clock_at"], "ingested_at": _now(), "synthetic": True}
        connection.execute(
            "INSERT INTO allocations(id,scope_id,prefix_id,pool_id,family,address,address_hex,owner,purpose,origin) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)", (allocation_id, pool["scope_id"], pool["prefix_id"], pool["id"], 4,
            row["candidate"], f"{int(ip_address(row['candidate'])):032x}", stored["payload"]["owner"],
            stored["payload"]["purpose"], _json(origin)))
        if reservation is not None:
            before_reservation = {key: reservation[key] for key in ("state", "version", "expires_at", "converted_allocation_id")}
            next_version = reservation["version"] + 1
            updated = connection.execute(
                "UPDATE reservations SET state='converted',version=?,converted_allocation_id=? "
                "WHERE id=? AND state='reserved' AND version=?",
                (next_version, allocation_id, reservation["id"], reservation["version"]))
            if updated.rowcount != 1:
                raise AppError("STALE_RESERVATION", "The reservation changed during allocation approval.", 409)
            after_reservation = {"state": "converted", "version": next_version,
                                 "expires_at": reservation["expires_at"], "converted_allocation_id": allocation_id}
            connection.execute(
                "INSERT INTO reservation_history(id,reservation_id,version,action,actor_id,occurred_at,reason,before_json,after_json) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (str(uuid4()), reservation["id"], next_version, "converted", actor["id"], _now(), reason,
                 _json(before_reservation), _json(after_reservation)))
        connection.execute("UPDATE pools SET pool_version=pool_version+1 WHERE id=?", (pool["id"],))
        connection.execute("UPDATE app_meta SET baseline_version=baseline_version+1 WHERE singleton=1")
        downstream = "not_requested" if tracked else "simulated_failure" if simulation else "simulated_success"
        after = {"state": "approved", "allocation_id": allocation_id, "pool_version": pool["pool_version"] + 1,
                 "baseline_version": meta["baseline_version"] + 1, "local_outcome": "allocated", "downstream_status": downstream}
    connection.execute(
        "UPDATE allocation_requests SET state=?,allocation_id=?,decided_at=?,decision_actor_id=?,decision_hash=?,"
        "decision_reason=?,downstream_status=? WHERE id=?", (after["state"], allocation_id, _now(), actor["id"],
        digest, reason, downstream, object_id))
    audit_event(connection, actor_id=actor["id"], action=f"allocation.{action}", outcome="succeeded", reason=reason,
                request_id=object_id, subject_id=object_id, scope_id=row["scope_id"], pool_id=row["pool_id"],
                address=row["candidate"], details={"before": before, "after": after, "limitations": limitations})
    if action == "approve" and reservation is not None:
        audit_event(connection, actor_id=actor["id"], action="reservation.convert", outcome="succeeded", reason=reason,
                    request_id=object_id, subject_id=reservation["id"], scope_id=row["scope_id"], pool_id=row["pool_id"],
                    address=row["candidate"], details={"before": before_reservation, "after": after_reservation,
                                                      "allocation_id": allocation_id,
                                                      "authority": "local_static_ledger"})
    return get_request(connection, object_id), False


def sync_exceptions(connection, run):
    """Track current comparable evidence separately; notify on semantic changes."""
    newest = connection.execute("SELECT id FROM calculation_runs ORDER BY rowid DESC LIMIT 1").fetchone()
    if newest is None:
        raise AppError("EXCEPTION_EVIDENCE_MISSING", "Save the calculation run before updating exceptions.", 500)
    if newest["id"] != run["id"]:
        # Immutable historical runs may be reread, never reapplied as current evidence.
        return 0
    current = {}
    for finding in run["findings"]:
        subject = finding["subject"]
        key = _json([finding["rule_id"], subject["scope_id"], subject["family"], subject["id"]])
        if key in current:
            raise AppError("DUPLICATE_FINDING_IDENTITY", "Run contains duplicate scoped finding identities.", 500)
        current[key] = finding
    existing = {row["subject_key"]: row for row in connection.execute("SELECT * FROM exceptions")}
    for key, row in existing.items():
        if row["latest_run_id"] == run["id"]:
            continue
        original = _saved_finding(connection, row["run_id"], row["finding_id"])
        latest = current.get(key)
        known = set(discrepancy_keys(original) if row["material_keys_json"] is None
                    else json.loads(row["material_keys_json"]))
        definitive = row["last_definitive_state"]
        episode, notification = row["episode_count"], row["notification_version"]
        notice_reason, closed_at = row["notification_reason"], row["closed_at"]
        state, acknowledged_at = row["state"], row["acknowledged_at"]
        event, additions = None, []
        if comparable_findings(original, latest):
            if latest["evidence_state"] == "healthy":
                if definitive != "healthy":
                    event = "evidence_resolved"
                definitive = "healthy"
            elif latest["evidence_state"] == "anomalous":
                observed = set(discrepancy_keys(latest))
                additions = sorted(observed - known)
                if definitive == "healthy":
                    event, notice_reason = "recurrence", "recurrence"
                    episode += 1
                    known = observed
                elif additions:
                    event, notice_reason = "new_discrepancy", "new_discrepancy"
                    known.update(observed)
                definitive = "anomalous"
                if event:
                    notification += 1
                    closed_at, acknowledged_at = None, None
                    state = "escalated" if state == "escalated" else "open"
        now = _now()
        connection.execute(
            "UPDATE exceptions SET latest_run_id=?,latest_finding_id=?,last_definitive_state=?,material_keys_json=?,"
            "notification_version=?,notification_reason=?,episode_count=?,closed_at=?,state=?,acknowledged_at=?,"
            "version=version+1,updated_at=?,last_action_hash=NULL WHERE id=?",
            (run["id"], latest["id"] if latest else None, definitive, _json(sorted(known)), notification, notice_reason,
             episode, closed_at, state, acknowledged_at, now, row["id"]))
        if event:
            reasons = {"evidence_resolved": "Comparable healthy evidence establishes resolution; closure remains an owner action.",
                       "recurrence": "Comparable anomalous evidence recurred after evidence-based resolution.",
                       "new_discrepancy": "New semantic discrepancies appeared within the existing unresolved case."}
            audit_event(connection, actor_id="system", action=f"exception.{event}", outcome="succeeded",
                        reason=reasons[event], subject_id=row["id"], scope_id=original["subject"]["scope_id"],
                        details={"original_run_id": row["run_id"], "original_finding_id": row["finding_id"],
                                 "latest_run_id": run["id"], "latest_finding_id": latest["id"],
                                 "new_material_keys": additions, "episode_count": episode,
                                 "notification_version": notification,
                                 "before": {"state": row["state"], "closed_at": row["closed_at"],
                                            "last_definitive_state": row["last_definitive_state"]},
                                 "after": {"state": state, "closed_at": closed_at, "last_definitive_state": definitive}})
    created = 0
    for key, finding in current.items():
        if key in existing or finding["evidence_state"] != "anomalous":
            continue
        subject = finding["subject"]
        object_id, now = str(uuid4()), _now()
        connection.execute(
            "INSERT INTO exceptions(id,subject_key,run_id,finding_id,owner_actor_id,state,version,created_at,updated_at,"
            "latest_run_id,latest_finding_id,material_keys_json) VALUES (?,?,?,?,?,'open',1,?,?,?,?,?)",
            (object_id, key, run["id"], finding["id"], "unassigned", now, now, run["id"], finding["id"],
             _json(discrepancy_keys(finding))))
        audit_event(connection, actor_id="system", action="exception.detected", outcome="succeeded",
                    reason="New calculated anomaly added to the in-app exception queue.", subject_id=object_id,
                    scope_id=subject["scope_id"], details={"run_id": run["id"], "finding_id": finding["id"],
                        "notification_version": 1, "episode_count": 1,
                        "after": {"state": "open", "owner_actor_id": "unassigned"}})
        created += 1
    return created


def _saved_finding(connection, run_id, finding_id):
    saved = connection.execute("SELECT result_json FROM calculation_runs WHERE id=?", (run_id,)).fetchone()
    finding = next((value for value in json.loads(saved["result_json"])["findings"]
                    if value["id"] == finding_id), None) if saved else None
    if finding is None:
        raise AppError("EXCEPTION_EVIDENCE_MISSING", "The saved finding referenced by this exception is unavailable.", 500)
    return finding


def _exception_payload(connection, row):
    item = dict(row)
    original = _saved_finding(connection, item["run_id"], item["finding_id"])
    latest = (_saved_finding(connection, item["latest_run_id"], item["latest_finding_id"])
              if item["latest_run_id"] and item["latest_finding_id"] else None)
    comparable = comparable_findings(original, latest)
    if item["latest_run_id"] is None:
        latest_state, latest_reason = "unknown", "Not refreshed since migration; reconcile to obtain current evidence."
    elif latest is None:
        latest_state, latest_reason = "missing", "The latest run did not evaluate this scoped finding identity."
    elif not comparable:
        latest_state, latest_reason = "unknown", "The latest finding changed rule or subject geometry and is not comparable to the original."
    else:
        latest_state, latest_reason = latest["evidence_state"], latest["explanation"]
    item.pop("subject_key")
    item.pop("last_action_hash")
    item["material_keys"] = json.loads(item.pop("material_keys_json") or "[]")
    item["finding"] = item["original_finding"] = original
    item["latest_finding"] = latest
    item["latest_comparable"] = comparable
    item["latest_evidence_state"] = latest_state
    item["latest_evidence_reason"] = latest_reason
    item["evidence_resolution"] = "resolved" if latest_state == "healthy" else "active" if latest_state == "anomalous" else "unknown"
    item["lifecycle_state"] = "closed" if item["closed_at"] else "open"
    context = _access_context.get()
    item["owner"] = actors()[0] if context is not None and item["owner_actor_id"] == context.principal_id else None
    for field in ("owner_actor_id", "handoff_from_actor_id"):
        if item.get(field) != (context.principal_id if context is not None else None):
            item[field] = None
    item["notification_pending"] = item["acknowledged_at"] is None and item["closed_at"] is None and latest_state != "healthy"
    item["synthetic"] = True
    return item


def list_exceptions(connection):
    return [_exception_payload(connection, row) for row in connection.execute(
        "SELECT * FROM exceptions ORDER BY created_at DESC,id DESC")]


def update_exception(connection, object_id, payload):
    _payload(payload, ("actor_id", "version", "action", "reason", "recipient_actor_id"))
    actor = require_actor(payload.get("actor_id"), "exception")
    version, reason = _version(payload.get("version"), "version"), _text(payload.get("reason"), "reason")
    action = payload.get("action")
    if action not in ("acknowledge", "escalate", "handoff", "close", "reopen"):
        raise AppError("INVALID_INPUT", "Use acknowledge, escalate, handoff, close or reopen for exception actions.", 422)
    recipient = require_actor(payload.get("recipient_actor_id"), "exception") if action == "handoff" else None
    if action != "handoff" and payload.get("recipient_actor_id") is not None:
        raise AppError("INVALID_INPUT", "Only handoff accepts a recipient.", 422)
    digest = _hash({"actor_id": actor["id"], "version": version, "action": action, "reason": reason,
                    "recipient_actor_id": recipient["id"] if recipient else None})
    row = connection.execute("SELECT * FROM exceptions WHERE id=?", (object_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "No exception exists with that ID.", 404)
    if row["version"] == version + 1 and row["last_action_hash"] == digest:
        return {**_exception_payload(connection, row), "replay": True}
    if row["version"] != version:
        raise AppError("STALE_EXCEPTION", "Exception ownership or state changed. Refresh before deciding.", 409)
    if row["owner_actor_id"] not in (actor["id"], "unassigned"):
        raise AppError("FORBIDDEN", "Only the assigned exception owner can change its workflow state.", 403)
    if row["closed_at"] and action != "reopen":
        raise AppError("EXCEPTION_CLOSED", "Reopen the closed exception before another owner action.", 409)
    now = _now()
    if row["owner_actor_id"] == "unassigned" and action != "handoff":
        connection.execute("UPDATE exceptions SET owner_actor_id=? WHERE id=?", (actor["id"], object_id))
    if action == "handoff":
        if recipient["team"] == actor["team"]:
            raise AppError("INVALID_HANDOFF", "Choose the named recipient on the other fictional team.", 422)
        connection.execute(
            "UPDATE exceptions SET owner_actor_id=?,state=?,handoff_from_actor_id=?,handoff_at=?,acknowledged_at=NULL,"
            "notification_version=notification_version+1,notification_reason='handoff' WHERE id=?",
            (recipient["id"], "escalated" if row["state"] == "escalated" else "open", actor["id"], now, object_id))
    elif action == "acknowledge":
        if row["acknowledged_at"] is not None:
            raise AppError("EXCEPTION_ALREADY_ACKNOWLEDGED", "This owner has already acknowledged the exception.", 409)
        # Acknowledging an escalated exception retains its escalation state.
        state = "escalated" if row["state"] == "escalated" else "acknowledged"
        connection.execute("UPDATE exceptions SET state=?,acknowledged_at=? WHERE id=?", (state, now, object_id))
    elif action == "escalate":
        if row["state"] == "escalated":
            raise AppError("EXCEPTION_ALREADY_ESCALATED", "This exception is already escalated.", 409)
        connection.execute("UPDATE exceptions SET state='escalated' WHERE id=?", (object_id,))
    elif action == "close":
        if _exception_payload(connection, row)["evidence_resolution"] != "resolved":
            raise AppError("RESOLUTION_NOT_ESTABLISHED", "Close requires healthy comparable evidence in the latest run.", 409)
        connection.execute("UPDATE exceptions SET closed_at=? WHERE id=?", (now, object_id))
    else:
        if not row["closed_at"]:
            raise AppError("EXCEPTION_ALREADY_OPEN", "The exception is already open.", 409)
        connection.execute(
            "UPDATE exceptions SET closed_at=NULL,state=?,acknowledged_at=NULL,notification_version=notification_version+1,"
            "notification_reason='owner_reopen' WHERE id=?",
            ("escalated" if row["state"] == "escalated" else "open", object_id))
    connection.execute("UPDATE exceptions SET version=version+1,updated_at=?,last_action_hash=? WHERE id=?",
                       (now, digest, object_id))
    updated = connection.execute("SELECT * FROM exceptions WHERE id=?", (object_id,)).fetchone()
    result = _exception_payload(connection, updated)
    audit_event(connection, actor_id=actor["id"], action=f"exception.{action}", outcome="succeeded", reason=reason,
                subject_id=object_id, scope_id=result["finding"]["subject"]["scope_id"],
                details={"before": dict(row), "after": dict(updated), "run_id": row["run_id"], "finding_id": row["finding_id"]})
    return {**result, "replay": False}
