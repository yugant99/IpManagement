# T020 — Integration/status matrix (complete, source-only)

Task: **T020**. Author: Muse 1.3 high (OpenCode), accountable to Astra / Main Lead 5.0
(`01a0ccc7-6219-73c1-bd3b-1521bb71a837`). Independent reviewer: GPT-6 Sol high.
Leased path: this file only. No other edits.
Ownership basis: user clarified Spencer had never been assigned this prepared task and
directed agents to do it; see `delivery/operator-preparation-ownership.md`.
Supersedes the former Spencer T020 dependency; the prepared Spencer worktree
(`ab005d8b…`) remains untouched, no acknowledgement inferred.

**Inspected source candidate:** `b8f294fc19b635dcf3c784125fd804d8a1a2616b`
(branch `codex/bridge-t020-agent-matrix`).
**Application assembly under review:** `a2b567b670129671f85498729753c4d577d4768e`
(T018 notice/occupancy UI + T023 stopped recovery, both Sol source-closed).
All application code through T018/T023 is independently source-reviewed; **no runtime
has run since T011**. T002 (`delivery/source-authority.md`) classification remains
**documentary**. All request/response examples in §4 are **illustrative, not observed**.

**Mode vocabulary:** `source-implemented` = present in inspected source and
source-reviewed, runtime unobserved (T025 pending) · `simulated` = runs inside
`internal-ticket-simulator/v1` only · `proposed` = frozen contract, not yet
implemented · `missing`/`unverified` = no adapter/contract/product fact in source.
No mode is runtime acceptance; T025/T026/T028 gates stay separate.

**Global non-claims:** owner_reference is descriptive, never a business-owner
identity; synthetic ingestion is never live vendor acquisition; no external
delivery, provisioning, or vendor SLA is claimed; no vendor endpoint/version/auth
is guessed; no live customer facts, new infrastructure, or broad vendor research.

## 1. Selection rule and completeness (for Sol, against all 111 public rows)

- **Included (§3, 48 rows):** the union of (a) every row whose primary category is
  Integration (19 rows: 011, 036, 041, 042, 044, 045, 046, 047, 048, 049, 050,
  051, 052, 055, 056, 058, 061, 067, 098) and (b) every row whose coverage.csv
  task gate lists T020 (28 rows: 009, 010, 011, 012, 013, 039, 041, 042, 043,
  044, 045, 046, 047, 055, 056, 060, 067, 068, 070, 081, 082, 090, 091, 092, 096,
  098, 104, 106 — union of (a)+(b) is 36 rows) **plus** 12 justified
  cross-category rows bearing an API/event/orchestration/delivery/readback
  integration clause (001, 022, 033, 034, 037, 053, 059, 063, 069, 072, 087,
  089). RFP-090/092/104/106 are included per their explicit T020 gate with
  honest preparation/unknown dispositions; retained evidence classes are
  preserved, not promoted.
- **Omitted (§5, 63 rows):** rows with no integration clause and no T020 gate
  (pure local application logic, deployment topology, scale measurement, or
  business/provider evidence). Each omitted ID has a one-line disposition in
  §5; 48 + 63 = 111, no invented rows, no denominator or evidence promotion.
- Retained evidence classes below are copied from `docs/QUESTIONNAIRE_ROW_MAP.md`;
  only the Lead may change them.

## 2. Cross-cutting integration rules (apply to all §3 rows)

- **Coordinator vs domain credentials (C-A):** global run/acquire/
  observation-callback mutations and their receipts are coordinator-only under an
  explicitly granted fixed synthetic-feed scope; ordinary domain sessions get saved-
  result refresh only. The acquire wrapper uses the separately provisioned
  coordinator credential, never a browser operator token; no token in args/logs/URLs.
  Coordinator has no allocation/correction/reservation/approval/ticket-delivery rights.
- **Raw vs scoped projections / legacy quarantine (C-A):** collections filter
  before count/pagination/export; saved mixed runs return a recomputed
  selected-domain projection that never replaces the immutable global result. Raw
  mixed-domain envelopes are denied unless every scope is selected and permitted.
  Unknown legacy ownership is quarantined, never default-domain assigned.
- **Normalized assessment rules (C-M):** canonical-JSON replay identity,
  all-or-nothing intended staging, input = accepted+rejected+duplicate,
  accepted = added+changed+unchanged+conflicting, active-only separation, governed
  snapshot, independent sign-off, staleness retention, no promotion/cutover.
- **Reservation / local-decision independence (C-L/C-T):** local approval commits
  despite routing/delivery failure; ticket approval never authorizes IPAM mutation;
  provisioning is unsupported/not requested.
- **Durable ticket effect / unknown / readback (C-T):** effect commit is durable
  and distinct from response observation. An `unknown` outcome resolves two
  ways: a persisted effect found by exact same correlation + business digest
  resolves it to `delivered` (attempt row updated to delivered with the actual
  synthetic ticket ID); definitive absence is the no-effect / fenced-failure
  path (crashed attempt fenced as failed, or zero-attempt intent closed as
  failed only when its source request is rejected or its linked reservation
  released — an active source keeps pending/routing_blocked). Readback never
  claims success without a found effect. Three total manual attempts; 5 s
  observation budget is a deadline, not a sleep; no auto-retry, queue, or
  budget reset.
- **Recipient ack as in-app receipt (notice-recipient-wire):** one configured
  Operator recipient per (domain, scope_id); immutable binding per notice
  notification version; only that recipient's explicit in-app acknowledgement
  counts as receipt (`acknowledgement_kind=recipient_in_app`); legacy rows are
  `legacy_operator`; `owner_signoff` stays false.

## 3. Row-level inventory

Format per row: requirement · interface/direction · product/contract/version ·
source/change authority · principal/role · payload-error-retry-readback · mode ·
responsible role · evidence pointers · gap · next gate.
Owner-role abbreviations follow T002: Lead, Grok-int (requirements/integration
sublead), Terra (schema/API owner), Muse 1.3 high (T020/T022/T024 operator
preparation; Spencer's former preparation role is historical/superseded per
`delivery/operator-preparation-ownership.md`), Human-int
(unassigned vendor-contract owner), Human-biz (unassigned business owner),
Luna (independent verifier, needs validation authority).

### RFP-001 Lifecycle — Partial (cross-category: reservation/ticket independence)
Requirement: request→approval→allocation lifecycle with visible local vs downstream
state. Interface: local `POST /api/allocation-requests`, `…/decision` (in-app);
ticket branch via C-T handoff (internal). Direction: app-internal. Product/
contract/version: local workflow + `internal-ticket-simulator/v1`, known.
Authority: Lead contracts; change via reviewed config (C-T routes) / schema owner
(C-L). Principal: Requester proposes, Approver decides, Operator attempts ticket.
Payload/error/retry/readback: idempotency-key replay; 409 changed-payload; exact-key
recovery (`GET /api/handoff-operations`, allocation list `idempotency_key` filter);
unknown preserved, no silent replacement. Current bridge source implements
reservation, extension, and independent unused release (conservative refusal only
while a linked intent is pending/routing_blocked/unknown). Mode: source-implemented (T012–T015).
Responsible: Terra (API), original authors retain fixes. Evidence:
`backend/ipam_demo/app.py:698-777` (handoff routes), `:1073-1269` (reservation
routes); `contracts/reservation-ticket-wire.md`, `contracts/ticket-api-wire.md`;
`docs/QUESTIONNAIRE_ROW_MAP.md` RFP-001. Historical old-baseline note, kept
separate: the S5-12 `primary/workflow-recovery-summary.json` observation belongs
to the pre-bridge baseline and is not bridge runtime evidence. Gap: allocated
reclaim/reuse remains Tier B (locked); Tier A provisioning is
unsupported/not_requested (a labeled absence, not a simulation). Next gate: T025 runtime observation; Tier B needs T029 contract.

