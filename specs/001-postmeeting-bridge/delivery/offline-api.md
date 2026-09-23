# T021 — Offline local HTTP API reference (source-only)

Task: **T021** (FR-009, FR-015, FR-019; contracts C-A, C-M, C-L, C-T). Author: Claude Code
`claude-opus-5-5` high, accountable to Astra / Main Lead 5.0
(`01a0ccc7-6219-73c1-bd3b-1521bb71a837`). Independent reviewer: GPT-6 Sol high.
Leased path: this file only. Ownership basis: `delivery/operator-preparation-ownership.md`
(the user reassigned the never-started Spencer preparation to agents; T022 Muse runs
separately; T024 waits for both reviews).

| Pin | Value |
|---|---|
| Inspected source (decisive) | **`cc4e281756b1847b1312d6b260b3f57bd7df0d98`**, branch `codex/bridge-t021-offline-api` |
| Application assembly contained | `a2b567b670129671f85498729753c4d577d4768e` (schema 7; T018 notice/occupancy UI; T023 stopped recovery) |
| Reviewed navigation aid | T020 `integration-matrix.md`, source-closed at `1123146ce60ac3636d9a38af8be90467c1df90bf`, integrated at `ce52b1f9b0fe527c8a84c3e80f0eed92e0f46907` |
| Runtime evidence | **None.** No bridge runtime has been observed; T025 is pending |

**Reading rule.** Where this document, the T020 matrix, a contract or an older document
disagree, the code at the pinned source is decisive for route names, fields, statuses and
roles. The line references below are to that commit.

**Every example is ILLUSTRATIVE and has not been executed.** Every request and response
example below was written by reading source code. None was captured from a running
service. Identifiers, digests, timestamps and tickets are `<placeholders>`. No token,
token digest, configuration digest or credential value appears anywhere in this document,
and none was generated. Only T025 can supply observed evidence.

---

## 0. Scope and non-claims

In scope: the complete local HTTP route inventory served by `backend/ipam_demo/app.py`,
with detailed contracts for the selected bridge interfaces (migration assessment,
reservations, allocation-request linkage, the durable ticket simulator, configured-recipient
reservation notices, current static occupancy, readiness/liveness/docs and the coordinator
schedule/acquisition surface).

This document does **not** claim any of the following:
- runtime acceptance, questionnaire row promotion, portable delivery, or human receipt. T025, T026 and T028 are separate gates.
- API activation, cutover, promotion, go-live, or any endpoint that does those things. None exists.
- external provisioning, external ticketing (ServiceNow or other), DNS/DHCP writes, CMDB, or any vendor endpoint, version or authentication. None exists, and none is guessed here.
- enterprise identity (SSO/LDAP/mTLS). The only principal is a locally configured bearer-digest principal.
- that reservation notices are the older finding/exception notifications. They are different records (§10.5).
- complete enterprise integration. The T020 matrix §3/§6 remains the register of missing integrations.

Mode vocabulary follows T020. *Source-implemented* means present in the pinned source,
source-reviewed and not observed at runtime. *Simulated* means it runs only inside
`internal-ticket-simulator/v1`. *Absent* means no route exists.

---

## 1. Authority and historical material

| Source | Role in this reference |
|---|---|
| `backend/ipam_demo/app.py`, `models.py`, `access.py`, `errors.py` | Decisive for routes, DTOs, headers, status codes and authorization order |
| `lifecycle.py`, `workflow.py`, `ticket_handoff.py`, `migration_compare.py`, `scheduler.py`, `reports.py`, `inventory.py` | Decisive for leaf validation, allowed fields, replay semantics and error codes |
| `frontend/src/api.ts`, `workflowApi.ts`, `firstPathApi.ts` | Reference client behaviour: pinning, stale/revoked clearing, recovery pointers |
| `contracts/access.md` (C-A), `migration.md` (C-M), `lifecycle.md` (C-L), `ticketing.md` (C-T), `operator.md` (C-O), `reservation-ticket-wire.md`, `ticket-api-wire.md`, `notice-api-wire.md`, `notice-recipient-wire.md`, `state-recovery-wire.md` | Frozen intent. Code implements them. Any contract-to-code difference is noted in §14 |
| `delivery/integration-matrix.md` §4 | Navigation aid only |

**Historical (pre-bridge) documents.** These describe an earlier baseline that used
actor-selected identity. They are **not** the current wire:
`docs/FOUNDATION_API.md`, `docs/STAGE2_API.md`, `docs/STAGE3_API.md`,
`docs/STAGE4_API.md` and `docs/SCHEDULING_CONTRACT.md`. For example, STAGE4_API.md §`POST /api/schedule`
documents an HTTP schedule configuration mutation that the bridge now always refuses
(§8). The `actor_id: demo-approver` examples in `docs/RUNNING.md` are also historical.
Historical runtime records, such as the S5-xx observations under `docs/evidence/` and S5-13 exception
acknowledgement, remain evidence **for their own old candidate only**. They are not bridge
runtime evidence and are not restated as such here.

---

## 2. Transport, authentication, bootstrap and configuration pins

### 2.1 Credential format and custody

- The header is `Authorization: Bearer <token>`. The token must be exactly 64 lowercase
  hexadecimal characters (`access.py:22,244-251`). Any other shape returns generic `401`.
- V1 offline issuance is `secrets.token_hex(32)`, which gives 256 random bits. The reviewed
  configuration stores only the SHA-256 of the token and `token_bits: 256`
  (`access.py:116-131`; C-A "Lead 4.0 implementation interface"). Shape validation does
  not prove randomness. Authorized offline issuance, custody and revocation are separate
  operator duties (C-A, C-O).
- Tokens never go in URLs, query strings, command arguments, logs, recovery pointers or
  browser persistent storage. The reference browser client keeps the token in memory only
  (`api.ts:125-138`).
- This document uses `<operator-token>`, `<approver-token>`,
  `<viewer-token>` and `<coordinator-token>` as placeholders only.

### 2.2 Request headers

| Header | When | Rule |
|---|---|---|
| `Authorization: Bearer <64-hex>` | Every `/api/*` path, including `/api/docs` and `/api/openapi.json` | Checked against enabled, unexpired configured principals |
| `X-IPAM-Domain: <domain>` | Every ordinary (non-coordinator) call except bootstrap and docs, where it is optional | Must name one domain the principal holds. It must be non-empty, have no surrounding whitespace, be at most 200 characters and not be `*`. A **coordinator must omit it**, otherwise `403` (`access.py:267-274`) |
| `X-IPAM-Configuration-Revision: <int>` and `X-IPAM-Configuration-Digest: <64-hex>` | Every `/api/*` call except `/api/access-context`, `/api/docs` and `/api/openapi.json`, including coordinator calls | Copy exactly from bootstrap. A mismatch returns `409 ACCESS_CONTEXT_STALE` |
| `Content-Type: application/json` | POST bodies | `POST /api/imports` refuses any other type with `422` |

The configuration digest is SHA-256 over the canonical reviewed configuration JSON
(`access.py:219`). It identifies the configuration and is not a credential. Clients must copy
it from bootstrap and must never compute or invent it.

### 2.3 Evaluation order (middleware `app.py:97-153`, then route)

1. The path is not under `/api/`. `/healthz`, `/` and static assets are anonymous (§7).
2. The reviewed configuration is loaded from `IPAM_ACCESS_CONFIG`. If it is missing or invalid, the response is `503`
   `ACCESS_CONFIGURATION_UNAVAILABLE`/`ACCESS_CONFIGURATION_INVALID`. This check comes before any bearer check.
3. The bearer is checked. An invalid, unknown, disabled or expired token returns `401 AUTHENTICATION_REQUIRED`. This response
   carries **no** configuration headers. A revoked token therefore returns 401 even when its pins are stale.
4. If a supplied `X-IPAM-Domain` is not permitted, or is sent by the coordinator, the response is `403 FORBIDDEN`.
5. If the coordinator grants do not exactly cover the registered synthetic feed, the response is `503`.
6. For non-bootstrap, non-docs calls by an ordinary principal with the domain header missing, the response is `403 FORBIDDEN`.
7. For non-bootstrap, non-docs calls with a pin mismatch, the response is `409 ACCESS_CONTEXT_STALE`. This happens before any protected output or mutation.
8. The route runs. Data routes open a transaction that validates the reviewed source-to-scope mappings
   against stored scopes (`503 ACCESS_CONFIGURATION_INVALID` on mismatch). Then the route checks
   role, resource ownership and payload. Every mutating route runs a **fresh authority check at a named
   point inside its write transaction**. It reloads the reviewed configuration file and re-authenticates
   against it. The mechanism depends on the route:
   - Domain mutations, `POST /api/imports`, `POST /api/runs` and import reconciliation use
     `write_operation` (`app.py:422-444`). Immediately after `BEGIN IMMEDIATE`, and before the operation
     runs, it re-authenticates the bearer, selected domain and pins, and re-validates the mappings.
   - `POST /api/schedule/run` does **not** use `write_operation`. The route first runs a fresh
     `require_coordinator` check (`app.py:521-528`). The scheduler then opens its own transactions in
     `SyntheticScheduler._acquire` (`scheduler.py:210-255`): first a read transaction, then its own
     `BEGIN IMMEDIATE` commit transaction. At the start of each one, before its replay lookup or state
     check, it calls the route's `authority_check`, which is `require_coordinator(request, "acquire", connection)`.
     That check freshly re-authenticates the bearer and pins, re-checks the coordinator identity and
     `acquire` grant, and re-validates the mappings and full feed authority.

   **The exact guarantee is narrow.** A revocation, disablement, expiry or configuration change that is
   already in effect when a transaction's authority check runs refuses that write. The refusal is
   401, 403, 409 `ACCESS_CONTEXT_STALE` or 503, depending on what changed. A replay or cycle is therefore
   disclosed or committed only under the authority that was valid at that check.

   The guarantee has limits:
   - **It is not atomic configuration fencing.** The reviewed configuration is a separate file. SQLite
     `BEGIN IMMEDIATE` locks only the database and does not lock or version that file.
   - A configuration replacement or revocation that takes effect **after** the final authority check can
     race the commit, and that write may still commit. Expiry that passes after the check is not re-evaluated either.
   - Later requests are evaluated against the new configuration. For a clean authority change, rely on the
     reviewed **stopped-service** configuration replacement procedure (C-A, C-O).
   - The source adds no fencing beyond the check itself.

FastAPI validates declared body and query types before the handler body runs. A malformed
body can therefore receive `422 INVALID_INPUT` (with `details.issues`) before a role or
refusal check inside the handler. This also applies to routes documented below as
"always 403". The authentication, domain and pin steps above always come first.

### 2.4 Bootstrap — `GET /api/access-context`

Bootstrap needs only the bearer. `X-IPAM-Domain` is optional. No pins are needed. It returns `AccessContext`
(`models.py:10-20`) and never returns inventory.

