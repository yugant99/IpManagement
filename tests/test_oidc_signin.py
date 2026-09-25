"""Focused OIDC checks with stubbed HTTP and JWT; no network, no real IdP."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from ipam_demo import oidc
from ipam_demo.access import Principal, ReviewedConfiguration
from ipam_demo.errors import AppError


def _principal(principal_id="alice", enabled=True, roles=frozenset({"viewer"}),
               domains=frozenset({"demo-core"}), expired=False) -> Principal:
    expires_at = datetime(2099 if not expired else 2000, 1, 1, tzinfo=timezone.utc)
    return Principal(id=principal_id, token_digest="d" * 64, token_bits=256, enabled=enabled,
                     expires_at=expires_at, roles=roles, domains=domains)


def _reviewed(principals=None) -> ReviewedConfiguration:
    principals = principals or {"alice": _principal()}
    return ReviewedConfiguration(revision=1, digest="e" * 64,
                                 effective_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                                 policy_revision="p1", connector_mode="simulated",
                                 principals=principals, coordinator_id="coordinator",
                                 coordinator_grants=frozenset(), source_domains={}, routes={})


def _write_mapping(directory: Path, claim="email", entries=None) -> Path:
    entries = entries if entries is not None else [{"value": "alice@example.com", "principal_id": "alice"}]
    path = directory / "mapping.json"
    path.write_text(json.dumps({"claim": claim, "entries": entries}))
    return path


class OidcConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ipam-oidc-config-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.mapping = _write_mapping(self.directory)
        self.secret_file = self.directory / "client-secret"
        self.secret_file.write_text("s3cr3t-value")
        self.addCleanup(oidc._reset_stores_for_tests)

    def _env(self, **overrides):
        base = {
            "IPAM_OIDC_ISSUER": "https://idp.example.com",
            "IPAM_OIDC_CLIENT_ID": "ipam-demo",
            "IPAM_OIDC_CLIENT_SECRET_FILE": str(self.secret_file),
            "IPAM_OIDC_REDIRECT_URI": "http://127.0.0.1:18942/api/auth/sso/callback",
            "IPAM_OIDC_MAPPING_FILE": str(self.mapping),
        }
        base.update(overrides)
        return base

    def test_missing_required_env_returns_none(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(oidc.get_configuration())
            self.assertFalse(oidc.is_configured())

    def test_missing_secret_file_returns_none(self):
        env = self._env(IPAM_OIDC_CLIENT_SECRET_FILE=str(self.directory / "not-there"))
        with patch.dict("os.environ", env, clear=True):
            self.assertIsNone(oidc.get_configuration())

    def test_bad_issuer_scheme_returns_none(self):
        env = self._env(IPAM_OIDC_ISSUER="ftp://idp.example.com")
        with patch.dict("os.environ", env, clear=True):
            self.assertIsNone(oidc.get_configuration())

    def test_fully_configured_returns_loaded_configuration(self):
        with patch.dict("os.environ", self._env(), clear=True):
            config = oidc.get_configuration()
        self.assertIsNotNone(config)
        self.assertEqual(config.client_id, "ipam-demo")
        self.assertEqual(config.client_secret, "s3cr3t-value")
        self.assertEqual(config.scopes, "openid email")

    def test_config_endpoint_reports_disabled_when_unconfigured(self):
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        oidc.mount(app)
        with patch.dict("os.environ", {}, clear=True):
            response = TestClient(app).get("/api/auth/sso/config")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"enabled": False, "provider_name": None})

    def test_config_endpoint_reports_enabled_with_provider_name(self):
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        oidc.mount(app)
        env = self._env(IPAM_OIDC_PROVIDER_NAME="Corp SSO")
        with patch.dict("os.environ", env, clear=True):
            response = TestClient(app).get("/api/auth/sso/config")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"enabled": True, "provider_name": "Corp SSO"})

    def test_callback_and_authorize_return_404_when_unconfigured(self):
        # Regression: request objects must resolve to Starlette Request, not query params.
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        app = FastAPI()

        @app.exception_handler(AppError)
        async def _(request, exc):
            return JSONResponse(exc.body("test"), status_code=exc.status)

        oidc.mount(app)
        with patch.dict("os.environ", {}, clear=True):
            client = TestClient(app)
            self.assertEqual(client.get("/api/auth/sso/authorize", follow_redirects=False).status_code, 404)
            self.assertEqual(client.get("/api/auth/sso/callback?code=x&state=y", follow_redirects=False).status_code, 404)


class ClaimMappingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ipam-oidc-mapping-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_email_entries_normalize_case(self):
        path = _write_mapping(self.directory, entries=[{"value": "Alice@Example.COM", "principal_id": "alice"}])
        mapping = oidc.load_mapping(path)
        self.assertEqual(mapping.claim, "email")
        self.assertEqual(mapping.entries, {"alice@example.com": "alice"})

    def test_unknown_claim_fails_closed(self):
        path = self.directory / "bad-claim.json"
        path.write_text(json.dumps({"claim": "name", "entries": [{"value": "x", "principal_id": "y"}]}))
        with self.assertRaises(AppError) as guard:
            oidc.load_mapping(path)
        self.assertEqual(guard.exception.code, "SSO_CONFIGURATION_INVALID")

    def test_duplicate_values_fail_closed(self):
        path = _write_mapping(self.directory, entries=[
            {"value": "a@x.com", "principal_id": "p1"},
            {"value": "A@X.COM", "principal_id": "p2"},
        ])
        with self.assertRaises(AppError):
            oidc.load_mapping(path)


class AuthorizationFlowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ipam-oidc-auth-")
        self.addCleanup(self.temporary.cleanup)
        directory = Path(self.temporary.name)
        secret_file = directory / "client-secret"
        secret_file.write_text("s3cr3t")
        mapping = _write_mapping(directory)
        self.env = {
            "IPAM_OIDC_ISSUER": "https://idp.example.com",
            "IPAM_OIDC_CLIENT_ID": "ipam-demo",
            "IPAM_OIDC_CLIENT_SECRET_FILE": str(secret_file),
            "IPAM_OIDC_REDIRECT_URI": "http://127.0.0.1:18942/api/auth/sso/callback",
            "IPAM_OIDC_MAPPING_FILE": str(mapping),
            "IPAM_OIDC_AUTHORIZATION_ENDPOINT": "https://idp.example.com/authorize",
            "IPAM_OIDC_TOKEN_ENDPOINT": "https://idp.example.com/token",
            "IPAM_OIDC_JWKS_URI": "https://idp.example.com/jwks",
        }
        self.addCleanup(oidc._reset_stores_for_tests)

    def test_begin_authorization_stores_state_and_returns_pkce_url(self):
        with patch.dict("os.environ", self.env, clear=True):
            config = oidc.get_configuration()
        url, state = oidc.begin_authorization(config)
        self.assertIn("https://idp.example.com/authorize?", url)
        self.assertIn("code_challenge_method=S256", url)
        self.assertIn(f"state={state}", url)
        self.assertIn("nonce=", url)
        self.assertIn(state, oidc._authorization_store)

    def test_token_exchange_passes_client_auth_to_keyword_only_transport(self):
        with patch.dict("os.environ", self.env, clear=True):
            config = oidc.get_configuration()
        calls = []

        def transport(url, form, *, auth):
            calls.append((url, form, auth))
            return {"id_token": "signed-token"}

        result = oidc._exchange_code(config, "provider-code", "pkce-verifier", None, transport)
        self.assertEqual(result, {"id_token": "signed-token"})
        self.assertEqual(calls[0][0], "https://idp.example.com/token")
        self.assertEqual(calls[0][1]["code_verifier"], "pkce-verifier")
        self.assertEqual(calls[0][2], ("ipam-demo", "s3cr3t"))

    def test_callback_requires_state_cookie_from_same_browser(self):
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.exception_handler(AppError)
        async def handle_error(request, exc):
            return JSONResponse(exc.body("test"), status_code=exc.status)

        oidc.mount(app, load_reviewed=lambda: _reviewed())
        with patch.dict("os.environ", self.env, clear=True):
            first_browser = TestClient(app)
            response = first_browser.get("/api/auth/sso/authorize", follow_redirects=False)
            self.assertEqual(response.status_code, 303)
            state = parse_qs(urlparse(response.headers["location"]).query)["state"][0]
            self.assertIn("httponly", response.headers["set-cookie"].lower())
            self.assertIn("samesite=lax", response.headers["set-cookie"].lower())
            callback = f"/api/auth/sso/callback?code=provider-code&state={state}"
            other_browser = TestClient(app)
            refused = other_browser.get(callback, follow_redirects=False)
            self.assertEqual(refused.status_code, 400)
            self.assertEqual(refused.json()["error"]["code"], "SSO_STATE_UNKNOWN")
            self.assertIn(state, oidc._authorization_store)

            with patch.object(oidc, "_exchange_code", return_value={"id_token": "signed-token"}), \
                 patch.object(oidc, "_verify_id_token", return_value={"email": "alice@example.com", "email_verified": True}):
                accepted = first_browser.get(callback, follow_redirects=False)
            self.assertEqual(accepted.status_code, 303)
            self.assertTrue(accepted.headers["location"].startswith("/#sso="))
            self.assertIn("max-age=0", accepted.headers["set-cookie"].lower())
            self.assertNotIn(state, oidc._authorization_store)


class ResolvePrincipalTests(unittest.TestCase):
    def setUp(self):
        self.mapping = oidc.ClaimMapping(claim="email", entries={"alice@example.com": "alice"})
        self.reviewed = _reviewed({"alice": _principal()})
        self.addCleanup(oidc._reset_stores_for_tests)

    def test_verified_email_maps_to_existing_principal(self):
        claims = {"email": "Alice@Example.com", "email_verified": True}
        self.assertEqual(oidc.resolve_principal(claims, self.mapping, self.reviewed), "alice")

    def test_unverified_email_is_rejected(self):
        claims = {"email": "alice@example.com", "email_verified": False}
        with self.assertRaises(AppError) as guard:
            oidc.resolve_principal(claims, self.mapping, self.reviewed)
        self.assertEqual(guard.exception.code, "SSO_CLAIM_UNMAPPED")

    def test_unmapped_email_is_rejected(self):
        claims = {"email": "eve@evil.com", "email_verified": True}
        with self.assertRaises(AppError):
            oidc.resolve_principal(claims, self.mapping, self.reviewed)

    def test_mapped_but_disabled_principal_is_rejected(self):
        reviewed = _reviewed({"alice": _principal(enabled=False)})
        claims = {"email": "alice@example.com", "email_verified": True}
        with self.assertRaises(AppError):
            oidc.resolve_principal(claims, self.mapping, reviewed)

    def test_sub_claim_mode_is_case_sensitive(self):
        mapping = oidc.ClaimMapping(claim="sub", entries={"user-abc": "alice"})
        with self.assertRaises(AppError):
            oidc.resolve_principal({"sub": "USER-ABC"}, mapping, self.reviewed)
        self.assertEqual(oidc.resolve_principal({"sub": "user-abc"}, mapping, self.reviewed), "alice")


class SessionStoreTests(unittest.TestCase):
    def setUp(self):
        self.reviewed = _reviewed({"alice": _principal()})
        self.addCleanup(oidc._reset_stores_for_tests)

    def test_exchange_code_is_single_use(self):
        code = oidc.mint_exchange_code("alice")
        token = oidc.redeem_exchange_code(code)
        self.assertEqual(len(token), 64)
        with self.assertRaises(AppError) as guard:
            oidc.redeem_exchange_code(code)
        self.assertEqual(guard.exception.code, "SSO_EXCHANGE_INVALID")

    def test_active_session_authenticates(self):
        code = oidc.mint_exchange_code("alice")
        token = oidc.redeem_exchange_code(code)
        context = oidc.try_authenticate_sso(f"Bearer {token}", self.reviewed)
        self.assertIsNotNone(context)
        self.assertEqual(context.principal_id, "alice")
        self.assertIn("viewer", context.roles)
        self.assertIsNone(context.selected_domain)

    def test_unknown_bearer_returns_none_not_error(self):
        context = oidc.try_authenticate_sso("Bearer " + "0" * 64, self.reviewed)
        self.assertIsNone(context)

    def test_revoke_removes_active_session(self):
        code = oidc.mint_exchange_code("alice")
        token = oidc.redeem_exchange_code(code)
        oidc.revoke_session(f"Bearer {token}")
        self.assertIsNone(oidc.try_authenticate_sso(f"Bearer {token}", self.reviewed))

    def test_session_falls_back_to_none_when_principal_disabled(self):
        code = oidc.mint_exchange_code("alice")
        token = oidc.redeem_exchange_code(code)
        reviewed = _reviewed({"alice": _principal(enabled=False)})
        self.assertIsNone(oidc.try_authenticate_sso(f"Bearer {token}", reviewed))


if __name__ == "__main__":
    unittest.main()
