# Feature Specification: Post-meeting IPAM / Pool Watch bridge

> Current authority, 2026-09-22: the user transferred oversight to Main Lead 4.0 and
> authorized bounded Tier A implementation. The original header/input and assumption
> below record the specification phase; they do not retain Main Lead 3.0 authority.
> Source adoption started at `6b66f943b7c7783285bfd1f70859ede42380bf60`, with the
> subsequent lead-adjudicated FABLE-DESIGN amendments in contracts/data-model and
> [T001](delivery/authorization-and-ownership.md). The dispatch manifest pins each
> worker's exact adopted base. Runtime acceptance remains pending.

**Feature Branch**: `codex/postmeeting-specification`

**Created**: 2026-09-22

**Status**: Revision 1.1 — AGENT-LOCKED CANDIDATE, Q100 reconfirmed after independent source-review amendments. Main Lead 3.0 adoption pending. No implementation authorized.

**Input**: Produce an evidence-grounded specification for a three-day bridge, resolved through exactly 100 agent-to-agent architecture decisions, then a locked plan/task graph for Main Lead 3.0.

## Resolved delivery boundary (normative)

This section and the actual answer/challenge/resolution entries in [questions.csv](questions.csv)
define the selected outcomes. The 22 cards below classify the entire questionnaire; their
future acceptance criteria do not turn deferred capabilities into three-day promises.
All behavior below is specified, not newly implemented or observed.

| Tier | Deliverable and finish line | Explicit limit |
|---|---|---|
| A — minimum bridge | Server-trusted principals, default-deny domain access across every API/detail/raw/export path | Internal domains, no independent customer tenancy or enterprise identity provider |
| A | Versioned JSON staging, complete dispositions, immutable candidate/active comparison and independent assessment sign-off | 10 MiB/10,000 records; fixed reviewed mapping; no cutover, CSV adapter or automatic promotion |
| A | Exact local static IPv4 reservation, independent allocation/conversion and unused-reservation release; aging and owner notices | Existing locally authoritative pool only; no network reclaim or subscriber IP move |
| A | One durable internal-ticket-simulator/v1 handoff, route/attempt/readback/unknown/retry history | Simulated ticketing; provisioning unsupported/not requested; no inbound external approval |
| A | Preserve existing scoped evidence/capacity workflows; same-candidate offline API, recovery and evidence package | Current static holds shown separately from saved evidence; runtime and human acceptance need later observations |
| B — stretch only after A | History-preserving allocated release/reassignment; one synthetic DHCP create-reservation; extra missing-child-prefix proposal UI | Separate gates/branches, reserve protected, none required to call Tier A complete |
| C — documented/deferred | Live vendors, DNS writes, enterprise auth, customer tenancy, HA/scale/encryption qualification, licensing enforcement, configurable workflows, IaC | No implementation or row promotion in this bridge |

### Access and authority — Q009–Q020
One server-trusted principal is derived from an individually issued opaque bearer token,
stored as a digest in reviewed operator configuration. Tokens stay in browser memory,
never URLs/localStorage/logs. Re-check active configuration revision, principal status,
expiry and selected-domain membership on every operation. Viewer reads/exports; requester
proposes (pending-request cancellation deferred); operator imports/validates/reserves/handles permitted
exceptions and attempts; approver independently decides; platform admin manages the
reviewed configuration procedure, without implicit data rights or approval bypass.
Roles may combine but one principal cannot approve its own request. One active domain per
ordinary user request; multi-domain membership is explicit. Fixed global evidence jobs use
a separate coordinator credential explicitly authorized for every configured synthetic
scope/source, with no wildcard or local change/approval/ticket-delivery rights. Region is only a filter. Mixed raw envelopes
are denied unless wholly in the selected domain; authorized derived projections are separate.
Apply policy to lists/counts/search, raw imports, saved runs/findings, audit, presets, exports,
schedule and API docs. Foreign direct IDs use non-disclosing 404 after authentication.
Only empty UI shell and minimal liveness are anonymous; authenticated readiness retains
details. Loopback-only HTTP is the deployment limit; non-loopback exposure needs separately
authorized TLS. Existing body actor fields must match derived identity or fail, never fallback.
Credential/membership/source/route configuration changes use a controlled stopped/reload
procedure with revision/digest and independent human/role review, not a new admin engine.

### Migration assessment — Q021–Q032
Reuse existing JSON parser and immutable staged source records. Counts are two layers:
`input = accepted + rejected + duplicate`;
`accepted = added + changed + unchanged + conflicting` with conflict precedence.
Active-only objects are a separate comparison set, never implicit deletion. Candidate
identity includes source run/hash, fixed approved mapping revision, authority/policy revision
and active baseline revision. Same source/run identity with changed canonical normalized JSON content conflicts; whitespace/key-order equivalents replay. Raw-byte hashes are provenance only. Validation
requires zero rejected rows, explained duplicates, approved source/domain mapping, no
unresolved conflicts, reconciled counts, acknowledged active-only objects and current
revisions. Intended-inventory staging is all-or-nothing: malformed/invalid/duplicate intended rows reject
the whole envelope; successful staged receipts have accepted=input and rejected=duplicate=0.
Partial row receipts belong only to coordinator observation imports, not migration assessment. A distinct
qualified approver signs the exact assessment; any governing revision change invalidates
its current status while retaining history. Actual recipient sign-off remains a human gate.
No candidate is promoted to active inventory and no restore is described as candidate undo.
Abandoning assessment review changes no persisted state; candidates/receipts/history remain.

### Local lifecycle — Q033–Q046
Pending allocation requests remain non-reserving. Add a narrow reservation record; do not
introduce a generic holds framework. Every reservation/allocation writer checks both tables
and eligible DHCP claims inside the existing immediate transaction. Default duration is
24 hours, maximum 168 hours from creation/extension; audited extensions retain total age.
Allocation converts the hold atomically with reservation→allocation lineage; there is no
availability gap or double count. Hold changes increment pool/baseline versions; evidence
imports do not. Expiry retains capacity, raises alert at expiry and alarm 24 hours later
using server UTC independent of evidence demo time. Scheduler stays default off. A distinct
approver may cancel/release an unused demonstrably local-only reservation after verifying
no allocation or unresolved external effect; network silence is irrelevant to that local-only
case. Allocated-address reclaim requires applicable evidence/authority and stays Tier B.
Tier B must preserve allocation IDs referenced by requests and migrate unconditional address
uniqueness to active-only uniqueness with every reader updated before reuse is executable.
No deletion of referenced allocation rows. Service reassignment changes only an opaque
synthetic service reference on the same assignment; IP moves and real provisioning deferred.
Fixed versioned states/policy, no workflow editor. Retain lineage through handoff and review
retention 30 days later; no automatic deletion or invented customer retention policy.

