"""Durable local simulator for C-T internal-ticket-simulator/v1.

Every function joins the caller's BEGIN IMMEDIATE transaction; none commits or
opens a connection. Callers pass the freshly authenticated context and reviewed
configuration. There is no remote client, queue, worker, automatic retry or
provisioning simulation. T014 runs reserve, effect and observation as three
separately committed transactions; crash recovery goes through readback.
"""

from datetime import datetime, timedelta, timezone
import json
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from . import access, workflow
from .errors import AppError

CONTRACT_VERSION = "internal-ticket-simulator/v1"
REQUEST_ACTION = "allocation.request"
ATTEMPT_LIMIT = 3
OBSERVATION_BUDGET = timedelta(seconds=5)
SCENARIOS = ("success", "definitive_failure", "committed_response_lost", "no_effect_response_lost")
_EFFECT_SCENARIOS = frozenset({"success", "committed_response_lost"})
_REASON_CODE = "local_allocation_review"
_UNMAPPED = "unmapped"
_LABEL = "Simulated ticketing handoff — ServiceNow mapping pending."
_PAYLOAD_FIELDS = ("service_reference", "reviewed_pool_version", "reviewed_baseline_version",
                   "reservation_version", "reason_code")
_EFFECT_PHASE = "ticket.simulator_effect"
_OBSERVE_PHASE = "ticket.attempt.observe"
_BLOCKS = {
    "connector_disabled": ("CONNECTOR_DISABLED",
                           "The simulated ticket connector is disabled; readback and history remain available."),
    "source_request_rejected": ("SOURCE_REQUEST_REJECTED",
                                "The local allocation request was rejected; new ticket attempts are refused."),
    "reservation_released": ("RESERVATION_RELEASED",
                             "The linked reservation was released; new ticket attempts are refused."),
    "delivered": ("HANDOFF_DELIVERED", "The simulated ticket is already delivered."),
    "readback_required": ("READBACK_REQUIRED",
                          "The previous attempt is uncertain. Record a definitive readback before another attempt."),
    "attempt_budget_exhausted": ("ATTEMPT_BUDGET_EXHAUSTED",
                                 "All three manual attempts are used. Owner review is required."),
    "routing_blocked": ("ROUTING_BLOCKED",
                        "No reviewed route is assigned. Reassign once the reviewed configuration provides one."),
    "route_changed": ("ROUTE_CHANGED",
                      "The reviewed route changed. Only a zero-attempt handoff can be reassigned; "
                      "otherwise owner resolution is required."),
}
_INTENT_SELECT = (
    "SELECT ti.*, ar.scope_id, ar.pool_id, ar.state AS request_state, ar.reservation_id, "
    "r.state AS reservation_state, s.domain AS scope_domain FROM ticket_intents ti "
    "JOIN allocation_requests ar ON ar.id=ti.source_request_id JOIN scopes s ON s.id=ar.scope_id "
    "LEFT JOIN reservations r ON r.id=ar.reservation_id ")


def _now():
    return datetime.now(timezone.utc)


def _stamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _deadline(attempt):
    return datetime.fromisoformat(attempt["started_at"].replace("Z", "+00:00")) + OBSERVATION_BUDGET


def _integrity():
    return AppError("TICKET_HANDOFF_INTEGRITY", "The saved ticket handoff record is inconsistent.", 409)


def _stale():
    return AppError("STALE_HANDOFF", "The handoff changed. Refresh it before this action.", 409)


def _conflict():
    return AppError("IDEMPOTENCY_CONFLICT", "This operation key already identifies a different payload.", 409)


def _authorize(context, configuration, role, *, mutation):
    """Current role, selected domain and configuration pin precede any lookup or replay."""
    if context is None:
        raise AppError("AUTHENTICATION_REQUIRED", "A valid bearer credential is required.", 401)
    if (context.is_evidence_coordinator or not context.selected_domain
            or context.selected_domain not in context.domains):
        raise AppError("FORBIDDEN", "Select a permitted domain before accessing domain data.", 403)
    access.require_role(context, role)
    if configuration is None:
        if mutation:
            raise AppError("ACCESS_CONFIGURATION_UNAVAILABLE", "Reviewed access configuration is unavailable.", 503)
    elif (context.configuration_revision != configuration.revision
            or context.configuration_digest != configuration.digest
            or context.policy_revision != configuration.policy_revision):
        raise AppError("ACCESS_CONTEXT_STALE", "Access configuration changed. Refresh the authenticated context.", 409)
    return context.selected_domain


