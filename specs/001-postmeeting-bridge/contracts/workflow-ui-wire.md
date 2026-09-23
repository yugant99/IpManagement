# T015 workflow UI boundary

Full feature owner: Muse1.3 high in OpenCode. Lead pins the reviewed T014/T016
source assembly before dispatch. Lease: frontend/src/Workflow.tsx and
frontend/src/workflowApi.ts only. Sol independently reviews the complete feature.
This is source implementation only; no tests/build/typecheck/browser/runtime before T025.

## Complete user path

Use existing accessible form, table, detail and error patterns. Preserve exception
queue/audit behavior and current C-A access/session guards. Implement reservation
create/list/detail/extension, unused release proposal and independent decision;
optional exact reservation-linked allocation with service reference and versions;
and scoped simulated ticket list/detail/manual attempt/readback/reassignment/
acknowledgement. Use actual T012/T014 DTOs and leaf constraints as authority, not
invented fields or endpoints. Unsupported actions remain unavailable. Preserve
historical unlinked allocation payload/hash and downstream results. New tracked
requests omit simulate_failure and show provisioning not_requested/unsupported.

Show reservation state and expiry (expired does not mean free), local allocation
request outcome and ticket handoff state separately. Ticket display includes fixed
correlation, route/assignment, manual attempt count/cap3, unknown/readback-required,
original operation versus current state, and simulated receipt. Use server-declared
attempt/reassignment availability and current version. No route change after an
attempt, automatic retry, timer, effect resumption or inferred provisioning success.

## Persistent recovery and context

Reuse Corrections.tsx/MigrationCompare.tsx patterns. Before sending a mutation,
persist a minimal pointer in sessionStorage: original principal/domain/config pin,
action, exact operation key and necessary immutable target IDs/version. Never store
tokens, credentials, form bodies/reasons/service references, private evidence or
raw receipts. Storage failure/malformed existing pointer blocks replacement writes.
Keep exact retry payload only in memory within the original active context. Changing
identity/domain/configuration clears protected in-memory data and pending payloads,
quarantines the pointer and requires authorized readback; no stale async render.
Pointer mismatch never permits sending the earlier mutation as a new principal.

Reservation operations use GET /api/reservation-operations with query key/action
(and reservation_id for release.propose). Handoff operations use GET
/api/handoff-operations with query key/action. Own allocation-create recovery uses
GET /api/allocation-requests?idempotency_key; reconcile canonical key/current own
principal and target. Allocation decision recovery uses direct request GET and
immutable own terminal decision. Preserve original outcome versus mutable current
state. A missing/denied/failed/mismatched receipt is unknown; it cannot prove a write
will not commit or authorize silent replacement. Clear only after the original
operation is confirmed; visible unresolved pointer continues to block replacement.

Attempt is three committed transactions. ApiError currently discards details,
including readback_required; therefore pointer plus exact-key GET is authoritative.
Retain the original pointer after ANY failed attempt POST, including server, stale
configuration, session change, revocation and late phase errors. Never automatically
repeat the POST or assume a4xx rolled back earlier phases. A found original reserve
receipt establishes the ordinal only; current unknown state requires separate manual
readback using current version and durable correlation/digest. Definitive absence
fences that attempt; error/missing readback remains unknown. Further manual attempts
require server permission and consume the next ordinal without resetting the cap.

Keep labels task-oriented and concise. No owner delivery claim, external ticket
system connection, customer/portable proof, saved finding rewrite or Tier B work.
T018 owns notice/occupancy UI next; this slice supplies its reservation/ticket path.