### Handoff and event authority — Q047–Q070
Persist local request and ticket intent atomically; attempt simulation independently.
Unique domain/request/action correlation and canonical payload hash prevent duplicate
logical tickets. Reviewed exact domain/action route revision is retained; missing/ambiguous
route blocks delivery, not an otherwise authorized local allocation. Three total manual
attempts per handoff, five-second observation budget, no queue service or auto-retries.
Unknown delivery requires correlation lookup; only definitive absence permits another
attempt. The simulator retains both effect-committed/response-lost and no-effect cases.
Disable blocks new attempts, retains history and requires reconciliation before resuming.
Local state, simulated delivery, simulated recipient receipt and evidence resolution stay
separate; external approval never grants IPAM authority. Allowlisted sanitized payloads
exclude raw/private evidence and secrets. Global acquisition/run generation/reconciliation/exception sync require the fixed internal
evidence coordinator credential, explicitly authorized for every configured source/scope.
Domain operators may import only wholly selected-domain intended candidates with reconciliation
disabled; mixed content, observation imports and requested callbacks fail before persistence.
No ordinary request delegates to the coordinator. Ordinary refresh reads saved projections;
global schedule/run controls are unavailable. Existing coordinator callbacks preserve source-run
identity/ingestion ordering and global clock/cursor; no per-domain feed rewrite is claimed.
Tier B DHCP uses a separate synthetic provider fixture; pending readback is not success,
with owner attention after five minutes. DNS has no live query/parser/write in Tier A.

### Evidence, reporting and operational qualification — Q071–Q099
Reuse exception semantics: acknowledgement does not clear evidence; only comparable healthy
evidence supports resolution followed by owner closure. Reservation notices use their own
lifecycle identity, never fabricated saved-run findings. Confirmed assignment conflicts can
be critical immediately; incomplete evidence remains unknown. Existing pressure policy is
p95 ≥80% OR eligible forecast <60 days; oversized is complete 30-day p95 <50% (720 samples).
DHCP lease occupancy and current static allocated-plus-reserved occupancy are different
metrics; show denominator, scope, source, time and completeness. Do not rewrite immutable
saved runs with present holds or invent IPv6 delegation utilization.
HA, encryption and carrier-scale work are future qualification protocols only. Q081–Q088
record explicit assumed cohorts/thresholds; original RFP clauses control eventual credit.
Recovery requires all readiness booleans plus business-state validation; a stopped backup
contains state, not code/UI/config/credentials. Existing 4.427-second prepared-host evidence
is historical and excludes provisioning, transfer and business validation.
Spencer has three bounded daily operator outputs, planned 2 hours/day plus at most 2 hours
contingency. One existing Linux amd64 target; human rehearsal/acknowledgement cannot be
replaced by agent review. Commercial owners remain unassigned roles until actually named.
License expiry is documentary future continuity policy, with no feature in Tier A.
Drop extra prefix UI, DHCP simulation, then allocated release/reassignment if needed; do not
drop access, history, explicit failures, independent evidence or recovery. If any Tier A
finish line fails, report partial/bridge incomplete. Sol replaces a blocked leaf after
45 minutes without a defensible path, immediately for authority/schema ownership risks.
Fable advisory remains a later explicit gate, not an invocation or acceptance claim.

## User Scenarios & Testing *(mandatory)*

“Testing” below defines future acceptance, not checks executed by this task. Priorities follow the resolved Tier A boundary below; broader capability cards do not override it.

### User Story 1 - Validate a migration candidate (Priority: P1)
A migration operator imports a supported inventory, compares it with active state and reviews rejected/conflicting rows without silently changing assignments.
**Why this priority**: Creates a usable source-to-review path and resolves the meeting's explicit migration-page need.
**Independent Test**: With a sanitized candidate, inspect receipts/comparison and prove preview/abandoned review leaves active state unchanged.
**Acceptance Scenarios**:
1. **Given** a valid scoped candidate, **When** previewed, **Then** every row has a disposition and each change has an active/candidate comparison.
2. **Given** conflicting ownership or stale review, **When** assessment sign-off is attempted, **Then** it is blocked visibly and active assignments remain intact. Candidate promotion is unavailable.

### User Story 2 - Route and review a scoped IP change (Priority: P1)
A domain owner follows a subscriber/address proposal through independent approval, responsible-team routing and separate local/external results.
**Why this priority**: Connects lifecycle, domain permission and the proposed ticketing flow.
**Independent Test**: Run the chosen action in its explicitly selected integration mode and inspect correlation, refusal and retry outcomes.
**Acceptance Scenarios**:
1. **Given** an authorized request, **When** independently approved, **Then** the exact reviewed local change is auditable and external outcome is separately labeled.
2. **Given** wrong-domain permission or an ambiguous ticket timeout, **When** retried, **Then** no unauthorized mutation or duplicate logical action occurs.

### User Story 3 - Explain capacity and operational conditions (Priority: P2)
A planner drills into scoped IPv4/IPv6 evidence; an operator distinguishes a warning, persistent alarm, unknown observation and resolved condition.
**Why this priority**: Makes review decisions explainable and prevents unsafe reclaim conclusions.
**Independent Test**: Compare saved results to independent calculations and exercise agreed alert/clear rules under healthy and incomplete evidence.
**Acceptance Scenarios**:
1. **Given** eligible observations, **When** viewing a block, **Then** numerator, denominator, units, window and source match detail/export.
2. **Given** stale source data, **When** refreshing, **Then** unknown does not appear as free space or clear an alarm.

### User Story 4 - Hand over truthful capability and operating evidence (Priority: P1)
A reviewer/recipient follows the package, interface matrix and row ledger without confusing promises with results.
**Why this priority**: All implementation paths need a credible finish line.
**Independent Test**: Trace each selected requirement to its exact evidence and have the nominated recipient perform the agreed handoff when execution is authorized.
**Acceptance Scenarios**:
1. **Given** a mock integration, **When** shown or exported, **Then** the result remains labeled simulated.
2. **Given** an unavailable business/reference artifact, **When** reporting readiness, **Then** its row stays missing/insufficient and names the owner of the gap.

### Edge Cases
- Duplicate/replayed input versus same identity with changed content.
- Partial import versus committed receipt followed by failed reconciliation.
- Missing source authority, time coverage, domain membership or subscriber mapping.
- Cross-scope private-address reuse versus concurrent same-scope conflict.
- Approval after revocation, changed candidate, stale inventory or intervening external use.
- Successful local change followed by failed/unknown external provisioning.
- Reservation aging versus DHCP occupancy; disabled/expired record is not free by itself.
- Out-of-order event, duplicate ticket, acknowledgement without evidence resolution.
- IPv6 cardinalities beyond ordinary numeric precision and invalid utilization denominator.
- Recovery prerequisites excluded from measured time; retained artifact tied to an older revision.
- Ambiguous handwriting and unknown vendor interfaces cannot become invented requirements.

