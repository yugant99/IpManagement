# C-A: Trusted principal and complete egress contract

Proposed contract, Q009–Q020/FR-005/015/019. Internal domain boundaries only.

## Request context
Bearer token verified server-side against individually provisioned digest, enabled state
and UTC expiry; derive principal ID, roles, allowed domains and current configuration revision.
For ordinary users require explicit selected domain on data requests (proposed `X-IPAM-Domain` header).
Never accept a body role/domain/actor as authentication. Legacy actor fields must match
derived principal or return an explained refusal. Requests remain same-origin; no wildcard
credentialed cross-origin policy. Browser token is memory-only; downloads use authenticated
fetch and a local blob, not an unauthenticated anchor or token in URL.

| Bundle | Allowed operations inside selected domain |
|---|---|
| Viewer | Scoped read, comparison display and permitted sanitized export |
| Requester | Viewer plus propose allocation/correction requests; pending-request cancellation deferred |
| Operator | Viewer plus existing bounded inventory_edit (safe child-prefix creation/edit), import/assess, reserve/extend, evaluate aging, permitted exception actions, protected readiness and manual ticket attempt/readback/zero-attempt reassignment |
| Approver | Viewer plus independently sign assessment or decide exact allocation/correction/release request; no general inventory_edit grant |
| Platform admin | Reviewed stopped configuration/state custody procedures; no implicit domain data or approval authority |

Bundles may combine; independent decision requires different principal IDs regardless of role.
Source scopes, target pool, referenced evidence and all nested links must be allowed.
Re-check permission/config/versions on mutation and readback after revocation/reload.
Missing/invalid/expired token: 401 without secret details. Authenticated forbidden operation:
403; foreign or unclassifiable direct resource: non-disclosing 404. Same-key changed content
and stale versions: 409 using the existing AppError response shape. Do not return protected
payloads in validation errors, traces, counts or denied export filenames.

## Route inventory: enforcement is not complete until every family is classified
- /api/scopes, /api/prefixes and detail/edit-context/child-preview/create/edit;
  /api/pools, /api/allocations.
- /api/actors and /api/workflow: current principal and permitted domain roster/context only.
- /api/schedule global read/run and /api/runs creation: coordinator only, explicitly granted
  every configured synthetic source/scope. Schedule configuration changes require the privileged evidence/configuration operator
  through the reviewed stopped/reload configuration procedure; ordinary domain operators have no such right.
  Ordinary domain callers cannot advance the singleton clock/cursor or global exception state.
- /api/correction-context, correction-requests list/create/detail/decision.
- /api/allocation-requests list/create/detail/decision and all proposed reservation routes.
- /api/audit and /export; /api/exceptions and actions.
- /api/run-comparison, /api/report-preset read/save/export.
- /api/imports list/create/detail/envelope/records; /api/source-catalog; /api/source-records.
  Domain creation permits only wholly owned intended-inventory candidates with reconciliation
  disabled. Reject observation input, mixed/unmapped scope/source and callback=true before
  persistence. Observation import/callback is coordinator-only; no delegated job from user input.
- /api/runs creation is coordinator-only; list/detail/export/findings/direct finding use
  separately identified authorized projections for ordinary domain reads.
- Proposed migration assessment and handoff routes.
- /api/docs and /api/openapi.json authenticated; no secret examples.
- /healthz becomes minimal non-sensitive process liveness only. Proposed /api/readiness
  contains protected readiness details. Empty UI shell/assets remain anonymous.

Collections filter before count, pagination, facet/search/summary and export. Saved mixed
runs return an explicitly identified selected-domain projection with recomputed projection
counts; do not expose global totals or links. Immutable saved result remains untouched.
Raw mixed-domain envelopes/records are denied unless every contained scope is selected and
permitted; any derived projection has separate provenance and cannot impersonate raw input.
Unknown legacy ownership is quarantined, never default-domain assigned. Domain presets are
separate; old singleton preset requires explicit classification. Scoped audit only where
all disclosed fields have known allowed provenance; otherwise retain restricted custody.

## Operator deployment boundary
Default loopback HTTP only, no enterprise identity claim. Non-loopback exposure requires
separate TLS/deployment authorization. Token digest config remains outside repository and
snapshots; document permissioned offline issuance/rotation/revocation and fail-closed startup
when configured authority is invalid. Stopped/reload revisions revalidate future operations.
Old actor-only requests fail, including old CLI wrappers; update wrappers explicitly.
The acquisition wrapper uses the separate protected coordinator credential, never the browser
operator token. It is explicitly granted fixed feed evidence/read/run/reconcile operations
across all registered scopes and sources, not arbitrary cross-domain data or local changes.
No wildcard/default-domain authority. Coordinator receives no allocation/correction/reservation/
approval/membership/ticket-delivery rights. It may update finding-derived exceptions only via
existing computation, not arbitrary close/ack instructions. Every retry rechecks authority
before disclosing stored results. Global receipts/replays/errors remain coordinator-only.
Ordinary UI refresh reloads saved results; global run/acquisition/schedule/callback controls
show unavailable, managed by evidence operator. Awaiting evidence is visible if none exists.
Container healthcheck must use minimal liveness, while operator readiness inspects all
protected booleans. Only the explicitly registered coordinator identity may run fixed global acquisition;
timer remains default off. No new per-domain clocks, feeds or reconciliation algorithm.

## Protected readiness

