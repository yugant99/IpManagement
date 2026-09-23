# T012/T013 shared wire freeze — 2026-09-22

Main Lead 5.0 / Astra adopts this source contract after independent GPT-6 Sol high
inspection of pickup `352f5a7ba891b4c13c9670beb9eee7d0b60bc764`. This document
settles the boundary for the two complete feature assignments. The commit that
publishes this freeze is their common source base, recorded in the dispatch registry.
No runtime evidence or earlier-main-merge permission follows.

## Ownership and integration

T012, OpenCode `opencode-go/muse-spark-1.3-contributor#high`, owns only
`backend/ipam_demo/app.py` and `backend/ipam_demo/models.py`.
T013, Claude Code `claude-opus-5-5` with high effort, owns only
`backend/ipam_demo/ticket_handoff.py` and `backend/ipam_demo/workflow.py`.
Both use separate codex branches/worktrees from the exact common base. Neither
worker changes schema, contracts, lifecycle.py, UI, packaging or global status.
Lead publishes commits/PRs for tool-restricted external workers. Sol independently
reviews both complete diffs and their combined invariants before source integration.
T014 follows that integration and owns ticket HTTP routes; no speculative T014
endpoint is included in T012.

## T012 reservation HTTP boundary

Expose GET/POST `/api/reservations`, GET `/api/reservations/{id}`, POST
`/api/reservations/{id}/extend`, GET/POST
`/api/reservations/{id}/release-requests`, GET
`/api/reservations/{id}/release-requests/{request_id}`, and POST
`/api/reservations/{id}/release-requests/{request_id}/decision`.
Use UUID path IDs, C-A scoped Viewer reads, Operator create/extend/propose and
independent Approver decision. Derive identity from the authenticated context;
an optional actor_id must match that identity, never grant permission.

Delegate to the existing lifecycle functions. Create accepts idempotency_key,
pool_id, candidate, pool_version, baseline_version, owner_reference,
service_reference, reason and duration_hours (default24; strict integer1..168).
Extend accepts idempotency_key, expected_version, expected_pool_version,
expected_baseline_version, reason and duration_hours. Release proposal uses the
same fields without duration; decision adds action approve/reject. Preserve leaf
validation, strict positive versions, unknown-field rejection and exact payload
hashes. expected_version names the reservation version in these leaf contracts.

All mutations use the existing audited_write/write_operation immediate transaction.
Authorize the actual saved scope before setting audit_scope_id or serializing any
resource. Reauthorize current target ownership even on replay. Use explicit response
DTOs/allowlists and existing foreign-actor redaction, including nested history and
operation receipts; do not expose raw before_json/after_json/payload_json/digests
as an accidental database-row API. JSONResponse must receive the same sanitized
projection as ordinary reads because it bypasses response_model filtering. Return
X-Request-Replay; create/propose use201 fresh and200 replay, other mutations200.
Lists retain existing Page/pagination conventions after authorized filtering.
Release proposals replay from their own unique requester/key row. Only release
decisions use receipt action reservation.release.decision. No new receipt action
or schema change. No evaluate/notice/current-occupancy endpoint before T017.

Allocation create retains existing payload fields and accepts reservation_id only
with service_reference and strict positive reservation_version. Reject companion
fields without reservation_id. Do not inject null/default reservation keys into old
unreserved payloads: retain dict forwarding or use exclude_unset and deliberately
preserve the original normalization/hash. Approval takes reservation identity only
from the saved request. Purpose remains descriptive.

## One shared call and local decision compatibility

T013 changes the core entry point to
`workflow.create_request(connection, payload, *, configuration)` and keeps its
`(result, replay)` return. T012 changes the allocation-create call to pass
`configuration=request.state.access_configuration` from inside the freshly
reauthenticated write boundary. Do not reread config in the leaf or accept it from
the request body. This is the only new T012 dependency on T013.

