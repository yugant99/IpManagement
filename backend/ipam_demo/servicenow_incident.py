"""Opt-in ServiceNow sandbox Incident for one existing simulated ticket intent.

Separate from the simulated connector, the local allocation ledger and
provisioning. Configuration is server-side environment only; the browser never
supplies a URL, group, assignee or free text. The database functions join the
caller's BEGIN IMMEDIATE transaction and never perform HTTP. Callers commit a
prepare phase, make one external call outside any transaction, then record the
observed outcome in a second transaction.

A send without a validated 201 stays unknown (or failed on a definitive 4xx)
until a manual correlation lookup resolves it. Only an exact zero-match lookup
permits another send. A failed lookup is not proof of absence. Duplicate
same-correlation matches block for owner review. There is no PATCH, DELETE,
automatic retry or scheduler. Credentials, headers and remote error bodies are
never stored, logged or returned.
"""

import base64
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import http.client
import json
import logging
import os
from pathlib import Path
import re
import stat
from urllib import error as urlerror, parse, request as urlrequest

from . import access, ticket_handoff, workflow
from .errors import AppError

ENV_ENABLED = "IPAM_SERVICENOW_ENABLED"
ENV_INSTANCE_URL = "IPAM_SERVICENOW_INSTANCE_URL"
ENV_USERNAME = "IPAM_SERVICENOW_USERNAME"
ENV_PASSWORD_FILE = "IPAM_SERVICENOW_PASSWORD_FILE"
ENV_GROUP = "IPAM_SERVICENOW_ASSIGNMENT_GROUP_SYS_ID"
ENV_ASSIGNEE = "IPAM_SERVICENOW_ASSIGNEE_SYS_ID"
ENV_DOMAIN = "IPAM_SERVICENOW_ALLOWED_DOMAIN"
ENV_TIMEOUT = "IPAM_SERVICENOW_TIMEOUT_SECONDS"
LABEL = "ServiceNow personal developer sandbox Incident — synthetic and opt-in; not production or customer evidence."
DEFAULT_TIMEOUT_SECONDS = 8.0  # Below the browser client's 12-second request timeout.
# A reserved send blocks lookup this long, so a slow in-flight POST cannot race an absence result.
IN_FLIGHT_GRACE = timedelta(seconds=60)
LOOKUP_LIMIT = 10
STATE_LABELS = {"1": "New", "2": "In Progress", "3": "On Hold", "6": "Resolved", "7": "Closed", "8": "Canceled"}
_ACTION_PREFIX = "servicenow.incident."
_INCIDENT_PATH = "/api/now/table/incident"
_FIELDS = "sys_id,number,state,assignment_group,assigned_to,correlation_id"
_SYS_ID = re.compile(r"^[0-9a-f]{32}$")
_NUMBER = re.compile(r"^[A-Z]{2,10}[0-9]{4,12}$")
_STATE = re.compile(r"^-?[0-9]{1,4}$")
_HOST = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$")
_SERVICE_REFERENCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,63}$")
_TRUE, _FALSE = ("1", "true", "yes", "on"), ("", "0", "false", "no", "off")
_BLOCKS = {
    "sandbox_disabled": ("SERVICENOW_DISABLED", "The ServiceNow sandbox path is not enabled on this server.", 409),
    "configuration_invalid": ("SERVICENOW_CONFIGURATION_INVALID",
                              "ServiceNow sandbox configuration is incomplete or invalid on this server.", 503),
    "domain_not_allowed": ("SERVICENOW_DOMAIN_NOT_ALLOWED",
                           "This domain is not the configured synthetic sandbox domain.", 409),
    "instance_changed": ("SERVICENOW_INSTANCE_CHANGED",
                         "The configured instance differs from the one this Incident was sent to.", 409),
    "source_request_rejected": ("SOURCE_REQUEST_REJECTED",
                                "The local allocation request was rejected; no sandbox Incident is sent.", 409),
    "lookup_required": ("SERVICENOW_LOOKUP_REQUIRED",
                        "The previous send is unresolved. A manual correlation lookup must find no exact match "
                        "before another send.", 409),
    "already_delivered": ("SERVICENOW_ALREADY_DELIVERED", "The sandbox Incident already exists for this handoff.", 409),
    "owner_review_required": ("SERVICENOW_OWNER_REVIEW_REQUIRED",
                              "Duplicate or conflicting sandbox Incidents need owner review in ServiceNow.", 409),
    "not_sent": ("SERVICENOW_NOT_SENT", "No sandbox Incident send is recorded for this handoff.", 409),
    "send_in_flight": ("SERVICENOW_SEND_IN_FLIGHT",
                       "The latest send was reserved less than a minute ago. Wait before looking up its "
                       "correlation.", 409),
    "not_delivered": ("SERVICENOW_NOT_DELIVERED", "Only a delivered sandbox Incident can be refreshed.", 409),
}