## Requirements *(mandatory)*

### Functional Requirements
All FR cards below are **proposed outcomes**, not claims of new implementation. RFP coverage
lists related rows; a card does not automatically satisfy every clause in those rows.
Each card is complete only when its decision dependencies and actual evidence gates are met.
Source IDs resolve in source-reconciliation.md; all 111 rows resolve in coverage.csv.
Permissions described for future behavior do not grant this task permission to execute it.

#### FR-001 — Evidence and accounting

**Delivery disposition:** A: evidence ledger and claim boundaries; lead adjudication only.

**Questionnaire IDs**: RFP-005, RFP-078, RFP-083, RFP-086.

- **User outcome:** Lead/reviewer can distinguish current evidence from intended capability without losing either ledger.
- **Actor:** Evidence reviewer; persistent lead is adjudicator.
- **Preconditions:** An identified requirement, clause, source revision and evidence scope exist.
- **Normal flow:** Inspect baseline and proposed result → follow evidence → record bounded assessment → lead adjudicates; review/feedback records retain owner and follow-through.
- **Failure behavior:** Absent artifacts, incompatible metrics or unresolved gaps leave the claim pending/partial; never promote on a label change.
- **Permissions:** Workers propose evidence; independent reviewer assesses; lead alone changes canonical row class.
- **Data/source:** S1–S6; immutable run/audit records and approved documentary sources.
- **Acceptance criteria:** For each of 111 rows show one accepted class, separate meeting target, material gap and evidence pointer; all promoted labels remain unaccepted without proof. Review outcomes have owner, decision and follow-up status.
- **Evidence required:** Independent clause-to-artifact comparison at exact candidate; retained denial/unknown cases and review history.
- **Dependencies:** All capability gates feed this ledger; Q001 and evidence decisions.
- **Explicit non-claims:** No 92-completed claim, aggregate satisfaction percentage, compliance certification or adopted operating process inferred from documents.

#### FR-002 — Migration import, compare and validate

**Delivery disposition:** A: immutable JSON assessment only; no cutover.

**Questionnaire IDs**: RFP-033, RFP-034, RFP-036, RFP-037, RFP-087, RFP-088, RFP-089.

- **User outcome:** Operator assesses a candidate inventory before it can affect active assignments.
- **Actor:** Migration operator and independent domain approver.
- **Preconditions:** Declared source, schema/mapping, domain/scope, candidate identity and current ledger revision.
- **Normal flow:** Select versioned JSON → apply reviewed fixed mapping → show all-accepted staged receipts or whole-envelope refusal → compare candidate and active inventory → review conflicts and validation report; promotion/cutover is excluded from this bridge (Q022).
- **Failure behavior:** Malformed envelope stops processing; invalid intended records reject the whole envelope with a visible reason; unmapped scope/ambiguous authority blocks validated assessment. A stale review requires fresh comparison. Abandoning review preserves all active state and retained assessment history.
- **Permissions:** Read/compare within one authorized domain; operator imports, different domain approver signs assessment; no activation permission or endpoint exists.
- **Data/source:** S1 rows 033/036/087–089; S8 migration-page narrative; existing immutable receipts and ledger.
- **Acceptance criteria:** Every input has one disposition; comparisons identify additions/changes/conflicts and source IDs. Active ledger unchanged after preview/abandoned review/failure. A wave signs off assessment only after Q028 reconciliation gates; abandoned/invalidated assessment has no active-state rollback because it never writes active state.
- **Evidence required:** Sanitized before/after inventories, receipt counts, mapping version, stale-review refusal, reconciliation report and independent sign-off. Customer migration requires actual authorized customer evidence.
- **Dependencies:** FR-005 permissions, FR-014 authority and FR-021 recovery; Q021–Q032 fixed JSON, single-domain assessment and sign-off contract.
- **Explicit non-claims:** No arbitrary format support, auto-discovery, active baseline promotion, customer cutover or migration validation claim from schema migration alone.

#### FR-003 — Fixed lifecycle, reservation, reclaim and retention

**Delivery disposition:** A: reservation, allocation/conversion and unused reservation release. B: allocated reclaim/reuse.

**Questionnaire IDs**: RFP-001, RFP-053, RFP-057, RFP-059, RFP-065, RFP-075, RFP-080.

- **User outcome:** Owner follows an address from reviewed request through assignment, reservation aging and controlled release without losing history.
- **Actor:** Requester, independent approver and domain operator.
- **Preconditions:** Authoritative scoped inventory, supported service type, reviewed candidate/version and approved lifecycle policy.
- **Normal flow:** Tier A: explicit local reservation → independently approved allocation/conversion, or independently approved cancellation of an unused local-only reservation; expiry retains the hold. Tier B: allocated reclaim/reuse after history-safe schema/readers and full authority/evidence gates. Record local and simulated ticket outcomes separately.
- **Failure behavior:** Contradictory eligible observation, stale version or missing authority blocks allocation/reclaim. Unused reservation cancellation proves no allocation or unresolved external effect without requiring irrelevant network-silence/readback evidence. Expiry raises review, not reuse; failed/unknown outcomes remain visible.
- **Permissions:** Independent approval for assignment/reclaim; domain-scoped transitions; retention/purge policy restricted to an authorized administrator.
- **Data/source:** S1 lifecycle/reservation/reclaim notes; S5 transaction, scope/time and pending-request contracts.
- **Acceptance criteria:** Pending requests continue not to reserve implicitly. Reserved capacity and age are visible separately from DHCP. Reclaim never follows silence alone. Release count increases only after the chosen release gate; retention preserves required lineage.
- **Evidence required:** Transition table, success/refusal/retry traces, exact candidate identities, reservation-aging record, before/after audit, no-partial-write evidence and retention policy review.
- **Dependencies:** FR-005 and exact current local state for Tier A. FR-013 applicable evidence and external authority/readback only for Tier B allocated reclaim; Q033–Q046.
- **Explicit non-claims:** No safe-to-reclaim claim from 30-day silence, traffic inactivity, automatic DNS change or configurable workflow framework.

#### FR-004 — Subscriber reassignment and ServiceNow routing

**Delivery disposition:** A: durable simulated ticket. B: local service-reference reassignment; real subscriber provisioning deferred.

