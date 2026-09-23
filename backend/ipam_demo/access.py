"""Fail-closed reviewed access configuration for the post-meeting bridge."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
from typing import Iterable

from .errors import AppError
from .models import AccessContext


ROLE_BUNDLES = frozenset({"viewer", "requester", "operator", "approver", "platform_admin"})
VIEWER_INHERITING_ROLES = frozenset({"viewer", "requester", "operator", "approver"})
EVIDENCE_OPERATIONS = frozenset({"read", "acquire", "run", "reconcile"})
CONNECTOR_MODES = frozenset({"simulated", "disabled"})
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_BEARER_TOKEN = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class Principal:
    id: str
    token_digest: str
    token_bits: int
    enabled: bool
    expires_at: datetime
    roles: frozenset[str]
    domains: frozenset[str]


@dataclass(frozen=True)
class CoordinatorGrant:
    source_id: str
    scope_id: str


@dataclass(frozen=True)
class TicketRoute:
    domain: str
    action: str
    revision: str
    team: str


@dataclass(frozen=True)
class ReviewedConfiguration:
    revision: int
    digest: str
    effective_at: datetime
    policy_revision: str
    connector_mode: str
    principals: dict[str, Principal]
    coordinator_id: str
    coordinator_grants: frozenset[CoordinatorGrant]
    source_domains: dict[tuple[str, str], str]
    routes: dict[tuple[str, str], TicketRoute]
    notice_recipients: dict[tuple[str, str], str] = field(default_factory=dict)


def _config_error() -> AppError:
    return AppError("ACCESS_CONFIGURATION_INVALID", "Reviewed access configuration is unavailable or invalid.")


def _text(value, field: str, maximum: int = 200) -> str:
    if not isinstance(value, str) or not value or value == "*" or value != value.strip() or len(value) > maximum:
        raise ValueError(field)
    return value


def _utc(value, field: str) -> datetime:
    text = _text(value, field, 64)
    try:
        instant = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(field) from exc
    if instant.utcoffset() != timezone.utc.utcoffset(instant):
        raise ValueError(field)
    return instant.astimezone(timezone.utc)


def _unique_texts(value, field: str, *, allow_empty: bool = False) -> frozenset[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(field)
    items = frozenset(_text(item, field) for item in value)
    if len(items) != len(value):
        raise ValueError(field)
    return items


def _object(value, keys: set[str]) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("configuration object")
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate configuration key")
        result[key] = value
    return result


def effective_roles(roles: Iterable[str]) -> frozenset[str]:
    """Return C-A's Viewer inheritance without treating platform admin as a data role."""
    declared = frozenset(roles)
    return declared | {"viewer"} if declared & VIEWER_INHERITING_ROLES else declared


def _principal(value) -> Principal:
    item = _object(value, {"id", "token_digest", "token_bits", "enabled", "expires_at", "roles", "domains"})
    principal_id = _text(item["id"], "principal id")
    digest = _text(item["token_digest"], "token digest", 64)
    if not _DIGEST.fullmatch(digest):
        raise ValueError("token digest")
    bits = item["token_bits"]
    if type(bits) is not int or bits != 256:
        raise ValueError("token bits")
    if type(item["enabled"]) is not bool:
        raise ValueError("enabled")
    roles = _unique_texts(item["roles"], "roles", allow_empty=True)
    if not roles.issubset(ROLE_BUNDLES):
        raise ValueError("roles")
    return Principal(principal_id, digest, bits, item["enabled"], _utc(item["expires_at"], "expiry"), roles,
                     _unique_texts(item["domains"], "domains", allow_empty=True))