logger = logging.getLogger("ipam_demo")


@dataclass(frozen=True)
class Settings:
    status: str  # disabled, invalid or enabled
    problems: tuple[str, ...] = ()
    instance_host: str | None = None
    username: str | None = field(default=None, repr=False)
    password: str | None = field(default=None, repr=False)
    assignment_group: str | None = None
    assignee: str | None = None
    allowed_domain: str | None = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS


def _instance_host(value):
    """Bare https origin only: no credentials, port, path, query or fragment."""
    try:
        parts = parse.urlsplit(value.strip())
        port = parts.port
    except (AttributeError, ValueError):
        return None
    host = (parts.hostname or "").lower()
    if (parts.scheme != "https" or parts.username is not None or parts.password is not None or port is not None
            or parts.path not in ("", "/") or parts.query or parts.fragment or not _HOST.fullmatch(host)
            or not host.endswith(".service-now.com")):
        return None
    return host


def _password(path):
    """Read the secret from an owner-only regular file; the environment carries only its path."""
    if not path:
        return None
    try:
        candidate = Path(path)
        status = candidate.lstat()
        if not stat.S_ISREG(status.st_mode) or status.st_mode & 0o077 or status.st_uid != os.getuid():
            return None
        value = candidate.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return None
    value = value[:-1] if value.endswith("\n") else value
    return value if value and len(value) <= 1024 and value.isprintable() else None


def load_settings(environ=None) -> Settings:
    """Validate server-side configuration. Problems name variables, never values."""
    env = os.environ if environ is None else environ
    flag = env.get(ENV_ENABLED, "").strip().lower()
    if flag in _FALSE:
        return Settings("disabled")
    if flag not in _TRUE:
        return Settings("invalid", (ENV_ENABLED,))
    problems = []
    host = _instance_host(env.get(ENV_INSTANCE_URL, ""))
    if host is None:
        problems.append(ENV_INSTANCE_URL)
    username = env.get(ENV_USERNAME, "")
    if not username or ":" in username or len(username) > 128 or not username.isprintable():
        problems.append(ENV_USERNAME)
    password = _password(env.get(ENV_PASSWORD_FILE, ""))
    if password is None:
        problems.append(ENV_PASSWORD_FILE)
    group, assignee = env.get(ENV_GROUP, "").strip(), env.get(ENV_ASSIGNEE, "").strip()
    if not _SYS_ID.fullmatch(group):
        problems.append(ENV_GROUP)
    if not _SYS_ID.fullmatch(assignee):
        problems.append(ENV_ASSIGNEE)
    domain = env.get(ENV_DOMAIN, "").strip()
    if not domain or len(domain) > 200:
        problems.append(ENV_DOMAIN)
    try:
        timeout = float(env.get(ENV_TIMEOUT, "") or DEFAULT_TIMEOUT_SECONDS)
        if not 1 <= timeout <= 10:
            raise ValueError
    except ValueError:
        problems.append(ENV_TIMEOUT)
        timeout = DEFAULT_TIMEOUT_SECONDS
    if problems:
        return Settings("invalid", tuple(problems))
    return Settings("enabled", (), host, username, password, group, assignee, domain, timeout)


