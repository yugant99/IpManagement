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
| Operator | Viewer plus existing bounded inventory_edit (safe child-prefix creation/edit), import/assess, reserve/extend, evaluate aging, permitted exception actions and manual ticket attempt/readback |
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