**Questionnaire IDs**: RFP-009, RFP-042, RFP-047, RFP-060, RFP-070, RFP-081, RFP-082, RFP-098.

- **User outcome:** Operator routes a scoped subscriber/address issue to the correct owner and follows a reassignment through review and outcome.
- **Actor:** Requester, domain owner, independent approver and ticket recipient.
- **Preconditions:** Chosen opaque subscriber/service identifier, source authority, team routing map, supported action and integration mode.
- **Normal flow:** Atomically persist request plus ticket intent, then follow two independent branches: local independent review/commit, and manual simulated ticket delivery/readback. Failed routing does not prevent an otherwise eligible local approval. Tier A provisioning is unsupported/not requested; recipient acknowledgement is explicitly simulated.
- **Failure behavior:** Unknown subscriber, missing route/team, duplicate request, permission refusal or timeout stays visible. Ambiguous ticket delivery requires lookup by correlation before retry. Ticket closure alone cannot resolve network evidence.
- **Permissions:** Domain-bound request/read/update; independent approver; ticket credentials have only chosen operations; no trust in a caller-supplied role.
- **Data/source:** S1 042/047/098 and cross-team comments; S8 reassignment narrative; existing request/exception records.
- **Acceptance criteria:** One request produces at most one logical simulated ticket despite retry. Wrong-domain action is refused. UI shows local state, simulated ticket delivery/receipt and evidence resolution separately; provisioning is unsupported/not requested. Only executed Tier B reassignment requires service-reference before/after history.
- **Evidence required:** Contract examples, simulated mode, duplicate/timeout/denial observations, ticket correlation and independent reviewer evidence; before/after service ownership only for an executed Tier B reassignment.
- **Dependencies:** FR-003 lifecycle, FR-005 access, FR-009 interfaces, FR-011 delivery; product and ServiceNow contract decisions.
- **Explicit non-claims:** No subscriber provisioning, live ServiceNow, tenant isolation or organizational adoption inferred from a local case or mock ticket.

#### FR-005 — Domain, region and role permissions

**Delivery disposition:** A: server-enforced internal domain permissions.

**Questionnaire IDs**: RFP-004, RFP-008, RFP-026, RFP-079.

- **User outcome:** Users see and act on only the inventory and workflows their domain responsibilities permit.
- **Actor:** Viewer, requester, domain operator, approver and platform administrator (fixed permission bundles).
- **Preconditions:** Server-authenticated principal, assigned domain memberships and scope mapping.
- **Normal flow:** Choose permitted domain/region → read inventory/evidence → perform permitted action → record actor and scope; administrator manages ownership within agreed authority.
- **Failure behavior:** Missing identity/membership or forbidden domain is denied before data disclosure/mutation. Filters do not grant access. Revoked membership cannot continue a privileged action.
- **Permissions:** Separate view/request/change/approve/admin rights; explicit multi-domain memberships with one selected domain per operation; no independent customer tenancy or admin bypass.
- **Data/source:** S1 004/008/026/079, S8 domain narrative; current scope metadata and fixed actor definitions.
- **Acceptance criteria:** Permitted role can complete its selected flow; same request/list/detail/export in another domain is denied or excluded consistently. Region grouping never changes network-scope identity.
- **Evidence required:** Role/action/domain matrix; direct-interface and UI evidence for allowed/denied access, cross-domain list/export and stale membership.
- **Dependencies:** FR-015 identity; Q009–Q020 fixed access matrix and trusted token identity.
- **Explicit non-claims:** Current domain dropdowns are not security. No enterprise RBAC, SSO or independent customer isolation claim until enforced and observed.

#### FR-006 — Alerts, alarms and owner escalation

**Delivery disposition:** A: reservation notices and existing exception semantics; no external paging/licensing feature.

**Questionnaire IDs**: RFP-022, RFP-072.

- **User outcome:** Owner sees an actionable warning and a distinct persistent condition requiring escalation.
- **Actor:** Domain operator, alarm recipient and platform operator.
- **Preconditions:** Agreed alert/alarm definitions, severity, ownership, timing and evidence freshness.
- **Normal flow:** Detect condition → create deduplicated alert → route to owner → escalate under chosen rule → acknowledge → clear only under agreed evidence/operational rules. Track platform health separately.
- **Failure behavior:** Missing recipient or delivery failure is visible with escalation ownership. Stale evidence cannot clear an alarm. Acknowledgement does not change anomaly truth.
- **Permissions:** Only permitted owner/recipient acknowledges or changes disposition; evidence clearance follows computation and policy.
- **Data/source:** S1 022/072 and reservation/escalation notes; S8 alert/alarm narrative; S5 exception semantics.
- **Acceptance criteria:** Same unchanged condition does not create duplicate alerts; new episode/material change creates a distinct notification. Clear, acknowledged, escalated, delivery failed and evidence unknown remain distinguishable.
- **Evidence required:** State/transition matrix; controlled repeat, escalation, missing owner, failed delivery and healthy-versus-unknown clearance records.
- **Dependencies:** FR-005 ownership, FR-011 delivery, FR-013 evidence; definitions and timer decisions.
- **Explicit non-claims:** No external paging or health-monitoring service inferred from in-app notices or /healthz. License expiry is a documentary future policy only; no implementation or commercial enforcement in Tier A.

#### FR-007 — DHCP updates and bounded orchestration

**Delivery disposition:** A: existing DHCP evidence view. B: one isolated synthetic reservation operation.

**Questionnaire IDs**: RFP-011, RFP-056, RFP-091, RFP-096.

- **User outcome:** Operator reviews a DHCP change, understands its effect and sees whether the external system actually accepted it.
- **Actor:** Domain approver and DHCP operator.
- **Preconditions:** Chosen DHCP system/operation contract, authoritative block identity, permission, integration mode and current observed state.
- **Normal flow:** Show block/lease context → propose exact change → validate/review → approve → submit or simulate explicitly → record response → read back/reconcile.
- **Failure behavior:** Timeout is unknown outcome; rejection preserves prior authoritative state. Partial external completion is exposed and requires reconciliation/compensation; local approval never stands in for external success.
- **Permissions:** Approved service operation plus independent domain approval; read-only credentials cannot trigger writes.
- **Data/source:** S1 011/056/091/096 and DHCP tab note; existing lease observations.
- **Acceptance criteria:** Supported update has before/after, approver, correlation and observed result. Unsupported action is refused. Mock/live status is visible for every result.
- **Evidence required:** Chosen vendor contract, invalid/rejected/timeout/replay examples and authoritative readback for live claims.
- **Dependencies:** FR-003/005/009/011; provider-service boundary and operation choice.
- **Explicit non-claims:** No operating provider DNS/DHCP servers, general orchestration platform, DNS writes or live DHCP result from simulation.