class TransportTimeout(Exception):
    """No complete response within the timeout; the remote effect is unknown."""


class TransportFailure(Exception):
    """No usable HTTP response; the remote effect is unknown."""


class _NoRedirect(urlrequest.HTTPRedirectHandler):
    # Never forward credentials to another location; a redirect surfaces as http_3xx.
    def redirect_request(self, *args, **kwargs):
        return None


def urllib_transport(method, url, headers, body, timeout):
    """Return (status, body bytes). Error bodies are discarded unread; causes are dropped."""
    opener = urlrequest.build_opener(_NoRedirect)
    try:
        with opener.open(urlrequest.Request(url, data=body, headers=headers, method=method), timeout=timeout) as response:
            return response.status, response.read(1_000_000)
    except urlerror.HTTPError as exc:
        exc.close()
        return exc.code, b""
    except TimeoutError:
        raise TransportTimeout() from None
    except urlerror.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise TransportTimeout() from None
        raise TransportFailure() from None
    except (OSError, ValueError, http.client.HTTPException):
        raise TransportFailure() from None


def _exchange(settings, transport, method, path, query, payload):
    """One request. Returns (code, status, result); code is 'ok' or a sanitized reason."""
    url = f"https://{settings.instance_host}{path}?{parse.urlencode(query)}"
    token = base64.b64encode(f"{settings.username}:{settings.password}".encode("utf-8")).decode("ascii")
    headers = {"Authorization": f"Basic {token}", "Accept": "application/json"}
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    try:
        status, raw = (transport or urllib_transport)(method, url, headers, data, settings.timeout_seconds)
    except TransportTimeout:
        return "timeout", None, None
    except TransportFailure:
        return "network_error", None, None
    except Exception as exc:  # Any transport fault is an unknown effect; record only its type.
        logger.warning("ServiceNow sandbox transport failed: %s", type(exc).__name__)
        return "network_error", None, None
    if type(status) is not int or not 100 <= status <= 599:
        return "http_invalid", None, None
    if not 200 <= status < 300:
        return f"http_{status}", status, None
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return "response_malformed", status, None
    return "ok", status, value.get("result") if isinstance(value, dict) else None


def _incident(value, correlation):
    """Allowlisted, validated Incident fields with the exact correlation, else None."""
    if not isinstance(value, dict) or value.get("correlation_id") != correlation:
        return None
    sys_id, number, state = value.get("sys_id"), value.get("number"), value.get("state")
    if not (isinstance(sys_id, str) and _SYS_ID.fullmatch(sys_id) and isinstance(number, str)
            and _NUMBER.fullmatch(number) and isinstance(state, str) and _STATE.fullmatch(state)):
        return None
    item = {"sys_id": sys_id, "number": number, "external_state": state}
    for key in ("assignment_group", "assigned_to"):
        reference = value.get(key)
        if isinstance(reference, dict):
            reference = reference.get("value")
        if reference in (None, ""):
            reference = None
        elif not isinstance(reference, str) or not _SYS_ID.fullmatch(reference):
            return None
        item[key] = reference
    return item


def _incident_payload(intent, settings):
    """The complete allowlisted synthetic payload. No browser-supplied text is included."""
    try:
        business = json.loads(intent["business_payload_json"])
    except (TypeError, ValueError) as exc:
        raise ticket_handoff._integrity() from exc
    if not isinstance(business, dict):
        raise ticket_handoff._integrity()
    reference = business.get("service_reference")
    reference = reference if isinstance(reference, str) and _SERVICE_REFERENCE.fullmatch(reference) else "not included"
    versions = [f"{label}: {business[key]}" for key, label in (("reviewed_pool_version", "Reviewed pool version"),
                                                                ("reviewed_baseline_version", "Reviewed baseline version"))
                if type(business.get(key)) is int]
    lines = ["Synthetic IPAM demonstration record. Not customer data. No provisioning is requested.",
             f"Correlation: {intent['correlation']}", f"Domain: {intent['domain']}",
             f"Source allocation request: {intent['source_request_id']}", f"Action: {intent['action']}",
             *versions, f"Synthetic service reference: {reference}"]
    return {"short_description": f"IPAM synthetic sandbox allocation review {intent['correlation'][:8]}",
            "description": "\n".join(lines), "correlation_id": intent["correlation"],
            "correlation_display": "ipam-demo", "impact": "3", "urgency": "3",
            "assignment_group": settings.assignment_group, "assigned_to": settings.assignee}


