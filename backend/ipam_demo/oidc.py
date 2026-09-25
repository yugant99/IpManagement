"""OpenID Connect sign-in as a second authentication path.

Design constraints:
- The reviewed access configuration in `access.py` remains the single source of
  role and domain authority. OIDC never grants roles or domains from claims.
- One deployment-managed mapping file translates one verified id_token claim
  (`sub` or `email`) into an existing principal id from the reviewed config.
  Unmapped identities are rejected.
- If any required deployment variable is missing, `is_configured()` returns
  False. The frontend renders the SSO button visibly disabled and every OIDC
  endpoint returns 404 so the surface is invisible.
- The existing bearer-token path is unchanged. This module runs before the
  bearer check in the middleware and only produces an AccessContext when the
  presented bearer matches an active SSO session.
- Nothing here is verified against a real identity provider yet; the exchange,
  discovery and JWKS calls are exercised only through stubbed tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import base64
from http import HTTPStatus
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import secrets
from threading import Lock
from typing import Callable
from urllib.parse import urlencode, urlparse
from urllib.request import Request as UrllibRequest, urlopen

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from .access import ReviewedConfiguration, effective_roles, load_reviewed_configuration
from .errors import AppError
from .models import AccessContext


logger = logging.getLogger("ipam_demo.oidc")

_MAPPING_CLAIMS = frozenset({"sub", "email"})
_STATE_TTL = timedelta(minutes=10)
_EXCHANGE_TTL = timedelta(seconds=60)
_SESSION_TTL = timedelta(hours=8)
_HTTP_TIMEOUT_SECONDS = 6
_MAX_HTTP_BYTES = 512 * 1024
_HEX64 = 64
_STATE_COOKIE = "ipam_sso_state"


@dataclass(frozen=True)
class OidcConfiguration:
    issuer: str
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: str
    provider_name: str
    mapping_path: Path
    authorization_endpoint: str | None
    token_endpoint: str | None
    jwks_uri: str | None


@dataclass(frozen=True)
class ClaimMapping:
    claim: str
    entries: dict[str, str]  # claim value -> principal id


@dataclass
class _AuthorizationState:
    state: str
    nonce: str
    code_verifier: str
    created_at: datetime


@dataclass
class _ExchangeCode:
    principal_id: str
    expires_at: datetime


@dataclass
class _Session:
    token_digest: str
    principal_id: str
    expires_at: datetime


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _read_secret(path_value: str | None) -> str | None:
    if not path_value:
        return None
    try:
        secret_path = Path(path_value).expanduser()
        if secret_path.is_symlink() or not secret_path.is_file() or secret_path.stat().st_size > 4096:
            return None
        with secret_path.open("r", encoding="utf-8") as handle:
            secret = handle.read().strip()
        return secret or None
    except OSError:
        return None


def get_configuration() -> OidcConfiguration | None:
    """Load deployment-provided OIDC configuration. Return None if incomplete.

    A None return means the SSO path stays invisible; no endpoint activates and
    the frontend renders the SSO button disabled. Callers must never treat a
    partial configuration as usable.
    """
    issuer = _env("IPAM_OIDC_ISSUER")
    client_id = _env("IPAM_OIDC_CLIENT_ID")
    redirect_uri = _env("IPAM_OIDC_REDIRECT_URI")
    mapping_value = _env("IPAM_OIDC_MAPPING_FILE")
    client_secret = _read_secret(_env("IPAM_OIDC_CLIENT_SECRET_FILE"))
    if not (issuer and client_id and client_secret and redirect_uri and mapping_value):
        return None
    if urlparse(issuer).scheme not in {"http", "https"}:
        return None
    if urlparse(redirect_uri).scheme not in {"http", "https"}:
        return None
    mapping_path = Path(mapping_value).expanduser()
    if not mapping_path.is_file():
        return None
    return OidcConfiguration(
        issuer=issuer,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=_env("IPAM_OIDC_SCOPES") or "openid email",
        provider_name=_env("IPAM_OIDC_PROVIDER_NAME") or "Single sign-on",
        mapping_path=mapping_path,
        authorization_endpoint=_env("IPAM_OIDC_AUTHORIZATION_ENDPOINT"),
        token_endpoint=_env("IPAM_OIDC_TOKEN_ENDPOINT"),
        jwks_uri=_env("IPAM_OIDC_JWKS_URI"),
    )


def is_configured() -> bool:
    return get_configuration() is not None


def load_mapping(path: Path) -> ClaimMapping:
    """Load the claim->principal mapping. Fail closed on any structural fault."""
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 128 * 1024:
            raise AppError("SSO_CONFIGURATION_INVALID", "OIDC mapping file is unavailable.", 500)
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AppError("SSO_CONFIGURATION_INVALID", "OIDC mapping file is unreadable.", 500) from exc
    if not isinstance(data, dict) or set(data) != {"claim", "entries"}:
        raise AppError("SSO_CONFIGURATION_INVALID", "OIDC mapping file has an unexpected shape.", 500)
    claim = data["claim"]
    if not isinstance(claim, str) or claim not in _MAPPING_CLAIMS:
        raise AppError("SSO_CONFIGURATION_INVALID", "OIDC mapping claim must be 'sub' or 'email'.", 500)
    entries_raw = data["entries"]
    if not isinstance(entries_raw, list) or not entries_raw:
        raise AppError("SSO_CONFIGURATION_INVALID", "OIDC mapping entries must be a non-empty list.", 500)
    entries: dict[str, str] = {}
    for item in entries_raw:
        if not isinstance(item, dict) or set(item) != {"value", "principal_id"}:
            raise AppError("SSO_CONFIGURATION_INVALID", "OIDC mapping entry has an unexpected shape.", 500)
        value, principal_id = item["value"], item["principal_id"]
        if not (isinstance(value, str) and value and isinstance(principal_id, str) and principal_id):
            raise AppError("SSO_CONFIGURATION_INVALID", "OIDC mapping entry values must be non-empty strings.", 500)
        normalized = value.lower() if claim == "email" else value
        if normalized in entries:
            raise AppError("SSO_CONFIGURATION_INVALID", "OIDC mapping contains duplicate claim values.", 500)
        entries[normalized] = principal_id
    return ClaimMapping(claim=claim, entries=entries)


# In-memory stores. This runtime is single-process; if the process restarts,
# in-flight sign-ins simply need to be retried, which is fine.
_authorization_lock = Lock()
_authorization_store: dict[str, _AuthorizationState] = {}
_exchange_lock = Lock()
_exchange_store: dict[str, _ExchangeCode] = {}
_session_lock = Lock()
_session_store: dict[str, _Session] = {}  # token_digest -> session


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _prune_authorizations(current: datetime) -> None:
    stale = [key for key, state in _authorization_store.items() if state.created_at + _STATE_TTL <= current]
    for key in stale:
        _authorization_store.pop(key, None)


def _prune_exchanges(current: datetime) -> None:
    stale = [code for code, entry in _exchange_store.items() if entry.expires_at <= current]
    for code in stale:
        _exchange_store.pop(code, None)


def _prune_sessions(current: datetime) -> None:
    stale = [digest for digest, session in _session_store.items() if session.expires_at <= current]
    for digest in stale:
        _session_store.pop(digest, None)


def _random_hex(length: int = _HEX64) -> str:
    return secrets.token_hex(length // 2)


def _pkce_pair() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode("ascii")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
    return verifier, challenge


def begin_authorization(config: OidcConfiguration, *, discover: Callable[[OidcConfiguration], dict] | None = None) -> tuple[str, str]:
    """Return (authorization_url, state). Caller sets state cookie on response."""
    state = _random_hex()
    nonce = _random_hex()
    verifier, challenge = _pkce_pair()
    with _authorization_lock:
        current = _now()
        _prune_authorizations(current)
        _authorization_store[state] = _AuthorizationState(state=state, nonce=nonce, code_verifier=verifier, created_at=current)
    endpoints = (discover or _discover)(config)
    authorization_endpoint = endpoints["authorization_endpoint"]
    parameters = {
        "response_type": "code",
        "client_id": config.client_id,
        "redirect_uri": config.redirect_uri,
        "scope": config.scopes,
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    return f"{authorization_endpoint}?{urlencode(parameters)}", state


def _pop_authorization(state: str) -> _AuthorizationState:
    with _authorization_lock:
        current = _now()
        _prune_authorizations(current)
        record = _authorization_store.pop(state, None)
    if record is None:
        raise AppError("SSO_STATE_UNKNOWN", "The SSO sign-in attempt has expired. Start again.", 400)
    return record


def _http_get_json(url: str) -> dict:
    request = UrllibRequest(url, method="GET", headers={"Accept": "application/json"})
    with urlopen(request, timeout=_HTTP_TIMEOUT_SECONDS) as response:  # noqa: S310 - deployment URLs only
        body = response.read(_MAX_HTTP_BYTES + 1)
    if len(body) > _MAX_HTTP_BYTES:
        raise AppError("SSO_UPSTREAM_FAILED", "Upstream OIDC response was too large.", 502)
    return json.loads(body)


def _http_post_form(url: str, form: dict[str, str], *, auth: tuple[str, str] | None = None) -> dict:
    data = urlencode(form).encode("ascii")
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    if auth is not None:
        credential = base64.b64encode(f"{auth[0]}:{auth[1]}".encode("ascii")).decode("ascii")
        headers["Authorization"] = f"Basic {credential}"
    request = UrllibRequest(url, data=data, method="POST", headers=headers)
    with urlopen(request, timeout=_HTTP_TIMEOUT_SECONDS) as response:  # noqa: S310 - deployment URLs only
        body = response.read(_MAX_HTTP_BYTES + 1)
    if len(body) > _MAX_HTTP_BYTES:
        raise AppError("SSO_UPSTREAM_FAILED", "Upstream OIDC response was too large.", 502)
    return json.loads(body)


_discovery_cache: dict[str, dict] = {}
_discovery_lock = Lock()


def _discover(config: OidcConfiguration) -> dict:
    """Return authorization_endpoint, token_endpoint and jwks_uri from the issuer.

    Explicit env overrides take precedence so a deployment can operate without
    outbound access to the discovery document.
    """
    override = {
        key: value for key, value in (
            ("authorization_endpoint", config.authorization_endpoint),
            ("token_endpoint", config.token_endpoint),
            ("jwks_uri", config.jwks_uri),
        ) if value
    }
    if len(override) == 3:
        return override
    with _discovery_lock:
        cached = _discovery_cache.get(config.issuer)
        if cached is None:
            document = _http_get_json(config.issuer.rstrip("/") + "/.well-known/openid-configuration")
            if not isinstance(document, dict):
                raise AppError("SSO_UPSTREAM_FAILED", "OIDC discovery document was malformed.", 502)
            _discovery_cache[config.issuer] = document
            cached = document
    result = {
        "authorization_endpoint": override.get("authorization_endpoint") or cached.get("authorization_endpoint"),
        "token_endpoint": override.get("token_endpoint") or cached.get("token_endpoint"),
        "jwks_uri": override.get("jwks_uri") or cached.get("jwks_uri"),
    }
    for key, value in result.items():
        if not isinstance(value, str) or not value:
            raise AppError("SSO_UPSTREAM_FAILED", f"OIDC discovery missing {key}.", 502)
    return result


def _exchange_code(config: OidcConfiguration, code: str, code_verifier: str,
                   discover: Callable[[OidcConfiguration], dict] | None,
                   transport: Callable[[str, dict, tuple[str, str] | None], dict] | None) -> dict:
    endpoints = (discover or _discover)(config)
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.redirect_uri,
        "code_verifier": code_verifier,
        "client_id": config.client_id,
    }
    request = transport or _http_post_form
    return request(endpoints["token_endpoint"], form, auth=(config.client_id, config.client_secret))


def _verify_id_token(id_token: str, config: OidcConfiguration, nonce: str,
                     discover: Callable[[OidcConfiguration], dict] | None,
                     fetch_jwks: Callable[[str], dict] | None) -> dict:
    """Verify id_token via PyJWT + JWKS. PyJWT is imported lazily; if it is not
    installed the SSO configuration is treated as unavailable and callers must
    surface a clear installation error."""
    try:
        import jwt  # type: ignore[import-not-found]
        from jwt import PyJWKClient  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised only when dep missing
        raise AppError("SSO_STACK_MISSING",
                       "OIDC verification stack is not installed on this deployment.", 503) from exc
    endpoints = (discover or _discover)(config)
    jwks_uri = endpoints["jwks_uri"]
    if fetch_jwks is not None:
        jwks = fetch_jwks(jwks_uri)
        signing_key = _select_signing_key(jwks, id_token, jwt)
    else:  # pragma: no cover - live IdP path, not exercised in stubbed tests
        client = PyJWKClient(jwks_uri)
        signing_key = client.get_signing_key_from_jwt(id_token).key
    try:
        claims = jwt.decode(
            id_token,
            signing_key,
            algorithms=["RS256"],
            audience=config.client_id,
            issuer=config.issuer,
            options={"require": ["exp", "iat", "iss", "aud", "sub"]},
        )
    except Exception as exc:  # pragma: no cover - PyJWT raises many specific types
        raise AppError("SSO_TOKEN_INVALID", "OIDC id_token failed verification.", 401) from exc
    if claims.get("nonce") != nonce:
        raise AppError("SSO_TOKEN_INVALID", "OIDC id_token nonce did not match.", 401)
    return claims


def _select_signing_key(jwks: dict, id_token: str, jwt_module) -> object:
    header = jwt_module.get_unverified_header(id_token)
    kid = header.get("kid")
    for entry in jwks.get("keys", []):
        if kid is None or entry.get("kid") == kid:
            return jwt_module.algorithms.RSAAlgorithm.from_jwk(json.dumps(entry))
    raise AppError("SSO_TOKEN_INVALID", "OIDC id_token references an unknown key.", 401)


def resolve_principal(claims: dict, mapping: ClaimMapping, reviewed: ReviewedConfiguration) -> str:
    """Return a principal id that exists in the reviewed access config.

    Fail closed if the claim is missing, unmapped, or the mapped principal is
    absent, disabled, or expired. No roles or domains are inferred here.
    """
    raw = claims.get(mapping.claim)
    if not isinstance(raw, str) or not raw:
        raise AppError("SSO_CLAIM_UNMAPPED", "OIDC claim did not identify a mapped principal.", 403)
    if mapping.claim == "email":
        if not claims.get("email_verified", False):
            raise AppError("SSO_CLAIM_UNMAPPED", "OIDC email claim was not verified by the identity provider.", 403)
        lookup = raw.lower()
    else:
        lookup = raw
    principal_id = mapping.entries.get(lookup)
    if principal_id is None:
        raise AppError("SSO_CLAIM_UNMAPPED", "OIDC claim did not identify a mapped principal.", 403)
    principal = reviewed.principals.get(principal_id)
    current = _now()
    if principal is None or not principal.enabled or principal.expires_at <= current:
        raise AppError("SSO_CLAIM_UNMAPPED", "OIDC-mapped principal is not currently permitted.", 403)
    return principal_id


def mint_exchange_code(principal_id: str) -> str:
    """Create a single-use handoff code the frontend redeems for a bearer token."""
    code = _random_hex()
    with _exchange_lock:
        current = _now()
        _prune_exchanges(current)
        _exchange_store[code] = _ExchangeCode(principal_id=principal_id, expires_at=current + _EXCHANGE_TTL)
    return code


def redeem_exchange_code(code: str) -> str:
    """Turn a one-time code into an active session bearer token. Fail closed."""
    if not isinstance(code, str) or len(code) != _HEX64:
        raise AppError("SSO_EXCHANGE_INVALID", "The SSO exchange code is invalid or already used.", 400)
    with _exchange_lock:
        current = _now()
        _prune_exchanges(current)
        entry = _exchange_store.pop(code, None)
    if entry is None or entry.expires_at <= _now():
        raise AppError("SSO_EXCHANGE_INVALID", "The SSO exchange code is invalid or already used.", 400)
    token = _random_hex()
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    with _session_lock:
        _prune_sessions(_now())
        _session_store[digest] = _Session(token_digest=digest, principal_id=entry.principal_id, expires_at=_now() + _SESSION_TTL)
    return token


def revoke_session(authorization: str | None) -> None:
    if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        return
    token = authorization[7:]
    if len(token) != _HEX64:
        return
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    with _session_lock:
        _session_store.pop(digest, None)


def try_authenticate_sso(authorization: str | None, reviewed: ReviewedConfiguration,
                         *, now: datetime | None = None) -> AccessContext | None:
    """Return AccessContext if the bearer belongs to an active SSO session.

    Returns None (not an error) if the bearer does not match a live SSO session
    so the caller can fall through to the ordinary reviewed-token path.
    """
    if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    if len(token) != _HEX64:
        return None
    digest = hashlib.sha256(token.encode("ascii")).hexdigest()
    current = (now or _now()).astimezone(timezone.utc)
    with _session_lock:
        _prune_sessions(current)
        entry = None
        for candidate in _session_store.values():
            if hmac.compare_digest(candidate.token_digest, digest):
                entry = candidate
                break
    if entry is None or entry.expires_at <= current:
        return None
    principal = reviewed.principals.get(entry.principal_id)
    if principal is None or not principal.enabled or principal.expires_at <= current:
        with _session_lock:
            _session_store.pop(digest, None)
        return None
    return AccessContext(
        principal_id=principal.id,
        roles=sorted(effective_roles(principal.roles)),
        domains=sorted(principal.domains),
        selected_domain=None,
        configuration_revision=reviewed.revision,
        configuration_digest=reviewed.digest,
        policy_revision=reviewed.policy_revision,
        is_evidence_coordinator=principal.id == reviewed.coordinator_id,
    )


def _reset_stores_for_tests() -> None:
    with _authorization_lock:
        _authorization_store.clear()
    with _exchange_lock:
        _exchange_store.clear()
    with _session_lock:
        _session_store.clear()
    with _discovery_lock:
        _discovery_cache.clear()


def mount(app, *, load_reviewed: Callable[[], ReviewedConfiguration] | None = None) -> None:
    """Attach the SSO endpoints. Safe to call whether or not OIDC is configured."""
    read_reviewed = load_reviewed or load_reviewed_configuration

    @app.get("/api/auth/sso/config")
    def sso_config() -> dict:
        configuration = get_configuration()
        if configuration is None:
            return {"enabled": False, "provider_name": None}
        return {"enabled": True, "provider_name": configuration.provider_name}

    @app.get("/api/auth/sso/authorize")
    def sso_authorize():
        configuration = get_configuration()
        if configuration is None:
            raise AppError("SSO_UNAVAILABLE", "OIDC sign-in is not configured on this deployment.", 404)
        url, state = begin_authorization(configuration)
        response = RedirectResponse(url=url, status_code=HTTPStatus.SEE_OTHER)
        response.set_cookie(_STATE_COOKIE, state, max_age=int(_STATE_TTL.total_seconds()),
                            httponly=True, secure=urlparse(configuration.redirect_uri).scheme == "https",
                            samesite="lax", path="/api/auth/sso")
        return response

    @app.get("/api/auth/sso/callback")
    def sso_callback(request: Request):
        configuration = get_configuration()
        if configuration is None:
            raise AppError("SSO_UNAVAILABLE", "OIDC sign-in is not configured on this deployment.", 404)
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        if not code or not state:
            raise AppError("SSO_CALLBACK_INVALID", "The SSO callback is missing required parameters.", 400)
        browser_state = request.cookies.get(_STATE_COOKIE)
        if not browser_state or not hmac.compare_digest(browser_state, state):
            raise AppError("SSO_STATE_UNKNOWN", "The SSO sign-in attempt was not started in this browser.", 400)
        record = _pop_authorization(state)
        try:
            token_response = _exchange_code(configuration, code, record.code_verifier, None, None)
        except OSError as exc:
            raise AppError("SSO_UPSTREAM_FAILED", "OIDC token exchange failed.", 502) from exc
        id_token = token_response.get("id_token") if isinstance(token_response, dict) else None
        if not isinstance(id_token, str) or not id_token:
            raise AppError("SSO_UPSTREAM_FAILED", "OIDC token response did not include an id_token.", 502)
        claims = _verify_id_token(id_token, configuration, record.nonce, None, None)
        mapping = load_mapping(configuration.mapping_path)
        reviewed = read_reviewed()
        principal_id = resolve_principal(claims, mapping, reviewed)
        exchange = mint_exchange_code(principal_id)
        response = RedirectResponse(url=f"/#sso={exchange}", status_code=HTTPStatus.SEE_OTHER)
        response.delete_cookie(_STATE_COOKIE, path="/api/auth/sso")
        return response

    @app.post("/api/auth/sso/exchange")
    async def sso_exchange(request: Request) -> JSONResponse:
        configuration = get_configuration()
        if configuration is None:
            raise AppError("SSO_UNAVAILABLE", "OIDC sign-in is not configured on this deployment.", 404)
        try:
            payload = await request.json()
        except ValueError as exc:
            raise AppError("SSO_EXCHANGE_INVALID", "The SSO exchange body is not valid JSON.", 400) from exc
        code = payload.get("code") if isinstance(payload, dict) else None
        token = redeem_exchange_code(code)
        return JSONResponse({"token": token}, status_code=200)

    @app.post("/api/auth/sso/logout", status_code=204)
    def sso_logout(request: Request):
        revoke_session(request.headers.get("authorization"))
        return JSONResponse(content=None, status_code=204)