```http
GET /api/access-context HTTP/1.1
Authorization: Bearer <operator-token>
X-IPAM-Domain: <selected-domain>
```
ILLUSTRATIVE response, not observed:
```http
HTTP/1.1 200 OK
X-Request-ID: <request-uuid>
X-IPAM-Configuration-Revision: <revision-int>
X-IPAM-Configuration-Digest: <configuration-digest-64-hex>

{"principal_id": "<operator-principal-id>", "roles": ["operator", "viewer"],
 "domains": ["<selected-domain>"], "selected_domain": "<selected-domain>",
 "configuration_revision": <revision-int>, "configuration_digest": "<configuration-digest-64-hex>",
 "policy_revision": "<policy-revision>", "is_evidence_coordinator": false}
```
`roles` includes the effective Viewer role inherited from Requester, Operator or Approver
(`access.py:110-113`). The client must check that the body's revision and digest equal
the response headers (`api.ts:182-185`). It then sends the same pins on every later call.

### 2.5 Response headers

- `X-Request-ID` is present on every response. It is the correlation handle for server logs.
- `X-IPAM-Configuration-Revision` and `X-IPAM-Configuration-Digest` are the **current** configuration. They appear on authenticated
  responses, including `403`, `409 ACCESS_CONTEXT_STALE` and other errors, and never on `401`
  (`app.py:128-150`).
- Replay headers are listed per route in §4.
- The reference client treats any response whose configuration headers differ from its captured
  pins as stale. It clears the session and does not use the body (`api.ts:152-159`).

### 2.6 Roles

These are the configured bundles (`access.py:17-19`; C-A). Bundles can be combined. Independence checks use
principal IDs, not roles.

| Bundle | Effective data rights inside the selected domain |
|---|---|
| Viewer | Scoped reads, projections, permitted exports and exact-key recovery reads |
| Requester | Viewer rights plus create allocation or correction requests |
| Operator | Viewer rights plus prefix create/edit, staged imports, create migration assessments, reservation create/extend/release-propose, notice evaluate/acknowledge, exception actions, report preset save, protected readiness, and ticket attempt/readback/simulated-ack/zero-attempt reassign |
| Approver | Viewer rights plus independent decisions on allocation, correction, release and assessment sign-off. No general `inventory_edit` right |
| `platform_admin` | **No** data role and no Viewer inheritance. It covers stopped custody procedures only |
| Evidence coordinator | Configured with no roles and no domains. It has global evidence operations only (§8) and **no** domain-local rights |

**Optional `actor_id`.** Many existing leaf bodies accept an optional `actor_id`. It never grants
identity or permission. When present it must equal the authenticated principal ID, or the call
fails with `403 ACTOR_MISMATCH` (`access.py:282-284`, `workflow.py:60-72`). It is accepted
**only** on routes whose field lists below include it. Notice evaluate accepts only `{}` or
`{"actor_id": "<own-id>"}`. Assessment create and sign-off bodies do **not** accept it; they are strict Pydantic
models, so it would be an unknown field and return 422.

### 2.7 Stale, revoked and changed context: client clearing

These rules follow C-A §"Lead 4.0 source-review amendments" and the `api.ts` reference.
- A `401` means the token was revoked or expired. Clear the session and all protected views, and abort in-flight
  requests. Do not retry with the old token.
- A `409 ACCESS_CONTEXT_STALE`, or any response header that mismatches the pins, means the configuration changed. Clear the session and
  bootstrap again before restoring any view. Discard late responses from an earlier session epoch.
- When the principal, domain or configuration changes, keep no protected payload. Keep at most a minimal recovery
  pointer that holds the original principal, domain, configuration revision and digest, the action and key, and an optional target
  ID. It must never hold a token, reason, form value or protected response. Only the same principal and domain may resolve that
  pointer, after fresh bootstrap. A different principal can neither resolve nor resend it.
- Remove legacy unscoped retry payloads. Keep a quarantine marker so the unresolved ambiguity stays visible
  (`Corrections.tsx:38-52`).

---

## 3. Errors

Every error uses the `AppError` shape (`errors.py:14-16`):
```json
{"error": {"code": "<CODE>", "message": "<safe text>", "details": {}, "request_id": "<request-uuid>"}}
```
- Leaf validation returns `422 INVALID_INPUT` with `details.field` naming the field.
  Framework validation of query, path or strict Pydantic bodies returns `422 INVALID_INPUT` with
  `details.issues[] = {location, message, type}` (`app.py:165-169`).
- If a domain mutation fails after its target scope is authorized (and the error is not 401, 403 or 404), the server records a
  failure audit in a fresh transaction. It adds `details.audit_recorded: true|false`
  (`app.py:446-498`). A failed audit write appends a note to the message.
- Errors never carry tokens, digests of tokens, foreign identifiers or counts, raw payloads or
  server paths.

| Status | Meaning and representative codes |
|---|---|
| 401 | `AUTHENTICATION_REQUIRED`: missing, malformed, unknown, disabled or expired bearer |
| 403 | `FORBIDDEN`: role denied, domain not selected or not permitted, coordinator on a domain route, domain principal on a coordinator route, or `POST /api/schedule`. `ACTOR_MISMATCH`: body `actor_id` differs from the principal. `SELF_APPROVAL_FORBIDDEN`: the same principal cannot perform the independent decision |
| 404 | `NOT_FOUND`, non-disclosing: absent, **foreign-domain** or unclassifiable resources all look the same. Also returned for an unknown `/api/*` path after authentication (`app.py:1971-1973`) |
| 409 | `ACCESS_CONTEXT_STALE`. `IDEMPOTENCY_CONFLICT` (same key, changed content). Version conflicts `STALE_REVIEW`, `STALE_RESERVATION`, `STALE_HANDOFF`, `STALE_NOTICE`, `STALE_ASSESSMENT` and `STALE_INVENTORY`. State refusals (§10). **Integrity errors**: `RESERVATION_OPERATION_INTEGRITY`, `TICKET_HANDOFF_INTEGRITY`, `RESERVATION_NOTICE_INTEGRITY`, `MIGRATION_ASSESSMENT_INTEGRITY` and `STATIC_OCCUPANCY_INTEGRITY` |
| 413 | `UPLOAD_LIMIT`: import envelope over 10 MiB |
| 422 | `INVALID_INPUT` (unknown field, type, range), `POOL_NOT_AUTHORIZED` (non-designated pool), `SIMULATION_UNSUPPORTED`, `ACTIVE_ONLY_ACK_REQUIRED`, `FEED_IMPORT_REJECTED` |
| 500 | `INTERNAL_ERROR` (generic; see server log by request ID), `RESERVATION_NOTICE_DATA_INVALID` |
| 503 | `ACCESS_CONFIGURATION_*`, `SERVICE_UNAVAILABLE` (startup error), `STORE_BUSY` / `STORE_ERROR` (default `AppError` status), `SETUP_NEEDED`, `INVENTORY_STATE_INVALID`, and readiness not all true (§7) |

**Integrity errors are terminal for the caller.** A `*_INTEGRITY` 409 means a saved record or
receipt disagrees with canonical history. Do not retry it or work around it. Record the
`request_id` and escalate to the owning role. The server never repairs history silently.

---

## 4. Idempotency and replay conventions

| Mutation | Key field (normalization) | Key scope | Fresh / replay status | Replay signal | What a replay returns |
|---|---|---|---|---|---|
| `POST /api/migration-assessments` | `idempotency_key` (1..200, no surrounding whitespace) | principal + domain + `assessment.create` | 201 / 200 | body `replayed: true` (no header) | **Current** assessment summary (current staleness), `original_signoff: null` |
| `POST /api/migration-assessments/{id}/signoff` | same | principal + domain + `assessment.signoff` | 200 / 200 | body `replayed: true` | Current summary plus `original_signoff` (the five receipt fields) |
| `POST /api/reservations` | `idempotency_key` (trimmed, ≤200) | principal + domain + `reservation.create` | 201 / 200 | `X-Request-Replay: true` | **Original** saved receipt result (the version-1 hold), not current state |
| `POST /api/reservations/{id}/extend` | same | principal + domain + `reservation.extend` | 200 / 200 | `X-Request-Replay` | Original saved result for that extension |
| `POST /api/reservations/{id}/release-requests` | same | requester + key (own row) | 201 / 200 | `X-Request-Replay` | The saved proposal row **as it is now**, which may already show a decision |
| `POST …/release-requests/{rid}/decision` | same | principal + domain + `reservation.release.decision` | 200 / 200 | `X-Request-Replay` | Original saved decision result |
| `POST /api/allocation-requests` | `idempotency_key` (trimmed, ≤200) | actor + key | 201 / 200 | `X-Request-Replay` | Saved request row (current decision fields) |
| `POST /api/allocation-requests/{id}/decision` | none (decision hash) | request + same body | 200 / 200 | `X-Decision-Replay: true` | Saved request row |
| `POST /api/handoffs/{id}/attempt` | `idempotency_key` | principal + domain + `ticket.attempt` | 201 / 200 | `X-Request-Replay` | `{handoff: current detail, operation: {phase:"reserve", attempt: that attempt's current row}}`. **Phases 2 and 3 are never re-run** |
| `POST /api/handoffs/{id}/readback`, `/acknowledge`, `/reassign` | `idempotency_key` | principal + domain + `ticket.*` | 200 / 200 | `X-Request-Replay` | Current handoff plus the **original** event or assignment |
| `POST /api/reservations/{rid}/notice` | none (exact `expected_notification_version` + same principal + same `reason`) | notice version | 200 / 200 | `X-Request-Replay` | Current notice (only while that version is still current and unresolved) |
| `POST /api/reservations/evaluate` | none; repeat-safe by episode identity | — | 200 | `X-Request-Replay: false` always | Canonical notice list |
| `POST /api/schedule/run` (coordinator) | `idempotency_key` | coordinator actor + key | 201 / 200 | `X-Acquisition-Replay: true` and body `replay: true` | Original operation result |
| `POST /api/imports` | canonical `(source_id, source_run_id)` + canonical JSON hash | — | 201 / 200 | `X-Import-Replay` | Original receipt |
| `POST /api/correction-requests` / `…/decision` | key / decision hash | — | 201/200 · 200 | `X-Request-Replay` · `X-Decision-Replay` | Saved row |

Rules that apply to all of these:
- The server **re-checks current authority before disclosing a replay**: token, domain, role and the target's
  current scope. A revoked or re-scoped caller receives 401, 403 or 404, never the stored result.
- The same key with changed content returns `409 IDEMPOTENCY_CONFLICT`. Normalization rules decide what
  counts as the same content. For example, reservation text fields are trimmed before hashing.
- **Original receipt versus current state.** A replay proves what the original operation did.
  It does not mean the resource is still in that state. Read the resource, or the recovery read's
  `current_*` field, for current state. An assessment signed earlier can now be `current: false`.
  A reservation created earlier can now be `converted` or `released`.
- A replay never consumes budget, bumps a version, re-runs an effect or re-signs anything.

---

## 5. Retries and lost-response recovery

Only one retry is ever safe: the **exact same body and key**, sent by the **same principal and domain** in
the same authorized context. Otherwise:

1. If the outcome is ambiguous (timeout, connection loss, 5xx or cleared page), do **not** send a new key and do
   **not** switch principal. Keep the minimal pointer (§2.7).
2. Bootstrap again with the original principal and domain. If the configuration changed, authorize under the
   new pins. Recovery GETs require current Viewer access, the selected domain and current pins.
3. Call the exact-key recovery GET for the action. A **`found: false` result, a denied result or a failed recovery
   does not prove the write did not commit.** It never authorizes a replacement key. Keep the
   work visibly unresolved.