def _parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _row(connection, intent_id):
    return connection.execute("SELECT * FROM servicenow_incidents WHERE intent_id=?", (intent_id,)).fetchone()


def _configuration_block(settings, intent, row):
    if settings.status == "disabled":
        return "sandbox_disabled"
    if settings.status != "enabled":
        return "configuration_invalid"
    if intent["domain"] != settings.allowed_domain:
        return "domain_not_allowed"
    if row is not None and row["instance_host"] != settings.instance_host:
        return "instance_changed"
    return None


def _send_block(settings, intent, row):
    block = _configuration_block(settings, intent, row)
    if block is not None:
        return block
    if intent["request_state"] == "rejected":
        return "source_request_rejected"
    if row is None or row["state"] == "absent":
        return None
    return {"unknown": "lookup_required", "failed": "lookup_required", "delivered": "already_delivered",
            "duplicate_review": "owner_review_required"}[row["state"]]


def _lookup_block(settings, intent, row, now):
    block = _configuration_block(settings, intent, row)
    if block is not None:
        return block
    if row is None:
        return "not_sent"
    if row["state"] == "delivered":
        return "already_delivered"
    # A timed-out POST may still commit remotely; absence is not trusted until the grace elapses.
    if row["state"] in ("unknown", "failed") and now < _parse_time(row["sent_at"]) + IN_FLIGHT_GRACE:
        return "send_in_flight"
    return None


def _refresh_block(settings, intent, row):
    block = _configuration_block(settings, intent, row)
    if block is not None:
        return block
    return None if row is not None and row["state"] == "delivered" else "not_delivered"


def _block_error(block):
    code, message, status = _BLOCKS[block]
    return AppError(code, message, status, {"reason": block})


def _events(connection, intent_id, principal_id):
    events = []
    for row in connection.execute("SELECT * FROM audit_events WHERE subject_id=? AND action LIKE ? ORDER BY rowid",
                                  (intent_id, _ACTION_PREFIX + "%")):
        try:
            details = json.loads(row["details_json"])
        except (TypeError, ValueError):
            details = {}
        details = details if isinstance(details, dict) else {}
        result = details.get("result", details.get("error_code"))
        events.append({"action": row["action"], "outcome": row["outcome"],
                       "result": result if isinstance(result, str) else None, "occurred_at": row["created_at"],
                       "actor_id": row["actor_id"] if row["actor_id"] == principal_id else None})
    return events