T013 inserts exactly one action=`allocation.request` intent after a new allocation
request row is inserted, in that same caller-owned transaction with the request
audit. The bound trusted context supplies principal/domain; the supplied reviewed
configuration supplies routing. Missing route records routing_blocked, not failed
request creation. Initial absent route_revision is `unmapped`; configuration_revision
is the string representation of the reviewed revision. Routes use the exact
`(selected_domain, allocation.request)` key. Disabled connector mode still records
the logical intent but blocks attempts. No legacy replay backfill.

For a new intent-backed request, local approval/rejection never simulates delivery
or provisioning. Preserve downstream_status=`not_requested`; reject
simulate_failure=true as unsupported for this new path. Keep the existing decision
hash algorithm for accepted fields and preserve all historical decision/status/replay
behavior for legacy rows without an intent. A legacy row remains not tracked by
ticketing. Do not manufacture a receipt or update local decision from ticket state.

## T013 durable simulator core

Implement scoped get/list, atomic intent creation, zero-attempt reassignment,
attempt reservation, durable simulated effect, response observation, readback and
explicit simulated recipient acknowledgement. Use the existing schema6 tables,
tier_a_operation_receipts and AppError conventions. Functions take a caller-owned
connection and current trusted context/reviewed configuration where needed; they
must not commit or open a hidden connection. No remote clients, queues or workers.

Expose these named entry points for T014: `get_handoff`, `list_handoffs`,
`reserve_attempt`, `commit_simulator_effect`, `observe_attempt`,
`readback_handoff`, `acknowledge_handoff`, `reassign_handoff`. Read functions use
connection plus context; mutations additionally take an intent/attempt ID, payload
and configuration. Each mutation returns `(result, replay)`; the author must report
the precise final signatures in its source handoff. T014 will orchestrate three
separately committed and freshly authorized immediate transactions: reserve ordinal
and operation identity; commit the selected synthetic effect; record observed result.
A replay never reserves another ordinal or reruns an effect. Crash recovery goes
through explicit readback. A reserved/pending attempt consumes its ordinal forever.

Business payload is an explicit allowlist from the saved request: domain, action,
source_request_id, correlation, service_reference when present, reviewed pool and
baseline revisions, reservation revision when present, and a fixed reason code.
Exclude raw payload, candidate address, owner, descriptive purpose, free-text reason,
credentials and source envelopes. Compute stable digest excluding route/team and
assignment metadata. Exactly one intent per domain/request/action; changed payload
for the same identity conflicts. Correlation and effect ID must never be invented
from a timeout or overwritten during reassignment.

Attempt body freezes expected_version, idempotency_key and synthetic_scenario
(success, definitive_failure, committed_response_lost, no_effect_response_lost).
Pin current assignment version and scenario in the attempt digest/record; three total
manual attempts, including the first. No automatic retry. Five-second observation
budget is a deadline, not an instruction to sleep; elapsed/ambiguous/crashed response
stays unknown. Definitive absence readback is required before retrying an uncertain
attempt. Readback requires expected_version, key, exact correlation and business
digest, returns found with the actual persisted synthetic ID, definitive_absence,
or sanitized error. Lookup errors retain unknown; every outcome is durable/audited.
Acknowledgement additionally pins that actual effect/ticket and explicit simulated
mode. Reassignment requires expected_version, key and reason, selects only the
current configured team and appends assignment history. It is allowed only in
pending/routing_blocked with zero attempts. After any attempt no route change.

Current authority/configuration is checked before all actions and replay disclosure.
Changed routing blocks new attempts until an allowed reassignment; it cannot move
an already attempted team. Disabled mode blocks attempts but permits authorized
history/readback. Audit, state and receipts share each phase transaction. Raw stored
payloads, foreign principal details and error text are not public projections.

## Conservative unused-release disposition

Preserve T011's current refusal while a linked intent is pending, routing_blocked or
unknown, including a zero-attempt intent. An unused reservation that has no linked
allocation request can be independently released normally. A linked hold may require
explicit ticket resolution first; T014/T015 must make that reason visible. This is a
deliberate conservative Tier A limitation, not implicit cancellation or a claim that
an external effect occurred. New attempts must also refuse a released reservation
or a rejected source request; authorized readback/history remain available. No
lifecycle.py ownership is reassigned or hidden cancellation behavior introduced.