#### FR-008 — IPv4/IPv6 utilization and prefix proposals

**Delivery disposition:** A: preserve correct current reporting. B: additional missing-child-prefix proposal UI; capacity expansion deferred.

**Questionnaire IDs**: RFP-002, RFP-035, RFP-073, RFP-074, RFP-076, RFP-095.

- **User outcome:** Planner explains block utilization and proposes an appropriate scoped prefix without hiding missing evidence.
- **Actor:** Capacity planner and authorized inventory approver.
- **Preconditions:** Declared family, scope/region parent, assignable ranges, exclusions, sampling window and completeness.
- **Normal flow:** Drill domain → region → block → supported saved DHCP/prefix measures and separately labeled current static holds. Retain existing permitted child edits. Additional missing-child-prefix proposal UI is Tier B; no new approval engine or delegated utilization without source evidence.
- **Failure behavior:** Invalid denominator, missing history or changed capacity yields unavailable, not zero. Overlap/out-of-region/out-of-domain candidate fails. Large IPv6 quantities retain exactness.
- **Permissions:** Planner can preview; permitted actor changes intended inventory through existing reviewed rules.
- **Data/source:** S1 035/073/074/095, S8 utilization/prefix narrative; S5 calculation and correction contracts.
- **Acceptance criteria:** Displayed numerator/denominator/window match saved detail and export. IPv6 uses only supported inventory/prefix-capacity units without host enumeration; no delegated utilization without delegation evidence. Proposals identify which intent—missing registration or capacity expansion—they address.
- **Evidence required:** Independent arithmetic, insufficient-data controls, exact prefix overlap/containment decisions and same-run UI/export comparison.
- **Dependencies:** FR-005/013/014; prefix meaning and threshold decisions.
- **Explicit non-claims:** No traffic or cell-radio utilization inference, IPv6 host density, forecast accuracy guarantee or subscriber allocator.

#### FR-009 — API documentation and integration inventory

**Delivery disposition:** A: local API/offline pack and selected simulated contract. Other integration entries documentary.

**Questionnaire IDs**: RFP-010, RFP-012, RFP-013, RFP-039, RFP-041, RFP-046.

- **User outcome:** Integrator can identify supported operations, authorization, failure semantics and which external systems are actually connected.
- **Actor:** Integrator, operator and reviewer.
- **Preconditions:** Pinned application revision and chosen external operation contracts.
- **Normal flow:** Inspect existing API description → document examples/errors/retries/auth → record integration matrix with owner, data direction, source authority, mode and evidence → identify unavailable operations explicitly.
- **Failure behavior:** Stale documentation, absent endpoint or incompatible schema is flagged; do not manufacture a working path or describe a mock as connected.
- **Permissions:** Documentation may use sanitized examples; endpoints retain enforced permissions; credential material never appears in examples.
- **Data/source:** S1 API notes; S10 existing API docs; S5 contracts.
- **Acceptance criteria:** Every documented operation is labeled existing, proposed or unavailable with revision and mode. Selected integrations include authentication, payload, timeout, retry, rate limit and outcome proof requirements.
- **Evidence required:** Source-to-document trace, sanitized request/response/error examples and separately retained runtime proof when authorized.
- **Dependencies:** Selected ServiceNow, DHCP, EMS, CMDB and OSS/BSS boundaries.
- **Explicit non-claims:** No API-documentation-equals-integration claim, generic adapter platform or customer schema disclosure.

#### FR-010 — CMTS/vCMTS and element-system boundaries

**Delivery disposition:** C: future read-only access-network/EMS contracts; no vendor adapter.

**Questionnaire IDs**: RFP-044, RFP-045, RFP-067.

- **User outcome:** Analyst can compare supported access-network evidence with scoped inventory and identify unsupported vendor assumptions.
- **Actor:** Network analyst and integration owner.
- **Preconditions:** Named product/version, operation, authoritative identifiers and legally available contract/sample.
- **Normal flow:** Inventory candidate targets → choose one bounded read path → map source identifiers/scope/time → validate observations → compare with intended state.
- **Failure behavior:** Unknown vendor/product/schema or ambiguous join blocks correlation; conflicts remain separate records. No guessed endpoint or vendor interchangeability.
- **Permissions:** Read-only by default; any write needs a separate specified and authorized operation.
- **Data/source:** S1 044/045/067; S8 notes name Cisco, Harmonic and Comcast as possible targets, not verified interfaces.
- **Acceptance criteria:** Each target has explicit role, product/version, data ownership and status; matching evidence names join keys and coverage. Unsupported targets are not counted integrated.
- **Evidence required:** Official documentation for chosen interface, sanitized mapping and positive/negative/ambiguous matching evidence.
- **Dependencies:** FR-009/013/014 and RFP-044 choice; vendor facts researched after target selection.
- **Explicit non-claims:** No live CMTS connection, operator/vendor equivalence or complete DNS/DHCP/CMTS validation from one sample.

#### FR-011 — Event-driven changes and delivery semantics

**Delivery disposition:** A: closed local event set and durable ticket outcomes; no event bus.

**Questionnaire IDs**: RFP-043, RFP-068.

- **User outcome:** Operator can trace a supported event to one intended action and distinguish retry from duplicate execution.
- **Actor:** Integration operator and reviewer.
- **Preconditions:** Chosen event types, producer identity, ordering/version policy and destination contract.
- **Normal flow:** Receive/record eligible event → validate identity/version → perform bounded action → retain correlation and result → expose retry or manual reconciliation.
- **Failure behavior:** Duplicates reuse the result; changed payload under the same identity conflicts. Late/out-of-order events follow agreed policy. Failed delivery or busy processing remains visible.
- **Permissions:** Producer is authenticated/authorized for chosen scope and operation; arbitrary event payloads cannot bypass approval.
- **Data/source:** Existing opt-in import callback and scheduler; S1 event intent; S8 event-driven narrative.
- **Acceptance criteria:** Each supported event has durable identity, observable state and retained cause/result. Repeated event does not duplicate assignment/ticket; approval-dependent changes still await approval.
- **Evidence required:** Duplicate, out-of-order, restart/unknown-result and failed-delivery records tied to candidate and integration mode.
- **Dependencies:** FR-003/004/007/009; delivery/ordering decisions.
- **Explicit non-claims:** No event bus, arbitrary trigger engine, exactly-once external guarantee or continuous live discovery inferred from a timer.

#### FR-012 — DNS validation and export boundary

**Delivery disposition:** A: existing IPAM context export. C: DNS parser/live validation/write.

**Questionnaire IDs**: RFP-055.