def _projection(connection, intent, context, settings):
    """Explicit public allowlist; credentials and raw remote bodies are never stored."""
    row = _row(connection, intent["id"])
    now = datetime.now(timezone.utc)
    record = None
    if row is not None:
        duplicates = json.loads(row["duplicate_numbers_json"]) if row["duplicate_numbers_json"] else []
        record = {key: row[key] for key in ("version", "state", "state_reason", "send_count", "instance_host",
                                            "sent_at", "sys_id", "number", "assignment_group", "assigned_to",
                                            "external_state", "observed_at", "last_error_code", "last_error_at",
                                            "updated_at")}
        record.update({"external_state_label": STATE_LABELS.get(row["external_state"]),
                       "duplicate_numbers": duplicates,
                       "sent_by": row["send_principal_id"] if row["send_principal_id"] == context.principal_id else None,
                       "assignment_matches_configuration": (
                           None if settings.status != "enabled" or row["state"] != "delivered" else
                           (row["assignment_group"], row["assigned_to"]) == (settings.assignment_group,
                                                                             settings.assignee))})
    blocks = {"send": _send_block(settings, intent, row), "lookup": _lookup_block(settings, intent, row, now),
              "refresh": _refresh_block(settings, intent, row)}
    return {"intent_id": intent["id"], "domain": intent["domain"], "correlation": intent["correlation"],
            "label": LABEL, "sandbox": True, "synthetic": True,
            "source_request_state": intent["request_state"], "simulated_handoff_state": intent["state"],
            "provisioning_status": "not_requested",
            "configuration": {"status": settings.status, "problems": list(settings.problems),
                              "instance_host": settings.instance_host,
                              "domain_allowed": (intent["domain"] == settings.allowed_domain
                                                 if settings.status == "enabled" else None)},
            "record": record,
            **{f"{name}_allowed": block is None for name, block in blocks.items()},
            **{f"{name}_block_reason": block for name, block in blocks.items()},
            "events": _events(connection, intent["id"], context.principal_id)}


def _audit(connection, context, intent, action, reason, details):
    workflow.audit_event(connection, actor_id=context.principal_id, action=_ACTION_PREFIX + action, outcome="succeeded",
                         reason=reason, request_id=intent["source_request_id"], subject_id=intent["id"],
                         scope_id=intent["scope_id"], pool_id=intent["pool_id"],
                         details={"intent_id": intent["id"], "correlation": intent["correlation"],
                                  "mode": "servicenow_sandbox", **details})


def _operator_target(connection, intent_id, payload, allowed, context, configuration):
    ticket_handoff._authorize(context, configuration, "operator", mutation=True)
    workflow._payload(payload, allowed)
    access.require_actor_match(context, payload.get("actor_id"))
    object_id = ticket_handoff._uuid(intent_id)
    return ticket_handoff._intent(connection, object_id, context)


def _expected_version(payload, minimum):
    value = payload.get("expected_version")
    if type(value) is not int or value < minimum:
        raise AppError("INVALID_INPUT", f"expected_version must be an integer of at least {minimum}.", 422,
                       {"field": "expected_version"})
    return value


def _checked_version(row, expected):
    if (row["version"] if row is not None else 0) != expected:
        raise ticket_handoff._stale()


def _update(connection, row, **values):
    """Version-fenced update; every recorded change advances the version."""
    values["updated_at"] = workflow._now()
    assignments = ",".join(f"{key}=?" for key in values)
    changed = connection.execute(
        f"UPDATE servicenow_incidents SET {assignments},version=version+1 WHERE intent_id=? AND version=?",
        (*values.values(), row["intent_id"], row["version"]))
    if changed.rowcount != 1:
        raise ticket_handoff._stale()


_CLEARED = {"sys_id": None, "number": None, "assignment_group": None, "assigned_to": None, "external_state": None,
            "observed_at": None, "duplicate_numbers_json": None}


def _external_id_owner(connection, sys_id, intent_id):
    row = connection.execute("SELECT intent_id FROM servicenow_incidents WHERE sys_id=? AND intent_id<>?",
                             (sys_id, intent_id)).fetchone()
    return row["intent_id"] if row is not None else None


def _delivered_values(connection, intent_id, incident, reason, now):
    """Delivered fields, or owner review when another handoff already owns this external ID locally."""
    if _external_id_owner(connection, incident["sys_id"], intent_id) is not None:
        return {**_CLEARED, "state": "duplicate_review", "state_reason": "external_id_conflict",
                "duplicate_numbers_json": workflow._json([incident["number"]])}
    return {"state": "delivered", "state_reason": reason, "duplicate_numbers_json": None, "observed_at": now,
            **{key: incident[key] for key in ("sys_id", "number", "assignment_group", "assigned_to",
                                               "external_state")}}


