# FR006 configured recipient amendment

The user explicitly selected one reviewed Operator recipient per domain/scope,
an immutable binding per notice notification version, and that recipient's explicit
in-app acknowledgement as receipt. Astra and independent Sol challenged the concrete
config/history/API design. This amendment does not infer external delivery or owner
identity from descriptive owner_reference. T025 evidence remains pending.

## Ownership and order

T016A: Muse1.3 high owns the complete reviewed configuration and schema7 notification
history foundation: access.py, store.py, new schema_v7.sql. T016B: retained Luna
T016 author owns lifecycle.py/workflow.py recipient binding, evaluation and receipt
transitions. T017A: retained Opus5.5 high T017 author owns app.py/models.py wire and
strict projection. Each uses a separate codex branch/worktree and reviewed exact
prerequisite; Sol reviews before source integration. Active T015/T017 are not
interrupted or reassigned. T018 and T023 wait for integrated T017A. These amendments
are part of FR006 Tier A; Tier B remains locked.

## Reviewed configuration

Optional root notice_recipients is a list of exact {domain,scope_id,principal_id}
objects, unique by (domain,scope_id), using existing canonical nonempty text rules.
Absent list means no routes; unknown extra fields/malformed/duplicate entries fail
configuration parsing. No fallback to creator, owner_reference, first Operator or
request payload. Existing reviewed configuration replacement authority remains the
only assignment mechanism; no browser configuration editor or caller route override.

ReviewedConfiguration adds notice_recipients keyed by (domain,scope_id). Append a
safe default so existing internal constructors remain source compatible. Export
resolve_notice_recipient(configuration, domain, scope_id, *, now=None), using aware
server UTC by default, returning {recipient_id, routing_status, routing_reason,
configuration_revision, configuration_digest}. Revision is an integer. Status is
assigned, unassigned or unroutable. Missing map: null recipient, unassigned,
reason missing_mapping. A configured unknown/disabled/expired/non-Operator/wrong-domain
principal remains internally identified but unroutable with an allowlisted reason
unknown_principal/disabled/expired/not_operator/wrong_domain. Eligible recipient:
assigned, reason null. Current eligibility is checked at evaluate and ack; invalid
recipient mapping must not hide unrelated domain data by invalidating all configuration.
This helper returns internal identity; public projections redact other principals.

## Recognized schema7 and history

Do not rewrite frozen schema_v6.sql or reinterpret a schema6 database as7. Add
schema_v7.sql; store recognizes7 as current and1..6 as explicitly migratable. Fresh
initialization appends7 after6; require_schema validates required table/columns and
recognized state operations retain their shared version policy. Migration remains
explicit, stopped, atomic and non-destructive. No tests or DB execution before T025.
Future Tier B T030/T035 must select the actual next version (at least8), not overwrite7.

New reservation_notice_notifications table has composite primary key
(notice_id,notification_version), notice FK, positive version, recipient_id nullable,
configuration_revision positive integer/configuration_digest paired, routing_status
assigned/unassigned/unroutable/legacy_unbound, routing_reason, issued_at, and nullable
acknowledged_by/acknowledged_at/acknowledgement_reason. New bindings always record
configuration and server UTC. Binding columns are immutable in leaf behavior; an
acknowledgement is one atomic immutable receipt, all three acknowledgement fields
present together. Only assigned current recipient can acquire a new receipt.

Legacy preservation is explicit in migration: copy only the known current version
and any distinct known older acknowledgement_version as legacy_unbound rows, with
actual retained acknowledgement fields. No recipient, configuration, issued time or
receipt is invented. Legacy routing_reason is legacy_unbound. Only a complete actual older acknowledgement
tuple creates a second legacy row; acknowledgement version beyond the current
notification version or partial tuples are inconsistent. Legacy rows permit null
provenance/time and classify old ack
as legacy_operator, never recipient_in_app. Do not reconstruct unknown historical
notification versions. Malformed legacy records must fail visibly/roll back rather
than silently discard or guess acknowledgement data.

## Lifecycle and projections

Keep protected context and current designated pool/scope policy. Notice reads,
evaluate and acknowledge receive reviewed configuration explicitly as a keyword;
all HTTP call sites pass request.state.access_configuration under existing current
request/transaction guards. Preserve caller-owned atomic transactions, no connection,
commit, server, scheduler or external delivery service in the leaf.

Create a child binding on first due episode, alert-to-alarm escalation, or explicit
manual evaluate when recipient identity/eligibility changed or the legacy binding
needs renewal. One evaluate transition increments notification_version once even if
both alarm and routing change together. Unchanged condition and routing dedup, and
unrelated configuration changes with the same eligible principal do not renew.
GET never reroutes. Audit old/new version, route status and configuration provenance.
Old receipt history remains immutable even after new notification or resolution.

Ack requires current mapped principal equal to bound recipient, currently enabled,
unexpired, selected-domain Operator, exact notice/version and eligible notice state.
Different current route refuses with409 until explicit evaluate creates a new version;
a different authenticated principal cannot acknowledge for the recipient. Current
identity checks precede replay. Same version/actor/reason replay returns the original
receipt without a new write. Any changed reason or existing other receipt conflicts.
Ack records the child receipt, parent summary and audit together. Resolution never
means delivery or acknowledgement and never erases retained receipt history.

Public notice includes current_notification with strict fields matching the child
record plus derived delivery_status: awaiting_receipt, unassigned, recipient_unavailable,
legacy_unbound or acknowledged. Show recipient_id and acknowledged_by/reason only to
that authenticated principal; others receive null. Include is_current_recipient
from current eligibility and mapping, not a client-side owner inference. Explicit acknowledgement_kind is
recipient_in_app, legacy_operator or null as appropriate. Do not call a configured
recipient a proven business owner: owner_signoff remains false; in_app_receipt is
true only for the explicitly acknowledged recipient-bound version. Current binding
may now be unavailable; historical receipt stays historical, separate from current
ack eligibility. Allowlisted routing reasons must not disclose another principal's
identity or credential detail.

Expose scoped GET /api/reservation-notices/{id}/notifications/{version} for immutable
prior-version recovery, with current authorization and own receipt redaction. The
parent GET and version GET never create records or claim a missing record proves
absence of an in-flight write. T018 persists only original principal/domain/config,
notice ID and notification version for ambiguous ack; authorized exact version read
can confirm the original own receipt after later renewal. No silent replacement.