- **User outcome:** Operator obtains validated DNS-relevant information for a separate controlled change process.
- **Actor:** Domain analyst and external DNS owner.
- **Preconditions:** Explicit source authority, scoped identity, selected records and desired export contract.
- **Normal flow:** Read supplied DNS evidence if available → catalog provenance → explain supported context → export validated IPAM context for separate approval. No new DNS parser or machine-validation claim.
- **Failure behavior:** Missing/stale DNS yields unknown. Ambiguous name/address ownership is flagged. No failure path attempts automatic repair.
- **Permissions:** Authorized read/export only; no DNS write capability in this bridge.
- **Data/source:** S1 explicit DNS-risk boundary; S8 narrative.
- **Acceptance criteria:** No bridge action performs a DNS mutation. Output shows source, time, limitations and recipient responsibility; no DNS data remains visibly unavailable.
- **Evidence required:** Document/interface inspection and later authorized negative evidence that write paths are absent; export comparison with source.
- **Dependencies:** FR-005/009/013; DNS read/export decision.
- **Explicit non-claims:** No automatic DNS update or DNS-service operation; RFP-055 remains a gap under this boundary.

#### FR-013 — Network evidence, discovery and unauthorized-use review

**Delivery disposition:** A: preserve existing evidence and unknown semantics; live collectors and attribution deferred.

**Questionnaire IDs**: RFP-061, RFP-062, RFP-063, RFP-064, RFP-066.

- **User outcome:** Analyst distinguishes an observed discrepancy from a proven unauthorized assignment and knows when evidence is insufficient.
- **Actor:** Network analyst and domain owner.
- **Preconditions:** Declared source coverage/time, scope/family, intended authority and any principal/service authorization source.
- **Normal flow:** Import or acquire supported observations → assess freshness/completeness → reconcile → inspect evidence → route suspicious use to authorized review.
- **Failure behavior:** Missing or stale source yields unknown. Same address in independent scopes is legitimate. An unexplained route/lease does not establish hijack or safe reclaim.
- **Permissions:** Authorized scoped viewing; reviewers cannot rewrite source evidence to clear a finding.
- **Data/source:** S1 061/063/066 including unauthorized-use intent; S5 rules and evidence contracts.
- **Acceptance criteria:** Each conclusion traces to eligible observations and explicit policy. Concurrent conflict differs from sequential reuse. No probe collection or continuous discovery claim without actual collector evidence.
- **Evidence required:** Healthy/anomaly/unknown controls, scope/time joins, source references and independent rule assessment.
- **Dependencies:** FR-005/009/010/014; detection authority and source choices.
- **Explicit non-claims:** No traffic inference, definitive hijack attribution, live discovery or mitigation from synthetic discrepancies.

#### FR-014 — Metadata, policy and maturity assessment

**Delivery disposition:** A: fixed registry/policy dictionary and documentary gap assessment; no customer maturity claim.

**Questionnaire IDs**: RFP-027, RFP-028, RFP-029, RFP-030, RFP-031, RFP-032, RFP-038, RFP-040, RFP-054, RFP-084, RFP-085.

- **User outcome:** Owner understands required metadata, assignment rules, data responsibility and assessed process gaps.
- **Actor:** Data steward, domain owner, approver and assessment reviewer.
- **Preconditions:** Declared metadata vocabulary, scope hierarchy, assignment rules and evidence-backed assessment method.
- **Normal flow:** Map ownership and terms → validate required fields/policies → document current process versus proposed process → record gaps and accountable next steps.
- **Failure behavior:** Unknown owner, incompatible classification or invalid policy blocks affected mutation; assessment marks not assessed rather than inventing a maturity score.
- **Permissions:** Stewards propose mappings/policies; authorized owner approves changes; reserved identity/version fields cannot be overwritten.
- **Data/source:** S1 metadata/governance/maturity and assignment notes; existing schema, custom metadata and hierarchy.
- **Acceptance criteria:** Each chosen field/rule has meaning, owner and failure behavior. Overlapping private space remains scoped. Assessment links each finding to supplied evidence and explicitly separates current from proposed workflow.
- **Evidence required:** Dictionary, policy examples including denied assignments, ownership matrix and reviewer-reviewed assessment with evidence gaps.
- **Dependencies:** FR-003/005/008/013; RFP-040 method and vocabulary decisions.
- **Explicit non-claims:** No adopted customer governance, real current-state assessment, generic policy language or invented benchmark.

#### FR-015 — Identity and service credentials

**Delivery disposition:** A: local token-backed principal; enterprise providers and vault deferred.

**Questionnaire IDs**: RFP-048, RFP-049, RFP-050, RFP-051, RFP-052.

- **User outcome:** Operator knows who performed an action and which service credentials may access which operations.
- **Actor:** Identity administrator, service owner and audit reviewer.
- **Preconditions:** Selected identity method/provider and explicit trust boundary; separately authorized access for any connection.
- **Normal flow:** Document selected login/service-auth flow → map verified identity to domain permissions → restrict credentials → record safe actor references.
- **Failure behavior:** Untrusted, expired, revoked or unmapped identity is refused; credential retrieval/rotation failure is visible without secret disclosure.
- **Permissions:** Least privilege per domain/operation; credential access separated from ordinary operator access.
- **Data/source:** S1 identity/API notes; S10 fixed demo actor boundary.
- **Acceptance criteria:** Selected authentication proves claimed actor origin and permission enforcement; unselected SAML/OAuth/LDAP/certificate methods remain unsupported, not implied by API availability.
- **Evidence required:** Versioned local token/principal contract; later authorized valid/invalid/expired/revoked observations; sanitized identity-to-role mapping and rotation procedure.
- **Dependencies:** FR-005 product security boundary and FR-009 interfaces.
- **Explicit non-claims:** No enterprise authentication claim from actor selection; no secret manager, credential storage or provider login invented.

#### FR-016 — Resilience, recovery and encryption boundaries

**Delivery disposition:** A: preserve bounded stopped recovery. C: HA, encryption, full outage/SLA qualification.

**Questionnaire IDs**: RFP-014, RFP-015, RFP-016, RFP-017, RFP-018, RFP-019, RFP-020, RFP-021, RFP-023.