def get_incident(connection, intent_id, *, context, configuration, settings):
    """Scoped read of one handoff's sandbox Incident state and allowed manual actions."""
    ticket_handoff._authorize(context, configuration, "viewer", mutation=False)
    intent = ticket_handoff._intent(connection, ticket_handoff._uuid(intent_id), context)
    return _projection(connection, intent, context, settings)


def prepare_send(connection, intent_id, payload, *, context, configuration, settings):
    """Durably record unknown/send_in_flight before any POST. Returns (view, replay, plan).

    expected_version is 0 before the first send. The same principal and key replays
    the latest send without another POST; plan is None on replay.
    """
    intent = _operator_target(connection, intent_id, payload, ("actor_id", "expected_version", "idempotency_key"),
                              context, configuration)
    expected, key = _expected_version(payload, 0), ticket_handoff._key(payload)
    digest = workflow._hash({"principal_id": context.principal_id, "intent_id": intent["id"],
                             "expected_version": expected, "idempotency_key": key})
    row = _row(connection, intent["id"])
    if row is not None and (row["send_principal_id"], row["send_idempotency_key"]) == (context.principal_id, key):
        if row["send_digest"] != digest:
            raise ticket_handoff._conflict()
        return _projection(connection, intent, context, settings), True, None
    block = _send_block(settings, intent, row)
    if block is not None:
        raise _block_error(block)
    _checked_version(row, expected)
    now = workflow._now()
    if row is None:
        connection.execute(
            "INSERT INTO servicenow_incidents(intent_id,correlation,business_payload_digest,instance_host,version,"
            "state,state_reason,send_count,send_principal_id,send_idempotency_key,send_digest,sent_at,updated_at) "
            "VALUES (?,?,?,?,1,'unknown','send_in_flight',1,?,?,?,?,?)",
            (intent["id"], intent["correlation"], intent["business_payload_digest"], settings.instance_host,
             context.principal_id, key, digest, now, now))
    else:
        _update(connection, row, **_CLEARED, state="unknown", state_reason="send_in_flight",
                send_count=row["send_count"] + 1, send_principal_id=context.principal_id, send_idempotency_key=key,
                send_digest=digest, sent_at=now, last_error_code=None, last_error_at=None)
    saved = _row(connection, intent["id"])
    _audit(connection, context, intent, "send", "Sandbox Incident send reserved before the external POST.",
           {"result": "send_reserved", "send_count": saved["send_count"], "instance_host": settings.instance_host,
            "after": {"state": "unknown", "version": saved["version"]}})
    plan = {"intent_id": intent["id"], "idempotency_key": key, "correlation": intent["correlation"],
            "payload": _incident_payload(intent, settings)}
    return _projection(connection, intent, context, settings), False, plan


def post_incident(plan, *, settings, transport=None):
    """The single POST, outside any transaction. No retry."""
    code, status, result = _exchange(settings, transport, "POST", _INCIDENT_PATH,
                                     {"sysparm_fields": _FIELDS, "sysparm_exclude_reference_link": "true"},
                                     plan["payload"])
    if code == "ok":
        incident = _incident(result, plan["correlation"]) if status == 201 else None
        if incident is None:
            return {"state": "unknown", "reason": "response_unexpected" if status != 201 else "response_malformed"}
        return {"state": "delivered", "reason": "created", "incident": incident}
    if code.startswith("http_4") and code != "http_408":
        return {"state": "failed", "reason": code}
    return {"state": "unknown", "reason": code}