4. A `found: true` result confirms only the original own operation. It does not confirm a later decision
   made by someone else.

| Family | Recovery read (GET, query transport so keys with `/` work) |
|---|---|
| Assessment create/sign-off | `/api/migration-assessments/operation-receipt?action=assessment.create\|assessment.signoff&idempotency_key=…` |
| Reservation create/extend/decision | `/api/reservation-operations?action=reservation.create\|reservation.extend\|reservation.release.decision&idempotency_key=…` |
| Release proposal | `/api/reservation-operations?action=reservation.release.propose&idempotency_key=…&reservation_id=<uuid>` (reservation_id required) |
| Allocation create | `/api/allocation-requests?idempotency_key=…` (own principal and selected scope, before paging) |
| Allocation decision | `GET /api/allocation-requests/{id}`. It confirms only if `decision_actor_id` equals you and the terminal state matches your intent |
| Ticket attempt/readback/ack/reassign | `/api/handoff-operations?action=ticket.attempt\|ticket.readback\|ticket.acknowledge\|ticket.reassign&idempotency_key=…` |
| Notice acknowledgement | `/api/reservation-notices/{notice_id}/notifications/{version}` (exact original version) |
| Evaluate | `/api/reservation-notices` (canonical list; evaluate is repeat-safe) |
| Coordinator acquisition | After an explicit, operator-confirmed decision, re-POST the **same original** key and reason (replay under current coordinator authority), then `GET /api/schedule`. Never generate a new key or auto-retry |

Retry budgets are bounded by the server: three manual ticket attempts in total, no automatic retry,
queue or background drain. Busy responses (`RUN_IN_PROGRESS`, `STORE_BUSY`) may be retried with the
**same** key after the conflicting work finishes.

---

## 6. Complete route inventory (pinned source)

Key to principals: **V** Viewer, **Rq** Requester, **Op** Operator, **Ap** Approver,
**C** evidence coordinator. "Domain" means `X-IPAM-Domain` is required (ordinary principals). All `/api/*`
routes also require the bearer. All except bootstrap and docs require pins.

| Method & path | Principal | Kind / notes | Source |
|---|---|---|---|
| `GET /healthz` | anonymous | Minimal liveness `{"process_ready": true}` | app.py:326 |
| `GET /`, static assets | anonymous | UI shell, or a 503 setup page if the UI is not built. Not in OpenAPI | app.py:1975-1989 |
| `GET /api/docs`, `GET /api/openapi.json` | any authenticated; domain optional; no pins | Protected interactive reference (§7.3) | app.py:94-95,113-114 |
| `GET /api/access-context` | any authenticated; domain optional; no pins | Bootstrap (§2.4) | app.py:330 |
| `GET /api/readiness` | Op + domain | Six booleans (§7.2) | app.py:334-371 |
| `GET /api/actors` | any authenticated (ordinary principals + domain) | Compatibility shape: current principal only, with derived `permissions`. There are no selectable identities | app.py:500, workflow.py:42-57 |
| `GET /api/workflow` | V + domain | Designated static pool context, `baseline_version`, limitations | app.py:569 |
| `GET /api/scopes` | V + domain | Page of selected-domain scopes | app.py:373 |
| `GET /api/prefixes[?scope_id,family,owner,tag,domain,region,q]`, `GET /api/prefixes/{id}` | V + domain | Filters before paging. A foreign `domain` filter returns an empty page. Unclassified legacy origin is hidden (§9) | app.py:379-400 |
| `GET /api/prefixes/{id}/edit-context`, `…/child-preview?prefix_length=` | Op + domain | Bounded safe child editing | app.py:530-549 |
| `POST /api/prefixes`, `POST /api/prefixes/{id}/edit` | Op + domain | Audited mutations | app.py:551-567 |
| `GET /api/pools`, `GET /api/allocations` | V + domain | Pages | app.py:402-420 |
| `GET /api/schedule` | **C only** | Scheduler status (§8) | app.py:511-515 |
| `POST /api/schedule` | — | **Always `403`**, for every principal including C | app.py:517-519 |
| `POST /api/schedule/run` | **C only** | Manual synthetic acquisition (§8) | app.py:521-528 |
| `POST /api/runs` | **C only** | Global reconciliation run, `RUN_IN_PROGRESS` when busy | app.py:1738-1751 |
| `GET /api/runs`, `/api/runs/{id}`, `/api/runs/{id}/findings[…]`, `/api/runs/{id}/findings/{fid}`, `/api/runs/{id}/export` | V + domain, or C (grant projection) | **Projections** of immutable saved runs (§9) | app.py:1753-1807 |
| `GET /api/run-comparison?before_run_id&after_run_id` | V + domain, or C | Compare two projections | app.py:1413 |
| `GET /api/report-preset`, `POST /api/report-preset` (Op), `GET /api/report-preset/export?revision=<64-hex>` | V + domain | Domain-scoped preset. An unclassified legacy singleton preset is quarantined | app.py:1419-1450 |
| `POST /api/imports[?reconcile_after_import=true]` | Op + domain (staged intended inventory only) or C (observation; callback) | Canonical JSON, at most 10 MiB, `X-Import-Replay` | app.py:1632-1667 |
| `GET /api/imports`, `/api/imports/{id}`, `/{id}/envelope`, `/{id}/records[?status]`, `GET /api/source-records/{id}` | V + domain (wholly owned only) or C (granted) | Raw access only when every contained scope is selected and permitted (§9) | app.py:1669-1736 |
| `GET /api/source-catalog[?scope_id]` | V + domain or C | Declared receipt catalogue. It is *not* discovery | app.py:1681-1700 |
| `GET /api/audit[?request_id,subject_id]`, `GET /api/audit/export` | V + domain or C | Scoped and redacted audit (CSV export) | app.py:1373-1385 |
| `GET /api/exceptions`, `POST /api/exceptions/{id}` (Op) | GET: V + domain, or C (grant projection); POST: Op + domain | **Finding exceptions**. These are not reservation notices | app.py:1387-1411 |
| `GET /api/correction-context`, `GET/POST /api/correction-requests[?idempotency_key]`, `GET /api/correction-requests/{id}`, `POST …/{id}/decision` (Ap) | V / Rq / Ap + domain | Bounded correction flow | app.py:577-632 |
| `GET /api/allocation-requests[?idempotency_key]`, `POST /api/allocation-requests` (Rq), `GET /{id}`, `POST /{id}/decision` (Ap) | + domain | §10.3 | app.py:634-677 |
| `GET /api/handoffs[?source_request_id]`, `GET /api/handoffs/{id}` | V + domain | §10.4 | app.py:698-715 |
| `POST /api/handoffs/{id}/attempt\|readback\|acknowledge\|reassign` | Op + domain | §10.4 (simulated) | app.py:717-782 |
| `GET /api/handoff-operations?action&idempotency_key` | V + domain | Exact-key recovery | app.py:958-966 |
| `GET/POST /api/reservations`, `GET /api/reservations/{id}`, `POST /{id}/extend` | V / Op + domain | §10.2 | app.py:1073-1093,1220-1236 |
| `GET/POST /api/reservations/{id}/release-requests`, `GET …/{rid}`, `POST …/{rid}/decision` (Ap) | + domain | §10.2 | app.py:1238-1280 |
| `GET /api/reservation-operations?action&idempotency_key[&reservation_id]` | V + domain | Exact-key recovery | app.py:1282-1371 |
| `GET /api/reservation-notices[?reservation_id]`, `GET /{id}`, `GET /{id}/notifications/{version}` | V + domain | §10.5 | app.py:1119-1156 |
| `POST /api/reservations/evaluate`, `POST /api/reservations/{rid}/notice` | Op + domain | §10.5 | app.py:1158-1208 |
| `GET /api/current-static-occupancy` | V + domain | §10.6 | app.py:1210-1218 |
| `GET/POST /api/migration-assessments`, `GET /operation-receipt`, `GET /{id}`, `GET /{id}/export`, `POST /{id}/signoff` (Ap) | V / Op / Ap + domain | §10.1 | app.py:1878-1969 |
| any other `/api/*` (any method) | authenticated | `404 NOT_FOUND` "No API route exists at this path." Reading of the routing suggests an unsupported method on a known path also reaches this catch-all; this is unobserved | app.py:1971-1973 |

The following do **not** exist at the pinned source:
- any activate, promote, cutover or baseline-promotion endpoint.
- any schedule configuration or enable/disable mutation. `POST /api/schedule` refuses.
- any provisioning endpoint.
- any external ticket, vendor, DNS, DHCP or CMDB endpoint.
- any token issuance or rotation endpoint.
- any delete, `PUT` or `PATCH` route.
- any per-domain clock, feed or reconciliation trigger for ordinary principals.

---

## 7. Liveness, readiness and interactive documentation

### 7.1 `GET /healthz` — minimal liveness (anonymous)
It returns only `{"process_ready": true}` with 200 while the process serves HTTP (`app.py:326-328`).
It never discloses configuration, schema, data or domain state. It is the container
health-check target (C-A, C-O). **It proves nothing about readiness or business state.**

### 7.2 `GET /api/readiness` — protected readiness (Operator + selected domain)
`ReadinessStatus` (`models.py:23-30`) has six booleans plus `reasons`. HTTP 200 **only if all six are true**.
Otherwise the response is 503 with the same shape and sorted allowlisted reasons: `configuration_unavailable`,
`schema_unavailable`, `data_unavailable`, `static_unavailable` or `domain_state_incompatible`
(`app.py:334-371`). The body never includes raw startup errors, paths or foreign counts.

ILLUSTRATIVE, not observed:
```http
GET /api/readiness HTTP/1.1
Authorization: Bearer <operator-token>
X-IPAM-Domain: <selected-domain>
X-IPAM-Configuration-Revision: <revision-int>
X-IPAM-Configuration-Digest: <configuration-digest-64-hex>
```
```json
{"process_ready": true, "schema_ready": true, "data_ready": true, "static_ready": true,
 "configuration_ready": true, "domain_state_compatible": true, "reasons": []}
```
Failure example (503): `{"process_ready": true, "schema_ready": true, "data_ready": false,
"static_ready": true, "configuration_ready": true, "domain_state_compatible": true,
"reasons": ["data_unavailable"]}`.

A caller must require **status 200 and all six `true`**. Status alone is not enough
(C-O notes the old wrapper treated any 200 as ready). Viewers and the coordinator receive 403. Six
true booleans never prove business-state recovery, like-for-like configuration, portability
or human acceptance (C-A §Protected readiness; `state-recovery-wire.md`).

### 7.3 Protected interactive reference: `/api/docs` and `/api/openapi.json`
FastAPI serves Swagger UI at `/api/docs` and the generated schema at `/api/openapi.json`
(`app.py:94-95`). Both require a valid bearer. Neither needs a domain or pins. They are authoritative
for the route list and for response models where `response_model` is declared. This document
did not generate or fetch them.

How to use them, and their limits (see also `delivery/access-review.md`):
- Fetch `/api/openapi.json` with an HTTP client that adds the `Authorization` header from
  protected storage. Never put the token in a URL, a command argument, shell history or a log. Stock
  browser navigation to `/api/docs` cannot attach the bearer, and the page's own schema fetch
  would be refused with 401. Interactive Swagger use is therefore limited. This is not an
  anonymous exception.