### RFP-009 Request portal — Demonstrated (cross-category: local request UI/API)
Requirement: requester subnet request flow. Interface: in-app request/approval API
+ UI; no external portal. Product/contract known (local). Authority: Terra/C-A.
Principal: Requester/Approver fixed demo actors. Mode: source-implemented;
bounded local flow only. Responsible: Terra. Evidence: row-map RFP-009; app.py
allocation-request routes; T015 UI. Gap: no enterprise portal/identity/external
provisioning. Next gate: T025; enterprise portal needs Human-int contract (out of Tier A).

### RFP-010 Central service — Demonstrated (cross-category: API host surface)
Requirement: one central API + shared state serving UI. Interface: local HTTP API
(inbound). Product: single-process FastAPI + SQLite, known. Authority: Terra;
topology change needs Lead + T019 HA gate. Principal: all authenticated roles.
Mode: source-implemented (single local service). Responsible: Terra; Muse for
packaging (T024). Evidence: app.py routes; row-map RFP-010; FR-009 spec §347-363.
Gap: single failure point; no HA/distributed claim. Next gate: T025; HA needs
FR-016 protocol + authorized observation (T019 §2).

### RFP-011 DNS/DHCP management — Missing (Integration; FR-007)
Requirement: integrated DNS/DHCP management. Interface: none exists (no adapter).
Product/contract/version: **unknown/unverified** — no vendor selected.
Authority: Human-int (unassigned) selects product/version; Grok-int documents after
official source; Terra implements only after contract freeze. Principal: none
(none exists; future DHCP operator role). Payload/error/retry/readback: none;
future gate requires before/after + approver + correlation + authoritative readback
(FR-007). Mode: missing. Responsible: Human-int; T020 records gap only.
Evidence: `delivery/source-authority.md` §2 (no DNS/DHCP `source_kind` fields);
row-map RFP-011; coverage.csv RFP-011 (B synthetic DHCP; live deferred).
Gap: synthetic DHCP observations are not management; no adapters. Next gate:
official vendor docs + sanitized sample + readback contract after authorized
selection; Tier B T034 synthetic fixture only after T025 + Lead selection.

### RFP-012 API access — Demonstrated (cross-category: local HTTP API detail §4)
Requirement: documented local resource API. Interface: inbound local HTTP
(`GET/POST` resource routes). Product/contract/version: local API at inspected
candidate, known; offline pack planned (T021). Authority: Terra (routes), Grok-int
(T021 pack). Principal: Viewer reads; role-gated mutations (C-A). Payload/error/
retry/readback: AppError shape; 401/403/404/409; X-Request-Replay (201 fresh/200
replay); exact-key operation readback. Mode: source-implemented; versioned offline
pack proposed. Responsible: Terra; Grok-int/Opus for T021. Evidence: app.py;
`docs/STAGE3_API.md`; §4 of this matrix. Gap: no external consumer/production
security claim. Next gate: T021 offline pack; T025 runtime proof.

### RFP-013 API-driven product — Demonstrated (cross-category)
Requirement: UI driven by the same API/backend results. Interface: internal
UI→API (inbound). Product: local UI + API, known. Authority: Terra. Principal:
authenticated context (no actor picker). Mode: source-implemented. Responsible:
Terra + UI owners. Evidence: row-map RFP-013 (S5-04/06/12 agreement). Gap: no
broader integration ecosystem. Next gate: T025 same-candidate UI/API agreement.

### RFP-022 Health and alerts — Partial (cross-category: readiness vs monitoring)
Requirement: platform health/alerting. Interface: `GET /healthz` (minimal
liveness, anonymous) + proposed authenticated `GET /api/readiness` (six booleans);
reservation due/alert/alarm notices are in-app lifecycle records, not platform
alerts. Direction: outbound-to-operator (read). Product: local wrappers known;
alert route/delivery **unverified**. Authority: Terra (endpoint semantics),
Muse (wrappers, T024). Principal: Operator (readiness); coordinator excluded
from domain data. Payload/error/retry/readback: all-six-true else failure status
with allowlisted reasons; no raw startup detail; readiness never proves business
recovery. Mode: source-implemented (liveness + in-app notices); alerting
integration missing. Responsible: Terra/Muse. Evidence:
`contracts/access.md` §§ readiness/operator-boundary; `contracts/state-recovery-wire.md`
§ remaining gates; row-map RFP-022. Gap: no monitoring service, route, or
delivery proof. Next gate: T024 wrapper bound to authenticated readiness; T025.

### RFP-033 Normalization — Partial (cross-category: assessment canonical rules)
Requirement: canonical normalization of inputs. Interface: `POST /api/imports`
(intended staging) + C-M assessment comparison. Product: canonical parser rules,
known. Authority: Terra. Principal: Operator (domain staging); coordinator
(observation imports). Payload/error/retry/readback: canonical-JSON identity;
same identity+hash replays receipt; changed content 409; whole-envelope refusal
leaves no receipt. Mode: source-implemented. Responsible: Terra. Evidence:
`contracts/migration.md` (comparison result); row-map RFP-033. Gap: corrective
cleansing / heterogeneous live-source transformation absent. Next gate: T025
count-equation + conflict/stale/denial cases.

### RFP-034 Duplicate inputs — Demonstrated (cross-category: receipt identity)
Requirement: exact duplicate detection. Interface: import receipts. Product:
`(source_id, source_run_id)` + SHA-256 canonical JSON, known. Authority: Terra.
Principal: Operator/coordinator per path. Payload/error/retry/readback: 9-input
accounting (1 accepted + 7 rejected + 1 duplicate); whole-batch replay returns
original receipt (not per-row duplicates). Mode: source-implemented. Responsible:
Terra. Evidence: row-map RFP-034; `contracts/migration.md`. Gap: acquisition
idempotency is separate evidence, not substituted. Next gate: T025 duplicate
control observation.

### RFP-036 Source discovery — Partial (Integration; FR-002)
Requirement: discovery of existing IPAM systems / complete source inventory.
Interface: `GET /api/source-catalog` (declared receipt projection, inbound read).
Direction: app-internal projection. Product: local catalog, known; customer
sources **unverified**. Authority: Terra (projection); Human-int for real source
authority. Principal: Viewer (selected domain). Payload/error/retry/readback:
`authority_status=declared` only — explicitly not discovery or live uniqueness;
staged rows `not_applicable`. Mode: source-implemented catalog; discovery
missing. Responsible: Terra; Human-int for authority verification. Evidence:
`backend/ipam_demo/source_catalog.py:44-64`; app.py `/api/source-catalog`;
row-map RFP-036. Gap: no verified source authority or customer inventory.
Next gate: authorized source program + declared-authority verification (Human-int).

### RFP-037 Data quality — Demonstrated (cross-category: import accounting)
Requirement: input quality/duplication assessment. Interface: import receipts +
assessment counts. Product: local importer, known. Authority: Terra. Principal:
Operator/coordinator. Payload/error/retry/readback: quality counts, seven
rejection reasons, duplicate count, reduced effective completeness. Mode:
source-implemented (bounded canonical inputs). Responsible: Terra. Evidence:
row-map RFP-037. Gap: customer-estate quality report outstanding (Phase 1).
Next gate: T025; customer assessment is separate Phase 1 work.