def record_send(connection, plan, outcome, *, context, configuration, settings):
    """Record the POST outcome. A late delivery is never discarded."""
    ticket_handoff._authorize(context, configuration, "operator", mutation=True)
    intent = ticket_handoff._intent(connection, plan["intent_id"], context)
    row = _row(connection, intent["id"])
    if row is None:
        raise ticket_handoff._integrity()
    now, delivered = workflow._now(), outcome["state"] == "delivered"
    same_send = (row["send_principal_id"], row["send_idempotency_key"]) == (context.principal_id,
                                                                           plan["idempotency_key"])
    if same_send and row["state_reason"] == "send_in_flight":
        values = (_delivered_values(connection, intent["id"], outcome["incident"], "created", now) if delivered else
                  {"state": outcome["state"], "state_reason": outcome["reason"]})
        values.update(last_error_code=None if delivered else f"send_{outcome['reason']}",
                      last_error_at=None if delivered else now)
    elif delivered and not (row["state"] == "delivered" and row["sys_id"] == outcome["incident"]["sys_id"]):
        # A lookup or later send already changed the record; keep both visible for owner review.
        numbers = sorted({outcome["incident"]["number"], *([row["number"]] if row["number"] else [])})
        values = {**_CLEARED, "state": "duplicate_review", "state_reason": "late_send_outcome",
                  "duplicate_numbers_json": workflow._json(numbers)}
    else:
        values = None
    if values is not None:
        _update(connection, row, **values)
    saved = _row(connection, intent["id"])
    _audit(connection, context, intent, "send", "Sandbox Incident POST outcome recorded.",
           {"result": outcome["reason"] if values is not None else "late_outcome_not_applied",
            "number": outcome["incident"]["number"] if delivered else None,
            "after": {"state": saved["state"], "version": saved["version"]}})
    return _projection(connection, intent, context, settings)


def prepare_lookup(connection, intent_id, payload, *, context, configuration, settings):
    """Validate a manual correlation lookup. Returns (view, False, plan); writes nothing."""
    intent = _operator_target(connection, intent_id, payload, ("actor_id", "expected_version"), context, configuration)
    expected = _expected_version(payload, 1)
    row = _row(connection, intent["id"])
    block = _lookup_block(settings, intent, row, datetime.now(timezone.utc))
    if block is not None:
        raise _block_error(block)
    _checked_version(row, expected)
    plan = {"intent_id": intent["id"], "expected_version": expected, "correlation": intent["correlation"]}
    return _projection(connection, intent, context, settings), False, plan


def lookup_incident(plan, *, settings, transport=None):
    """GET by exact correlation. Only a complete, valid, zero-exact-match response is absence."""
    code, status, result = _exchange(settings, transport, "GET", _INCIDENT_PATH,
                                     {"sysparm_query": f"correlation_id={plan['correlation']}",
                                      "sysparm_fields": _FIELDS, "sysparm_exclude_reference_link": "true",
                                      "sysparm_limit": str(LOOKUP_LIMIT)}, None)
    if code != "ok" or status != 200 or not isinstance(result, list):
        return {"outcome": "lookup_failed", "reason": code if code != "ok" else "response_malformed"}
    if len(result) >= LOOKUP_LIMIT:
        return {"outcome": "lookup_failed", "reason": "lookup_truncated"}
    # A row outside the exact filter means the response cannot prove absence or completeness.
    if any(not isinstance(item, dict) or item.get("correlation_id") != plan["correlation"] for item in result):
        return {"outcome": "lookup_failed", "reason": "query_mismatch"}
    incidents = [_incident(item, plan["correlation"]) for item in result]
    if any(item is None for item in incidents):
        return {"outcome": "lookup_failed", "reason": "response_malformed"}
    if len(incidents) >= 2:
        return {"outcome": "duplicate", "numbers": sorted(item["number"] for item in incidents)}
    if incidents:
        return {"outcome": "found", "incident": incidents[0]}
    return {"outcome": "absent"}