- Many mutation routes declare the body as a generic `payload: dict`. The schema shows them as
  free-form objects. **The strict field lists in §10 are the actual accepted bodies.** The leaf
  functions reject unknown fields.
- Routes excluded from the schema: the `/api/*` catch-all, `/` and static assets.

---

## 8. Coordinator-only global actions and receipts versus domain projections

The evidence coordinator is a configured principal with no roles and no domains
(`access.py:179-191`). It must omit `X-IPAM-Domain` but must send pins. Its explicit grants must
equal the registered synthetic feed source/scope pairs exactly (`app.py:46-49,206-224`).
Scope of the coordinator:
- **Global mutations:** `POST /api/schedule/run`, `POST /api/runs`, observation `POST /api/imports`, and the
  `reconcile_after_import=true` callback. These are coordinator-only, and their receipts and replays are
  disclosed only to the coordinator.
- **Reads:** `GET /api/schedule` (coordinator only). Coordinator-grant projections of runs, imports,
  the source catalogue, audit and exceptions (`projection.domain = "coordinator_grants"`).
- **Denied (403):** every domain-local route (`require_domain`, `ordinary_domain` and
  `require_local_role` refuse the coordinator). The coordinator therefore has no allocation, correction, reservation,
  approval, notice, readiness or ticket rights.
- **Ordinary domain principals** calling a coordinator route receive `403`. Ordinary refresh re-reads **saved**
  results. It cannot advance the clock, cursor or feed, and cannot run reconciliation.

### 8.1 `GET /api/schedule` (coordinator status)
It returns the scheduler row (for example `enabled`, `interval_hours`, `config_version`, `next_due_at`,
`last_attempt_at`, `last_success_at`, `last_outcome`, `feed_version`, `cycle_index`, `cycle_id`,
`run_id`) plus `demo_clock_at`, a sanitized `last_error`, `eligibility {eligible, error}`,
`in_progress` and `timer_error` (`scheduler.py:81-113`). The timer is off by default, and there is no HTTP
way to change it. The exact column set is whatever the schema-7 `schedule_status` table holds. Treat
the list above as the fields known from schema v4.

### 8.2 `POST /api/schedule` — always refused
```json
{"error": {"code": "FORBIDDEN", "message": "Schedule configuration requires the reviewed stopped-service procedure.",
 "details": {}, "request_id": "<request-uuid>"}}
```
Status is 403 for every authenticated, pinned caller, including the coordinator, once the body parses as a JSON
object (`app.py:517-519`). Schedule changes use the reviewed stopped-service configuration
procedure only. The frontend `scheduleApi.ts` still has a caller for this route. Under the bridge, that caller gets this 403.

### 8.3 `POST /api/schedule/run` — coordinator manual acquisition
Body: strict `{idempotency_key, reason, actor_id?}` (`scheduler.py:146-158`).

ILLUSTRATIVE, not observed:
```http
POST /api/schedule/run HTTP/1.1
Authorization: Bearer <coordinator-token>
X-IPAM-Configuration-Revision: <revision-int>
X-IPAM-Configuration-Digest: <configuration-digest-64-hex>
Content-Type: application/json

{"idempotency_key": "<acquire-key>", "reason": "Manual synthetic acquisition."}
```
```http
HTTP/1.1 201 Created
X-Acquisition-Replay: false

{"operation_id": "<uuid>", "feed_version": "<feed-version>", "cycle_index": <n>, "cycle_id": "<cycle-id>",
 "demo_clock_at": "<utc-timestamp>", "run_id": "<run-uuid>", "outcome": "complete|partial",
 "completed_at": "<utc-timestamp>", "batch_ids": ["<batch-uuid>", "…"], "replay": false}
```
A replay with the same key and reason returns 200, `X-Acquisition-Replay: true` and the original body with `replay: true`.
Refusals:
- `RUN_IN_PROGRESS` (409): the service is busy. Retry the same key later.
- `FEED_EXHAUSTED` (409).
- `STALE_SCHEDULE` (409).
- `FEED_IMPORT_REJECTED` (422): the whole cycle rolled back.
- `SETUP_NEEDED` (503).
- `IDEMPOTENCY_CONFLICT` (409).

Synthetic acquisition is replayed fixture data. It is **not** live discovery.

---

## 9. Collections, pagination, export, raw versus projection, and legacy quarantine

- **Pagination.** `limit` is 1..200 (default 50) and `offset` is ≥0. Pages have the shape `{items, total, limit, offset}`
  (`inventory.py:41-42`). The migration page adds `baseline_version`. The source catalogue adds
  `evaluated_at` and `limitations`. **Authorization and scope filtering happen before counting and
  slicing.** `total` never includes foreign rows.
- **Saved runs are immutable.** `GET /api/runs…` returns a **projection**
  (`reports.py:35-100`). It contains only allowed-scope findings, calculations and batches whose sources are
  mapped, recomputed `overview` counts, and
  `projection: {kind: "selected_domain", domain, scope_ids, source_run_id}`. The stored global
  result is never rewritten. A run with nothing in the caller's scope returns 404. Run list items
  omit `findings`.
- **Raw versus projection.** `/api/imports/{id}/envelope`, `/records` and `/api/source-records/{id}`
  return raw stored input only when **every** contained scope belongs to the selected domain and its
  source/scope mapping points to that domain. Otherwise they return 404 (`app.py:1479-1495`). Records are then
  filtered to allowed scopes. A projection never impersonates raw input.
- **Legacy quarantine.** Inventory rows are hidden unless their `origin.source_id` is a
  local source or is mapped for that scope (`app.py:281-290`). Imports whose scope cannot be
  classified gain an unclassified marker and are denied. A legacy report preset with unclassified ownership is
  not assigned to a default domain. Unknown ownership is never inferred.
- **Redaction.** Foreign principal IDs in nested `actor_id`, `decision_actor_id`,
  `created_by`, `signer_id`, `requester_id`, `approver_id`, `assigned_by`, `recipient_id`,
  `acknowledged_by` and similar fields become `null`. Every scoped audit row carries a fixed reason
  and empty details. Rows written by other actors also show `restricted` as actor and role (`app.py:250-276`).
- **Exports.** Exports require authentication and domain selection before the body or filename is produced, and use fixed safe
  filenames:
  - `ipam-migration-assessment.json` (the same sanitized detail as the read).
  - `ipam-run-<run-uuid>.json` (a projection).
  - `ipam-audit.csv`.
  - `ipam-findings.csv` (headers `X-Run-ID`, `X-Preset-Revision`, `X-Report-Filters`).

  Browsers download through an authenticated fetch into a local blob (`api.ts:189-245`). There is no
  token-in-URL link.

---

## 10. Selected bridge interfaces (detailed)

All requests in this section are ordinary domain calls. They carry the four headers from §2.2, which are omitted from
the examples for brevity. All IDs are UUID strings. All responses are ILLUSTRATIVE and were not observed.

### 10.1 Immutable migration assessment (C-M; T008/T009)

**Create** (`POST /api/migration-assessments`, Operator). The strict body is
`MigrationAssessmentCreateRequest` (`models.py:236-242`):
`{source_batch_id, expected_baseline_version (strict int ≥1), idempotency_key, reason,
supersedes_id?, supersedes_reason?}`. `supersedes_reason` requires `supersedes_id`. Unknown fields,
including `actor_id`, return 422. The server derives actor, domain and mapping/authority/policy revisions from
trusted context. The source must be a complete, wholly accepted staged intended-inventory receipt
in the selected domain. It is created through `POST /api/imports` with `reconcile_after_import=false`.
```json
{"source_batch_id": "<staged-batch-uuid>", "expected_baseline_version": <baseline-int>,
 "idempotency_key": "<assess-key>", "reason": "Assess staged candidate."}
```
Response (201 fresh, 200 replay). The wrapper is `MigrationAssessmentMutation`:
```json
{"assessment": {"id": "<assessment-uuid>", "source_batch_id": "<staged-batch-uuid>",
   "source": {"id": "<staged-batch-uuid>", "source_id": "<source-id>", "source_run_id": "<run-id>",
              "source_kind": "inventory_staged", "envelope_hash": "<hash>", "ingested_at": "<utc-timestamp>"},
   "canonical_hash": "<hash>", "domain": "<selected-domain>", "mapping_revision": "<mapping-rev>",
   "authority_revision": "<canonical ipam.authority_revision.v1 JSON>", "policy_revision": "<policy-revision>",
   "baseline_version": <baseline-int>, "input_count": <n>, "accepted_count": <n>, "rejected_count": 0,
   "duplicate_count": 0, "added_count": <a>, "changed_count": <c>, "unchanged_count": <u>,
   "conflicting_count": 0, "active_only_acknowledged": false, "active_only_count": <k>,
   "created_by": "<operator-principal-id>", "created_by_current_principal": true,
   "created_at": "<utc-timestamp>", "version": 1, "state": "validated", "signer_id": null,
   "signed_by_current_principal": false, "signed_at": null, "signoff_reason": null,
   "supersedes_id": null, "supersedes_reason": null, "digest": "sha256:<64-hex>",
   "current": true, "staleness_reasons": []},
 "replayed": false, "original_signoff": null}
```
- `state` is `validated` when there are zero conflicts and `assessed` otherwise. It becomes `signed` after sign-off.
- Accounting: `input = accepted + rejected + duplicate` and
  `accepted = added + changed + unchanged + conflicting`.
- `staleness_reasons` is drawn from `baseline_changed`, `authority_changed`, `policy_changed`,
  `source_missing` and `mapping_changed`. It is computed on every read without rewriting history
  (`migration_compare.py:325-356`).
- Errors:
  - `STALE_INVENTORY` (409): baseline mismatch.
  - `MIGRATION_SOURCE_INCOMPLETE` or `MIGRATION_SOURCE_INVALID` (409).
  - `MIGRATION_ACCOUNTING_INVALID` (409).
  - `NOT_FOUND`: foreign or absent batch.
  - `IDEMPOTENCY_CONFLICT`.

**List and detail.** `GET /api/migration-assessments?limit&offset` returns
`{items: [summary], total, limit, offset, baseline_version}`, filtered to the selected domain. `GET /{id}` returns the summary
plus `rows[] {source_record_id, matching_key, candidate, active, disposition, reason}` and
`active_only[] {matching_key, active, reason}`. `GET /{id}/export` returns the same detail as an
attachment `ipam-migration-assessment.json`. The digest is recomputed on each read. An anchor mismatch
returns `MIGRATION_ASSESSMENT_INTEGRITY` (409).