### RFP-039 Integration inventory — Documentary (FR-009; this matrix is the artifact)
Requirement: documented system/interface inventory. Interface: documentary matrix
(this file). Product: synthetic sources/dependencies described; organizational
systems **unverified**. Authority: T020 author (Muse) → Lead acceptance → Sol
review. Principal: reviewer/integrator (readers). Payload/error/retry/readback:
n/a (document); per-row mode/owner/evidence/gap recorded. Mode: proposed until
Sol-reviewed/Lead-accepted. Responsible: Muse (T020); Lead accepts. Evidence:
this file; `docs/SYNTHETIC_DATA.md`; `docs/CONTRACTS.md`; T002 register. Gap: no
discovered organizational inventory or validated dependency map. Next gate: Sol
review → Lead acceptance → T021/T022 consume.

### RFP-041 CMDB — Missing (Integration; FR-009)
Requirement: CMDB adapter/connection/outcome. Interface: none. Product/version/
table/API/auth: **unverified, mapping pending**. Authority: Human-int
(unassigned); T020 records gap only. Principal: none. Payload/error/retry/
readback: future gate needs official product/version/interface + sanitized sample
+ positive/negative/ambiguous join. Mode: missing. Responsible: Human-int.
Evidence: source-authority §FR-009 table (RFP-041 row); row-map RFP-041. Gap:
no adapter, table, or join key. Next gate: official instance contract after
selection; never guessed.

### RFP-042 Ticketing — Missing as external; simulated locally (Integration; FR-004, detail §4)
Requirement: external ticket-platform connection. Interface: `internal-ticket-
simulator/v1` (local, explicitly simulated) at `POST /api/handoffs/{id}/attempt|/
readback|/acknowledge|/reassign`, `GET /api/handoffs[/{id}]`. Direction:
app-internal simulation; no outbound vendor call. Product: simulator known;
ServiceNow object/table/API **unverified, mapping pending** (UI labels mapping
pending). Authority: Lead/C-T; route map = reviewed configuration revision;
change = config revision + explicit reassignment. Principal: Operator
(attempt/readback/reassign); Viewer reads; coordinator has no domain rights.
Payload/error/retry/readback: allowlisted business payload (domain/action, opaque
service ref, source request ID, correlation, revisions, reason code); no raw
envelope/token; 3 manual attempts; 5 s budget; `unknown` resolves to `delivered`
only when a persisted effect is found by exact same correlation +
`business_payload_digest` (attempt updated with the actual synthetic ticket ID);
definitive absence is the no-effect/fenced-failure path, never a delivery claim;
exact-key `handoff-operations` recovery; strict readback body field names in
§4.3 (`key`/`digest` aliases rejected); zero-attempt reassignment only;
no route change after attempt. Mode: simulated (local); external missing.
Responsible: Terra/T014 author; original authors retain fixes. Evidence:
`contracts/ticketing.md`; `contracts/ticket-api-wire.md`;
`backend/ipam_demo/ticket_handoff.py:562-885`; `app.py:698-777`. Gap: no live
platform, auth scopes, idempotency/rate contract. Next gate: official
product/version/interface + mapping + auth scopes (Human-int); T025 simulator
behavior.

### RFP-043 Event trigger — Demonstrated (cross-category: closed local events)
Requirement: import-triggered reconciliation. Interface: opt-in ordinary-import
callback invoking existing reconciler (internal); no event bus. Product: local
callback, known. Authority: Terra/C-A (callback disabled default; coordinator-only
observation submission planned). Principal: coordinator (global jobs); ordinary
domain callers cannot advance clock/cursor. Payload/error/retry/readback: busy/
failure shown separately from success; held-lock separation; post-run
rollback/retry; failed attempt-audit. Mode: source-implemented (local
synchronous only). Responsible: Terra. Evidence: row-map RFP-043. Gap: no event
bus, arbitrary triggers, external orchestration. Next gate: T025 busy/failure/
replay cases.

### RFP-044 Element systems — Missing (Integration; FR-010)
Requirement: equipment/element-management adapter. Interface: none. Desired future
read: interface/subnet inventory, status, observation time (documentary only).
Product/version: **unverified** (Cisco/Harmonic/Comcast are named targets, not
interfaces). Authority: Human-int selects; Grok-int documents after official
source; Terra implements only after freeze. Principal: none (future network
analyst). Mode: missing. Responsible: Human-int. Evidence: source-authority
§FR-010; T019 §2 EMS row; row-map RFP-044. Gap: no adapter, interface pack, or
join keys. Next gate: official docs for chosen interface + sanitized mapping
(positive/negative/ambiguous), read-only default.

### RFP-045 Access-network system — Missing (Integration; FR-010)
Requirement: CMTS/vCMTS connection + matching evidence. Interface: none.
Product/version: **unverified**; Cisco docs are first future research priority
(when research is authorized — this task does not research). Authority:
Human-int. Principal: none. Mode: missing. Responsible: Human-int. Evidence:
source-authority §FR-010; spec FR-010 §365-381; row-map RFP-045. Gap: no
connection or matching evidence; config writes excluded. Next gate: named
product + version + legally available contract/sample + stable keys.

### RFP-046 OSS/BSS — Missing (Integration; FR-009)
Requirement: live operational/business-system integration. Interface: none.
Product/version: **unverified**. Authority: Human-int; T020 records gap.
Principal: none. Mode: missing. Responsible: Human-int. Evidence:
source-authority §FR-009 (RFP-046 row); row-map RFP-046. Gap: no adapter.
Next gate: same official-contract gate as RFP-041.

### RFP-047 Provisioning — Missing as external (Integration; FR-004)
Requirement: provisioning-system integration. Interface: none external; the
ticket handoff DTO projection carries constant `provisioning_status=
"not_requested"` (models.py `TicketHandoffSummary:185`, set in
ticket_handoff.py:419) while new allocation requests carry the separate legacy
column `downstream_status="not_requested"` (workflow.py:450,502,507; legacy rows
may carry `simulated_success`/`simulated_failure`) — two distinct fields on two
distinct projections, never interchanged. Product: **no vendor**.
Authority: Lead (Tier A provisioning unsupported/not requested). Principal: n/a.
Payload: local decision vs simulated ticket shown separately; UI states
"provisioning unsupported/not requested". Mode: missing (external); local
allocation source-implemented. Responsible: Terra (labels); Human-int (any
future). Evidence: `contracts/ticketing.md` (independence); row-map RFP-047.
Gap: local allocation ≠ provisioning integration. Next gate: none in Tier A;
future needs full operation contract (out of scope).

### RFP-048/049/050 Enterprise directory / SSO / LDAP — Missing (Integration; FR-005/015)
Requirement: enterprise directory connector / IdP login / LDAP auth. Interface:
none; demo uses bearer-digest principal + fixed bundles (Viewer/Requester/
Operator/Approver/platform-admin), memory-only token, `X-IPAM-Domain` selection.
Direction: inbound auth (local). Product: local token auth known; enterprise
providers **deferred/unverified**. Authority: Terra (C-A); Human-int for any
future provider. Principal: locally authenticated principal (not enterprise
identity). Payload/error/retry/readback: 401 invalid/expired, 403 forbidden,
non-disclosing 404; config-revision pins with 409 stale; no secret in errors.
Mode: source-implemented (local auth); enterprise missing. Responsible: Terra.
Evidence: `contracts/access.md`; row-map RFP-048/049/050; coverage.csv (token
principal; providers deferred). Gap: no connector, configured identities, or
IdP login. Next gate: frozen provider contract + observed login/deny cases
(Human-int + Terra); T025 local-auth cases.