Protected GET /api/readiness requires Operator rights and an explicitly selected permitted
domain. Its required booleans are process_ready, schema_ready, data_ready, static_ready,
configuration_ready and domain_state_compatible; HTTP200 requires all six true.
Otherwise return a failure status and allowlisted generic reasons. Never forward raw
startup_error details, paths, foreign objects/counts or historical revision lists.
Configuration readiness validates loaded authority. Domain-state compatibility checks
prerequisites required to interpret the selected domain's current state and enforce
its permissions, not equality of every historical revision to current configuration.
Unknown ownership remains quarantined. Readiness does not prove business-state recovery;
the operator must separately compare the retained candidate/configuration and business
state evidence. /healthz discloses only minimal process liveness.

## Required later observations
Allowed/denied list/detail/export/direct-ID and nested errors; mixed raw/source/run payloads;
revocation on read and stale approval; self-approval; principal mismatch; unknown legacy data;
presets/search/count leak attempts; CLI/readiness compatibility; no token in URL/log/artifact.
These are future acceptance cases, not tests executed by this specification task.

## Lead 4.0 source-review amendments — 2026-09-22

Preserve existing safe prefix editing through the Operator bundle. Correction approval
authorizes only the exact independently reviewed correction mutation; adapt the existing
inventory_commands approval helper so an Approver does not need a general inventory_edit
grant. Direct inventory-edit routes still require Operator rights and existing validation.

T006 covers every component that owns an actor picker, including Corrections, InventoryEditor
and Workflow. Derive displayed actor and permitted actions from authenticated context.
Bind requests, protected component state and retries to principal/domain/configuration
revision; discard late responses after a context switch. Clear protected views on logout,
revocation and identity/domain change. Never render a persisted retry before authenticating
its original context; quarantine/purge the old unscoped correction payload format.
An ambiguous request remains unknown when its UI payload is cleared: retain only a minimal
original-context recovery pointer, require authorized readback before replacement, and
never silently generate a new key or resend it as another principal. Server history remains
authoritative. Within the same authorized context, exact-key retry semantics remain intact.
No token enters browser persistent storage, URLs, logs or recovery pointers.


## Lead 4.0 implementation interface — T004/T005/T006

This freezes the wire boundary for parallel implementation; it is not runtime evidence.

- V1 offline issuance uses `secrets.token_hex(32)`: exactly 32 cryptographically random
  bytes, encoded as 64 lowercase hexadecimal characters. The authority stores SHA-256
  of that exact ASCII token and `token_bits=256`. The bearer parser rejects any other
  shape. Shape validation does not prove randomness; authorized offline issuance and
  custody remain required. Never generate or retain real tokens in repository artifacts.
- `GET /api/access-context` authenticates the bearer and returns only `AccessContext`
  from T004, without inventory. Omitted domain is allowed for this bootstrap; a supplied
  `X-IPAM-Domain` must be permitted. Roles contain effective Viewer inheritance.
- All ordinary data calls send `Authorization: Bearer ...` and `X-IPAM-Domain`. Clients
  also pin `X-IPAM-Configuration-Revision` and `X-IPAM-Configuration-Digest` from bootstrap;
  a mismatch returns `409 ACCESS_CONTEXT_STALE` before protected output or mutation.
  Authenticate the bearer, enabled state and expiry before comparing pins: a revoked
  or invalid token returns generic 401 even with stale pins. Unauthenticated responses
  carry no configuration headers.
  Bootstrap and authenticated API docs do not require these pins. Coordinator calls
  use freshly authenticated explicit grants rather than an ordinary selected domain.
- Authenticated responses include the current `X-IPAM-Configuration-Revision` and
  `X-IPAM-Configuration-Digest`. The browser rejects responses from an earlier local
  session epoch or a different configuration. Refresh bootstrap before restoring any
  protected view. No credential or digest-of-token is returned.
- `GET /api/actors` is a compatibility shape containing only the current trusted
  principal, with permissions derived from its effective roles. Existing nested actor
  arrays follow the same rule; no fabricated teammate names or selectable identities.
  `request` requires Requester, `approve` Approver, `inventory_edit` and `exception`
  Operator. Combined roles combine these grants; platform admin and coordinator add none.
- `GET /api/readiness` returns T004 `ReadinessStatus` (six booleans and sanitized reasons),
  Operator-only with selected domain. `/healthz` returns only `{"process_ready": true}`.
  Ordinary viewing must not depend on permission to inspect readiness.
- Existing resource response shapes remain where safe. Saved-run projections identify
  selected domain and projection provenance, recompute counts, and never replace the
  immutable saved global result. The UI labels the projection and never displays global
  totals or raw envelopes obtained under a different context.
- `GET /api/correction-requests` may accept an optional `idempotency_key` filter for
  recovery, additionally restricted to the current principal and selected domain before
  count/pagination. Ordinary list behavior remains scoped. A request ID readback also
  rechecks current authority. This uses existing persisted request identity.
- Retain a minimal correction recovery pointer containing original principal, domain,
  configuration revision/digest, operation kind (`proposal`, `approve` or `reject`), and request ID or idempotency key.
  No token, payload, source finding, form values or actor metadata enters that pointer.
  Purge legacy unscoped saved payloads. Within one active authorized context the exact
  retry payload can remain in memory. After reload or a context change, reauthenticate
  the original principal/domain before any readback; a new configuration requires fresh
  authorization. Confirm a readback only when saved key/request ID, original principal
  (actor_id for proposals, decision_actor_id for decisions), and intended outcome match.
  A decision made by another principal does not confirm this original ambiguous call.
  Missing/denied/failed readback does not prove the old write absent or
  authorize silent replacement. Keep ambiguous work visibly unresolved.

T005 validates configuration ownership against stored scope domains and registered feed
scope/source grants. T006 resets the mounted protected application on logout, revocation
and principal/domain/configuration change, and checks its captured session epoch after
all response-body reads including downloads. Tokens stay only in memory.