**Sign-off** (`POST /api/migration-assessments/{id}/signoff`, Approver, a **different** principal
from the creator). The strict body `MigrationAssessmentSignoffRequest` is
`{expected_version (strict int), expected_digest ("sha256:"+64 lowercase hex), active_only_acknowledged (strict bool),
idempotency_key, reason}`.
```json
{"expected_version": 1, "expected_digest": "sha256:<64-hex-from-detail>",
 "active_only_acknowledged": true, "idempotency_key": "<signoff-key>", "reason": "Reviewed counts and active-only list."}
```
Response (always 200):
`{"assessment": {…, "state": "signed", "version": 2, "signer_id": "<approver-principal-id>",
"signed_by_current_principal": true, "active_only_acknowledged": true, …}, "replayed": false,
"original_signoff": {"assessment_id": "<assessment-uuid>", "assessment_digest": "sha256:<64-hex>",
"signer_id": "<approver-principal-id>", "signed_by_current_principal": true,
"signed_at": "<utc-timestamp>", "signed_version": 2}}`.
Refusals:
- `SELF_APPROVAL_FORBIDDEN` (403).
- `STALE_ASSESSMENT` (409). This covers a version or digest mismatch, and any staleness, with `details.reasons`.
- `ASSESSMENT_ALREADY_SIGNED` (409).
- `ASSESSMENT_NOT_SIGNABLE` (409): rejected input or conflicts.
- `MIGRATION_ACCOUNTING_INVALID` (409).
- `ACTIVE_ONLY_ACK_REQUIRED` (422).
- `DUPLICATE_EXPLANATION_REQUIRED` (409).

**Own-key recovery.** `GET /api/migration-assessments/operation-receipt?action=assessment.signoff&idempotency_key=<signoff-key>`
returns `{"found": true, "action": "assessment.signoff", "assessment": <current detail>,
"original_outcome": {five fields + signed_by_current_principal}}`. It returns `{"found": false, "action": …,
"assessment": null, "original_outcome": null}` for an unknown own key, which is not proof of absence. A create
outcome carries only `{assessment_id, assessment_digest}`. The original success stays visible even if the
assessment is now `current: false`.

There is **no activate, promote or cutover endpoint**. Abandoning review changes no persisted state.
A signed assessment neither changes inventory nor starts a migration.

### 10.2 Reservations (C-L; T011/T012)

Only the designated local static IPv4 pool is supported: `STATIC_POOL_ID =
8821c420-18ea-4caa-9d97-83a331c0c002` (`workflow.py:21,130-152`), which must retain family 4,
`static`, `local` and valid ranges. Holds are exact addresses.

**Create** (`POST /api/reservations`, Operator). The strict body is (`lifecycle.py:491-506`)
`{idempotency_key, pool_id, candidate (IPv4), pool_version, baseline_version, owner_reference,
service_reference, reason, duration_hours? (strict int 1..168, default 24), actor_id?}`.
Obtain `pool_version` from `GET /api/pools` (`pool_version`) and `baseline_version` from `GET /api/workflow`.
```json
{"idempotency_key": "<reserve-key>", "pool_id": "8821c420-18ea-4caa-9d97-83a331c0c002",
 "candidate": "<ipv4-in-pool>", "pool_version": <pool-int>, "baseline_version": <baseline-int>,
 "owner_reference": "<descriptive-owner>", "service_reference": "<opaque-service-ref>",
 "reason": "Hold for planned service.", "duration_hours": 24}
```
Response 201 (`X-Request-Replay: false`). The body is `ReservationSummary` (`models.py:367-387`):
```json
{"id": "<reservation-uuid>", "scope_id": "<scope-uuid>", "prefix_id": "<prefix-uuid>",
 "pool_id": "8821c420-18ea-4caa-9d97-83a331c0c002", "family": 4, "address": "<ipv4-in-pool>",
 "owner_reference": "<descriptive-owner>", "service_reference": "<opaque-service-ref>",
 "created_by": "<operator-principal-id>", "reason": "Hold for planned service.",
 "created_at": "<utc-timestamp>", "expires_at": "<utc-timestamp>", "version": 1,
 "policy_revision": "<policy-revision>", "state": "reserved", "converted_allocation_id": null,
 "released_at": null, "synthetic": true}
```
A successful create bumps the pool version and the global baseline version. Refusals:
- `STALE_REVIEW` (409).
- `CANDIDATE_OUTSIDE_POOL`, `CANDIDATE_EXCLUDED`, `CANDIDATE_RESERVED`, `CANDIDATE_OCCUPIED` and `CANDIDATE_OBSERVED` (all 409).
- `POOL_NOT_AUTHORIZED` (422 for a non-designated pool; 409 when the designated pool has lost its policy).
- `INVALID_INPUT` (422): IPv6 or malformed candidate, or out-of-range duration.
- `NOT_FOUND`: foreign pool.

**Extend** (`POST /api/reservations/{id}/extend`, Operator). The strict body is `{idempotency_key,
expected_version, expected_pool_version, expected_baseline_version, reason, duration_hours?,
actor_id?}`. The response is 200 with the new `version` and `expires_at`. Extending also resolves any open notice episode with
`resolution_reason: "reservation_extended"`. Refusals are `RESERVATION_TERMINAL`, `STALE_REVIEW`, `STALE_RESERVATION` and candidate eligibility errors.

**Reads.** `GET /api/reservations` returns a page of summaries for the selected domain. `GET /api/reservations/{id}` returns
`ReservationDetail`, which adds `history[] {id, reservation_id, version, action (created|extended|converted|released),
actor_id (own or null), occurred_at, reason, before, after}`.

**Independent unused release.**
- Propose: `POST /api/reservations/{id}/release-requests`, Operator. The strict body is
  `{idempotency_key, expected_version, expected_pool_version, expected_baseline_version, reason,
  actor_id?}`. The response is 201 or 200 replay.
- Decide: `POST /api/reservations/{id}/release-requests/{rid}/decision`, Approver ≠ requester.
  The strict body is `{idempotency_key, action: "approve"|"reject", expected_version,
  expected_pool_version, expected_baseline_version, reason, actor_id?}` (`lifecycle.py:678-700`).
  The three expected versions must equal both the versions reviewed at proposal time and the live versions.

```json
{"idempotency_key": "<decide-key>", "action": "approve", "expected_version": <reservation-version>,
 "expected_pool_version": <pool-int>, "expected_baseline_version": <baseline-int>, "reason": "Unused hold."}
```
Response 200, `ReservationReleaseRequest`:
```json
{"id": "<release-uuid>", "reservation_id": "<reservation-uuid>", "reservation_version": <reviewed-version>,
 "requester_id": null, "reason": "<proposal reason>", "expected_pool_version": <pool-int>,
 "expected_baseline_version": <baseline-int>, "state": "approved", "created_at": "<utc-timestamp>",
 "decided_at": "<utc-timestamp>", "approver_id": "<approver-principal-id>", "decision_reason": "Unused hold.",
 "synthetic": true}
```
`requester_id` is `null` here because the requester is another principal (redaction). An approve
decision sets the reservation to `released`, bumps its version, the pool version and the baseline version, and resolves notices with
`approved_local_release`. A reject decision leaves the hold in place.

Eligibility refusals:
- `RESERVATION_IN_USE` (409): an allocation exists at that address.
- `EXTERNAL_EFFECT_UNRESOLVED` (409): a linked allocation request's ticket intent is still
  `pending`, `routing_blocked` or `unknown`, **including an intent with zero attempts** (§10.4). This is a
  deliberate conservative Tier A limitation. A hold with no linked request releases normally.
- `SELF_APPROVAL_FORBIDDEN` (403).
- `RELEASE_REQUEST_TERMINAL` and `RESERVATION_TERMINAL` (409).
- `INVALID_INPUT` "Use approve or reject."

**Key recovery** (`GET /api/reservation-operations`) returns the strict DTO `ReservationOperationReadback`
`{found, action, original_outcome, current_reservation, current_release_request}`.
ILLUSTRATIVE example for `?action=reservation.create&idempotency_key=<reserve-key>` after a later extension:
```json
{"found": true, "action": "reservation.create",
 "original_outcome": {"id": "<reservation-uuid>", "version": 1, "state": "reserved", "expires_at": "<original-expiry>", "…": "…"},
 "current_reservation": {"id": "<reservation-uuid>", "version": 2, "state": "reserved", "expires_at": "<extended-expiry>", "…": "…"},
 "current_release_request": null}
```
For `reservation.release.propose`, the `reservation_id` parameter is required. `original_outcome` is the proposal as it stood when
submitted (`state: "pending"`), and `current_release_request` shows its present state. For the decision
action, the original decision and the current request are shown separately. A receipt that disagrees with canonical history
returns `RESERVATION_OPERATION_INTEGRITY` (409). A later change of state does not invalidate a valid receipt.

### 10.3 Allocation requests, the reservation link and status fields

**Create** (`POST /api/allocation-requests`, Requester). The strict body is (`workflow.py:342-361`)
`{idempotency_key, pool_id, candidate, pool_version, baseline_version, owner, purpose, reason,
supersedes_request_id?, reservation_id?, service_reference?, reservation_version?, actor_id?}`.
To **link a reservation**, supply `reservation_id` **together with** `service_reference` and a strict positive
`reservation_version`. These companions without `reservation_id` return 422. The hold must still be
`reserved` and must match the scope, pool, address, `owner = owner_reference` and `service_reference`. Otherwise
the result is `RESERVATION_MISMATCH` or `STALE_RESERVATION`. `purpose` remains descriptive. A pending request never reserves
an address.
```json
{"idempotency_key": "<alloc-key>", "pool_id": "8821c420-18ea-4caa-9d97-83a331c0c002",
 "candidate": "<reserved-ipv4>", "pool_version": <pool-int>, "baseline_version": <baseline-int>,
 "owner": "<descriptive-owner>", "purpose": "<descriptive purpose>", "reason": "Convert hold.",
 "reservation_id": "<reservation-uuid>", "service_reference": "<opaque-service-ref>", "reservation_version": 2}
```
The response is 201 (`X-Request-Replay`) with the existing row-shaped request projection: `id, actor_id, idempotency_key,
pool_id, scope_id, candidate, pool_version, baseline_version, state: "pending", allocation_id,
created_at, decided_at, decision_actor_id, decision_reason, downstream_status, reservation_id,
payload, synthetic, local_outcome`, with foreign actors shown as null. The same transaction records exactly one
ticket intent (§10.4). A missing route yields `routing_blocked` and the request is still created.

**Decision** (`POST /api/allocation-requests/{id}/decision`, Approver ≠ requester). The body is
`{action: "approve"|"reject", reason, simulate_failure?, actor_id?}`. For every intent-backed (new)
request, `simulate_failure: true` returns `422 SIMULATION_UNSUPPORTED`. Approval uses only the saved
request's reservation identity. It inserts the allocation and converts the hold (`state: "converted"`,
`converted_allocation_id`, version+1, notices resolved with `reservation_converted`) with a single pool/baseline bump
in one transaction. The response is 200 with `X-Decision-Replay`.

**Two distinct status fields. Never interchange them.**
| Field | Where | Values | Meaning |
|---|---|---|---|
| `downstream_status` | Allocation request row (`workflow.py:450,502-508`) | New intent-backed decisions: `"not_requested"`. Pending: `null`. **Legacy** rows without an intent: `simulated_success` or `simulated_failure` | Historical compatibility column. It is not ticket state |
| `provisioning_status` | Ticket handoff DTO (`models.py:185`, `ticket_handoff.py:419`) | Always `"not_requested"` | Tier A provisioning is unsupported and not requested. This is a labeled absence, not a simulation |

Local approval changes only the local ledger. Ticket delivery is separately simulated. A legacy request with no
intent is **not tracked**: `GET /api/handoffs?source_request_id=<legacy>` returns an empty page, which is not a failure.

### 10.4 Durable ticket handoff — `internal-ticket-simulator/v1` (C-T; T013/T014), simulated

