# Proposed Tier A data model

Design only. Reuse SQLite conventions and the one-owner schema migration; no SQL or runtime
change is made here. Existing IDs, foreign keys, source records and saved JSON stay intact.

## Identity and reviewed configuration (operator artifact, not new admin tables)
Principal: stable nonempty ID, token digest, enabled flag, UTC expiry, fixed roles, explicit
domain memberships, configuration revision. Token is at least 256 bits of cryptographically
random opaque material, provisioned offline; plaintext is not retained in repo/database/logs.
No shared browser identity or token picker. One entered token lives only in browser memory.
Fixed evidence coordinator has explicit grants for all configured synthetic feed scopes/sources
and global evidence read/acquire/run/reconcile only, no local mutation/approval/ticket rights.
Ordinary domain callers cannot trigger or delegate global jobs; timer stays default off.
Configuration: positive revision, digest, reviewer references, effective time, source→domain/
scope mappings, domain/action→team route, connector mode, fixed policy version. Single
selected domain per request. Unmapped scopes/ambiguous routes are blocked.
Source-qualified opaque service IDs are sensitive; synthetic registry only for this bridge.

## Migration assessment (new narrow persisted record)
ID; source batch ID/canonical normalized JSON hash; selected domain; mapping/authority/policy revisions; active baseline
version; derived row results; receipt counts; active-only list; creator; created UTC; state;
signer/signature time; supersedes ID/reason where corrected. States: assessed, validated,
signed, stale. Assessment is retained even when not validated; status is not import status.
`input = accepted + rejected + duplicate` and
`accepted = added + changed + unchanged + conflicting`.
All counts are nonnegative integers, conflict precedence is deterministic. Intended staging
accepts the entire valid envelope or rejects it; successful receipt rejected=duplicate=0.
Whole-batch normalized replay returns the original receipt, not duplicate rows. Every accepted
record has exactly one comparison class; partial/rejected/duplicate observation rows retain their original receipt reasons only in the
coordinator import path; they are not migration assessment candidates. Active-only records are outside the input-count equation.
Signature requires creator != signer, permitted approver, zero rejected/unresolved conflicts,
documented duplicates, approved mapping, active-only acknowledgement and current revisions.
Any governing revision change makes current sign-off stale, never rewrites old assessment.
Keep derived results separate from immutable raw source. No activation flag/endpoint. Abandoning review changes no persisted state; no cancelled state.
Pending allocation-request cancellation is deferred; unused reservation release stays explicit.

## Reservation and local release decision (new narrow tables)
Reservation: ID, scope/pool/family/address, opaque owner/service reference, created_by, reason,
created UTC, expires UTC, positive version, policy revision, state, converted allocation ID,
released UTC, lineage/action references. Family must be IPv4 and pool the designated locally
authoritative static pool. States: reserved, converted, released; overdue is derived from
UTC >= expiry while reserved. Converted requires linked allocation; released retains history.
A unique active reservation exists per scope/family/address. Cross-table eligibility with
allocations and eligible external claims is checked within BEGIN IMMEDIATE on every writer.
Duration: positive, default 24 hours, at most 168 hours from operation; extension retains
before/after expiry, total age and history. Changed expiry is a new audited version.
Release decision: ID, reservation ID/version, requester, reason, expected pool/baseline version,
idempotency key/digest, state pending/approved/rejected, approver/reason/time. A different
permitted approver rechecks no allocation or unresolved external effect. Successful decision
and release/audit commit together. No network evidence is required for this local-only case.
Pending decisions never remove holds. Rejection retains hold and nonempty reason.
Existing allocation_requests gain optional reservation_id; conversion matches exact
scope/pool/address and owner/service reference. Another request cannot substitute its chosen
address or consume another service's hold; eligibility rechecked under the same transaction.
Pool/baseline versions increment on hold-changing commits. Do not change
capacity_history_version merely because occupancy changes; it describes denominator history.
Atomic conversion links reservation to the existing new allocation ID; no allocation deletion.
The pool authority is the existing workflow.STATIC_POOL_ID and _pool policy check
(see C-L), not a new configurable pool set. baseline_version is the existing global
app_meta singleton, so a hold change can stale an assessment in another domain without
disclosing that domain's data. Do not introduce per-domain clocks or version counters.

