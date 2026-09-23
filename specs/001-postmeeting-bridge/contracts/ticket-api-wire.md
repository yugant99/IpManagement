# T014 HTTP wire — source-only continuation

Astra lead, independent GPT-6 Sol high challenge. T014 starts only after exact
T012/T013 source integration. Own app.py/models.py only on an isolated codex branch;
no schema/core/UI edits, tests, imports, builds or application execution before T025.

## Routes and authority

Expose GET /api/handoffs (Page with optional source_request_id, selected-domain
filtering before count/pagination), GET /api/handoffs/{id}, and POST
/api/handoffs/{id}/attempt, /readback, /acknowledge, /reassign. UUID resource IDs,
current Viewer reads and Operator mutations; coordinator has no domain rights.
Scope the canonical intent/source request before exposing nested fields or setting
audit_scope_id, then check mutation role before payload semantics. Pass freshly
authenticated context/configuration to existing T013 functions inside audited_write.
Forward the existing strict leaf dict payloads without silently dropping fields.

Define explicit nested DTOs for the exact public core projection and validate
JSONResponse bodies too. Keep current local request state, simulated ticket state,
receipt and provisioning_status=not_requested distinct. Legacy allocation requests
without intent remain not tracked: no backfill or invented success. List-by-source
empty for an authorized legacy request is not a failed delivery. Foreign source
filters/direct resources are non-disclosing. No route change after an attempt.

## Three committed phases

POST attempt first calls reserve_attempt in one audited_write transaction. On fresh
reservation only, take its canonical attempt ID and call commit_simulator_effect
in a second audited_write transaction, then observe_attempt in a third. Each
transaction commits independently and refreshes current token/domain/configuration.
The original HTTP body supplies expected_version/key/scenario only to phase1;
subsequent phases use the same key and optional matching actor, never caller-controlled
replacement IDs or scenario. No sleep, automatic retry, background drain or new
connection/commit inside the leaf. A replayed reserve returns its authorized saved
operation/current handoff immediately; never automatically executes later phases.
A phase2/3 failure preserves the earlier committed ordinal/effect and visible
unknown/readback requirement, with ordinary sanitized error handling. Authentication
revocation may block disclosure; it never authorizes stale return data.

Use X-Request-Replay on mutations, 201 fresh attempt and200 replay; other successful
mutations200. Core readback/ack/reassign use one audited_write. Disable blocks new
attempt/effect but preserves authorized reconciliation of committed effects. The
five-second deadline is enforced by the core; HTTP success alone is not delivery.

## Exact-key recovery after a cleared payload

GET /api/handoff-operations?idempotency_key=...&action=... is current-principal,
selected-domain Viewer read-only lookup. Actions: ticket.attempt, ticket.reassign,
ticket.readback, ticket.acknowledge. Query transport supports all previously accepted
keys, including slash; use the existing nonempty normalized max200 key rule.
Return a strict DTO with found, action, original_operation and current_handoff.
A missing own-key record returns found=false/nulls; it does not prove a pending
write cannot commit or permit silent replacement. Denied/failed lookup stays unknown.

For attempt: resolve receipt target attempt -> canonical intent/source scope and
authorize before parsing receipt JSON. Reconcile target kind/id and saved intent ID,
attempt ID, ordinal, pinned assignment/scenario against the canonical immutable
attempt. Original operation identifies its durable pending reservation/ordinal;
current_handoff separately carries later observed state. Do not return raw receipts,
request hashes or an unobserved simulator effect ID.

For other actions: resolve canonical intent and authorize before receipt parsing.
Reassign reconciles the saved assignment version with immutable assignment identity,
current principal and reason/time/route data. Readback/ack reconciles saved event ID
against canonical receipt-linked event, action/event_type/outcome, actor, intent,
correlation/digest and matching effect/ticket/attempt references. Reuse the core's
already sanitized public detail history for output after identity checks, not raw
database-row output. Any malformed or inconsistent authorized receipt is generic409,
foreign/unclassifiable resource generic404. Current mutable intent state may differ
from historical operation; that does not invalidate a legitimate receipt.

Astra will freeze the exact implementation SHA for T015. Sol independently reviews
whole T014 routes, three commit boundaries, partial failure, replay, nested isolation
and recovery before source acceptance. Application and portable/human evidence stay
pending. Tier B and bridge-to-main merge gates remain unchanged.

## Allocation create recovery dependency for T015

The existing allocation-request list also accepts optional idempotency_key query
filter, normalized by the original key rule. In this filtered mode restrict results
to current principal and selected scope before pagination, matching the saved
normalized request payload key. Preserve ordinary list behavior and mutation hashes.
This reuses C-A's correction recovery pattern for a lost allocation create response;
no new write or legacy backfill. Direct-ID immutable decision recovery can confirm
its saved terminal outcome and current principal as decision actor. Missing own key
or unmatched decision remains ambiguous and never silently authorizes replacement.