def _load_configuration(value) -> ReviewedConfiguration:
    base_keys = {"revision", "effective_at", "policy_revision", "connector_mode", "reviewer_references",
                           "principals", "evidence_coordinator", "source_mappings", "routes"}
    if not isinstance(value, dict):
        raise ValueError("configuration object")
    keys = set(value)
    if "notice_recipients" in value:
        if keys != base_keys | {"notice_recipients"}:
            raise ValueError("configuration object")
    elif keys != base_keys:
        raise ValueError("configuration object")
    root = value
    revision = root["revision"]
    if type(revision) is not int or revision < 1:
        raise ValueError("revision")
    effective_at = _utc(root["effective_at"], "effective time")
    policy_revision = _text(root["policy_revision"], "policy revision")
    connector_mode = _text(root["connector_mode"], "connector mode")
    if connector_mode not in CONNECTOR_MODES:
        raise ValueError("connector mode")
    _unique_texts(root["reviewer_references"], "reviewer references")
    if not isinstance(root["principals"], list) or not root["principals"]:
        raise ValueError("principals")
    principals = [_principal(item) for item in root["principals"]]
    by_id = {item.id: item for item in principals}
    if len(by_id) != len(principals) or len({item.token_digest for item in principals}) != len(principals):
        raise ValueError("principal identity")

    mappings = root["source_mappings"]
    if not isinstance(mappings, list) or not mappings:
        raise ValueError("source mappings")
    source_domains: dict[tuple[str, str], str] = {}
    scope_domains: dict[str, str] = {}
    for item in mappings:
        item = _object(item, {"source_id", "scope_id", "domain"})
        scope_id = _text(item["scope_id"], "scope id")
        domain = _text(item["domain"], "domain")
        key = (_text(item["source_id"], "source id"), scope_id)
        if key in source_domains:
            raise ValueError("source mapping")
        if scope_id in scope_domains and scope_domains[scope_id] != domain:
            raise ValueError("scope domain")
        source_domains[key] = domain
        scope_domains[scope_id] = domain

    coordinator = _object(root["evidence_coordinator"], {"principal_id", "grants"})
    coordinator_id = _text(coordinator["principal_id"], "coordinator id")
    coordinator_principal = by_id.get(coordinator_id)
    if coordinator_principal is None or coordinator_principal.roles or coordinator_principal.domains:
        raise ValueError("coordinator")
    if not isinstance(coordinator["grants"], list):
        raise ValueError("coordinator grants")
    grants = set()
    for item in coordinator["grants"]:
        item = _object(item, {"source_id", "scope_id"})
        grants.add(CoordinatorGrant(_text(item["source_id"], "source id"), _text(item["scope_id"], "scope id")))
    if len(grants) != len(coordinator["grants"]) or {(item.source_id, item.scope_id) for item in grants} != set(source_domains):
        raise ValueError("coordinator grants")

    routes = root["routes"]
    if not isinstance(routes, list):
        raise ValueError("routes")
    by_route: dict[tuple[str, str], TicketRoute] = {}
    for item in routes:
        item = _object(item, {"domain", "action", "revision", "team"})
        route = TicketRoute(_text(item["domain"], "domain"), _text(item["action"], "action"),
                            _text(item["revision"], "route revision"), _text(item["team"], "route team"))
        key = (route.domain, route.action)
        if key in by_route:
            raise ValueError("route")
        by_route[key] = route

    notice_recipients: dict[tuple[str, str], str] = {}
    if "notice_recipients" in root:
        raw_recipients = root["notice_recipients"]
        if not isinstance(raw_recipients, list):
            raise ValueError("notice recipients")
        for item in raw_recipients:
            item = _object(item, {"domain", "scope_id", "principal_id"})
            recipient_key = (_text(item["domain"], "domain"), _text(item["scope_id"], "scope id"))
            recipient_id = _text(item["principal_id"], "principal id")
            if recipient_key in notice_recipients:
                raise ValueError("notice recipient")
            notice_recipients[recipient_key] = recipient_id

    digest = hashlib.sha256(json.dumps(root, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")).hexdigest()
    return ReviewedConfiguration(revision, digest, effective_at, policy_revision, connector_mode, by_id, coordinator_id,
                                 frozenset(grants), source_domains, by_route, notice_recipients)


def load_reviewed_configuration(path: str | Path | None = None, *, now: datetime | None = None) -> ReviewedConfiguration:
    """Load the separately provisioned configuration without disclosing its path or contents."""
    candidate = path if path is not None else os.environ.get("IPAM_ACCESS_CONFIG")
    if not isinstance(candidate, (str, Path)) or not str(candidate):
        raise AppError("ACCESS_CONFIGURATION_UNAVAILABLE", "Reviewed access configuration is unavailable.")
    try:
        config_path = Path(candidate).expanduser()
        if config_path.is_symlink() or not config_path.is_file() or config_path.stat().st_size > 1024 * 1024:
            raise ValueError("configuration file")
        with config_path.open("rb") as source:
            value = json.loads(source.read(), object_pairs_hook=_reject_duplicate_keys)
        configuration = _load_configuration(value)
    except (OSError, TypeError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        raise _config_error() from exc
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if configuration.effective_at > current:
        raise _config_error()
    return configuration


def _bearer(authorization: str | None) -> str:
    """Enforce the offline-issued v1 shape; offline issuance, not shape, establishes entropy."""
    if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        raise AppError("AUTHENTICATION_REQUIRED", "A valid bearer credential is required.", 401)
    token = authorization[7:]
    if not _BEARER_TOKEN.fullmatch(token):
        raise AppError("AUTHENTICATION_REQUIRED", "A valid bearer credential is required.", 401)
    return token


def authenticate_bearer(authorization: str | None, configuration: ReviewedConfiguration, *, now: datetime | None = None) -> AccessContext:
    """Return only trusted identity claims. Call require_selected_domain for ordinary operations."""
    token_digest = hashlib.sha256(_bearer(authorization).encode("ascii")).hexdigest()
    principal = next((item for item in configuration.principals.values() if hmac.compare_digest(item.token_digest, token_digest)), None)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if principal is None or not principal.enabled or principal.expires_at <= current:
        raise AppError("AUTHENTICATION_REQUIRED", "A valid bearer credential is required.", 401)
    return AccessContext(principal_id=principal.id, roles=sorted(effective_roles(principal.roles)), domains=sorted(principal.domains),
                         selected_domain=None, configuration_revision=configuration.revision,
                         configuration_digest=configuration.digest, policy_revision=configuration.policy_revision,
                         is_evidence_coordinator=principal.id == configuration.coordinator_id)


def require_selected_domain(context: AccessContext, selected_domain: str | None) -> AccessContext:
    try:
        domain = _text(selected_domain, "selected domain") if selected_domain is not None else None
    except ValueError as exc:
        raise AppError("FORBIDDEN", "Select a permitted domain before accessing domain data.", 403) from exc
    if not domain or context.is_evidence_coordinator or domain not in context.domains:
        raise AppError("FORBIDDEN", "Select a permitted domain before accessing domain data.", 403)
    return context.model_copy(update={"selected_domain": domain})


def require_role(context: AccessContext, role: str) -> None:
    if role not in ROLE_BUNDLES or role not in effective_roles(context.roles):
        raise AppError("FORBIDDEN", "The current principal is not permitted to perform this operation.", 403)


def require_actor_match(context: AccessContext, actor_id: str | None) -> None:
    if actor_id is not None and actor_id != context.principal_id:
        raise AppError("ACTOR_MISMATCH", "Request actor does not match the authenticated principal.", 403)


def require_independent_principal(context: AccessContext, other_principal_id: str) -> None:
    if context.principal_id == other_principal_id:
        raise AppError("SELF_APPROVAL_FORBIDDEN", "A different authenticated principal must make this decision.", 403)


def require_domain_access(context: AccessContext, resource_domain: str | None) -> None:
    if context.selected_domain is None:
        raise AppError("FORBIDDEN", "Select a permitted domain before accessing domain data.", 403)
    if resource_domain is None or resource_domain != context.selected_domain:
        raise AppError("NOT_FOUND", "Requested resource was not found.", 404)


def require_source_domain(configuration: ReviewedConfiguration, context: AccessContext, *, source_id: str,
                          scope_ids: Iterable[str]) -> None:
    """Require every supplied source scope to be mapped to the selected ordinary domain."""
    if context.selected_domain is None or context.is_evidence_coordinator or isinstance(scope_ids, str):
        raise AppError("FORBIDDEN", "The current principal is not permitted to use these source scopes.", 403)
    try:
        source = _text(source_id, "source id")
        scopes = {_text(scope_id, "scope id") for scope_id in scope_ids}
    except ValueError as exc:
        raise AppError("FORBIDDEN", "The current principal is not permitted to use these source scopes.", 403) from exc
    if not scopes or any(configuration.source_domains.get((source, scope_id)) != context.selected_domain for scope_id in scopes):
        raise AppError("FORBIDDEN", "The current principal is not permitted to use these source scopes.", 403)


def require_coordinator(configuration: ReviewedConfiguration, context: AccessContext, *, operation: str,
                        source_id: str, scope_ids: Iterable[str]) -> None:
    if not context.is_evidence_coordinator or operation not in EVIDENCE_OPERATIONS:
        raise AppError("FORBIDDEN", "The current principal is not permitted to run this evidence operation.", 403)
    if isinstance(scope_ids, str):
        raise AppError("FORBIDDEN", "The configured coordinator lacks the required source and scope grant.", 403)
    try:
        source = _text(source_id, "source id")
        requested = {_text(scope_id, "scope id") for scope_id in scope_ids}
    except ValueError as exc:
        raise AppError("FORBIDDEN", "The configured coordinator lacks the required source and scope grant.", 403) from exc
    if not requested or any(CoordinatorGrant(source, scope_id) not in configuration.coordinator_grants for scope_id in requested):
        raise AppError("FORBIDDEN", "The configured coordinator lacks the required source and scope grant.", 403)


def resolve_ticket_route(configuration: ReviewedConfiguration, context: AccessContext, action: str) -> TicketRoute:
    if context.selected_domain is None:
        raise AppError("FORBIDDEN", "Select a permitted domain before routing a handoff.", 403)
    try:
        route = configuration.routes.get((context.selected_domain, _text(action, "action")))
    except ValueError as exc:
        raise AppError("ROUTE_UNAVAILABLE", "No reviewed route is available for this handoff.", 409) from exc
    if route is None:
        raise AppError("ROUTE_UNAVAILABLE", "No reviewed route is available for this handoff.", 409)
    return route


def resolve_notice_recipient(configuration: ReviewedConfiguration, domain: str, scope_id: str, *,
                             now: datetime | None = None) -> dict:
    """Return the internal reviewed recipient binding for one domain and scope.

    Missing mapping returns unassigned with reason missing_mapping. A configured
    but currently unavailable principal stays internally identified with an
    allowlisted unroutable reason. Only a currently enabled, unexpired,
    selected-domain Operator is assigned. Never invalidates the whole
    configuration merely because one recipient is unavailable.
    """
    try:
        lookup = (_text(domain, "domain"), _text(scope_id, "scope id"))
    except ValueError:
        return {"recipient_id": None, "routing_status": "unassigned", "routing_reason": "missing_mapping",
                "configuration_revision": configuration.revision, "configuration_digest": configuration.digest}
    recipient_id = configuration.notice_recipients.get(lookup)
    if recipient_id is None:
        return {"recipient_id": None, "routing_status": "unassigned", "routing_reason": "missing_mapping",
                "configuration_revision": configuration.revision, "configuration_digest": configuration.digest}
    principal = configuration.principals.get(recipient_id)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if principal is None:
        reason = "unknown_principal"
    elif not principal.enabled:
        reason = "disabled"
    elif principal.expires_at <= current:
        reason = "expired"
    elif "operator" not in effective_roles(principal.roles):
        reason = "not_operator"
    elif lookup[0] not in principal.domains:
        reason = "wrong_domain"
    else:
        return {"recipient_id": recipient_id, "routing_status": "assigned", "routing_reason": None,
                "configuration_revision": configuration.revision, "configuration_digest": configuration.digest}
    return {"recipient_id": recipient_id, "routing_status": "unroutable", "routing_reason": reason,
            "configuration_revision": configuration.revision, "configuration_digest": configuration.digest}


def authenticate_request(authorization: str | None, selected_domain: str | None = None, *,
                         path: str | Path | None = None, now: datetime | None = None) -> tuple[ReviewedConfiguration, AccessContext]:
    """Reload reviewed authority for each request and optionally bind one ordinary domain."""
    configuration = load_reviewed_configuration(path, now=now)
    context = authenticate_bearer(authorization, configuration, now=now)
    return configuration, require_selected_domain(context, selected_domain) if selected_domain is not None else context