**Read.** `GET /api/handoffs[?source_request_id=<uuid>]` returns a page of `TicketHandoffSummary`.
`GET /api/handoffs/{id}` returns `TicketHandoffDetail` (`models.py:123-198`). ILLUSTRATIVE detail excerpt:
```json
{"id": "<intent-uuid>", "domain": "<selected-domain>", "source_request_id": "<request-uuid>",
 "source_request_state": "approved", "action": "allocation.request", "correlation": "<correlation-uuid>",
 "business_payload_digest": "<business-payload-digest-64-hex>",
 "business_payload": {"reviewed_pool_version": <pool-int>, "reviewed_baseline_version": <baseline-int>,
                      "service_reference": "<opaque-service-ref>", "reservation_version": 2,
                      "reason_code": "local_allocation_review"},
 "contract_version": "internal-ticket-simulator/v1", "mode": "simulated", "state": "pending", "version": 1,
 "created_at": "<utc-timestamp>", "current_route_assignment_version": 1,
 "route": {"assignment_version": 1, "configuration_revision": "<revision-as-text>", "route_revision": "<route-rev>",
           "team": "<configured-team>", "reason": "Initial reviewed route.", "assigned_at": "<utc-timestamp>",
           "assigned_by": null},
 "attempt_limit": 3, "attempts_used": 0, "attempts_remaining": 3, "observation_budget_seconds": 5,
 "latest_attempt": null, "readback_required": false, "resolution_reason": null,
 "recipient_acknowledged": false, "provisioning_status": "not_requested",
 "label": "Simulated ticketing handoff — ServiceNow mapping pending.", "simulated": true, "synthetic": true,
 "availability_evaluated": true, "attempt_allowed": true, "attempt_block_reason": null,
 "reassignment_allowed": false, "route_history": ["…"], "attempts": [], "events": []}
```
- Intent `state` is one of `pending`, `routing_blocked`, `unknown`, `delivered` or `failed`. `version` increments on
  every intent transition. It is the `expected_version` for every mutation.
- `attempt_block_reason` is one of `connector_disabled`, `source_request_rejected`, `reservation_released`,
  `delivered`, `readback_required`, `attempt_budget_exhausted`, `routing_blocked` or `route_changed`. The same
  reasons are refused at attempt time as 409 with codes such as `CONNECTOR_DISABLED` and `READBACK_REQUIRED`
  (`ticket_handoff.py:30-47`).

**Attempt** (`POST /api/handoffs/{id}/attempt`, Operator). The strict body is `{expected_version, idempotency_key,
synthetic_scenario, actor_id?}`. `synthetic_scenario` is one of `success`, `definitive_failure`,
`committed_response_lost` or `no_effect_response_lost`. The route runs **three separately committed,
separately re-authenticated transactions** (`app.py:717-755`):
1. **Reserve.** Consumes the next ordinal (1..3) forever. The intent goes to `unknown` and the `ticket.attempt`
   receipt is saved. The scenario and route assignment version are pinned.
2. **Effect.** Commits the durable simulator effect for `success` and `committed_response_lost` only.
   It creates the synthetic ticket ID (`SIM-…`). No response is observed in this phase.
3. **Observe.** Records the observed response against the 5-second deadline measured from `started_at`. This is a deadline, not a sleep.

| Scenario | Effect committed | Observed `result` / `reason` | Intent after observe |
|---|---|---|---|
| `success` | yes | `delivered` / `simulated_success` with `observed_ticket_id` | `delivered` |
| `definitive_failure` | no | `failed` / `simulated_definitive_failure` | `failed` (another attempt allowed within budget) |
| `committed_response_lost` | yes | `unknown` / `response_lost` | `unknown`, readback required |
| `no_effect_response_lost` | no | `unknown` / `response_lost` | `unknown`, readback required |
| any, observed after 5 s | — | `unknown` / `observation_deadline_elapsed` | `unknown` |

```json
{"expected_version": 1, "idempotency_key": "<attempt-key>", "synthetic_scenario": "committed_response_lost"}
```
The fresh response is 201 with `X-Request-Replay: false`: `{"handoff": {…, "state": "unknown", "version": 3, "readback_required": true, …},
"operation": {"phase": "observe", "attempt": {"id": "<attempt-uuid>", "ordinal": 1,
"route_assignment_version": 1, "synthetic_scenario": "committed_response_lost",
"started_at": "<utc-timestamp>", "observation_deadline_at": "<utc-timestamp>", "ended_at": "<utc-timestamp>",
"result": "unknown", "reason": "response_lost", "observed_ticket_id": null, "observed_effect_id": null},
"effect_phase_recorded": null}}`.

A replay with the same key returns 200 with `operation.phase: "reserve"`, and **does not run phases 2 or 3**.

If phase 2 or phase 3 fails after phase 1 committed, the recovery pointers depend on the error
(`app.py:748-753`):
- For an `AppError` whose status is **not** 401, 403 or 404, the route adds `details.handoff_id`,
  `details.attempt_id`, `details.readback_required: true` and
  `details.recovery_action: "POST /api/handoffs/<id>/readback"`. This covers, for example, 409 block or state errors
  and 503 `STORE_BUSY`/`STORE_ERROR`, because `audited_write` converts store errors to `AppError`.
- A **401, 403 or 404** from phase 2 or 3 carries **no** recovery pointers and no handoff or attempt
  identifiers. That covers a token already revoked or expired when phase 2 or 3 re-authenticates, a role or domain denial, or a target no longer in scope, and the
  body is the ordinary generic error. Any other unexpected failure is a generic `500 INTERNAL_ERROR`, which also has no pointers.

In every case phase 1 may already have committed. The ordinal stays consumed, and any committed effect stays
committed. There is no automatic retry and no reset of the budget. If the response had no pointers, or was
lost, the caller must still treat the attempt as possibly reserved. Keep the original-context recovery
information: principal, domain, configuration pins, the handoff `id`, the action `ticket.attempt` and the
original `idempotency_key`. Then, after re-establishing that same authorized context:
1. Call `GET /api/handoff-operations?action=ticket.attempt&idempotency_key=<original-key>` to find the
   reserved attempt.
2. Call `GET /api/handoffs/{id}` for current state.
3. Send an explicit readback. Do not send a new attempt key.

A denied or failed recovery keeps the attempt unresolved. It is not proof of absence.

**Readback** (`POST /api/handoffs/{id}/readback`, Operator). The strict body is **exactly**
`{expected_version, idempotency_key, correlation, business_payload_digest, actor_id?}`
(`ticket_handoff.py:803-805`). **`key` and `digest` are not accepted aliases.** Any unknown field returns 422.
`correlation` and `business_payload_digest` must equal the handoff's values exactly. Otherwise the result is
`HANDOFF_IDENTITY_MISMATCH` (409).
```json
{"expected_version": 3, "idempotency_key": "<readback-key>", "correlation": "<correlation-uuid>",
 "business_payload_digest": "<business-payload-digest-64-hex>"}
```
Outcomes are recorded as an event and a receipt. The response is 200.
- `found`: a persisted effect exists for that exact correlation and digest. The attempt is updated to `delivered`
  with the **actual** synthetic ticket ID. The intent becomes `delivered`. Event: `{"event_type": "readback",
  "outcome": "found", "effect_id": "<effect-uuid>", "returned_ticket_id": "<SIM-ticket-id>", …}`.
- `definitive_absence`: an uncertain (`pending` or `unknown`) latest attempt is fenced as `failed`
  (`reason: readback_definitive_absence`, `resolution: "uncertain_attempt_absent"`). A later
  effect phase for that attempt is refused. Another attempt is allowed if budget remains. For a **zero-attempt** intent,
  absence changes the intent to `failed` only when the source request is `rejected`
  (`zero_attempt_source_rejected`) or the linked hold is `released`
  (`zero_attempt_reservation_released`). This creates no attempt and no ticket, releases no hold and cancels no request. An active
  source stays `pending` or `routing_blocked`.
- `error` (`error_code`, for example `SIMULATOR_LOOKUP_INCONSISTENT`): the outcome is unchanged and stays unknown.

Readback never claims success without a found effect. It remains available while the connector is disabled,
after route changes and for rejected or released sources.

**Simulated acknowledgement** (`POST /api/handoffs/{id}/acknowledge`, Operator). The strict body is
`{expected_version, idempotency_key, correlation, business_payload_digest, effect_id, ticket_id,
acknowledgement_mode: "simulated", actor_id?}`. It requires intent `delivered`. `effect_id` and `ticket_id`
must match the delivered attempt (from `latest_attempt.observed_effect_id` and `observed_ticket_id`).
It sets `recipient_acknowledged: true` and records an event with `acknowledgement_mode: "simulated"`. It grants
**no** local authority, changes no decision and creates no effect. Refusals are `HANDOFF_NOT_DELIVERED`,
`EFFECT_MISMATCH` and `ALREADY_ACKNOWLEDGED` (409).

**Zero-attempt reassignment** (`POST /api/handoffs/{id}/reassign`, Operator). The strict body is
`{expected_version, idempotency_key, reason, actor_id?}`. There is **no destination field**. The team always
comes from the current reviewed configuration. It is allowed only while the intent is `pending` or `routing_blocked` with zero
attempts, and only when the configured route differs from the current assignment. It appends
`route_history`, returns the intent to `pending` and keeps correlation and digest unchanged. Refusals are
`REASSIGNMENT_NOT_ALLOWED` (any attempt exists, which also means a route change after an attempt is unsupported in Tier A),
`ROUTE_UNAVAILABLE`, `ROUTE_UNCHANGED` and `STALE_HANDOFF`.

**Own-key recovery** (`GET /api/handoff-operations?action=ticket.attempt&idempotency_key=<attempt-key>`) returns
`TicketHandoffOperationReadback` `{found, action, original_operation, current_handoff}`.
ILLUSTRATIVE:
```json
{"found": true, "action": "ticket.attempt",
 "original_operation": {"phase": "reserve", "attempt": {"id": "<attempt-uuid>", "ordinal": 1,
   "route_assignment_version": 1, "synthetic_scenario": "committed_response_lost", "result": "pending",
   "reason": null, "ended_at": null, "observed_ticket_id": null, "observed_effect_id": null, "…": "…"},
   "assignment": null, "event": null},
 "current_handoff": {"id": "<intent-uuid>", "state": "delivered", "version": 4, "…": "…"}}
```
The original operation shows only the durable reservation of the ordinal. Later observed state appears only in
`current_handoff`. Readback and ack recovery return the original sanitized `event`. Reassign recovery returns the
original `assignment`. Other responses:
- An unknown own key returns `found: false` with nulls. This is not proof that nothing committed.
- A malformed or inconsistent authorized receipt returns `TICKET_HANDOFF_INTEGRITY` (409).
- A foreign receipt returns 404.

**Disable.** `connector_mode: "disabled"` in the reviewed configuration blocks new attempts and effects (`CONNECTOR_DISABLED`).
Reads, readback, history and simulated acknowledgement of an already delivered effect remain available.
No external ticket system is contacted in any mode. The ServiceNow mapping is pending and unverified
(T020 §6).

### 10.5 Reservation notices: per-version configured recipient (FR006; T016A/B, T017A)

