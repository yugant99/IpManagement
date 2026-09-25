# Part 6: OpenID Connect sign-in (Spencer)

Owner: Spencer. Branch: `sj/oauth_oidc`. Base: `codex/part-4-sources-polling`.

## Win

A deployment can enable OpenID Connect sign-in as a second, independent path into Pool Watch. When it is enabled, an operator signs in through the configured identity provider, is mapped to an existing reviewed principal, and reaches the same protected inventory UI as the token path. When it is not enabled, the SSO button is visibly disabled and every SSO endpoint refuses to activate. The existing reviewed access-token path is unchanged.

## Owned files

- `backend/ipam_demo/oidc.py` — configuration loader, PKCE authorization, state/nonce store, callback, id_token verification (via `pyjwt[crypto]`), single-use exchange code, in-memory session store, claim→principal mapping.
- `tests/test_oidc_signin.py` — 23 focused unit tests. All pass. Callback state binding and keyword-only token transport have regression coverage.
- `frontend/src/ssoAuth.ts` — thin client for `/api/auth/sso/*`.
- `frontend/src/App.tsx` — one small block added inside the existing sign-in card: SSO button, config probe, fragment-code exchange, logout hook. No changes to navigation, Sources default view or protected UI.
- `frontend/src/styles.css` — five lines for the SSO separator and button.
- `sample-config/oidc-mapping.example.json` — schema example, no real secrets.
- `pyproject.toml` and `uv.lock` — pin `pyjwt[crypto]==2.10.1` for production and `httpx2==2.13.1` for Starlette's TestClient in development.
- `backend/ipam_demo/app.py` — mount OIDC and share one authentication path across middleware, coordinator checks, and protected writes. A reviewed bearer is checked first; a live SSO session is checked when that bearer is rejected.

## Output contract

**Deployment configuration.** All required to enable SSO. Missing any one keeps SSO invisible.

| Environment variable | Required | Purpose |
| --- | --- | --- |
| `IPAM_OIDC_ISSUER` | yes | Identity provider issuer URL. |
| `IPAM_OIDC_CLIENT_ID` | yes | Registered public client id. |
| `IPAM_OIDC_CLIENT_SECRET_FILE` | yes | Path to a file containing the client secret. The value is not read from an env var. |
| `IPAM_OIDC_REDIRECT_URI` | yes | Must match the identity provider registration exactly. |
| `IPAM_OIDC_MAPPING_FILE` | yes | Path to the claim→principal mapping file. |
| `IPAM_OIDC_PROVIDER_NAME` | optional | Button label. |
| `IPAM_OIDC_SCOPES` | optional | Defaults to `openid email`. |
| `IPAM_OIDC_AUTHORIZATION_ENDPOINT` | optional | Explicit override of the discovery result. |
| `IPAM_OIDC_TOKEN_ENDPOINT` | optional | Explicit override of the discovery result. |
| `IPAM_OIDC_JWKS_URI` | optional | Explicit override of the discovery result. |

**Mapping file** (`sample-config/oidc-mapping.example.json`).

```json
{
  "claim": "email",
  "entries": [
    {"value": "alice@example.com", "principal_id": "operator-alice"}
  ]
}
```

- `claim` must be `sub` or `email`.
- Each `principal_id` must already exist in the reviewed access configuration; unknown, disabled or expired principals fail closed.
- For `email`, values are lowercased for lookup and the identity provider must set `email_verified: true`; unverified emails are rejected.
- Roles and domains are never derived from claims; only the reviewed configuration grants them.

**HTTP surface.**

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/auth/sso/config` | Public. `{enabled: bool, provider_name: string \| null}`. |
| GET | `/api/auth/sso/authorize` | Public. Redirects to the identity provider with PKCE. |
| GET | `/api/auth/sso/callback` | Public. Validates id_token, mints a single-use exchange code, redirects to `/#sso=<code>`. |
| POST | `/api/auth/sso/exchange` | Public. Redeems the exchange code and returns `{token: <64-hex>}`. |
| POST | `/api/auth/sso/logout` | Public. Best-effort session revocation. Unknown tokens are silently ignored. |

Session tokens minted by SSO share the shape of the reviewed bearer (64-hex). They map to the same reviewed `AccessContext`. Unknown SSO tokens are rejected; the existing reviewed-token path remains available. The callback also checks that the returned state matches a short-lived HTTP-only browser cookie.

## Acceptance and limits

**Verified locally (separate store and port, not the recorded demo on 18841).**

- The frontend typechecks cleanly (`npx tsc --noEmit`).
- 23 backend unit tests pass with `PYTHONPATH="backend:fixtures/evolving" .venv/bin/python -m unittest tests.test_oidc_signin`. The focused OIDC and ServiceNow checks pass together (31 tests). The wider legacy suite still has the previously reproduced 25 errors and 1 failure unrelated to OIDC.
- Backend imports and creates the FastAPI app; all five SSO routes register.
- Configuration gating: missing env → `is_configured()` False, `/api/auth/sso/config` returns `{enabled:false}`, other SSO endpoints return 404 `SSO_UNAVAILABLE`.
- Claim resolution rejects unverified email, unknown mapping, disabled principals and case-mismatched `sub` values.
- Single-use exchange code, session revocation, browser-bound state, and reviewed-bearer fallback are covered by tests and/or the local browser pass.
- A fresh `uv sync --frozen --no-dev` installs PyJWT and cryptography; the frontend build passes on the combined UI + OIDC candidate.
- In an isolated copied store on port 18853, a local simulated OIDC provider completed authorization, PKCE token exchange, RS256 JWKS verification, reviewed-principal mapping and domain selection. Sources, Inventory, Reconciliation, Capacity, report-preset save, sign-out, reviewed-token fallback and the 15-second source refresh worked in the browser. No console errors or warnings were observed.

**Not verified.** No end-to-end run against a real deployment identity provider. The local provider is simulated and cannot establish Rogers connectivity or production SSO configuration.

**Out of scope for this slice.** Refresh tokens, back-channel logout, session persistence across process restarts, per-user rate limits, and any change to the reviewed access-configuration schema.

## Coordination with Opus

This branch is based on `codex/part-4-sources-polling` (23aa12a), which contains the Evidence Sources slice. Its merge is coordinated with the later UI work; the combined candidate was tested in a separate integration worktree.

## Next visible result after R1

Point `IPAM_OIDC_*` at a live identity provider (or a Keycloak container) with a matching mapping entry, click the SSO button, and complete the round trip into the Sources landing view. Report the actual provider, mapped principal and any behavioral gaps back to Spencer.