- **User outcome:** Operator can state recoverability and security limits accurately and follow a bounded recovery procedure.
- **Actor:** Platform operator and independent reviewer.
- **Preconditions:** Pinned package/state format, declared target, recovery protocol, backup identity and chosen qualification scope.
- **Normal flow:** Record current topology → identify recovery prerequisites → preserve backup → follow stopped restore process → validate state → separately document future HA/security design.
- **Failure behavior:** Unavailable snapshot/key/dependency blocks recovery visibly; failed restore preserves prior state. No old result is relabeled as new recovery evidence.
- **Permissions:** Explicit state-operation authority; backup access restricted; infrastructure and deployment remain outside this task.
- **Data/source:** S1 resilience labels; S5 state contracts; S6 bounded Linux observation.
- **Acceptance criteria:** Recovery report names start/end boundary, excluded preparation, observed loss and logical-state checks. Encryption at rest and in transit each have distinct controls/evidence. HA/failover remain unproved until their actual failure scenario is observed.
- **Evidence required:** Retained backup/restore/refusal evidence; declared failure model; independent target observation if later authorized.
- **Dependencies:** FR-021 handoff; architecture and qualification decisions.
- **Explicit non-claims:** No active-active, geo-DR, RPO/RTO SLA, sustained hybrid operation or encryption-at-rest claim from packaging/TLS.

#### FR-017 — Scale and concurrency qualification

**Delivery disposition:** C: future scale protocol, no measurements or implementation in this window.

**Questionnaire IDs**: RFP-025, RFP-093, RFP-094, RFP-097.

- **User outcome:** Reviewer knows exactly what workload has been measured and which scale claims remain future work.
- **Actor:** Product owner, performance engineer and independent verifier.
- **Preconditions:** Chosen address/record populations, history, operation mix, concurrency, duration, latency/error targets and authorized environment.
- **Normal flow:** Define workload/measurement protocol → identify architecture gaps → schedule separately authorized measurements → compare results with declared criteria.
- **Failure behavior:** Reduced sample, interrupted run or exhausted resource produces a bounded/incomplete result, never extrapolated success.
- **Permissions:** Read-only planning now; measurement owner cannot approve its own claims; resource provisioning needs separate authority.
- **Data/source:** S1 scale clauses and comments; current scale gaps in S3/S5.
- **Acceptance criteria:** Each scale claim specifies stored active objects versus address-space size, query/mutation mix, p95/p99 or chosen response measure, error ceiling and observation duration. Proposed qualification thresholds are recorded in Q081–Q088; source requirement thresholds remain controlling for row credit.
- **Evidence required:** Protocol, actual dataset counts, resource limits, raw measurements and independent interpretation tied to revision.
- **Dependencies:** RFP-025/093/094 and concurrency decisions; FR-005/015 real multi-user boundary.
- **Explicit non-claims:** No carrier scale, millions of records, large-team concurrency or large-reference equivalence from arithmetic or tiny benchmarks.

#### FR-018 — Virtual/container network management boundary

**Delivery disposition:** C: managed-network inventory contract; no controller integration or new parser.

**Questionnaire IDs**: RFP-024.

- **User outcome:** Reviewer can tell application packaging from management of virtual-network address space.
- **Actor:** Network administrator and product owner.
- **Preconditions:** Decision on whether managed network inventory is required and a named inventory source.
- **Normal flow:** Document scoped virtual-network inventory fields and required source/controller mapping; preserve current supported imports without claiming a new parser or controller adapter.
- **Failure behavior:** Unknown tenant/network identity blocks joins; deployment labels alone do not populate managed inventory.
- **Permissions:** Read-only scoped management by default; mutations require an explicitly chosen controller operation.
- **Data/source:** S1 024, S3 packaging-versus-network distinction.
- **Acceptance criteria:** Selected outcome names managed objects and source/controller; one synthetic mapping is labeled as such. Deployment evidence remains solely under its own row.
- **Evidence required:** Sanitized object mapping and authorized observation from chosen source, with ambiguous identity refusal.
- **Dependencies:** FR-005/009/014; RFP-024 interpretation decision.
- **Explicit non-claims:** No Kubernetes/VM network-management integration inferred from a Docker image.

#### FR-019 — Inventory and reporting continuity

**Delivery disposition:** A: existing inventory/reporting compatibility under new access controls.

**Questionnaire IDs**: RFP-003, RFP-006, RFP-007, RFP-069, RFP-071, RFP-077.

- **User outcome:** Existing users keep usable inventory, saved-run comparisons and exports while new workflows are added.
- **Actor:** Viewer, planner and permitted inventory editor.
- **Preconditions:** Existing saved run, filter semantics, inventory revision and actor rights.
- **Normal flow:** Search/filter → inspect detail → compare eligible saved runs → export same selection; make supported inventory edits through existing validation/audit.
- **Failure behavior:** Failed refresh preserves visibly dated previous result; missing evidence stays unknown; unsafe prefix resize is refused.
- **Permissions:** Reads/exports respect new domain policy; edits preserve existing actor/revision constraints.
- **Data/source:** S3/S5/S6 and existing UI source.
- **Acceptance criteria:** Full-run totals differ clearly from filtered counts; detail/export share the selected run and definitions. Existing allocations, runs/audits and supported editing survive any future migration.
- **Evidence required:** Before/after selected-path evidence, exact candidate, export comparison and state preservation; reuse prior evidence only when unaffected.
- **Dependencies:** FR-005 access changes, FR-008 calculations; no new UI framework.
- **Explicit non-claims:** No newly demonstrated questionnaire credit for cosmetic changes or unobserved regression-free behavior.

#### FR-020 — Corporate, delivery and commercial evidence

**Delivery disposition:** C/documentary: business evidence register and future expiry continuity policy; no commercial claims.

**Questionnaire IDs**: RFP-099, RFP-100, RFP-101, RFP-102, RFP-103, RFP-105, RFP-107, RFP-108, RFP-109, RFP-110.

- **User outcome:** Lead can present substantiated delivery facts and clearly identify business evidence still owed by its owner.
- **Actor:** Authorized business owner, delivery owner and reviewer.
- **Preconditions:** Authentic source documents and permission to use sanitized conclusions.
- **Normal flow:** List required reference/staffing/support/licensing/compliance artifacts → assign human owner → assess exact claim/metric/applicability → record accepted, insufficient or missing; propose roadmap separately. Document future expiry alarm while preserving service/data; implementation and commercial restrictions require separate authorized business terms.
- **Failure behavior:** Unsupported reference, mismatched unit/population, missing approval or expired evidence stays insufficient/missing.
- **Permissions:** Only authorized owners make commercial commitments; agents prepare templates and traceability.
- **Data/source:** S1 business rows; S3 provider-evidence gaps; S7a license-expiry proposal; public delivery documents.
- **Acceptance criteria:** Every external claim has actual approved support for its exact scope; methodology and proposed roadmap are labeled documentary. Future expiry handling must preserve service and data; this bridge has no licensing implementation or invented commercial restrictions. No customer detail enters repository.
- **Evidence required:** Private evidence pointers under authorized custody, sanitized review conclusion and approval identity; actual recipient/adoption evidence where required.
- **Dependencies:** Business-owner inputs; FR-001 evidence; roadmap priority decisions.
- **Explicit non-claims:** No fabricated references, promised staffing, signed SLA, compliance certification or authorized license offer.