A reservation notice is a **local reservation-expiry lifecycle record**. It is **not** a
reconciliation finding or a finding exception (`/api/exceptions`, whose older S5-13 acknowledgement
evidence is historical and separate). Acknowledging a notice never clears an exception, a due
condition or a hold. Resolution, delivery and acknowledgement are distinct states.

- **Recipient.** The optional `notice_recipients[]` list in the reviewed configuration maps
  `(domain, scope_id)` to **one** Operator principal. There is no fallback to the creator,
  `owner_reference` or any Operator. Binding is immutable **per `notification_version`**. The routing status
  at binding time is `assigned`, `unassigned` (`missing_mapping`) or `unroutable` (`unknown_principal`,
  `disabled`, `expired`, `not_operator` or `wrong_domain`). Migrated schema-6 versions are
  `legacy_unbound` (`access.py:340-380`, `lifecycle.py:74-116`).
- **Versions.** `episode_number` identifies the due episode. `notification_version` increments on a
  new binding: the alarm upgrade at due+24 h, a changed recipient or eligibility, or renewal of a legacy or missing binding. One
  evaluate increments it at most once per notice.
- `acknowledgement_version` is **not** acknowledgement evidence. A new notice is inserted unacknowledged with
  `acknowledgement_version = 1` (`lifecycle.py:247-252`), and the schema-6 column defaults to 1. The value is
  set to the acknowledged version only when a recipient receipt is recorded (`lifecycle.py:350-354`), so on its own it
  proves nothing, whether it is `1` or the value of a legacy or migrated row.
  - **Receipt evidence** is the exact notification version's binding, from `current_notification`,
    `notification_history[]` or `GET …/notifications/{version}`. It requires `in_app_receipt: true`,
    `acknowledgement_kind: "recipient_in_app"`, `delivery_status: "acknowledged"` and a non-null
    `acknowledged_at`. The recipient can confirm its own receipt when `acknowledged_by` equals its principal ID; for
    every other caller `acknowledged_by` is redacted to `null`.
  - The parent `state` and `acknowledged_*` fields and a `legacy_operator` acknowledgement are **not** recipient
    receipts.

**Evaluate** (`POST /api/reservations/evaluate`, Operator). The body must be `{}` or `{"actor_id": "<own-id>"}`.
Caller time, configuration or finding IDs are refused. It uses server UTC only. For each `reserved` hold in the
designated pool whose `expires_at` has passed, it opens an `alert` notice, or an `alarm` notice when at least 24 h have passed.
An existing `alert` is upgraded to `alarm` at +24 h as a new notification version. Expiry never frees the hold. The response is 200,
`X-Request-Replay: false`, `ReservationNoticeEvaluation`:
`{"evaluated_at": "<utc-timestamp>", "created_count": <n>, "renewed_count": <n>,
"alarm_upgrade_count": <n ≤ renewed>, "notices": [<ReservationNotice>…], "synthetic": true}`.

**Read.** `GET /api/reservation-notices[?reservation_id]` returns a page, and `GET /api/reservation-notices/{id}` returns
`ReservationNotice` (`models.py:553-623`). ILLUSTRATIVE, as seen by the bound recipient:
```json
{"id": "<notice-uuid>", "reservation_id": "<reservation-uuid>", "episode_number": 1,
 "policy_revision": "<policy-revision>", "first_due_at": "<utc-timestamp>", "alert_level": "alarm",
 "owner_reference": "<descriptive-owner>", "state": "open", "acknowledgement_version": 1,
 "notification_version": 2, "acknowledged_at": null, "acknowledged_by": null, "acknowledgement_reason": null,
 "acknowledgement_current": false,
 "current_notification": {"notice_id": "<notice-uuid>", "notification_version": 2,
   "recipient_id": "<operator-principal-id>", "configuration_revision": <revision-int>,
   "configuration_digest": "<configuration-digest-64-hex>", "routing_status": "assigned", "routing_reason": null,
   "issued_at": "<utc-timestamp>", "acknowledged_by": null, "acknowledged_at": null,
   "acknowledgement_reason": null, "delivery_status": "awaiting_receipt", "is_current_recipient": true,
   "acknowledgement_kind": null, "owner_signoff": false, "in_app_receipt": false},
 "notification_history": ["<version 1 binding>", "<version 2 binding>"],
 "notification_history_coverage": "complete", "delivery_status": "awaiting_receipt",
 "is_current_recipient": true, "acknowledgement_kind": null, "owner_signoff": false,
 "in_app_receipt": false, "resolved_at": null, "resolution_reason": null, "synthetic": true}
```
Other principals see `recipient_id`, `acknowledged_by` and `acknowledgement_reason` as `null`, and
`is_current_recipient: false`. `delivery_status` is one of `awaiting_receipt`, `unassigned`,
`recipient_unavailable`, `legacy_unbound` or `acknowledged`. `acknowledgement_kind` is
`recipient_in_app`, `legacy_operator` or `null`. `owner_signoff` is always `false`: a configured recipient is not a
proven business owner.

**Acknowledge** (`POST /api/reservations/{reservation_id}/notice`, Operator). The body is `{notice_id,
expected_notification_version, reason, actor_id?}`. `notice_id` is used for routing. The remaining fields are strictly validated.
The caller must be the recipient **bound to that version** and must also be the current mapped, eligible recipient.
```json
{"notice_id": "<notice-uuid>", "expected_notification_version": 2, "reason": "Seen; extension under review."}
```
The fresh response is 200 with `X-Request-Replay: false`. What evidences the receipt is the version-2 binding in
`current_notification`: `notification_version: 2`, `acknowledged_by: "<own-principal-id>"`,
`acknowledged_at: "<utc-timestamp>"`, `delivery_status: "acknowledged"`,
`acknowledgement_kind: "recipient_in_app"` and `in_app_receipt: true`. The route refuses to return success
unless exactly this own receipt is present (`app.py:1200-1205`). The parent also shows `state: "acknowledged"`,
`acknowledgement_version: 2` and `acknowledgement_current: true`, but these are summaries and not receipt evidence
on their own.

A replay by the same principal with the same reason, while that version is still current and unresolved, returns 200 with
`X-Request-Replay: true` and the original receipt. Refusals:
- `NOTICE_ROUTE_CHANGED` (409): evaluate must bind the new recipient first.
- `FORBIDDEN` (403): the caller is not the bound recipient.
- `NOTICE_BINDING_MISSING` (409).
- `STALE_NOTICE` (409): the version changed.
- `NOTICE_RESOLVED` (409).
- `NOTICE_ALREADY_ACKNOWLEDGED` (409): a different reason, or another receipt exists.
- `NOTICE_INELIGIBLE` (409).
- `RESERVATION_NOTICE_INTEGRITY` (409).

**Original-version recovery** uses `GET /api/reservation-notices/{notice_id}/notifications/{version}`. The version must be a canonical
positive decimal. This read never binds, renews or reroutes. After a lost response, and even after a later
renewal or resolution, it confirms the caller's own receipt on the exact original version
(`acknowledged_by` equals the caller, `in_app_receipt: true`). The response adds `reservation_id` and `episode_number`
to the binding shape. A missing version returns 404, which is not proof of absence. A different, changed or foreign
acknowledgement does not confirm the original call. At that point a POST replay would return
`STALE_NOTICE` or `NOTICE_RESOLVED`, so use this GET instead.

### 10.6 Current static occupancy versus immutable saved DHCP metrics

`GET /api/current-static-occupancy` (Viewer; designated static pool in the selected domain) returns a
**current local-ledger** metric (`workflow.py:174-210`). ILLUSTRATIVE:
```json
{"metric": "current_static_ipv4_occupancy", "pool_id": "8821c420-18ea-4caa-9d97-83a331c0c002",
 "scope_id": "<scope-uuid>", "domain": "<selected-domain>", "family": 4, "unit": "IPv4 addresses",
 "as_of": "<utc-timestamp>",
 "components": {"active_allocations": {"count": <a>, "unit": "IPv4 addresses"},
   "reserved_holds": {"count": <h>, "unit": "IPv4 addresses", "includes_expired": true},
   "occupied_total": {"count": <a+h>, "unit": "IPv4 addresses"},
   "assignable_capacity": {"count": <cap>, "unit": "IPv4 addresses"},
   "remaining_assignable": {"count": <cap-a-h>, "unit": "IPv4 addresses"}},
 "provenance": {"source": "current local intended ledger",
   "capacity": "designated static IPv4 pool ranges minus exclusions",
   "allocations": "allocations in the designated pool and selected scope",
   "reservations": "reservations with state=reserved, including expired holds",
   "saved_runs_modified": false, "synthetic": true}, "synthetic": true}
```
Converted and released holds are excluded. Expired holds still count, because expiry never frees capacity.

**Saved DHCP metrics are a different thing.** They live in immutable saved runs
(`GET /api/runs/{id}` → `calculations[]` per pool, with `current`, `p95` (720 hourly samples,
nearest-rank) and `forecast`; `calculations.py:42-99`). They apply only to DHCP-managed IPv4 pools. A static
pool's saved metric reports `status: "not_applicable"`. The occupancy endpoint never reads or rewrites a
saved run, and a saved run is never recomputed from current occupancy. Never add, compare or
substitute one for the other. They have different authority, time basis and units. There is no IPv6 delegation or
host-occupancy metric.

---

## 11. Known unsupported inputs, pools, families and actions

| Input | Result |
|---|---|
| Any unknown body field on the leaf mutations in §10 | `422 INVALID_INPUT` ("only the documented fields"). There is no silent drop |
| `key`, `digest`, `destination`, `team`, `time`, `configuration`, `finding_id`, `role` or `domain` in any §10 mutation body | Unknown field returns 422. Identity, domain, time and routing always come from server context |
| `actor_id` ≠ authenticated principal | `403 ACTOR_MISMATCH` |
| Non-designated pool for reservation or allocation | `422 POOL_NOT_AUTHORIZED` in-domain, or `404` if foreign |
| IPv6 or malformed candidate | `422 INVALID_INPUT` (IPv4 only) |
| Designated pool not family 4 / static / local, or with invalid ranges | `409 POOL_NOT_AUTHORIZED` or `INVALID_CAPACITY` |
| `duration_hours` not a strict int in 1..168 (for example `true`, `1.5` or `0`) | `422` |
| Versions that are booleans, floats, non-positive or strings | `422` "must be a positive integer" |
| Release decision `action` not `approve`/`reject`; ticket `synthetic_scenario` off the allowlist; `acknowledgement_mode` ≠ `simulated` | `422` |
| `simulate_failure: true` on an intent-backed allocation decision | `422 SIMULATION_UNSUPPORTED` |
| Ordinary import with observation records, mixed or unmapped scopes, or `reconcile_after_import=true` | `403` before persistence |
| Non-JSON import, or import over 10 MiB | `422` or `413` |
| `POST /api/schedule` | After authentication, domain and pin checks pass (§2.3), a well-formed JSON-object body reaches the handler and always gets `403 FORBIDDEN`, including for the coordinator (§8.2). A malformed, missing or non-object body can get `422 INVALID_INPUT` from request validation before the handler runs. No body ever configures the schedule |
| Ticket route change after any attempt | `409 REASSIGNMENT_NOT_ALLOWED` (Tier A unsupported) |
| Allocated reclaim or reuse, provisioning, external ticket delivery, DNS/DHCP writes | No route exists (Tier B locked or absent) |