### RFP-051 Certificate API auth — Missing (Integration)
Requirement: client-certificate validation / identity mapping. Interface: none.
Product: **unverified**. Authority: Human-int; Terra integrates only after
freeze. Principal: none. Mode: missing. Responsible: Human-int. Evidence:
row-map RFP-051; T002 missing-fact register. Gap: no validation or mapping.
Next gate: official contract + observed accept/refuse cases.

### RFP-052 Service credentials — Missing (Integration)
Requirement: service credential storage/access/rotation. Interface: none in
scope; token-digest config stays outside repo/snapshots (C-A/C-O boundary).
Product: **no store**. Authority: platform/security owner unassigned; Terra owns
only the exclusion (no secret logging). Principal: n/a. Mode: missing.
Responsible: unassigned owner; T020 records exclusion. Evidence: row-map RFP-052;
`contracts/access.md` (token custody); `contracts/operator.md` (no live tokens
in package/backup). Gap: no storage, access controls, or rotation. Next gate:
named owner + approved custody/rotation procedure.

### RFP-053 Allocation/reservation — Partial (cross-category: C-L detail)
Requirement: approval-created durable local allocation; reservation lifecycle.
Interface: `GET/POST /api/reservations`, `…/extend`, `…/release-requests`,
`…/decision`, allocation `reservation_id` link (inbound local HTTP). Product:
designated local static IPv4 pool `STATIC_POOL_ID`, known. Authority: Terra/C-L;
pool policy fixed (no per-domain list). Principal: Operator (create/extend/
propose), Approver (independent decision; no direct edit grant). Payload/error/
retry/readback: strict positive versions; duration 1–168 h (default 24);
idempotency-key replay; cross-table eligibility in one immediate transaction;
conservative unused-release refusal while linked intent pending/unknown. Current
bridge source implements reservation, extension, and independent unused release
(an unlinked hold releases normally). Mode:
source-implemented (T011/T012). Responsible: Terra; original authors retain
fixes. Evidence: `contracts/lifecycle.md`; `contracts/reservation-ticket-wire.md`
§§T012/conversion-identity; app.py `:1073-1269`. Historical old-baseline note,
kept separate: S5-12 allocation observations belong to the pre-bridge baseline,
not bridge runtime evidence. Gap: reservation lifecycle is Tier A complete but
allocated reclaim/reuse remains Tier B (locked); pending requests do not
reserve; Tier A provisioning is unsupported/not_requested (labeled absence, not
simulated).
Next gate: T025 success/refusal/replay/concurrency; Tier B reclaim locked.

### RFP-055 DNS changes — Missing (Integration; FR-012)
Requirement: real DNS write/outcome. Interface: none; only IPAM-context export
exists (`reports.py`, export routes). Product/zone/nameserver/API: **none in
schema/importer**. Authority: Terra preserves no-write; Human-int owns any later
product. Principal: domain analyst (export read only). Payload: export shows
source, time, limitations, recipient responsibility. Mode: missing (write path
intentionally absent in Tier A). Responsible: Terra (boundary); Human-int
(future). Evidence: source-authority §FR-012; spec FR-012 §401-414; row-map
RFP-055. Gap: no parser, live query, write, or machine validation. Next gate:
authorized negative evidence that write paths are absent (T025); any future DNS
source needs its own contract.

### RFP-056 DHCP changes — Missing live; synthetic fixture Tier B only (Integration; FR-007)
Requirement: real DHCP write/outcome. Interface: none live. Product/vendor API:
**unverified**. Authority: Human-int; optional T034 synthetic fixture only after
T025 + Lead selection, kept distinct from local-static authority. Principal:
none (future DHCP operator). Mode: missing. Responsible: Human-int; Lead selects
T034 later. Evidence: row-map RFP-056; source-authority §2 (no live DHCP vendor
API); coverage.csv RFP-056. Gap: no write/outcome capability. Next gate: isolated
synthetic fixture contract (T034, locked) → official vendor contract for live.

### RFP-058 Infrastructure integration — Missing (Integration; FR-022/T019 boundary)
Requirement: IaC integration. Interface: none; Compose packages the app (not an
integration). Product/tool/operation: **unselected**. Authority: Human-int
(selects tool/contract); Terra implements only after amendment. Principal: none.
Mode: missing. Responsible: Human-int. Evidence: T019 §2 fixed-workflow/IaC row;
row-map RFP-058. Gap: no tool contract or observed operation/readback. Next gate:
chosen tool contract + authorized observed operation/readback.

### RFP-059 Lifecycle framework — Partial (cross-category)
Requirement: orchestration framework spanning reservation/provisioning/reclaim.
Interface: one fixed workflow (see RFP-053 routes); no designer/engine.
Product: fixed local lifecycle, known. Authority: Terra; product/lifecycle owner
unassigned for configurability. Principal: Requester/Operator/Approver (fixed).
Mode: source-implemented (fixed path); framework missing. Responsible: Terra.
Evidence: row-map RFP-059; `contracts/lifecycle.md`. Gap: no configurable
transitions, provisioning, or reclamation. Next gate: T025 fixed-path evidence;
configurability needs versioned admin-transition contract (RFP-111, out of Tier A).

### RFP-060 Approval flow — Demonstrated (cross-category: independence)
Requirement: independent approval with local/ticket separation. Interface: local
decision routes + C-T handoff (see RFP-001/042). Product: known local. Authority:
Terra; independence rule (different principal IDs). Principal: Approver ≠
requester. Payload: self/unauthorized/stale refusals; durable audit. Mode:
source-implemented. Responsible: Terra. Evidence: row-map RFP-060. Gap: trusted
enterprise identity and external actions unclaimed. Next gate: T025.

### RFP-061 Continuous discovery — Missing (Integration; FR-013)
Requirement: actual network-discovery mechanism. Interface: none; synthetic
acquisition (feed adapter pins 8 observation files + policy; timer) is not
discovery. Product: **no discovery source**. Authority: Terra (synthetic feed);
Human-int for any live source. Principal: coordinator (synthetic acquisition
only). Mode: missing. Responsible: Human-int (future mechanism). Evidence:
`backend/ipam_demo/feed_adapter.py:23-30,305-326`; row-map RFP-061; T002 §2.1.
Gap: replay + timer ≠ network observation. Next gate: named mechanism + live
observation evidence (out of Tier A).

### RFP-063 Reconciliation — Demonstrated (cross-category: local engine)
Requirement: saved intended-vs-observed reconciliation over synthetic inputs.
Interface: internal reconciler invoked by coordinator run / opt-in callback /
timer (one-run lock). Product: local engine, known. Authority: coordinator-only
global invocation. Principal: coordinator; domain users read saved results.
Mode: source-implemented. Responsible: Terra. Evidence: row-map RFP-063.
Gap: live adapters/network state outside scope; S5-09 partial branches remain.
Next gate: T025.

### RFP-067 Cross-system validation — Missing (Integration; FR-010)
Requirement: DNS+DHCP+CMTS authority join. Interface: none (authorities stay
separate records). Product: **no join keys**. Authority: Human-int + Grok-int;
T019 records exclusion. Principal: none. Mode: missing. Responsible: Human-int.
Evidence: source-authority §FR-010; row-map RFP-067. Gap: DNS and CMTS absent;
one sample cannot complete validation. Next gate: each authority evidenced
separately, then join contract.