def record_lookup(connection, plan, outcome, *, context, configuration, settings):
    ticket_handoff._authorize(context, configuration, "operator", mutation=True)
    intent = ticket_handoff._intent(connection, plan["intent_id"], context)
    row = _row(connection, intent["id"])
    if row is None:
        raise ticket_handoff._integrity()
    # Anything recorded since the prepare phase (for example a late send outcome) wins; look up again.
    _checked_version(row, plan["expected_version"])
    now, kind = workflow._now(), outcome["outcome"]
    if kind == "lookup_failed":
        values, result = {"last_error_code": f"lookup_{outcome['reason']}", "last_error_at": now}, outcome["reason"]
    elif kind == "absent":
        values, result = {**_CLEARED, "state": "absent", "state_reason": "lookup_no_exact_match"}, "no_exact_match"
    elif kind == "found":
        values = _delivered_values(connection, intent["id"], outcome["incident"], "lookup_exact_match", now)
        result = "exact_match" if values["state"] == "delivered" else "external_id_conflict"
    else:
        values = {**_CLEARED, "state": "duplicate_review", "state_reason": "same_correlation_duplicates",
                  "duplicate_numbers_json": workflow._json(outcome["numbers"])}
        result = "same_correlation_duplicates"
    if kind != "lookup_failed":
        values.update(last_error_code=None, last_error_at=None)
    _update(connection, row, **values)
    saved = _row(connection, intent["id"])
    _audit(connection, context, intent, "lookup", "Manual sandbox Incident correlation lookup recorded.",
           {"result": result, "before": {"state": row["state"], "version": row["version"]},
            "after": {"state": saved["state"], "version": saved["version"]}})
    return _projection(connection, intent, context, settings)


def prepare_refresh(connection, intent_id, payload, *, context, configuration, settings):
    """Validate a manual readback of the saved sys_id. Returns (view, False, plan); writes nothing."""
    intent = _operator_target(connection, intent_id, payload, ("actor_id", "expected_version"), context, configuration)
    expected = _expected_version(payload, 1)
    row = _row(connection, intent["id"])
    block = _refresh_block(settings, intent, row)
    if block is not None:
        raise _block_error(block)
    _checked_version(row, expected)
    plan = {"intent_id": intent["id"], "expected_version": expected, "correlation": intent["correlation"],
            "sys_id": row["sys_id"], "number": row["number"]}
    return _projection(connection, intent, context, settings), False, plan


def refresh_incident(plan, *, settings, transport=None):
    """GET the saved sys_id. A human changes the Incident in ServiceNow; this only observes it."""
    code, status, result = _exchange(settings, transport, "GET", f"{_INCIDENT_PATH}/{plan['sys_id']}",
                                     {"sysparm_fields": _FIELDS, "sysparm_exclude_reference_link": "true"}, None)
    if code != "ok" or status != 200:
        return {"outcome": "refresh_failed", "reason": code if code != "ok" else "response_unexpected"}
    incident = _incident(result, plan["correlation"])
    if incident is None or (incident["sys_id"], incident["number"]) != (plan["sys_id"], plan["number"]):
        return {"outcome": "refresh_failed", "reason": "identity_mismatch"}
    return {"outcome": "observed", "incident": incident}


def record_refresh(connection, plan, outcome, *, context, configuration, settings):
    ticket_handoff._authorize(context, configuration, "operator", mutation=True)
    intent = ticket_handoff._intent(connection, plan["intent_id"], context)
    row = _row(connection, intent["id"])
    if row is None:
        raise ticket_handoff._integrity()
    _checked_version(row, plan["expected_version"])
    now = workflow._now()
    if outcome["outcome"] == "observed":
        incident = outcome["incident"]
        values = {"assignment_group": incident["assignment_group"], "assigned_to": incident["assigned_to"],
                  "external_state": incident["external_state"], "observed_at": now,
                  "last_error_code": None, "last_error_at": None}
        result = "observed"
    else:
        # The previous observation stays; the failure is recorded, not hidden.
        values, result = {"last_error_code": f"refresh_{outcome['reason']}", "last_error_at": now}, outcome["reason"]
    _update(connection, row, **values)
    saved = _row(connection, intent["id"])
    _audit(connection, context, intent, "refresh", "Manual sandbox Incident readback recorded.",
           {"result": result, "external_state": saved["external_state"],
            "after": {"state": saved["state"], "version": saved["version"]}})
    return _projection(connection, intent, context, settings)