---

## 12. Operator and recovery links (canonical elsewhere)

- Stopped backup, restore and migrate CLI with the `<snapshot>.recovery.json` manifest, and configuration
  recovery classification `like_for_like`, `changed_configuration` or `unverified`: see
  `contracts/state-recovery-wire.md` (frozen T023) and `docs/STATE_OPERATIONS.md`. After any restore,
  run §7.2 readiness (all six booleans) **and** a separate selected-domain business-state comparison. A
  configuration classification never proves readiness or business recovery.
- Operator deployment boundary, token custody and non-loopback TLS gate: C-A §Operator deployment
  boundary and `contracts/operator.md`.
- Integration gaps and vendor unknowns: `delivery/integration-matrix.md` §3 and §6.
- Local service start and seeding: `docs/RUNNING.md`, whose actor-based API examples are historical (§1).

---

## 13. Handoff to T024 (operator package, Muse)

**Status: T024 has not started.** The user has explicitly paused T024 until they resume it tomorrow. Nothing
in this section is implemented. It records the API contract that a **future** T024 implementation must
meet. Everything here is derived from the pinned API source, and none of it was executed.

**Current wrappers at the pinned source, which predate the bridge.** Neither meets the bridge
authentication contract:
- `scripts/ops/health.sh` sends only anonymous `GET /healthz` (default `http://127.0.0.1:8000/healthz`). It maps
  200 to exit 0 and a 503 body containing `SETUP_NEEDED` to exit 1. Under the bridge, `/healthz` returns only
  `{"process_ready": true}`, so this script proves liveness only. Its `SETUP_NEEDED` branch is never
  produced by the current `/healthz`. It does not call `/api/readiness`.
- `scripts/ops/acquire.sh` sends `POST /api/schedule/run` with **no** `Authorization` header and no configuration
  pins. Its default body is `{"actor_id": "demo-approver", …}`, and it takes `--actor`, `--reason` and the idempotency key on the command line and logs
  them. Against the bridge API it would receive `401 AUTHENTICATION_REQUIRED` (§2.3). No
  `demo-approver` identity or actor selection exists in the bridge.
- `scripts/ops/start.sh` still tells operators to check `/healthz` for `SETUP_NEEDED`, and names the Docker volume
  `ipam_demo_data`. Those are historical or unverified statements. They are not readiness or volume evidence.

**Required future T024 behaviour** (C-A, C-O and this reference):
- **Container liveness.** The container health check targets anonymous `GET /healthz` and treats it as process liveness only.
- **Readiness wrapper** (future `scripts/ops/health.sh`):
  - It must use a separately provisioned **domain Operator** credential and send `X-IPAM-Domain` for one selected domain.
  - It must bootstrap `GET /api/access-context` to obtain the configuration revision and digest.
  - It must call `GET /api/readiness` with those pins.
  - It must report ready only on HTTP 200 **and** all six booleans `true`. Otherwise it reports the allowlisted `reasons`.
  - It must state that readiness is not a business-state comparison or human acceptance.
- **Acquire wrapper** (future `scripts/ops/acquire.sh`):
  - It must use the separately provisioned **coordinator** credential, never a browser, Operator or approver token. It must
    **not** send `X-IPAM-Domain`.
  - It must bootstrap for pins and then send `POST /api/schedule/run` with `{idempotency_key, reason}`.
  - It must interpret `X-Acquisition-Replay`, the 201 or 200 status, and the body `replay`.
  - It must have no `demo-approver` default and no actor selection. If `actor_id` is sent at all, it must equal the
    coordinator principal ID.
  - It must never assume that `POST /api/schedule` can configure anything, because that route always returns 403.
- **Both wrappers:**
  - Take the token from protected storage, never from command arguments, URLs, environment dumps, shell history or logs.
    Log `X-Request-ID`, not tokens or protected bodies.
  - Treat a `401` as a hard stop, because the credential is revoked or expired. Do not retry.
  - On `409 ACCESS_CONTEXT_STALE`, refresh the access context explicitly with one bootstrap to obtain the current pins.
    This is a **context refresh only**. It must **never** automatically re-send a mutation.
  - After a stale, ambiguous or failed acquisition, any retry must be an explicit, operator-confirmed action. It
    must reuse the **same original** `idempotency_key` and `reason`, so the server either replays the committed result
    or refuses. It must never generate a new key.
  - For recovery of an uncertain outcome, re-send the same key and reason, which replays under current coordinator
    authority, and then read `GET /api/schedule`, as described in §5.

**Scope boundaries for the future T024 lease:**
- T024 owns the six task-graph package and ops paths (`task-graph.csv` T024 row).
- The lead has approved a narrow expansion, recorded in the lead's ownership and pickup records. It covers only the
  authentication, readiness and configuration text in `docs/RUNNING.md`, and the readiness and actual-volume text in the
  start and backup scripts.
- This T021 document does not edit those files and does not claim to implement them.
- A target platform that is absent from source today does not prevent later authorized T024 source or documentation work.
  Target observations remain separate.

**Pinning and evidence split:**
- T024 pins the **declared** package references: assets, dependency and licence declarations, and the presenter path.
- **Observed** Compose plugin versions, target behaviour and all runtime evidence for this API belong to the later,
  separately authorized **T025**. They are not T021 or T024 source claims.
- T025 supplies the first observed evidence for everything in this document.

---

## 14. Source-inspection record

Inspected read-only at `cc4e281…`, with no execution:
- Repository rules: `AGENTS.md`, `DEVELOPMENT_RULES.md`, `docs/STATUS.md`.
- Task records: the T021 and T024 rows in `task-graph.csv` and `tasks.md`, and `delivery/operator-preparation-ownership.md`.
- T020 material: `integration-matrix.md` and `integration-matrix-source-review.md`.
- Contracts: C-A, C-M, C-L, C-T, C-O, `reservation-ticket-wire.md`, `ticket-api-wire.md`, `notice-api-wire.md`,
  `notice-recipient-wire.md` and `state-recovery-wire.md`.
- Backend code: `backend/ipam_demo/app.py` (all 1991 lines), `models.py`, `access.py`, `errors.py`,
  `lifecycle.py`, `workflow.py` (1-520), `ticket_handoff.py`, `migration_compare.py` (selected sections),
  `scheduler.py` (selected sections), `reports.py` (`project_run`), `inventory.py` (`page`),
  `calculations.py` (metric shape), and the schema v3, v4 and v6 table definitions for `allocation_requests`,
  `schedule_status` and `ticket_intents`.
- Frontend code: `frontend/src/api.ts` (session, pins, clearing, downloads), and the `/api/` call sites in
  `workflowApi.ts`, `firstPathApi.ts`, `correctionApi.ts`, `inventoryCommandsApi.ts` and `scheduleApi.ts`.
- Historical documents: a grep of `docs/STAGE4_API.md` and `docs/RUNNING.md` for markers of historical API use.
- Current operator wrappers, read as part of the correction pass: `scripts/ops/health.sh` and `scripts/ops/acquire.sh` in full, and a grep of
  `scripts/ops/start.sh`, `backup.sh` and `common.sh` for readiness and volume text. None was run or edited.

Correction pass after the independent Sol review of initial candidate
`b57d9283b7ffdb24347afabf5706b4bd48c0e0ed`. Each item was re-checked against the pinned source:
1. §13 now presents the protected health and acquire wrappers as **required future T024** behaviour. It records
   the current pre-bridge wrappers (anonymous `/healthz`, and an unauthenticated `demo-approver` acquire). It states that T024 is on hold, that stale context
   is handled by explicit context refresh only with no automatic mutation retry, and that T024 pins declared references while observations belong to T025.
2. §2.3 narrows the fresh-authentication claim. `write_operation` covers domain, import and run mutations.
   `POST /api/schedule/run` re-authenticates through `authority_check` inside `SyntheticScheduler._acquire`'s
   own transactions.
3. §10.4 now states that recovery pointers are added only to caught `AppError`s other than 401, 403 and 404, and
   keeps the original-context recovery steps.
4. §10.5 no longer treats `acknowledgement_version` as acknowledgement evidence. Receipt evidence is the exact
   version's `in_app_receipt`, the recipient's own `acknowledged_by` and `acknowledged_at`.
5. The dangling reference to §15 in §1 now points to §14.

Final precision pass, after Sol's complete-source review, keeping items 1–5 above:
6. The §11 quick-reference row for `POST /api/schedule` now matches §2.3 and §8.2. A well-formed JSON object gets 403, while a
   malformed or non-object body can get 422 before the handler.
7. §2.3 now states the exact guarantee: fresh authority at a named check inside the write transaction. Revocation
   that is already effective at that check refuses the write. A change to the separate configuration file after the final
   check can race the commit, because `BEGIN IMMEDIATE` does not fence the file. §10.4's 401 wording is aligned with this. No code changed.

Consistency with the T020 matrix §4:
- All routes and field names there match the source.
- This document adds the notice acknowledgement body name `notice_id`, the migration POSTs' use of the body `replayed` flag
  instead of a replay header, `X-Decision-Replay` on decisions, sign-off being always 200, the acknowledge body fields, and
  coordinator omission of `X-IPAM-Domain`. All come from source.
- One contract-to-code wording difference: C-A describes `platform_admin` custody without data. The code gives
  `platform_admin` no effective Viewer role, which is consistent.

### Unverified limits
- **Nothing here was executed.**
  - No tests, builds, imports, type checks, lint, SQL or DB access, runtime, browser, shell, Git or network were used.
  - `/api/openapi.json` was not generated.
  - Status codes, headers and bodies are derived from reading source. Framework behaviours are inferred and unobserved:
    - request-validation ordering;
    - catch-all versus 405 handling;
    - how `null` renders for `effect_phase_recorded`.
- `workflow.py` beyond line 520 and parts of `migration_compare.py` and `scheduler.py` were read only in the sections
  cited. The exact schema-7 `schedule_status` columns and the exception, correction and prefix leaf bodies are not detailed
  here. They are outside the selected bridge interfaces.
- Pool and baseline version sources for clients (`GET /api/pools` → `pool_version`; `GET /api/workflow`
  → `baseline_version`) are read from source and unobserved.
- No evidence of a customer, vendor, portable target or human recipient exists or is implied. Questionnaire ledgers
  are unchanged. Tier B stays locked.

READY FOR PROJECT-LEAD REVIEW — Stage T021: complete source-only offline API reference at
`specs/001-postmeeting-bridge/delivery/offline-api.md`, pinned to inspected source
`cc4e281756b1847b1312d6b260b3f57bd7df0d98` (branch `codex/bridge-t021-offline-api`; assembly
`a2b567b…`, schema 7). Lead commits and opens the PR; one file changed. Draft next prompt: "Sol, independently
review `delivery/offline-api.md` at the T021 commit against the pinned `app.py`, `models.py`, `access.py`,
`lifecycle.py`, `workflow.py`, `ticket_handoff.py`, `migration_compare.py` and `scheduler.py` for route, field, status,
role and replay accuracy. Check that no example claims to be observed, that no secrets or digests are invented, that no alias or vendor endpoint appears, that
`downstream_status` and `provisioning_status` are separate, and that notices and exceptions are separate. Once T022 is also reviewed, record T024-ready and STOP before implementation; release T024 only when the user resumes tomorrow."