### RFP-068 Run schedule — Demonstrated (cross-category: coordinator-only schedule wire)
Requirement: configurable local scheduling plus manual Run now. Interface: `GET
/api/schedule` (coordinator-only status read, app.py:511 — requires coordinator
`read` + full feed authority); `POST /api/schedule` **always 403, including the
coordinator** (app.py:517-519 — no HTTP schedule mutation exists; configuration
changes go through the reviewed stopped-service replacement procedure only);
`POST /api/schedule/run` (manual coordinator acquisition, app.py:521-528, 201
fresh / 200 replay via `X-Acquisition-Replay`). There is no enable/disable HTTP
mutation in bridge source, and no old controlled-time evidence is promoted to
bridge runtime. Product: local scheduler, known. Authority: coordinator-only
run/status; config replacement = reviewed stopped-service procedure (ordinary
domain operators have no schedule rights). Principal: coordinator.
Payload: manual acquisition payload with idempotency/replay; busy/failure shown
separately. Mode: source-implemented (bounded; wire as above, runtime
unobserved). Responsible: Terra. Evidence: app.py `:511-528`; row-map RFP-068.
Gap: S5-09 partial branches from the old baseline (held-guard, no
OS-signal-in-flight, no elapsed-hour endurance) remain old-baseline limits, not
bridge claims. Next gate: T025; endurance/live excluded.

### RFP-069 Reconciliation reports — Demonstrated (cross-category: export interface)
Requirement: run reports + export matching saved results. Interface: `GET /api/
runs…/export`, `/api/report-preset`, CSV/JSON export (outbound read). Product:
local export, known. Authority: Terra/C-A (scoped projections; fixed safe
filenames; authenticated downloads). Principal: Viewer (selected domain).
Payload: selected-run report/export matches saved results; scheduled external
delivery absent. Mode: source-implemented. Responsible: Terra. Evidence: row-map
RFP-069. Gap: no scheduled external delivery. Next gate: T025 export/projection
cases.

### RFP-070 Remediation — Demonstrated (cross-category: bounded local correction)
Requirement: local intended-inventory correction/reconciliation. Interface: local
correction/missing-prefix registration (bounded F1 contract). Product: known
local. Authority: Terra; Operator `inventory_edit`, Approver exact-correction
decision (no general edit grant). Principal: Operator/Approver. Mode:
source-implemented (bounded). Responsible: Terra. Evidence: row-map RFP-070.
Gap: no external remediation, release, or reclamation; missing-route policy
unknown. Next gate: T025.

### RFP-072 Discrepancy notice — Demonstrated (cross-category: notice transport)
Requirement: new-finding notification + transfer + recipient acknowledgement
clearing pending flag. Interface: in-app notice transport only
(`GET /api/reservation-notices…`, `POST …/notice`, per-version ack). Direction:
app→configured recipient, in-app. Product: notice-recipient-wire, known;
external ticket/email/paging: none. Authority: reviewed configuration
(one Operator recipient per domain/scope); change = config replacement only.
Principal: configured recipient acknowledges own binding; others see redacted
projection (`is_current_recipient`, allowlisted reasons only). Payload/error/
retry/readback: exact notice/version; different-route 409 until evaluate renews;
same version/actor/reason replay returns original receipt; exact-version GET
recovery; GET never reroutes. Two evidences kept strictly separate, no
equivalence: (a) **historical S5-13** finding/exception notification with
pending-flag acknowledgement (`primary/exception-summary.json`,
`primary/exception-acknowledged.txt`) — pre-bridge baseline, in-app transport
only; (b) **new FR006 bridge source implementation** above (T016A/B, T017A,
T018), runtime unobserved. A reservation acknowledgement never clears an
exception pending flag, a reservation condition, or a hold; resolution,
delivery, and acknowledgement are distinct states. Mode: (a) historical
Demonstrated retained class, (b) source-implemented. Responsible: Terra/Luna/Opus authors (retain fixes). Evidence:
`contracts/notice-recipient-wire.md`; app.py `:1119-1210`;
`backend/ipam_demo/lifecycle.py:182-308`. Gap: in-app only; no external
integration. Next gate: T025 notice/ack/replay cases; human receipt is T026.

### RFP-081 Team handoff — Partial (cross-category: ticket-adjacent transfer)
Requirement: standardized cross-team transfer/ack/audit. Interface: C-T
reassignment (current configured team only) + in-app exception transfer.
Product: local team map, known; real team integrations **unverified**. Authority:
reviewed configuration (team map); Lead for process adoption. Principal:
Operator (reassign, zero-attempt only); fictional named teams observed.
Payload: expected intent version + key + reason; assignment history append-only.
Mode: source-implemented (fixed fictional transfer); broader process partial.
Responsible: Terra; Lead (adoption). Evidence: row-map RFP-081; C-T reassignment
clauses. Gap: broader adopted cross-team process + real integrations absent.
Next gate: T025; adoption evidence is organizational, not Tier A code.

### RFP-082 Exception escalation — Demonstrated (cross-category)
Requirement: bounded in-app escalation/handoff/ack/close/reopen with audit.
Interface: in-app exception actions. Product: known local. Authority: Terra/C-A
(permitted exception actions, Operator). Principal: Operator/fixed actors.
Payload: acknowledged/escalated state + reason/history. Mode:
source-implemented. Responsible: Terra. Evidence: row-map RFP-082. Gap: no
external paging or adopted customer process. Next gate: T025.

### RFP-087 Legacy migration — Partial (cross-category: assessment input path)
Requirement: synthetic import/provenance + selected rejections as migration input
evidence. Interface: `POST /api/imports` + C-M assessment (see §4). Product:
canonical importer, known; customer dataset conversion **absent**. Authority:
Terra; customer migration needs authorized evidence. Principal: Operator
(staging); coordinator (observations). Mode: source-implemented (synthetic
inputs only). Responsible: Terra. Evidence: row-map RFP-087; `contracts/
migration.md`. Gap: no source-specific adapter, cutover, baseline promotion, or
customer acceptance. Next gate: T022 recipient pack records counts/signoff
boundary; T025.

### RFP-089 Migration validation — Missing (cross-category: assessment outcome)
Requirement: migrated customer dataset with before/after reconciliation +
sign-off. Interface: C-M sign-off/export exist locally, but no customer dataset
has passed through them. Product: local assessment known; customer data: none.
Authority: Terra (mechanism); Human-biz/recipient for actual sign-off (T022/
T026). Principal: independent approver (mechanism ready, no customer execution).
Mode: missing (outcome). Responsible: Terra (mechanism); recipient (execution).
Evidence: row-map RFP-089 (excluded from final 51-ID mapping); T019 evidence
vocabulary. Gap: schema preservation ≠ customer migration validation. Next gate:
T022 pack + authorized customer evidence (out of Tier A runtime).