def _uuid(value):
    try:
        return str(value if isinstance(value, UUID) else UUID(str(value)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404) from exc


def _key(payload):
    return workflow._text(payload.get("idempotency_key"), "idempotency_key", 200)


def _intent(connection, intent_id, context):
    row = connection.execute(_INTENT_SELECT + "WHERE ti.id=?", (intent_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    access.require_domain_access(context, row["domain"])
    if row["scope_domain"] != row["domain"]:
        # The nested source request must belong to the same selected domain.
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    return row


def _attempt(connection, attempt_id):
    return connection.execute("SELECT * FROM ticket_attempts WHERE id=?", (attempt_id,)).fetchone()


def _attempts(connection, intent_id):
    return connection.execute("SELECT * FROM ticket_attempts WHERE intent_id=? ORDER BY ordinal", (intent_id,)).fetchall()


def _assignments(connection, intent_id):
    return connection.execute(
        "SELECT * FROM ticket_route_assignments WHERE intent_id=? ORDER BY assignment_version", (intent_id,)).fetchall()


def _assignment(connection, intent_id, version):
    row = connection.execute("SELECT * FROM ticket_route_assignments WHERE intent_id=? AND assignment_version=?",
                             (intent_id, version)).fetchone()
    if row is None:
        raise _integrity()
    return row


def _effect(connection, intent_id):
    return connection.execute("SELECT * FROM ticket_simulator_effects WHERE intent_id=?", (intent_id,)).fetchone()


def _phase_recorded(connection, action, attempt_id):
    """Effect and observation phases have no receipt action; their audit is the durable identity."""
    return connection.execute(
        "SELECT 1 FROM audit_events WHERE action=? AND subject_id=? AND outcome='succeeded' LIMIT 1",
        (action, attempt_id)).fetchone() is not None


def _receipt(connection, context, action, key):
    return connection.execute(
        "SELECT * FROM tier_a_operation_receipts WHERE principal_id=? AND domain=? AND action=? AND idempotency_key=?",
        (context.principal_id, context.selected_domain, action, key)).fetchone()


def _save_receipt(connection, context, action, key, digest, target_kind, target_id, result):
    receipt_id = str(uuid4())
    connection.execute(
        "INSERT INTO tier_a_operation_receipts(id,principal_id,domain,action,idempotency_key,request_digest,"
        "target_kind,target_id,result_json,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (receipt_id, context.principal_id, context.selected_domain, action, key, digest, target_kind, target_id,
         workflow._json(result), workflow._now()))
    return receipt_id


def _replayed_intent(connection, receipt, context, digest):
    # Reauthorize the original target before disclosing either its result or a key conflict.
    if receipt["target_kind"] != "ticket_intent":
        raise _integrity()
    intent = _intent(connection, receipt["target_id"], context)
    if receipt["request_digest"] != digest:
        raise _conflict()
    return intent


def _receipt_event(connection, receipt, intent_id):
    row = connection.execute("SELECT * FROM ticket_handoff_events WHERE operation_receipt_id=? AND intent_id=?",
                             (receipt["id"], intent_id)).fetchone()
    if row is None:
        raise _integrity()
    return row


def _require_attempt_receipt(connection, context, key, attempt_id):
    """Effect and observation share the reserving principal's ticket.attempt receipt identity."""
    row = _receipt(connection, context, "ticket.attempt", key)
    if row is None or row["target_kind"] != "ticket_attempt" or row["target_id"] != attempt_id:
        raise AppError("ATTEMPT_IDENTITY_MISMATCH",
                       "This key does not identify your reservation of this attempt.", 409)


def _gate(intent, configuration, assignment):
    """Conditions outside the intent's own history that forbid a new effect."""
    if configuration.connector_mode != "simulated":
        return "connector_disabled"
    if intent["request_state"] == "rejected":
        return "source_request_rejected"
    if intent["reservation_state"] == "released":
        return "reservation_released"
    if assignment["team"] is None:
        return "routing_blocked"
    route = configuration.routes.get((intent["domain"], intent["action"]))
    if route is None or route.team != assignment["team"] or route.revision != assignment["route_revision"]:
        return "route_changed"
    return None


def _attempt_block(intent, configuration, attempts, effect, assignment):
    if intent["state"] == "delivered":
        return "delivered"
    if effect is not None or (attempts and attempts[-1]["result"] in ("pending", "unknown")):
        return "readback_required"
    if len(attempts) >= ATTEMPT_LIMIT:
        return "attempt_budget_exhausted"
    if intent["state"] == "routing_blocked":
        return "routing_blocked"
    return _gate(intent, configuration, assignment)


def _block_error(block):
    code, message = _BLOCKS[block]
    return AppError(code, message, 409, {"reason": block})


def _reassignable(intent, configuration, attempts, assignment):
    route = configuration.routes.get((intent["domain"], intent["action"]))
    return (intent["state"] in ("pending", "routing_blocked") and not attempts and route is not None
            and (route.team, route.revision, str(configuration.revision))
            != (assignment["team"], assignment["route_revision"], assignment["configuration_revision"]))


def _own(principal_id, value):
    return value if value == principal_id else None


def _assignment_projection(row, principal_id):
    return {"assignment_version": row["assignment_version"], "configuration_revision": row["configuration_revision"],
            "route_revision": row["route_revision"], "team": row["team"], "reason": row["reason"],
            "assigned_at": row["assigned_at"], "assigned_by": _own(principal_id, row["assigned_by"])}


def _attempt_projection(row, effect):
    observed_effect = (effect["id"] if effect is not None and row["observed_ticket_id"] is not None
                       and effect["attempt_id"] == row["id"]
                       and effect["synthetic_ticket_id"] == row["observed_ticket_id"] else None)
    return {"id": row["id"], "ordinal": row["ordinal"], "route_assignment_version": row["route_assignment_version"],
            "synthetic_scenario": row["synthetic_scenario"], "started_at": row["started_at"],
            "observation_deadline_at": _stamp(_deadline(row)), "ended_at": row["ended_at"],
            "result": row["result"], "reason": row["reason"], "observed_ticket_id": row["observed_ticket_id"],
            "observed_effect_id": observed_effect}


def _error_code(text):
    try:
        value = json.loads(text) if text else None
    except (TypeError, ValueError):
        value = None
    return value["code"] if isinstance(value, dict) and isinstance(value.get("code"), str) else "lookup_error"


def _event_projection(row, principal_id):
    return {"id": row["id"], "event_type": row["event_type"], "outcome": row["outcome"],
            "attempt_id": row["attempt_id"], "effect_id": row["effect_id"],
            "returned_ticket_id": row["returned_ticket_id"],
            "error_code": _error_code(row["sanitized_error_json"]) if row["outcome"] == "error" else None,
            "acknowledgement_mode": row["acknowledgement_mode"], "occurred_at": row["occurred_at"],
            "actor_id": _own(principal_id, row["actor_id"])}


def _projection(connection, intent, context, configuration, *, detail):
    """Explicit public allowlist. Stored JSON, digests of requests and foreign principals stay private."""
    principal_id = context.principal_id
    try:
        payload = json.loads(intent["business_payload_json"])
    except (TypeError, ValueError) as exc:
        raise _integrity() from exc
    if not isinstance(payload, dict):
        raise _integrity()
    assignments = _assignments(connection, intent["id"])
    current = next((row for row in assignments
                    if row["assignment_version"] == intent["current_route_assignment_version"]), None)
    if current is None:
        raise _integrity()
    attempts = _attempts(connection, intent["id"])
    effect = _effect(connection, intent["id"])
    events = connection.execute("SELECT * FROM ticket_handoff_events WHERE intent_id=? ORDER BY occurred_at,id",
                                (intent["id"],)).fetchall()
    latest = attempts[-1] if attempts else None
    item = {"id": intent["id"], "domain": intent["domain"], "source_request_id": intent["source_request_id"],
            "source_request_state": intent["request_state"], "action": intent["action"],
            "correlation": intent["correlation"], "business_payload_digest": intent["business_payload_digest"],
            "business_payload": {key: payload[key] for key in _PAYLOAD_FIELDS if key in payload},
            "contract_version": intent["contract_version"], "mode": intent["mode"], "state": intent["state"],
            "version": intent["version"], "created_at": intent["created_at"],
            "current_route_assignment_version": intent["current_route_assignment_version"],
            "route": _assignment_projection(current, principal_id),
            "attempt_limit": ATTEMPT_LIMIT, "attempts_used": len(attempts),
            "attempts_remaining": max(0, ATTEMPT_LIMIT - len(attempts)),
            "observation_budget_seconds": int(OBSERVATION_BUDGET.total_seconds()),
            "latest_attempt": _attempt_projection(latest, effect) if latest is not None else None,
            "readback_required": latest is not None and latest["result"] in ("pending", "unknown"),
            "recipient_acknowledged": any(row["event_type"] == "recipient_acknowledgement" for row in events),
            "provisioning_status": "not_requested", "label": _LABEL, "simulated": True, "synthetic": True,
            "availability_evaluated": configuration is not None,
            "attempt_allowed": None, "attempt_block_reason": None, "reassignment_allowed": None}
    if configuration is not None:
        block = _attempt_block(intent, configuration, attempts, effect, current)
        item["attempt_allowed"] = block is None
        item["attempt_block_reason"] = block
        item["reassignment_allowed"] = _reassignable(intent, configuration, attempts, current)
    if detail:
        item["route_history"] = [_assignment_projection(row, principal_id) for row in assignments]
        item["attempts"] = [_attempt_projection(row, effect) for row in attempts]
        item["events"] = [_event_projection(row, principal_id) for row in events]
    return item


def _result(connection, context, configuration, intent_id, operation):
    intent = _intent(connection, intent_id, context)
    return {"handoff": _projection(connection, intent, context, configuration, detail=True), "operation": operation}


def _attempt_operation(connection, phase, attempt_id):
    attempt = _attempt(connection, attempt_id)
    if attempt is None:
        raise _integrity()
    return {"phase": phase, "attempt": _attempt_projection(attempt, _effect(connection, attempt["intent_id"]))}


def _event_operation(phase, event, principal_id):
    return {"phase": phase, "event": _event_projection(event, principal_id)}


def _bump(connection, intent, state):
    changed = connection.execute("UPDATE ticket_intents SET state=?,version=version+1 WHERE id=? AND version=?",
                                 (state, intent["id"], intent["version"]))
    if changed.rowcount != 1:
        raise _stale()


def _audit(connection, context, intent, action, reason, details, *, subject_id=None):
    workflow.audit_event(connection, actor_id=context.principal_id, action=action, outcome="succeeded", reason=reason,
                         request_id=intent["source_request_id"], subject_id=subject_id or intent["id"],
                         scope_id=intent["scope_id"], pool_id=intent["pool_id"],
                         details={"intent_id": intent["id"], "correlation": intent["correlation"],
                                  "business_payload_digest": intent["business_payload_digest"],
                                  "mode": "simulated", **details})


def _require_identity(intent, payload):
    correlation = workflow._text(payload.get("correlation"), "correlation", 200)
    digest = workflow._text(payload.get("business_payload_digest"), "business_payload_digest", 200)
    if correlation != intent["correlation"] or digest != intent["business_payload_digest"]:
        raise AppError("HANDOFF_IDENTITY_MISMATCH",
                       "Correlation and business payload digest must exactly match this handoff.", 409)
    return correlation, digest


def create_intent(connection, source_request_id, *, context, configuration):
    """Record the single allocation.request intent inside the new request's transaction.

    Returns the intent ID. A missing route records routing_blocked; it never fails
    request creation. Disabled connector mode still records the logical intent.
    """
    domain = _authorize(context, configuration, "requester", mutation=True)
    request = connection.execute(
        "SELECT ar.*, s.domain AS scope_domain FROM allocation_requests ar JOIN scopes s ON s.id=ar.scope_id "
        "WHERE ar.id=?", (source_request_id,)).fetchone()
    if request is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    access.require_domain_access(context, request["scope_domain"])
    stored = json.loads(request["payload_json"])
    correlation = str(uuid5(NAMESPACE_URL, "urn:ipam-demo:ticket-correlation:"
                            + workflow._json([domain, request["id"], REQUEST_ACTION])))
    business = {"domain": domain, "action": REQUEST_ACTION, "source_request_id": request["id"],
                "correlation": correlation, "reviewed_pool_version": request["pool_version"],
                "reviewed_baseline_version": request["baseline_version"], "reason_code": _REASON_CODE}
    if "service_reference" in stored:
        business["service_reference"] = stored["service_reference"]
    if request["reservation_id"] is not None:
        if type(stored.get("reservation_version")) is not int:
            raise AppError("RESERVATION_MISMATCH", "The saved allocation request has incomplete reservation identity.", 409)
        business["reservation_version"] = stored["reservation_version"]
    digest = workflow._hash(business)
    existing = connection.execute("SELECT * FROM ticket_intents WHERE domain=? AND source_request_id=? AND action=?",
                                  (domain, request["id"], REQUEST_ACTION)).fetchone()
    if existing is not None:
        if existing["business_payload_digest"] != digest or existing["correlation"] != correlation:
            raise AppError("TICKET_INTENT_CONFLICT", "A different handoff payload already exists for this request.", 409)
        return existing["id"]
    try:
        route = access.resolve_ticket_route(configuration, context, REQUEST_ACTION)
    except AppError as exc:
        if exc.code != "ROUTE_UNAVAILABLE":
            raise
        route = None
    intent_id, now = str(uuid4()), workflow._now()
    state = "pending" if route is not None else "routing_blocked"
    connection.execute(
        "INSERT INTO ticket_intents(id,domain,source_request_id,action,correlation,business_payload_json,"
        "business_payload_digest,version,current_route_assignment_version,contract_version,mode,state,created_at) "
        "VALUES (?,?,?,?,?,?,?,1,1,?,'simulated',?,?)",
        (intent_id, domain, request["id"], REQUEST_ACTION, correlation, workflow._json(business), digest,
         CONTRACT_VERSION, state, now))
    connection.execute(
        "INSERT INTO ticket_route_assignments(intent_id,assignment_version,configuration_revision,route_revision,"
        "team,assigned_by,reason,assigned_at) VALUES (?,1,?,?,?,?,?,?)",
        (intent_id, str(configuration.revision), route.revision if route else _UNMAPPED,
         route.team if route else None, context.principal_id,
         "Initial reviewed route." if route else "No reviewed route is configured; routing is blocked.", now))
    workflow.audit_event(connection, actor_id=context.principal_id, action="ticket.intent.create", outcome="succeeded",
                         reason="Simulated ticket handoff intent recorded with the local request.",
                         request_id=request["id"], subject_id=intent_id, scope_id=request["scope_id"],
                         pool_id=request["pool_id"],
                         details={"intent_id": intent_id, "correlation": correlation, "business_payload_digest": digest,
                                  "state": state, "mode": "simulated", "connector_mode": configuration.connector_mode,
                                  "route_assignment_version": 1, "configuration_revision": str(configuration.revision),
                                  "route_revision": route.revision if route else _UNMAPPED,
                                  "team": route.team if route else None})
    return intent_id


def get_handoff(connection, intent_id, *, context, configuration=None):
    """Scoped detail. With configuration, also report current attempt/reassignment availability."""
    _authorize(context, configuration, "viewer", mutation=False)
    intent = _intent(connection, _uuid(intent_id), context)
    return _projection(connection, intent, context, configuration, detail=True)


def list_handoffs(connection, *, context, configuration=None, source_request_id=None):
    """Selected-domain summaries, newest first; filtered before any caller pagination."""
    domain = _authorize(context, configuration, "viewer", mutation=False)
    query, parameters = _INTENT_SELECT + "WHERE ti.domain=? AND s.domain=? ", [domain, domain]
    if source_request_id is not None:
        try:
            source_request_id = str(UUID(str(source_request_id)))
        except (TypeError, ValueError, AttributeError) as exc:
            raise AppError("INVALID_INPUT", "source_request_id must be a UUID.", 422,
                           {"field": "source_request_id"}) from exc
        query += "AND ti.source_request_id=? "
        parameters.append(source_request_id)
    rows = connection.execute(query + "ORDER BY ti.created_at DESC,ti.id DESC", parameters).fetchall()
    return [_projection(connection, row, context, configuration, detail=False) for row in rows]


def reassign_handoff(connection, intent_id, payload, *, context, configuration):
    """Select the current reviewed team for a zero-attempt pending/routing_blocked intent."""
    workflow._payload(payload, ("actor_id", "expected_version", "idempotency_key", "reason"))
    _authorize(context, configuration, "operator", mutation=True)
    access.require_actor_match(context, payload.get("actor_id"))
    object_id = _uuid(intent_id)
    intent = _intent(connection, object_id, context)
    normalized = {"principal_id": context.principal_id, "intent_id": object_id,
                  "expected_version": workflow._version(payload.get("expected_version"), "expected_version"),
                  "idempotency_key": _key(payload), "reason": workflow._text(payload.get("reason"), "reason", 2000)}
    digest = workflow._hash(normalized)
    receipt = _receipt(connection, context, "ticket.reassign", normalized["idempotency_key"])
    if receipt is not None:
        original = _replayed_intent(connection, receipt, context, digest)
        try:
            version = json.loads(receipt["result_json"])["assignment_version"]
        except (TypeError, ValueError, KeyError) as exc:
            raise _integrity() from exc
        assignment = _assignment(connection, original["id"], version)
        return _result(connection, context, configuration, original["id"],
                       {"phase": "reassign",
                        "assignment": _assignment_projection(assignment, context.principal_id)}), True
    if intent["version"] != normalized["expected_version"]:
        raise _stale()
    if intent["state"] not in ("pending", "routing_blocked") or _attempts(connection, object_id):
        raise AppError("REASSIGNMENT_NOT_ALLOWED",
                       "Only a pending or routing-blocked handoff with zero attempts can be reassigned.", 409)
    route = configuration.routes.get((intent["domain"], intent["action"]))
    if route is None:
        raise AppError("ROUTE_UNAVAILABLE", "No reviewed route is available for this handoff.", 409)
    current = _assignment(connection, object_id, intent["current_route_assignment_version"])
    if not _reassignable(intent, configuration, [], current):
        raise AppError("ROUTE_UNCHANGED", "The current assignment already matches the reviewed route.", 409)
    version, now = intent["current_route_assignment_version"] + 1, workflow._now()
    connection.execute(
        "INSERT INTO ticket_route_assignments(intent_id,assignment_version,configuration_revision,route_revision,"
        "team,assigned_by,reason,assigned_at) VALUES (?,?,?,?,?,?,?,?)",
        (object_id, version, str(configuration.revision), route.revision, route.team, context.principal_id,
         normalized["reason"], now))
    changed = connection.execute(
        "UPDATE ticket_intents SET state='pending',current_route_assignment_version=?,version=version+1 "
        "WHERE id=? AND version=? AND current_route_assignment_version=?",
        (version, object_id, intent["version"], intent["current_route_assignment_version"]))
    if changed.rowcount != 1:
        raise _stale()
    _audit(connection, context, intent, "ticket.reassign", normalized["reason"],
           {"before": {"state": intent["state"], "route_assignment_version": current["assignment_version"],
                       "route_revision": current["route_revision"], "team": current["team"]},
            "after": {"state": "pending", "route_assignment_version": version,
                      "configuration_revision": str(configuration.revision),
                      "route_revision": route.revision, "team": route.team}})
    _save_receipt(connection, context, "ticket.reassign", normalized["idempotency_key"], digest, "ticket_intent",
                  object_id, {"intent_id": object_id, "assignment_version": version})
    assignment = _assignment(connection, object_id, version)
    return _result(connection, context, configuration, object_id,
                   {"phase": "reassign", "assignment": _assignment_projection(assignment, context.principal_id)}), False


def reserve_attempt(connection, intent_id, payload, *, context, configuration):
    """Phase 1: durably consume the next ordinal and save the ticket.attempt receipt.

    No effect happens here. A reserved attempt consumes its ordinal forever.
    """
    workflow._payload(payload, ("actor_id", "expected_version", "idempotency_key", "synthetic_scenario"))
    _authorize(context, configuration, "operator", mutation=True)
    access.require_actor_match(context, payload.get("actor_id"))
    object_id = _uuid(intent_id)
    intent = _intent(connection, object_id, context)
    scenario = payload.get("synthetic_scenario")
    if scenario not in SCENARIOS:
        raise AppError("INVALID_INPUT", "synthetic_scenario must be one of the allowlisted simulator scenarios.", 422,
                       {"field": "synthetic_scenario"})
    normalized = {"principal_id": context.principal_id, "intent_id": object_id,
                  "expected_version": workflow._version(payload.get("expected_version"), "expected_version"),
                  "idempotency_key": _key(payload), "synthetic_scenario": scenario}
    digest = workflow._hash(normalized)
    receipt = _receipt(connection, context, "ticket.attempt", normalized["idempotency_key"])
    if receipt is not None:
        if receipt["target_kind"] != "ticket_attempt":
            raise _integrity()
        attempt = _attempt(connection, receipt["target_id"])
        if attempt is None:
            raise _integrity()
        original = _intent(connection, attempt["intent_id"], context)
        if receipt["request_digest"] != digest:
            raise _conflict()
        return _result(connection, context, configuration, original["id"],
                       _attempt_operation(connection, "reserve", attempt["id"])), True
    if intent["version"] != normalized["expected_version"]:
        raise _stale()
    attempts = _attempts(connection, object_id)
    assignment = _assignment(connection, object_id, intent["current_route_assignment_version"])
    block = _attempt_block(intent, configuration, attempts, _effect(connection, object_id), assignment)
    if block is not None:
        raise _block_error(block)
    ordinal = len(attempts) + 1
    attempt_id, started_at = str(uuid4()), _stamp(_now())
    request_digest = workflow._hash({"intent_id": object_id, "correlation": intent["correlation"],
                                     "business_payload_digest": intent["business_payload_digest"],
                                     "ordinal": ordinal, "route_assignment_version": assignment["assignment_version"],
                                     "synthetic_scenario": scenario, "expected_version": intent["version"],
                                     "idempotency_key": normalized["idempotency_key"],
                                     "principal_id": context.principal_id})
    connection.execute(
        "INSERT INTO ticket_attempts(id,intent_id,ordinal,route_assignment_version,synthetic_scenario,request_digest,"
        "started_at,result) VALUES (?,?,?,?,?,?,?,'pending')",
        (attempt_id, object_id, ordinal, assignment["assignment_version"], scenario, request_digest, started_at))
    # Until observed or read back, the in-flight attempt's outcome is unknown.
    _bump(connection, intent, "unknown")
    _audit(connection, context, intent, "ticket.attempt.reserve", "Manual simulated ticket attempt reserved.",
           {"attempt_id": attempt_id, "ordinal": ordinal, "synthetic_scenario": scenario,
            "route_assignment_version": assignment["assignment_version"], "team": assignment["team"],
            "before": {"state": intent["state"], "version": intent["version"]},
            "after": {"state": "unknown", "version": intent["version"] + 1}})
    _save_receipt(connection, context, "ticket.attempt", normalized["idempotency_key"], digest, "ticket_attempt",
                  attempt_id, {"intent_id": object_id, "attempt_id": attempt_id, "ordinal": ordinal,
                               "route_assignment_version": assignment["assignment_version"],
                               "synthetic_scenario": scenario})
    return _result(connection, context, configuration, object_id,
                   _attempt_operation(connection, "reserve", attempt_id)), False


def _phase_target(connection, attempt_id, payload, context, configuration):
    workflow._payload(payload, ("actor_id", "idempotency_key"))
    _authorize(context, configuration, "operator", mutation=True)
    access.require_actor_match(context, payload.get("actor_id"))
    object_id = _uuid(attempt_id)
    attempt = _attempt(connection, object_id)
    if attempt is None:
        raise AppError("NOT_FOUND", "The requested resource was not found.", 404)
    intent = _intent(connection, attempt["intent_id"], context)
    _require_attempt_receipt(connection, context, _key(payload), object_id)
    return attempt, intent


def commit_simulator_effect(connection, attempt_id, payload, *, context, configuration):
    """Phase 2: commit the selected synthetic effect, separately from observing a response.

    Replay never reruns the effect. The caller learns the outcome only by observation or readback.
    """
    attempt, intent = _phase_target(connection, attempt_id, payload, context, configuration)
    if _phase_recorded(connection, _EFFECT_PHASE, attempt["id"]):
        return _result(connection, context, configuration, intent["id"],
                       {**_attempt_operation(connection, "effect", attempt["id"]), "effect_phase_recorded": True}), True
    if attempt["result"] != "pending":
        raise AppError("ATTEMPT_RESOLVED", "Readback already resolved this attempt; its effect cannot run.", 409)
    assignment = _assignment(connection, intent["id"], attempt["route_assignment_version"])
    gate = _gate(intent, configuration, assignment)
    if gate is not None:
        raise _block_error(gate)
    committed = attempt["synthetic_scenario"] in _EFFECT_SCENARIOS
    if committed:
        if _effect(connection, intent["id"]) is not None:
            raise _integrity()
        connection.execute(
            "INSERT INTO ticket_simulator_effects(id,intent_id,attempt_id,correlation,business_payload_digest,"
            "route_assignment_version,synthetic_scenario,synthetic_ticket_id,committed_at,recipient_state) "
            "VALUES (?,?,?,?,?,?,?,?,?,'received')",
            (str(uuid4()), intent["id"], attempt["id"], intent["correlation"], intent["business_payload_digest"],
             attempt["route_assignment_version"], attempt["synthetic_scenario"], f"SIM-{uuid4().hex[:12].upper()}",
             workflow._now()))
    _audit(connection, context, intent, _EFFECT_PHASE, "Simulated ticket effect phase recorded.",
           {"attempt_id": attempt["id"], "ordinal": attempt["ordinal"],
            "synthetic_scenario": attempt["synthetic_scenario"], "effect_committed": committed},
           subject_id=attempt["id"])
    return _result(connection, context, configuration, intent["id"],
                   {**_attempt_operation(connection, "effect", attempt["id"]), "effect_phase_recorded": True}), False


def observe_attempt(connection, attempt_id, payload, *, context, configuration):
    """Phase 3: record the observed response within the five-second deadline.

    A late, lost or ambiguous response is unknown; no ticket ID is invented.
    """
    attempt, intent = _phase_target(connection, attempt_id, payload, context, configuration)
    if _phase_recorded(connection, _OBSERVE_PHASE, attempt["id"]):
        return _result(connection, context, configuration, intent["id"],
                       _attempt_operation(connection, "observe", attempt["id"])), True
    if attempt["result"] != "pending":
        raise AppError("ATTEMPT_RESOLVED", "Readback already resolved this attempt.", 409)
    if not _phase_recorded(connection, _EFFECT_PHASE, attempt["id"]):
        raise AppError("EFFECT_PHASE_REQUIRED", "The attempt's effect phase has not been recorded; use readback.", 409)
    now = _now()
    scenario, ticket_id = attempt["synthetic_scenario"], None
    if now > _deadline(attempt):
        result, reason = "unknown", "observation_deadline_elapsed"
    elif scenario == "success":
        effect = _effect(connection, intent["id"])
        if effect is None or effect["attempt_id"] != attempt["id"]:
            result, reason = "unknown", "observation_inconsistent"
        else:
            result, reason, ticket_id = "delivered", "simulated_success", effect["synthetic_ticket_id"]
    elif scenario == "definitive_failure":
        result, reason = "failed", "simulated_definitive_failure"
    else:
        result, reason = "unknown", "response_lost"
    changed = connection.execute(
        "UPDATE ticket_attempts SET result=?,reason=?,ended_at=?,observed_ticket_id=? WHERE id=? AND result='pending'",
        (result, reason, _stamp(now), ticket_id, attempt["id"]))
    if changed.rowcount != 1:
        raise _stale()
    _bump(connection, intent, result)
    _audit(connection, context, intent, _OBSERVE_PHASE, "Simulated ticket response observation recorded.",
           {"attempt_id": attempt["id"], "ordinal": attempt["ordinal"], "synthetic_scenario": scenario,
            "result": result, "observation_reason": reason, "observed_ticket_id": ticket_id,
            "before": {"state": intent["state"], "version": intent["version"]},
            "after": {"state": result, "version": intent["version"] + 1}},
           subject_id=attempt["id"])
    return _result(connection, context, configuration, intent["id"],
                   _attempt_operation(connection, "observe", attempt["id"])), False


def _insert_event(connection, event_id, receipt_id, intent, context, event_type, outcome, attempt, *,
                  effect_id=None, ticket_id=None, error=None, mode=None):
    connection.execute(
        "INSERT INTO ticket_handoff_events(id,operation_receipt_id,intent_id,correlation,business_payload_digest,"
        "actor_id,event_type,outcome,attempt_id,route_assignment_version,synthetic_scenario,effect_id,"
        "returned_ticket_id,sanitized_error_json,acknowledgement_mode,occurred_at) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (event_id, receipt_id, intent["id"], intent["correlation"], intent["business_payload_digest"],
         context.principal_id, event_type, outcome,
         attempt["id"] if attempt is not None else None,
         attempt["route_assignment_version"] if attempt is not None else None,
         attempt["synthetic_scenario"] if attempt is not None else None,
         effect_id, ticket_id, workflow._json(error) if error is not None else None, mode, workflow._now()))
    return connection.execute("SELECT * FROM ticket_handoff_events WHERE id=?", (event_id,)).fetchone()


def readback_handoff(connection, intent_id, payload, *, context, configuration):
    """Look up the simulator by exact correlation and digest; record found, absence or error.

    Found attaches the actual persisted ticket ID. Definitive absence closes an
    uncertain or crashed attempt as failed, permitting another attempt within the
    budget. Error changes no outcome. Zero-attempt readback never claims success.
    Available while disabled, after route changes and for rejected/released sources.
    """
    workflow._payload(payload, ("actor_id", "expected_version", "idempotency_key", "correlation",
                                "business_payload_digest"))
    _authorize(context, configuration, "operator", mutation=True)
    access.require_actor_match(context, payload.get("actor_id"))
    object_id = _uuid(intent_id)
    intent = _intent(connection, object_id, context)
    normalized = {"principal_id": context.principal_id, "intent_id": object_id,
                  "expected_version": workflow._version(payload.get("expected_version"), "expected_version"),
                  "idempotency_key": _key(payload),
                  "correlation": workflow._text(payload.get("correlation"), "correlation", 200),
                  "business_payload_digest": workflow._text(payload.get("business_payload_digest"),
                                                            "business_payload_digest", 200)}
    digest = workflow._hash(normalized)
    receipt = _receipt(connection, context, "ticket.readback", normalized["idempotency_key"])
    if receipt is not None:
        original = _replayed_intent(connection, receipt, context, digest)
        event = _receipt_event(connection, receipt, original["id"])
        return _result(connection, context, configuration, original["id"],
                       _event_operation("readback", event, context.principal_id)), True
    if intent["version"] != normalized["expected_version"]:
        raise _stale()
    _require_identity(intent, payload)
    attempts = _attempts(connection, object_id)
    latest = attempts[-1] if attempts else None
    effect = connection.execute("SELECT * FROM ticket_simulator_effects WHERE correlation=?",
                                (intent["correlation"],)).fetchone()
    inconsistent = {"code": "SIMULATOR_LOOKUP_INCONSISTENT"}
    subject, error = latest, None
    if effect is not None:
        owner = next((row for row in attempts if row["id"] == effect["attempt_id"]), None)
        if (effect["intent_id"] != object_id or effect["business_payload_digest"] != intent["business_payload_digest"]
                or owner is None or owner["route_assignment_version"] != effect["route_assignment_version"]
                or owner["synthetic_scenario"] != effect["synthetic_scenario"]
                or effect["synthetic_scenario"] not in _EFFECT_SCENARIOS):
            outcome, error = "error", inconsistent
        else:
            outcome, subject = "found", owner
    elif latest is not None and latest["result"] == "delivered":
        outcome, error = "error", inconsistent
    else:
        outcome = "definitive_absence"
    now, state = workflow._now(), intent["state"]
    if outcome == "found":
        if subject["result"] != "delivered" or subject["observed_ticket_id"] != effect["synthetic_ticket_id"]:
            connection.execute(
                "UPDATE ticket_attempts SET result='delivered',reason='readback_found',observed_ticket_id=?,"
                "ended_at=COALESCE(ended_at,?) WHERE id=?", (effect["synthetic_ticket_id"], now, subject["id"]))
        state = "delivered"
    elif outcome == "definitive_absence" and subject is not None and subject["result"] in ("pending", "unknown"):
        # Fences a crashed reservation: a later effect phase for this attempt is refused.
        connection.execute(
            "UPDATE ticket_attempts SET result='failed',reason='readback_definitive_absence',"
            "ended_at=COALESCE(ended_at,?) WHERE id=?", (now, subject["id"]))
        state = "failed"
    event_id = str(uuid4())
    receipt_id = _save_receipt(connection, context, "ticket.readback", normalized["idempotency_key"], digest,
                               "ticket_intent", object_id,
                               {"intent_id": object_id, "event_id": event_id, "outcome": outcome})
    found = outcome == "found"
    event = _insert_event(connection, event_id, receipt_id, intent, context, "readback", outcome, subject,
                          effect_id=effect["id"] if found else None,
                          ticket_id=effect["synthetic_ticket_id"] if found else None, error=error)
    _bump(connection, intent, state)
    _audit(connection, context, intent, "ticket.readback", "Simulated ticket readback recorded.",
           {"event_id": event_id, "outcome": outcome, "attempt_id": subject["id"] if subject is not None else None,
            "before": {"state": intent["state"], "version": intent["version"]},
            "after": {"state": state, "version": intent["version"] + 1}})
    return _result(connection, context, configuration, object_id,
                   _event_operation("readback", event, context.principal_id)), False


def acknowledge_handoff(connection, intent_id, payload, *, context, configuration):
    """Record an explicitly simulated recipient acknowledgement of the actual delivered effect.

    This neither approves IPAM changes nor alters the local decision.
    """
    workflow._payload(payload, ("actor_id", "expected_version", "idempotency_key", "correlation",
                                "business_payload_digest", "effect_id", "ticket_id", "acknowledgement_mode"))
    if payload.get("acknowledgement_mode") != "simulated":
        raise AppError("INVALID_INPUT", "acknowledgement_mode must be simulated.", 422, {"field": "acknowledgement_mode"})
    _authorize(context, configuration, "operator", mutation=True)
    access.require_actor_match(context, payload.get("actor_id"))
    object_id = _uuid(intent_id)
    intent = _intent(connection, object_id, context)
    try:
        effect_id = str(UUID(str(payload.get("effect_id"))))
    except (TypeError, ValueError, AttributeError) as exc:
        raise AppError("INVALID_INPUT", "effect_id must be a UUID.", 422, {"field": "effect_id"}) from exc
    normalized = {"principal_id": context.principal_id, "intent_id": object_id,
                  "expected_version": workflow._version(payload.get("expected_version"), "expected_version"),
                  "idempotency_key": _key(payload),
                  "correlation": workflow._text(payload.get("correlation"), "correlation", 200),
                  "business_payload_digest": workflow._text(payload.get("business_payload_digest"),
                                                            "business_payload_digest", 200),
                  "effect_id": effect_id, "ticket_id": workflow._text(payload.get("ticket_id"), "ticket_id", 64),
                  "acknowledgement_mode": "simulated"}
    digest = workflow._hash(normalized)
    receipt = _receipt(connection, context, "ticket.acknowledge", normalized["idempotency_key"])
    if receipt is not None:
        original = _replayed_intent(connection, receipt, context, digest)
        event = _receipt_event(connection, receipt, original["id"])
        return _result(connection, context, configuration, original["id"],
                       _event_operation("acknowledge", event, context.principal_id)), True
    if intent["version"] != normalized["expected_version"]:
        raise _stale()
    _require_identity(intent, payload)
    if configuration.connector_mode != "simulated":
        raise _block_error("connector_disabled")
    if intent["state"] != "delivered":
        raise AppError("HANDOFF_NOT_DELIVERED", "Only a delivered simulated ticket can be acknowledged.", 409)
    effect = connection.execute(
        "SELECT * FROM ticket_simulator_effects WHERE id=? AND intent_id=? AND correlation=? "
        "AND business_payload_digest=? AND synthetic_ticket_id=?",
        (effect_id, object_id, intent["correlation"], intent["business_payload_digest"],
         normalized["ticket_id"])).fetchone()
    attempt = _attempt(connection, effect["attempt_id"]) if effect is not None else None
    if (attempt is None or attempt["result"] != "delivered"
            or attempt["observed_ticket_id"] != effect["synthetic_ticket_id"]):
        raise AppError("EFFECT_MISMATCH", "The effect and ticket do not match this handoff's delivered attempt.", 409)
    if effect["recipient_state"] == "acknowledged":
        raise AppError("ALREADY_ACKNOWLEDGED", "The simulated recipient already acknowledged this ticket.", 409)
    changed = connection.execute(
        "UPDATE ticket_simulator_effects SET recipient_state='acknowledged' WHERE id=? AND recipient_state=?",
        (effect["id"], effect["recipient_state"]))
    if changed.rowcount != 1:
        raise _stale()
    event_id = str(uuid4())
    receipt_id = _save_receipt(connection, context, "ticket.acknowledge", normalized["idempotency_key"], digest,
                               "ticket_intent", object_id,
                               {"intent_id": object_id, "event_id": event_id, "outcome": "acknowledged"})
    event = _insert_event(connection, event_id, receipt_id, intent, context, "recipient_acknowledgement",
                          "acknowledged", attempt, effect_id=effect["id"], ticket_id=effect["synthetic_ticket_id"],
                          mode="simulated")
    _bump(connection, intent, intent["state"])
    _audit(connection, context, intent, "ticket.acknowledge", "Simulated recipient acknowledgement recorded.",
           {"event_id": event_id, "attempt_id": attempt["id"], "effect_id": effect["id"],
            "acknowledgement_mode": "simulated", "local_decision_changed": False})
    return _result(connection, context, configuration, object_id,
                   _event_operation("acknowledge", event, context.principal_id)), False