## Reservation notice (narrow lifecycle identity, no fake findings)
Reservation ID + episode number + policy revision; first due time; alert/alarm level;
owner; acknowledgement and notification versions; resolved time/reason. Condition derives
from current reservation/expiry. One notice per due episode; new overdue episode after an
extension creates new lineage. Alarm threshold expiry+24 hours. Acknowledgement is not
clearance. Extension or approved cancellation resolves; conversion ends reservation aging
and retains the closed episode with conversion reason. Existing finding-backed exceptions
keep their own saved-run evidence IDs and clearance rules.

## Ticket intent, attempt and simulator effect (new narrow tables)
Intent: ID, domain, source request ID, action type, stable correlation, payload JSON/digest,
positive intent version, current route-assignment version, contract version,
immutable mode=simulated, state, created UTC. Route assignments retain version,
configuration/route revision, nullable team while blocked, assigning principal, reason
and UTC as append-only lineage. These logical records need only the narrow existing
SQLite/JSON representation; no generic routing framework.
Unique domain+request+action and unique correlation. Persist with the request transaction.
States: pending, routing_blocked, delivered, failed, unknown; recipient receipt is separate.
Attempt: ID, intent ID, ordinal in 1..3, pinned route-assignment version, chosen synthetic
scenario, request digest, start/end UTC, result, reason,
observed simulator ticket ID if any. Unknown requires readback before another attempt.
Mode cannot be changed retrospectively. Changed digest with same logical key conflicts.
Business payload digest excludes route/team and assignment metadata. Reassignment only
from pending/routing_blocked with zero attempts preserves intent/correlation, records
lineage and returns to pending after a unique reviewed route is selected. Every attempted
route is thereafter frozen in Tier A; owner resolution cannot reset the three-attempt budget.
Simulator effect: unique correlation, exact intent digest, synthetic ticket ID, committed UTC,
simulated recipient state. Persist effect separately from delivery-observation update to
demonstrate effect committed/response lost and subsequent correlation recovery.
Definitive-not-found is an explicit successful lookup outcome, not any error/empty response.
Provisioning is unsupported/not requested. No independent provisioning state machine in Tier A.
Disable prevents new attempts; historical committed effects survive restart and readback.
Five-second observation budget; three total manual attempts, no auto-drain or reset-by-new-ID.

## Existing entities and compatibility
Allocation rows/IDs and unconditional allocation uniqueness stay unchanged in Tier A.
All inventory, scopes, imports, records, runs, findings, corrections and audit reads use a
trusted access context. Raw mixed-domain envelopes denied; projections never replace raw.
Existing report presets need domain ownership in schema 6; legacy singleton preset is
quarantined until classified, not exposed globally.
Existing audit evidence with provable scope can be scoped; unclassifiable legacy records
remain restricted to explicit platform audit custody, never implicitly granted to admins.
A platform admin without data entitlement cannot inspect arbitrary domain payload.
All database changes are explicit migration and reflected in fresh initialization/store checks.
Backups/restores support recognized schema versions, never implicitly migrate.

## Deferred Tier B model contract
Allocated release/reuse needs allocation active status, release history and active-only
unique index while preserving IDs/foreign keys and updating every reader/calculation/export.
Reassignment keeps IP/pool/scope/domain, versions opaque service reference and preserves
before/after lineage. One schema owner must design the migration against the integrated
Tier A revision before it is executable. Separate synthetic DHCP fixture/provider reservation
must never share local-static authority. No Tier B tables are provisioned speculatively.

Optional DHCP persistence has its own core-owned T035 gate after T034, independent of allocated release. Core reserves the actual next schema and updates recognized migration/fresh initialization/stopped recovery before the leaf. No optional tables are created in Tier A.