### RFP-090 App deployment — Demonstrated (T020 gate; FR-021 operator pack)
Requirement: application package deployment interface for the operator handoff.
Interface: packaged app + stopped backup/restore/readiness protocol (T023/T024
boundary); no new infrastructure. Direction: operator consumes package.
Product/contract/version: existing Linux amd64 target work (T022 declares one
target or its unavailability); bridge package source known at inspected
candidate, runtime unobserved. Authority: Muse (operator pack, T024, reassigned
from Spencer per `delivery/operator-preparation-ownership.md`; Spencer retains
no current authority) with
core-supplied protected configuration/application contract (T023); Astra/Main
Lead 5.0 accountable. Principal: operator roles (pack consumers); coordinator credential vs domain
credential separation (C-A/C-O). Payload/error/retry/readback: stopped
backup/restore with recovery manifest + sidecar classification
(like_for_like/changed_configuration/unverified); six-boolean authenticated
readiness; missing assets/invalid schema/failed readiness block visibly, never
quietly re-seed. Mode: source-implemented preparation (T023 done); package
assembly and runtime pending T024/T025. Responsible: Muse (pack, T024), Terra
(core contract). Evidence: `contracts/state-recovery-wire.md`;
`contracts/operator.md`; coverage.csv RFP-090 (T020 gate); row-map RFP-090.
Gap: portable/human evidence separate (T024/T025/T026). Next gate: T022 target
declaration → T024 pack → T025 observation; T028 merge.

### RFP-091 Orchestration deployment — Partial (cross-category: FR-007)
Requirement: broader orchestration platform / external orchestration
integrations. Interface: fixed local workflow deployed (same binary); no
orchestration platform API. Product: local workflow known; platform: none.
Authority: Terra; Human-int for any external orchestrator. Principal: n/a.
Mode: source-implemented (fixed workflow deployment); orchestration missing.
Responsible: Terra; Human-int (future). Evidence: row-map RFP-091; coverage.csv
RFP-091. Gap: fixed workflow ≠ orchestration platform. Next gate: T025; platform
claim needs selected product + observed integration (out of Tier A).

### RFP-092 Training material — Documentary (T020 gate; FR-021 handoff docs)
Requirement: user/operator guidance material for recipient handoff. Interface:
documentary (`DEMO_STORY.md`, `DEMO_RUNBOOK.md`, `STATE_OPERATIONS.md`, final
procedural handoff); no training delivery interface exists. Product: guidance
docs known; delivered program **absent**. Authority: Lead (material); Astra
records true T026 human evidence or a pending disposition — no agent or former
assignee rehearsal substitutes. Principal:
operator/recipient readers. Payload/error/retry/readback: n/a (documents);
substantive guidance supplied, practice/acceptance unobserved. Mode: documentary
preparation; retained class Documentary preserved, not promoted. Responsible:
Lead; Astra records true T026 human evidence or pending (no recipient invented
here). Evidence: row-map RFP-092; coverage.csv
RFP-092 (T020 gate). Gap: no delivered training program, human practice, or
recipient acceptance. Next gate: T022 recipient pack → T026 actual human
evidence or pending disposition.

### RFP-096 Provider DNS/DHCP — Missing (cross-category scale/integration; FR-007)
Requirement: provider-scale DNS/DHCP serving + integration + load evidence.
Interface: none. Product/load/serving: **unverified**. Authority: Human-int;
performance owner for any future load run. Principal: none. Mode: missing.
Responsible: Human-int. Evidence: row-map RFP-096; T019 §2 scale row; T002
missing-fact register. Gap: no serving, integration, load, or service-operation
evidence. Next gate: approved scale protocol (T019 §3 assumptions are planning
inputs, not thresholds) + exact-candidate observation.

### RFP-098 Subscriber allocation — Missing (Integration; FR-004)
Requirement: subscriber/service-identity integration + subscriber-facing
provisioning outcome. Interface: none; `service_reference` is an opaque local
field, not an identity join. Product: **no subscriber platform**. Authority:
Human-int. Principal: none. Mode: missing. Responsible: Human-int. Evidence:
row-map RFP-098; C-L conversion-identity clarification (purpose ≠ service
identifier). Gap: fixed local request supplies no subscriber capability.
Next gate: official subscriber-system contract + identity mapping + observed
outcome (out of Tier A; Tier B reassignment is local-only).

### RFP-104 Knowledge transfer — Missing (T020 gate; FR-021 human gate)
Requirement: accepted recipient knowledge-transfer program with walkthrough/
practice/acknowledgement. Interface: none yet — T022 will produce
`recipient-validation.md` + `configuration-example.json`; T026 records actual
human evidence. Product: no transfer program. Authority: Lead assigns actual
people; agents prepare, never acknowledge. Principal: actual human recipient
(unassigned until Lead names). Payload/error/retry/readback: future actual ack
fields on pinned candidate; agent reproduction is never a substitute. Mode:
missing (outcome); preparation tasks T022/T026 own the path. Retained class
Missing preserved. Responsible: Astra/Lead (records true human evidence or
pending); Muse owns T022 preparation (Spencer's former preparation assignment
is superseded, retained here as history only). Evidence: row-map RFP-104; coverage.csv RFP-104
(T020 gate); `delivery/operator-preparation-ownership.md`. Gap: no accepted
program, walkthrough, practice, or acknowledgement. Next gate: reviewed T020 →
T022 pack → T026 actual evidence or pending disposition limiting the package claim.

### RFP-106 Dependency disclosure — Documentary (T020 gate; FR-021 pack manifest)
Requirement: pinned dependency disclosure for the operator package. Interface:
manifest/lock files consumed by T024 pack (`pyproject.toml`, `uv.lock`,
`frontend/package.json`, `frontend/package-lock.json`) + S5-01
`primary/environment-inputs.json`. Product: pinned core manifests known;
complete transitive/container license disclosure **unverified**. Authority:
Muse (T024 records actual Compose plugin version, deps/licenses/presenter
path; reassigned from Spencer, who retains no current authority); Lead adjudicates. Principal: operator/packager. Payload/error/retry/
readback: manifests pin versions; complete notices remain a T024 deliverable.
Mode: documentary preparation; retained class Documentary preserved. Responsible:
Muse (T024). Evidence: row-map RFP-106; coverage.csv RFP-106 (T020 gate).
Gap: complete transitive/container license disclosure and notices unverified.
Next gate: T024 dependency/license inventory → T025 exact-candidate check.

## 4. Detailed contracts (selected only: local HTTP API, C-M assessment, ticket simulator)

### 4.1 Selected local HTTP API (source-implemented, runtime unobserved)
- **Auth/transport (C-A):** `Authorization: Bearer <64-hex>` + `X-IPAM-Domain`;
  clients pin `X-IPAM-Configuration-Revision/Digest`, 409 `ACCESS_CONTEXT_STALE`
  on mismatch (401 first for revoked/invalid token). Memory-only browser token;
  authenticated blob downloads; `/api/docs`, `/api/openapi.json` authenticated.
- **Reservations (C-L):** routes at app.py `:1073-1269`; create
  `{idempotency_key, pool_id, candidate, pool_version, baseline_version,
  owner_reference, service_reference, reason, duration_hours=24 (1..168)}`;
  extend `{idempotency_key, expected_version, expected_pool_version,
  expected_baseline_version, reason, duration_hours}`; release propose strict
  `{actor_id?, idempotency_key, expected_version, expected_pool_version,
  expected_baseline_version, reason}` and release decision strict
  `{actor_id?, idempotency_key, action: approve|reject, expected_version,
  expected_pool_version, expected_baseline_version, reason}`
  (`lifecycle.py:628-639,679-699`; optional `actor_id` must match the trusted
  principal; no literal `key` alias is accepted — the field is
  `idempotency_key`); 201 fresh /
  200 replay with `X-Request-Replay`; exact-key recovery `GET /api/
  reservation-operations?idempotency_key=…&action=…` (+`reservation_id` for
  propose). Allocation links `reservation_id` only with `service_reference` +
  positive `reservation_version`.