## Review and deferred evidence

Sol checks strict identities/versions, selected-domain and nested/replay isolation,
historical hashes, atomic conversion and exactly one pool/baseline bump, durable
ordinal/effect separation, route lineage, lookup uncertainty, local/ticket independence
and source compatibility. T025 later observes these on the final assembled disposable
synthetic candidate after all prerequisites. Source review is not runtime, portable,
human or production acceptance. Tier B remains locked.

## T012 exact-key recovery amendment — independent source review

Sol's review of T012 `c5b59cb4a47e07a87b594f13bee0ca7316c0d965` found that
list/detail alone cannot recover a lost create/proposal response after a reload
clears the payload. Add GET `/api/reservation-operations/{idempotency_key}` with
action query enum reservation.create, reservation.extend,
reservation.release.decision, reservation.release.propose. Proposal lookup also
requires reservation_id. The first three use existing tier_a_operation_receipts;
proposal lookup uses its own requester/key row, never a new schema receipt action.

Restrict lookup to current principal, selected domain and exact action/key, using
ordinary authorized Viewer readback. Reauthorize the receipt's current resource
scope and related reservation before decoding/disclosing historical outcome.
For proposal lookup authorize the supplied and saved reservation before comparing
identities. A foreign/unclassifiable target remains a generic404. Reconcile raw
receipt target_kind/target_id, reservation identity and historical version/state
against canonical reservation/history or immutable release decision before
projection. Inconsistent receipt data is a generic409 integrity error, not a
different outcome or an exposed raw payload. A later extension/conversion/release
must not invalidate a valid historical receipt merely because current state differs.

Return a strict allowlisted DTO: found, action, original_outcome,
current_reservation, current_release_request. For missing own-key records return
found=false and null outcomes. Found create/extend carries sanitized historical
reservation outcome plus current reservation; found proposal/decision carries
the sanitized release outcome plus current reservation/current release request.
Foreign actor redaction and raw-JSON exclusions apply identically to read and
mutation responses. Missing/denied/failed readback does not prove an in-flight
operation cannot commit or authorize replacement. T015 must retain that ambiguity.

This completes C-A's existing recovery requirement without changing schema,
legacy payload hashes, source base or file ownership. The frozen base remains
b557137; this review-driven documentary amendment is separately committed by lead.

## T013 source-review resolution clarification

Sol's review of initial T013 `8d0b49e88bb8355a4f746cd1e1cdb721bb4dd12e`
identified a release dead end for a rejected linked request that never attempted
ticket delivery. A fresh authorized exact-correlation/digest readback that proves
definitive absence resolves an eligible pending/routing_blocked zero-attempt intent
to failed when the saved source request is rejected or its reservation is released.
Record the reason, readback event and before/after audit. Do not create an attempt,
claim delivery, cancel the request, release the hold or change lifecycle eligibility.
An inconsistent zero-attempt delivered/unknown record is an integrity failure, not
permission to overwrite its state. Active zero-attempt requests retain pending or
routing_blocked so the existing reassignment path remains possible. If local
rejection follows an earlier absence readback, a fresh readback is required; old-key
replay does not silently resolve the new state. An uncertain attempted absence still
fences that attempt before setting failed.

C-T's disabled setting blocks new attempts/effects. Current authorized readback,
history and explicitly simulated acknowledgement of a previously delivered exact
persisted effect remain available. Acknowledgement requires the same version, key,
correlation, digest, effect and ticket checks, creates no new delivery and grants no
local decision authority. This interpretation was independently challenged by Sol
and accepted by lead; no new external connector or broader mutation right follows.

Ticket mutation leaves authorize current role/configuration before payload semantics;
T014 also scopes the saved target before mutation dispatch. Workflow presentation
says local approval affects only the local ledger, ticket delivery is separately
simulated and provisioning is unsupported/not requested. Legacy stored statuses
retain their historical meaning. Source base and file ownership remain unchanged.