#### FR-021 — Portability, operator and recipient handoff

**Delivery disposition:** A: bounded operator pack and later independent qualification; human handoff separately gated.

**Questionnaire IDs**: RFP-090, RFP-092, RFP-104, RFP-106.

- **User outcome:** Recipient can understand startup, state preservation, recovery and limits from one bounded package.
- **Actor:** Spencer as delivery owner; recipient/presenter and independent verifier.
- **Preconditions:** Lead-selected candidate, documented dependencies, sanitized configuration and later execution permission.
- **Normal flow:** Day 1 endpoint/integration matrix and mock/live boundaries; Day 2 migration/recipient validation pack with reconciliation/rollback/sign-off; Day 3 fresh-start/rehearsal, recovery, notices, evidence and handoff.
- **Failure behavior:** Missing entrypoint, unsupported platform, failed state validation or absent acknowledgement remains an explicit gate; no silent ephemeral storage or claimed training.
- **Permissions:** Spencer owns operator artifacts only; core fixes application/schema; independent recipient/verifier observes; lead accepts.
- **Data/source:** S6 current portability limits; S1 training/KT/dependencies; explicit task's three-day lane.
- **Acceptance criteria:** One bounded finish line per day. Handoff records exact source/package, target, state IDs, commands, actual outcomes and remaining gaps; human training/acknowledgement are distinct from agent reproduction.
- **Evidence required:** Documentation matrix, signed validation checklist, actual rehearsal/recovery records when authorized, dependency/license inventory and recipient acknowledgement.
- **Dependencies:** Stable core candidate, FR-002/009/016; available hours and evidence schedule decisions.
- **Explicit non-claims:** No new infrastructure, universal portability, completed human training or complete license review from manifests alone.

#### FR-022 — Configurable lifecycle and infrastructure-as-code boundary

**Delivery disposition:** C: fixed transitions documented; workflow designer and IaC integrations deferred.

**Questionnaire IDs**: RFP-058, RFP-111.

- **User outcome:** Owner sees which automation/configuration needs are achievable now and which require a separately designed capability.
- **Actor:** Product owner, lifecycle administrator and integrator.
- **Preconditions:** Decision whether fixed states suffice and which external infrastructure tool/operation is actually needed.
- **Normal flow:** Document supported fixed transitions and deployment configuration; if extensibility is essential, specify validation, compatibility, audit and migration before assigning implementation.
- **Failure behavior:** Unknown transition/configuration is refused; invalid edits never reinterpret historical decisions or execute arbitrary commands.
- **Permissions:** Restricted configuration administrator; independent approval and evidence rules cannot be disabled by configuration.
- **Data/source:** S1 058/111; S5 fixed-state/no-workflow-designer boundary.
- **Acceptance criteria:** Fixed workflow is labeled fixed. A configurable claim needs an actual admin-defined transition and enforced allowed/refused behavior with versioned history; IaC claim needs an actual chosen tool contract and observed operation.
- **Evidence required:** Versioned transition/configuration examples and later authorized enforcement observations; separate integration proof.
- **Dependencies:** FR-003/005/009; scope decision and lead contract amendment.
- **Explicit non-claims:** No workflow designer or IaC integration from a label, Compose file or generic API.

### Key Entities
- **Scoped inventory subject**: scope, family, address/prefix, domain/region context, intended owner and revision.
- **Source observation**: immutable source/batch/record identity, scope, interval, authority, freshness and completeness.
- **Migration candidate**: mapping version, input identity, row dispositions, comparison and assessment/sign-off status distinct from active inventory.
- **Lifecycle decision**: reviewed exact subject, requester/approver, version, reason, transition and local outcome.
- **Reservation**: explicit held subject, purpose/owner, expiry/review policy; distinct from pending request and DHCP lease.
- **Subscriber/service reference**: opaque business identifier with declared source authority; no private profile required by default.
- **External action/ticket**: correlation, selected integration mode, requested operation, delivery/execution/readback outcomes.
- **Alert/alarm**: condition/evidence, severity, owner, episode, acknowledgement, escalation and delivery state.
- **Evidence claim**: row/clause, revision, context, observation, artifact, reviewer and limitations.
- **Decision record**: Q ID, prerequisite, recommendation, real answer, rationale, affected requirements and status.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: All 111 questionnaire IDs appear once in coverage.csv, with separate accepted baseline and meeting answer; no unlabeled promotion.
- **SC-002**: All 22 capability cards contain outcome, actor, preconditions, flow, failure, permission, source, acceptance, evidence, dependencies and non-claims.
- **SC-003**: Exactly Q001–Q100 have actual agent answers and adversarial resolutions before lock; no user answers are invented and recommendations alone do not count.
- **SC-004**: Every selected migration input is accounted for exactly once; unapproved/failed candidate work leaves active state unchanged.
- **SC-005**: Every chosen mutating path has allowed, unauthorized, stale/replay and failure outcomes specified; no successful claim without its corresponding evidence.
- **SC-006**: All selected integrations expose mode and separate local decision, delivery, external execution and observed resolution.
- **SC-007**: Every selected capability has one owner, prerequisites, completion gate, evidence, escalation and handoff in the post-lock task graph.
- **SC-008**: Spencer has one bounded daily deliverable; the post-lock schedule preserves a declared risk reserve and explicit drop order.
- **SC-009**: Every artifact claims only its measured/observed scope; absent live/customer/production evidence stays absent.
- **SC-010**: Source gaps and material conflicts are resolved or explicitly excluded by decision before lead review of a locked package.

## Assumptions and authority
- Three relative days begin only after implementation and validation authorization, staffed planning slots and contract adoption. This specification grants none of those permissions.
- Spencer is planned for 2 hours/day (6 hours), with at most 2 additional contingency hours if available; availability is not confirmed. Reserve 20% of core delivery time for integration/review.
- Architecture agents make routine design decisions. External credentials, real human acknowledgement, commercial commitments and model availability remain explicit external gates.
- Current source architecture and evidence semantics are preserved unless a named task and lead-approved contract amendment says otherwise.
- Retained original image representations were inspected; byte identity with deleted temporary files is unverified. Ambiguous handwriting was resolved as architecture scope, not asserted as an exact transcript.
- Existing evidence remains tied to its original candidate and context. This task has performed no application execution, tests, smokes, builds or runtime qualification.
- Agent agreement locks a review candidate. Main Lead 3.0 alone coordinates canonical acceptance; Fable remains advisory.