- **Notices/occupancy (T016A/B, T017A):** `GET /api/reservation-notices[?reservation_id]`,
  `GET …/{id}`, `GET …/{id}/notifications/{version}` (immutable recovery),
  `POST /api/reservations/evaluate` (empty-or-actor body), `POST /api/
  reservations/{rid}/notice` `{notice_id, expected_notification_version, reason}`,
  `GET /api/current-static-occupancy` (active allocations + reserved holds over
  assignable capacity, UTC as-of). Ack: current mapped recipient == bound
  recipient, enabled/unexpired/Operator/right-domain, exact version, eligible
  state; else 409; same actor/reason replay returns original receipt.
- **Readiness (C-A/C-O):** `GET /api/readiness` (Operator + selected domain),
  six booleans `process_ready, schema_ready, data_ready, static_ready,
  configuration_ready, domain_state_compatible`; HTTP 200 iff all true, else
  failure status + allowlisted reasons. `/healthz` = `{"process_ready": true}`
  only. Six booleans never promote to business/human evidence.
- **Errors:** AppError shape throughout; 401 unauthenticated, 403 forbidden,
  404 foreign/unclassifiable (non-disclosing), 409 same-key-changed-content/stale/
  integrity. No protected payloads in errors/traces/counts/filenames.

### 4.2 Immutable migration assessment C-M (source-implemented T008/T009, UI T010)
- **Create:** `POST /api/migration-assessments` accepts only `{source_batch_id,
  expected_baseline_version, idempotency_key, reason, supersedes_id?,
  supersedes_reason?}`; actor/domain/mapping/authority/policy revisions derived
  server-side. Unknown fields rejected. Staging is all-or-nothing; successful
  staged receipt: accepted=input, rejected=duplicate=0.
- **Read:** `GET /api/migration-assessments?limit=50&offset=0` (selected-domain
  filter before count/paging + current baseline); `GET …/{id}` (summary + rows +
  active_only + digest + lineage + sign-off + computed staleness); `GET …/{id}/
  export` (same sanitized detail, fixed safe filename).
- **Sign-off:** `POST …/{id}/signoff` accepts only `{expected_version,
  expected_digest, active_only_acknowledged: true, idempotency_key, reason}`;
  independent approver; requires zero rejected, explained duplicates, approved
  mapping, no conflicts, reconciled counts, acknowledged active-only, unchanged
  baseline + governing revisions. Both POSTs return `{assessment, replayed,
  original_signoff}`; sign-off receipt fields allowlisted to five.
- **Digest:** `ipam.assessment_digest.v1`, SHA-256 over canonical header +
  rows sorted by `source_record_id` + active-only sorted by `matching_key`;
  anchored in creation receipt, recomputed on read, mismatch fails visibly.
  Authority revision: `ipam.authority_revision.v1` (`config_digest`,
  positive `config_revision`).
- **Readback:** `GET /api/migration-assessments/operation-receipt?action=
  assessment.create|assessment.signoff&idempotency_key=…` (≤200 chars),
  current principal + selected domain; returns `{found, action, assessment,
  original_outcome}`; missing key ≠ proof of absence. No activate/promote/
  cutover endpoint exists; abandoning review changes no state.

### 4.3 `internal-ticket-simulator/v1` C-T (source-implemented T013/T014, UI T015)
- **Intent:** one logical intent per domain/request/action, atomically persisted
  with the allocation request in the caller's transaction; stable correlation;
  business digest excludes route/team metadata; changed payload on same identity
  → 409. Missing route → `routing_blocked` (request still created).
- **Attempt (manual only):** `reserve_attempt` (ordinal reserved first, consumed
  forever) → `commit_simulator_effect` (durable, distinct) → `observe_attempt`,
  three separately committed, freshly authorized transactions; strict body
  `{expected_version, idempotency_key, synthetic_scenario: success |
  definitive_failure | committed_response_lost | no_effect_response_lost}`
  plus optional `actor_id` matching the authenticated principal
  (`ticket_handoff.py:627-628`);
  scenario + assignment version pinned in attempt digest. 5 s budget = deadline.
- **Readback/ack/reassign:** `POST …/readback` accepts only the strict body
  `{expected_version, idempotency_key, correlation, business_payload_digest}`
  plus optional `actor_id` which must match the authenticated principal
  (`ticket_handoff.py:803-805`; `key`/`digest` aliases are rejected by the
  strict payload allowlist). Readback returns found + actual synthetic ID
  (found resolves unknown to delivered, attempt row updated), definitive-absence
  (no-effect/fenced-failure path only), or sanitized
  error; error stays unknown; definitive absence permits retry; uncertain attempt
  fences before failed. Ack pins effect/ticket, explicitly simulated, grants no
  local authority. Reassign: zero-attempt pending/routing_blocked only, current
  configured team (never caller destination), history append-only; after any
  attempt, route change unsupported in Tier A. Rejected-request/​released-hold
  zero-attempt intents resolve to failed only via fresh exact-correlation
  definitive-absence readback (no attempt created, no hold released).
- **Recovery:** `GET /api/handoff-operations?idempotency_key=…&action=
  ticket.attempt|ticket.reassign|ticket.readback|ticket.acknowledge`
  (Viewer, own principal/domain); strict DTO `{found, action,
  original_operation, current_handoff}`; missing own key → found=false, never
  proof of non-commit; malformed authorized receipt → 409; foreign → 404.
- **Disable:** blocks new attempts/effects; readback/history/simulated-ack of
  delivered effects remain. UI label: "Simulated ticketing handoff — ServiceNow
  mapping pending." Provisioning: unsupported/not requested, always separate.

## 5. Omissions disposition (63 rows, no integration clause and no T020 gate)

Local-application (no external interface; C-A/C-L/C-M local behavior only):
002 dual-stack records, 003 subnet editing, 004 permissions, 005 activity audit,
006 search/reports, 007 browser UI, 026 network domains, 027 metadata, 028
classification, 029 overlap, 030 hierarchy, 031 common metadata, 035 IPv6
planning, 054 assignment policy, 057 reclaim execution (absent capability, Tier B),
062 validation, 064 conflicting assignments, 065 stale allocation, 066 unassigned
usage, 071 run history, 073 utilization, 074 forecasting, 075 candidate space,
076 operational metrics, 077 dashboard, 078 audit reporting, 084 change controls,
085 validation policy, 095 regional hierarchy, 111 configurable lifecycle (missing).
Deployment/topology (no integration wire; T019/T023–T024 own the boundary):
008 tenant isolation, 014 single-failure-point, 015 deployment modes, 016
failover, 017 geography, 018 backup/restore, 019 recovery point, 020 recovery
time, 021 encryption, 023 hybrid, 024 virtual-network (packaging ≠ inventory).
Scale/measurement (no protocol run; T019 §3 values are planning assumptions):
025 carrier scale, 093 large inventory, 094 millions of records, 097 concurrency.
Delivery/business (documentary or human-owned; T019/T026 own the gates):
032 governance, 038 workflow docs, 040 maturity (missing), 079 ownership, 080
lifecycle process, 083 review cadence, 086 improvement method, 088 migration
plan, 099 references, 100 telecom refs, 101 large ref, 102 method, 103 staffing,
105 roadmap,
107 support, 108 licensing, 109 SLA, 110 compliance.
(RFP-090/092/104/106 carry an explicit T020 gate and are dispositioned in §3.)

## 6. Unknown-vendor-fact register (closed; no guesses)

