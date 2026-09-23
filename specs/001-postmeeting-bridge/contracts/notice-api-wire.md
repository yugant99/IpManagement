# T017 notice and current occupancy HTTP wire

Lead: Main Lead5.0 / Astra. T017 starts after independent T014/T016 source closure
and integration; app.py/models.py only. No tests/imports/builds/runtime before T025.
Use the existing C-A request context and audited_write transaction boundary; no
scheduler/service/timer changes, raw source exports or saved-run rewriting.

## Routes

- GET /api/reservation-notices: Viewer, optional reservation_id, Page limit/offset.
  Authorize a supplied reservation before filtering and pagination; absent or foreign
  resource is generic404. The core list is already selected-domain scoped.
- GET /api/reservation-notices/{notice_id}: Viewer, canonical scoped notice detail.
- POST /api/reservations/evaluate: Operator; body accepts only optional matching
  actor_id, otherwise an empty object. Reject caller time/config/saved finding IDs.
  Resolve the current designated static pool and selected scope inside audited_write,
  then call lifecycle.evaluate_reservation_notices(connection). Server UTC only.
- POST /api/reservations/{reservation_id}/notice: Operator; body carries notice_id,
  expected_notification_version, reason and optional matching actor_id. Inside the
  write transaction authorize the canonical reservation, authorize the notice and
  require its reservation_id to match before invoking acknowledge_reservation_notice.
  Remove only the routing notice_id from the strict forwarded leaf body; never
  discard other unknown fields. Current pool policy and notice version are rechecked.
- GET /api/current-static-occupancy: Viewer, selected-domain designated pool only;
  call workflow.current_static_occupancy(connection). Preserve exact component units,
  UTC as_of, domain/scope/pool, current-ledger provenance. Do not infer external evidence completeness.

Define explicit nested response DTOs matching actual T016 fields; validate
JSONResponse bodies as well as ordinary reads. Mutation responses use200 and
X-Request-Replay from the leaf. Authorization/scoping precedes payload semantics;
audit_scope_id may be set only from an authorized canonical resource. Failed audit
persistence retains the existing visible error convention. No fabricated receipt
action or idempotency-key field: evaluate is repeat-safe by episode identity and
ack uses exact notification version plus same-principal/reason replay.

## Meaning and recovery

A notice is a local reservation lifecycle record, not a saved-run finding or proof
of owner delivery. Responses explicitly label operator_acknowledgement and
owner_signoff=false. Ack never clears the condition. Alarm escalation opens a new
notification version; an old ack cannot acknowledge it. Resolved episodes retain
history while acknowledgement_current is false. FR006 owner/recipient mapping
remains an explicit open acceptance disposition, not an implicitly met criterion.

After an ambiguous acknowledgement, authorized GET notice can confirm only the
original notification version, trusted own acknowledged_by and acknowledged state;
missing/changed/foreign acknowledgement is not proof of the original result. Retain
unknown in the UI instead of automatic replacement. Evaluation readback is the
canonical notice list; no promised operator recipient delivery or background run.

Current occupancy counts active allocations plus state=reserved holds, including
expired holds, over current assignable ranges minus exclusions. Converted/released
holds are excluded. Saved DHCP metrics/runs/p95/forecast remain independent.
T018 will show the identities and units separately; no new IPv6/delegation metric.