| Unknown fact | Rows | Accountable role | Evidence gate |
|---|---|---|---|
| ServiceNow product/instance/table/API/auth/idempotency/rate limits | 041, 042 | Human-int | Official instance contract after selection |
| CMDB class/CI keys + join to allocations | 041 | Human-int | Official mapping + pos/neg/ambiguous sample |
| OSS/BSS product/version/contract | 046 | Human-int | Official contract |
| Cisco CMTS/vCMTS product/version/interface (docs-first priority, research not yet authorized) | 044, 045, 067 | Human-int | Official Cisco docs + sanitized mapping |
| Harmonic product/version/interface | 045 | Human-int | Official Harmonic source |
| Comcast-named platform interface | 045 | Human-int | Official source if legally available |
| EMS read operation contract | 044 | Human-int | Read-only official op + observation time |
| DNS product/zones/TSIG/update API | 055 | Human-int | Scoped read contract; Tier A writes forbidden |
| Live DHCP vendor API | 011, 056 | Human-int | Isolated fixture (T034, locked) then vendor contract |
| K8s/VM/CNI controller + network IDs | 058 | Human-int | Named controller + object mapping |
| Orchestration platform product/contract | 091 | Human-int | Selected product + observed integration |
| Provider-scale serving/load design | 096 | Human-int + performance owner | Approved protocol + exact-candidate run |
| Subscriber-system identity/contract | 098 | Human-int | Official contract + identity mapping |
| Directory/IdP/LDAP/mTLS provider contracts | 048–051 | Human-int | Frozen provider contract + accept/refuse cases |
| Credential custody/rotation owner | 052 | Unassigned platform/security owner | Approved custody/rotation procedure |
| Customer source authority/inventory | 036 | Human-int | Authorized source program + verification |
| Commercial refs/staffing/license/SLA/compliance owners | (business rows, §5) | Human-biz (unassigned) | Approved authentic artifacts; private stays out of Git |

## 7. Handoff to T021 / T022 (usable without reopening settled plans)

- **T021 (offline API, Opus):** consume §4.1 + §4.2 + §4.3 as the source-accurate
  interface baseline at candidate `b8f294fc…` / assembly `a2b567b…`; reuse
  authenticated interactive reference; mark all examples illustrative until Luna
  T025; no secret/vendor invention. Prerequisites: reviewed T020 + T009/T014/T017A.
- **T022 (recipient preparation, Muse):** consume §4.2 counts/sign-off/cancel
  boundary + per-version recipient ack semantics (§2, RFP-072) + readiness six-
  boolean rule (§4.1); one Linux amd64 target declared or explicitly unavailable;
  no fabricated signoff/cutover; actual acknowledgement fields only (T026
  pending). Prerequisites: reviewed T020 + T010/T015/T017A.
- **Not written here:** `offline-api.md`, `recipient-validation.md`,
  `configuration-example.json` (later tasks own them).
- Human (T026), portable/business (T019, T024, T028), and runtime (T025) gates
  are separate and unchanged; Tier B stays locked.

## 8. Source-consistency inspection (this document)

- Inspected: `AGENTS.md`, `DEVELOPMENT_RULES.md`, `docs/STATUS.md`,
  `docs/QUESTIONNAIRE_ROW_MAP.md`, `docs/QUESTIONNAIRE_PRIORITIES.md`,
  `specs/001-postmeeting-bridge/task-graph.csv` (T020 row),
  `delivery/source-authority.md` (T002), `delivery/gaps-and-qualification.md`
  (T019), `coverage.csv`, `delivery/operator-preparation-ownership.md`,
  `contracts/access.md` (C-A), `contracts/migration.md` (C-M),
  `contracts/lifecycle.md` (C-L), `contracts/ticketing.md` (C-T),
  `contracts/operator.md` (C-O), `contracts/ticket-api-wire.md`,
  `contracts/reservation-ticket-wire.md`, `contracts/notice-api-wire.md`,
  `contracts/notice-recipient-wire.md`, `contracts/state-recovery-wire.md`,
  `spec.md` FR-004/007/009/010/011/012, and current implementation presence via
  `backend/ipam_demo/app.py` (handoff :698–777, reservation :1073–1269, notice
  :1119–1210, migration :1878–1964, schedule :511–528), `ticket_handoff.py` (six entry points,
  strict readback/attempt payload allowlists :627/803, handoff DTO
  `provisioning_status` :419), `models.py` (`TicketHandoffSummary:185`),
  `workflow.py` (allocation `downstream_status` :450/502/507),
  `lifecycle.py` (notice evaluate/ack/versioned recovery).
- Consistency notes: all §4 routes/fields exist at the inspected candidate;
  T002's unverified-vendor cells are copied as unverified (T002 stays
  documentary); T019's assumption labels (§3) are preserved as assumptions, not
  thresholds; coverage.csv "post-meeting answer" column is a future/meeting
  classification, not new evidence — retained S3 classes control; no runtime,
  build, test, SQL/DB, shell, git, network, or private-source access was used.
- Limits: source-only — every `source-implemented` claim awaits T025 exact-
  candidate observation; every `simulated` claim is local-only; every `missing`
  cell needs its §6 gate before any integration credit.
- Correction pass (Sol whole-review + Astra, seven grounded blockers) applied
  over prior T020 commit `4c55eb7101263654fc6803978dce7e670933de70`: (1) added
  RFP-090/092/104/106 per T020 gate, selection now union Integration ∪ T020-gate
  (36) + 12 justified cross-category = 48, omissions 63; (2) unknown resolves to
  delivered on found effect, absence is no-effect/fenced path only; (3) RFP-068
  rewired to actual coordinator-only GET / always-403 POST / manual run POST;
  (4) RFP-001/053 gaps state implemented unused release, Tier B reclaim, and
  unsupported-not-simulated provisioning with old-baseline notes separated;
  (5) RFP-072 splits historical S5-13 finding ack from new FR006 notices, no
  equivalence; (6) RFP-047 separates ticket-DTO `provisioning_status` from
  allocation-column `downstream_status`; (7) §4.3 uses strict readback/attempt
  field names, aliases rejected. All 44 original row meanings preserved.

READY FOR PROJECT-LEAD REVIEW — Stage T020: T020 integration matrix at inspected
candidate `b8f294fc19b635dcf3c784125fd804d8a1a2616b` (branch
`codex/bridge-t020-agent-matrix`), assembly `a2b567b670129671f85498729753c4d577d4768e`.
Row coverage: 48 included — union of Category=Integration (19) and coverage.csv
T020 gate (28), i.e. 36 rows, plus 12 justified cross-category rows
(001/022/033/034/037/053/059/063/069/072/087/089; RFP-048/049/050 share one
block, all three covered) — with full per-row fields and §4 detailed contracts;
63 omitted with §5 disposition; 111 total, no invented rows, no promotion
(RFP-090 Demonstrated / 092 Documentary / 104 Missing / 106 Documentary
retained). Modes: local interfaces source-implemented where stated (runtime
unobserved, T025 pending); only RFP-042's ticket leg is simulated-local with
its external leg missing; RFP-039 is the documentary matrix itself (pending
review); all §6 vendor facts unverified.
Gaps: all §6 vendor facts unknown with Human-int gates; runtime (T025), human
(T026), portable/business (T024/T028) separate. Source-only limits: no tests,
builds, runtime, or private sources touched; one file leased, no other edits.
Draft next prompt: "Sol, independently review
`specs/001-postmeeting-bridge/delivery/integration-matrix.md` at the T020 commit
against T002/T019/contracts/row-map/coverage.csv for completeness (48+63=111), unverified-cell
fidelity, and any guessed endpoint/version/auth or simulated-as-live entry; then
release T021 (Opus) and T022 (Muse) on the reviewed matrix."
