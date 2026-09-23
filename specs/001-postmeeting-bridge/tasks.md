# Tasks: Post-meeting IPAM / Pool Watch bridge

Input: locked spec, plan, data model, contracts and Q001–Q100 decisions.
The original package was planning only. Checked tasks now refer to the dated source-only
closures in delivery/foundation-source-review.md and its linked T007 report; no runtime acceptance is implied.
Implementation and validation each require later authority. No test code tasks added.
Future independent observations are acceptance gates, never implied completed runs.

Task-graph.csv holds task-level owner, files, requirements, contracts, spawn, completion,
evidence, non-claims, escalation and handoff. [P] allows overlap only after prerequisites
with a disjoint-file task. Capacity and file leases control all spawns. A single worker
cannot do two tasks at once. US1 and US2 can be independently observed against fixtures;
migration never authorizes a local change. US4 prepares alongside core implementation.



## Phase 1 — Setup and authority

- [x] T001 Adopt contracts; record actual implementation/validation authority, model/staff availability, base SHA, schema reservation and file ownership. Files: `specs/001-postmeeting-bridge/delivery/authorization-and-ownership.md`.

  Prerequisites: authority gate; owner: Astra / Main Lead 5.0; FR-001 FR-005 FR-015 FR-021. Completion: Explicit lead decision before dispatch; no inferred execution permission.

- [x] T002 [P] Inventory source/field authority and missing vendor/business facts; Cisco is future documentation priority, no invented product/endpoint. Files: `specs/001-postmeeting-bridge/delivery/source-authority.md`.

  Prerequisites: T001; owner: Grok 4.6 under Grok 4.7; FR-009 FR-010 FR-012 FR-014 FR-018 FR-020. Completion: Every gap has a requirement, owner role and evidence gate.


T001/T002 are documentary source checkpoints. T003 is source accepted at9c73fd8; its checked task marker records the schema source handoff only. SQL/migration/runtime observations and full Tier A acceptance remain T025 gates.

## Phase 2 — Shared foundation

- [x] T003 Implement Tier A assessments, reservation/release/notice, request reservation link, ticket intent/attempt/effect and scoped preset schema. Positive versions; ordinals 1..3; unique active reservations/correlations. Preserve IDs/FKs and quarantine legacy presets; no Tier B schema. Files: `backend/ipam_demo/schema.sql`, `backend/ipam_demo/schema_v6.sql`, `backend/ipam_demo/store.py`, `backend/ipam_demo/seed.py`. Retain versioned ticket route assignments; attempts pin assignment version and chosen synthetic scenario. Scoped presets quarantine legacy ownership.

  Prerequisites: T001; owner: Terra in Codex; FR-002 FR-003 FR-004 FR-005 FR-016. Completion: Explicit recognized upgrade and fresh initialization; no destructive reseed or history loss.

- [x] T004 Implement bearer-digest principal and reviewed config: token at least 256 random bits, enabled/UTC expiry/roles/domains/revision; one domain, no actor fallback/admin bypass, no secret logging. Define the fixed internal evidence coordinator with explicit complete synthetic feed scope/source grants, global evidence operations only and no user delegation. Files: `backend/ipam_demo/access.py`, `backend/ipam_demo/models.py`.

  Prerequisites: T003; owner: Terra in Codex; FR-005 FR-015. Completion: Default-deny trusted context, fail-closed invalid authority and stopped/reload revocation.

- [x] T005 Enforce all C-A routes/nested serializers before counts/export; project authorized saved runs without raw mutation; deny mixed raw/unmapped legacy data; scoped presets/audit/timer/docs/readiness, anonymous minimal liveness only. Global run/acquire/observation-callback mutations and receipts are coordinator-only; ordinary imports intended candidates only, callback disabled, mixed/observation/callback=true rejected before persistence. Ordinary refresh reads saved projections. Files: `backend/ipam_demo/app.py`, `backend/ipam_demo/inventory.py`, `backend/ipam_demo/reports.py`, `backend/ipam_demo/imports.py`, `backend/ipam_demo/source_catalog.py`, `backend/ipam_demo/scheduler.py`, `backend/ipam_demo/workflow.py`, `backend/ipam_demo/feed_adapter.py`, `backend/ipam_demo/inventory_commands.py`. Preserve Operator inventory_edit and independent Approver correction decisions without general direct-edit rights.

  Prerequisites: T004; owner: Terra in Codex; FR-005 FR-009 FR-013 FR-015 FR-019. Completion: Every route has allow/deny/projection classification and no global data leak.

- [x] T006 [P] Wire memory-only token/domain through all clients and authenticated blob downloads; remove actor picker as identity; expose auth/stale/permission failures. Disable global run/acquisition/schedule/callback controls for ordinary domain sessions; saved-result refresh only. Files: `frontend/src/api.ts`, `frontend/src/firstPathApi.ts`, `frontend/src/workflowApi.ts`, `frontend/src/inventoryCommandsApi.ts`, `frontend/src/correctionApi.ts`, `frontend/src/scheduleApi.ts`, `frontend/src/App.tsx`, `frontend/src/FirstPath.tsx`, `frontend/src/Schedule.tsx`, `frontend/src/CapacityReports.tsx`, `frontend/src/Corrections.tsx`, `frontend/src/InventoryEditor.tsx`, `frontend/src/Workflow.tsx`. Bind protected state/retries to authenticated principal/domain/config revision, reject late prior-context responses and require original-context readback for ambiguous operations before replacement.

  Prerequisites: T004; owner: DeepSeek UI under Terra; FR-005 FR-009 FR-015 FR-019. Completion: No token in URL/localStorage/logs; browser uses trusted context everywhere.

- [x] T007 Review all routes, clients, legacy data and errors against C-A before feature integration; record allowed/denied/projected/quarantined cases. Files: `specs/001-postmeeting-bridge/delivery/access-review.md`.

  Prerequisites: T005 T006; owner: Luna independent verifier; FR-005 FR-015 FR-019. Completion: No unresolved source/design access findings; runtime still requires T025.


T005/T006/T007 are source accepted at `aee0ade8bbeb6405aab4a6cf0c35079d76e6318e` after independent GPT-6 Sol review and owner corrections. Runtime remains unverified; T025 is open. Latest routes are in delivery/model-routes.md.

## Phase 3 — US1 migration assessment (P1)

Goal/gate: account for all candidate inputs with no active writes; independent count/conflict/stale/sign-off evidence.

- [x] T008 [US1] Reuse parser/receipts for immutable assessment. Enforce input=accepted+rejected+duplicate and accepted=added+changed+unchanged+conflicting; conflict precedence, active-only separation, governed snapshot and independent sign-off/staleness; no promotion. Preserve canonical normalized JSON replay (whitespace/key-order equivalent); abandoning review changes no persisted state. Files: `backend/ipam_demo/migration_compare.py`.

  Prerequisites: T007; owner: DeepSeek backend under Terra; FR-002 FR-014. Completion: Exactly one class per accepted row; partial/conflicted/stale cannot sign; active state unchanged.

- [x] T009 [US1] Expose C-M create/list/detail/signoff/export with existing AppError/transaction, trusted context and idempotency/version guards. Files: `backend/ipam_demo/app.py`, `backend/ipam_demo/models.py`.

  Prerequisites: T008; owner: Terra in Codex; FR-002 FR-005 FR-009. Completion: Only independent exact-current assessment sign-off; no cutover endpoint.

- [x] T010 [P] [US1] Render receipt/comparison layers, active-only/conflict/refused/stale/sign-off states and scoped same-assessment export; no activation control. Files: `frontend/src/MigrationCompare.tsx`, `frontend/src/FirstPath.tsx`, `frontend/src/firstPathApi.ts`, `frontend/src/App.tsx`.

  Prerequisites: T008 T006; owner: DeepSeek UI under Terra; FR-002 FR-019. Completion: Usable assessment against T009; visible complete accounting and immutable provenance.


T008/T009/T010 have source-only acceptance at the exact SHAs in delivery/migration-source-review.md. Checked markers record implementation/source review, not observed runtime acceptance.

## Phase 4 — US2 local change and simulated handoff (P1)

Goal/gate: exact local approved transition with independent honest ticket outcome; refusal/replay/unknown/readback evidence.

- [x] T011 [US2] Implement exact local IPv4 reservation/extension/conversion/independent unused release: default24h/max168h, positive version, reserved/converted/released; immediate transaction checks both hold tables and eligible claims, matching owner/service and lineage, pool/baseline bump not denominator history. Files: `backend/ipam_demo/lifecycle.py`, `backend/ipam_demo/workflow.py`.

  Prerequisites: T009; owner: DeepSeek backend under Terra; FR-003 FR-014. Completion: No double hold, substitution, self-approval or free-on-expiry; local cancellation distinct from reclaim.

T011 has source-only acceptance at `3fcdb49d955c39cf08f0a0d6f9483384e43163b1`; see delivery/lifecycle-source-review.md. Main Lead 5.0 is registered and continues this checkpoint; T025 remains open.

- [x] T012 [US2] Expose C-L reservation/create/extend/release-request/decision and optional reservation_id allocation API; derive principal/domain and audit in existing write boundary. Files: `backend/ipam_demo/app.py`, `backend/ipam_demo/models.py`.

  Prerequisites: T011; owner: Muse 1.3 high in OpenCode; FR-003 FR-005 FR-009. Completion: Exact versions and supported authority checked; unsupported pool/family/action refused.

- [x] T013 [US2] Persist request+intent atomically and independent durable simulator effect/attempt/readback. Fixed route revision, unique correlation/digest, three total manual attempts with ordinal reserved before effect, five-second observation budget; no provisioning simulator. Files: `backend/ipam_demo/ticket_handoff.py`, `backend/ipam_demo/workflow.py`. Zero-attempt route reassignment preserves logical intent/digest/correlation and returns to pending after valid reviewed routing; attempted routes cannot change in Tier A.

  Prerequisites: T011; owner: Opus 5.5 high in Claude Code; FR-004 FR-009 FR-011. Completion: Effect-committed/response-lost recovers via same correlation; no duplicate or budget reset.

T012/T013 are independently source-reviewed at `0e8fb4b`/`a5ce063`, with T014/T016 assembled at `ede6cb6`; see delivery/reservation-ticket-source-review.md. These checkmarks do not claim runtime acceptance.

- [x] T014 [US2] Expose C-T handoff list/detail/attempt/readback/simulated acknowledgement; local approval independent of routing/delivery; disable new attempts without losing history, legacy downstream status historical only. Files: `backend/ipam_demo/app.py`, `backend/ipam_demo/models.py`. Include operator zero-attempt reassignment, exact-version/key refusal and immutable attempted route history.

  Prerequisites: T012 T013; owner: GPT-6 Luna high in Codex; FR-004 FR-005 FR-009 FR-011. Completion: Unknown never success; no ticket approval grants local authority; old requests not tracked.

- [x] T015 [P] [US2] Show reservation/decisions and independent local/ticket states, correlation/attempt cap/unknown lookup/simulated receipt; provisioning unsupported/not requested. Files: `frontend/src/Workflow.tsx`, `frontend/src/workflowApi.ts`.

  Prerequisites: T010 T014; owner: Muse 1.3 high in OpenCode; FR-003 FR-004 FR-019. Completion: Complete allocation and unused release path; downstream failure preserves visible local state.


## Phase 5 — US3 evidence and operational conditions (P2)

Goal/gate: exact current/saved metric identity and due conditions; arithmetic/ack/unknown evidence.

- [x] T016 [US3] Implement UTC reservation episodes/evaluate/ack: due alert, due+24h alarm, no auto-free; resolve on extension/conversion/release; preserve finding clearance and historical metrics, expose current active-hold occupancy separately. Files: `backend/ipam_demo/lifecycle.py`, `backend/ipam_demo/workflow.py`.

  Prerequisites: T013; owner: GPT-6 Luna high in Codex; FR-003 FR-006 FR-008. Completion: One due episode, ack not clearance, no forged finding IDs or saved-run rewriting.

- [x] T017 [US3] Integrate bounded evaluate/notice/current static occupancy endpoints with protected UTC/config context; timer default off, no new monitor/retry service. Files: `backend/ipam_demo/app.py`, `backend/ipam_demo/models.py`.

  Prerequisites: T014 T016; owner: Opus 5.5 high in Claude Code; FR-003 FR-006 FR-008. Completion: All new reads/actions scoped and authority bounded.

### Authorized FR006 recipient amendment

The user selected configured domain/scope Operator recipients and explicit in-app
acknowledgement as receipt. See contracts/notice-recipient-wire.md. Schema7 is TierA;
historical schema6 remains unchanged and no old Operator ack becomes a receipt.

- [x] T016A Implement complete reviewed recipient configuration and recognized schema7 notification history foundation. Files: `backend/ipam_demo/access.py`, `backend/ipam_demo/store.py`, `backend/ipam_demo/schema_v7.sql`. Prerequisites: T017 source acceptance; owner: Muse1.3 high in OpenCode. Independent Sol review, no application execution.
- [x] T016B Integrate immutable per-version binding, explicit evaluation renewal, recipient-only receipt and original-version readback into the notice lifecycle. Files: `backend/ipam_demo/lifecycle.py`, `backend/ipam_demo/workflow.py`. Prerequisites: T016A; owner: retained Luna T016 author. Independent Sol review; legacy facts and no-free-on-expiry preserved.
- [x] T017A Integrate reviewed configuration forwarding, strict current/history DTOs and scoped notification-version recovery endpoint. Files: `backend/ipam_demo/app.py`, `backend/ipam_demo/models.py`. Prerequisites: T016B; owner: retained Opus5.5 high T017 author. Independent Sol review; no external delivery claim.

- [x] T018 [P] [US3] Present alert/alarm, ack/resolution and current static versus saved DHCP with units/time/components; preserve safe child editing, unknown semantics and existing thresholds. Files: `frontend/src/Workflow.tsx`, `frontend/src/CapacityReports.tsx`, `frontend/src/workflowApi.ts`.

  Prerequisites: T015 T017A; owner: Muse1.3 high in OpenCode; FR-006 FR-008 FR-013 FR-019. Completion: No invented IPv6 delegation, hijack attribution or health monitoring; same metric identity across views.


T018 and T023 are source accepted at `6173efa` / `adb2dc1`, assembled at `a2b567b`. See delivery/notice-ui-source-review.md and delivery/state-recovery-source-review.md. No runtime or portable acceptance follows.

## Phase 6 — US4 operator and truthful handoff (P1)

Goal/gate: same-candidate package with actual target/recovery observations and separate human acknowledgement. Preparation follows the existing dependencies. The user reassigned the unstarted Spencer preparation to agents on 2026-09-23; see delivery/operator-preparation-ownership.md. Human T026 evidence remains separate.

- [x] T019 [P] [US4] Write evidence-based maturity/authority gaps and future HA/scale/encryption/virtual-network/EMS/DNS/IaC/fixed-workflow dispositions; human business-owner register, licensing continuity documentary only. Files: `specs/001-postmeeting-bridge/delivery/gaps-and-qualification.md`.

  Prerequisites: T002; owner: Grok 4.6 under Grok 4.7; FR-010 FR-012 FR-014 FR-016 FR-017 FR-018 FR-020 FR-022. Completion: Each exclusion has owner/evidence boundary/future gate; numeric cohorts are assumptions, not source requirement replacements.

- [ ] T020 [P] [US4] Day1 two-hour finish: inventory every integration RFP row, detailed selected local API/assessment/ticket contracts, mode/authority/owner/evidence/unknown vendor fields. Files: `specs/001-postmeeting-bridge/delivery/integration-matrix.md`.

  Prerequisites: T002; owner: Muse 1.3 high in OpenCode; FR-004 FR-007 FR-009 FR-010 FR-011 FR-012 FR-021. Completion: All integration clauses classified; no guessed endpoint or simulated-as-live entry.

- [ ] T021 [US4] Pin offline API to candidate with auth/domain/errors/reviewed versions/replay/raw-versus-projection/simulation examples; reuse authenticated interactive reference. Files: `specs/001-postmeeting-bridge/delivery/offline-api.md`.

  Prerequisites: T009 T014 T017A T020; owner: Opus 5.5 high in Claude Code; FR-009 FR-015 FR-019. Completion: Source-accurate examples distinguish illustrative from observed; no secret/vendor invention.

- [ ] T022 [P] [US4] Day2 two-hour finish: one recipient prerequisites/config template, migration reconciliation/counts/signoff/cancel boundary, separate operational compensation, actual acknowledgement fields. Files: `specs/001-postmeeting-bridge/delivery/recipient-validation.md`, `specs/001-postmeeting-bridge/delivery/configuration-example.json`.

  Prerequisites: T010 T015 T020 T017A; owner: Muse 1.3 high in OpenCode; FR-002 FR-014 FR-021. Completion: One Linux amd64 target declared or explicitly unavailable; no fabricated signoff/cutover.

- [x] T023 [US4] Integrate current schema7 stopped backup/restore/readiness and supply protected configuration/application contract to the package owner; preserve one worker and global evidence coordinator boundary. No implicit migration/reseed; no packaging edits in core. Files: `backend/ipam_demo/state_ops.py`, `backend/ipam_demo/__main__.py`. Preserve historical revision references; record changed-configuration recovery distinctly, apply normal staleness, and require all six C-A readiness booleans plus separate business-state evidence.

  Prerequisites: T003 T017A; owner: Muse1.3 high in OpenCode; FR-005 FR-016 FR-021. Completion: Supported history survives recognized state operations; code/UI/config/secrets not assumed in snapshots.

- [ ] T024 [US4] Day3 operator/package preparation: Muse owns Dockerfile/Compose liveness/config wiring, protected separate coordinator credential for acquisition and domain credential for readiness, stable keys and all-boolean readiness. Pin state/code/UI/config assets, stopped recovery, dependencies/licenses/presenter path. Record actual Compose plugin version, not inferred v2. Files: `scripts/ops/acquire.sh`, `scripts/ops/health.sh`, `scripts/ops/README.md`, `specs/001-postmeeting-bridge/delivery/operator-handoff.md`, `Dockerfile`, `compose.yaml`.

  Prerequisites: T021 T022 T023; owner: Muse 1.3 high in OpenCode; FR-009 FR-016 FR-020 FR-021. Completion: Wrappers/docs match core auth contract; no token args/logging; no universal portability/license-clearance claim.


## Phase 7 — Independent evidence and lead adjudication

**Current merge/routing clarification —2026-09-22:** Follow
[the explicit main merge rule](../../docs/MAIN_MERGE_POLICY.md). T028 merges the
complete technical Tier A candidate after exact-candidate T025 passes and blocking
reviews close. Record T026 human status honestly; its permitted pending disposition
limits claims but does not alone block technical-package integration. The user's
Claude stop supersedes the old T027 Fable route below: GPT-6 Sol performs that final
candidate/evidence review intent, with the actual route recorded. Do not invoke or
mark Fable completed. Historical task-graph role labels do not override this update.

- [ ] T025 Only after explicit validation permission, observe quickstart Tier A success/denial/stale/replay/concurrency/unknown/aging and stopped recovery at exact candidate; missing permission is not run and blocks runtime acceptance. Include domain denial of every global job/callback and no replay leakage; normalized-content duplicate control. Files: `specs/001-postmeeting-bridge/delivery/independent-evidence.md`.

  Prerequisites: T018 T019 T021 T022 T023 T024; owner: Luna independent verifier; FR-001 FR-002 FR-003 FR-004 FR-005 FR-006 FR-008 FR-009 FR-013 FR-015 FR-016 FR-019 FR-021. Completion: Every Tier A criterion has independent evidence or blocker; no reduced passing bar.

- [ ] T026 Record later authorized guided human rehearsal role/candidate/target/steps/outcome/ack; if unavailable/unauthorized record pending and limit handoff to technical package. Files: `specs/001-postmeeting-bridge/delivery/human-rehearsal.md`.

  Prerequisites: T025; owner: Astra records actual human evidence or pending disposition; FR-020 FR-021. Completion: Human-handoff claim only with actual acknowledgement; agent reproduction not substitute.

- [ ] T027 Final pre-acceptance Fable advisory on the exact implementation candidate and retained T025 evidence for contradictions/history/authority/recovery/false claims and critical-path feasibility. Files: `specs/001-postmeeting-bridge/delivery/fable-advisory.md`.

  Prerequisites: T024 T025; owner: Fable via Claude Code CLI, direct advisory to Main Lead; FR-001 FR-002 FR-003 FR-004 FR-005 FR-009 FR-016 FR-021. Completion: Actual candidate advice or a user-run prompt with lead adjudication of open findings; Fable is advisory and not an implementation dependency. The separate post-spec/dispatch-lock design advisory (FABLE-DESIGN after T001) does not complete T027.

- [ ] T028 Adjudicate evidence/Fable/human/business gates, accept only proved clauses, coordinate PR merges and authorized next stage prompt; incomplete Tier A remains partial. Files: `specs/001-postmeeting-bridge/delivery/lead-adjudication.md`, `docs/STATUS.md`, `docs/QUESTIONNAIRE_ROW_MAP.md`.

  Prerequisites: T025 T026 T027; owner: Astra / Main Lead 5.0; FR-001 FR-020 FR-021. Completion: Lead alone changes canonical ledger/status; no hidden external gate or92-completed claim.


## Optional Tier B — off the three-day critical path

- [ ] T029 [US2] After Tier A passes and explicit lead selection, finalize allocated release/reassignment history schema/readers/authority contract and complete affected-reader inventory. Files: `specs/001-postmeeting-bridge/delivery/tier-b-release-contract.md`.

  Prerequisites: T025; owner: Grok 4.7 requirements/integration sublead; FR-003 FR-004. Completion: Accepted contract before optional code; no referenced allocation deletion.

- [ ] T030 [US2] Reserve actual next schema; preserve allocation IDs/FKs, add versioned active/release history and active-only uniqueness; update all readers/export/recovery under settled optional contract. Files: `backend/ipam_demo/schema_v8.sql`, `backend/ipam_demo/schema.sql`, `backend/ipam_demo/store.py`, `backend/ipam_demo/inventory.py`, `backend/ipam_demo/reports.py`, `backend/ipam_demo/state_ops.py`.

  Prerequisites: T029; owner: Terra in Codex; FR-003 FR-004 FR-016. Completion: Historical requests remain valid; active uniqueness correct before reuse executable.

- [ ] T031 [US2] Implement independently approved local allocated release and same-IP synthetic service-reference reassignment under evidence/authority/version guards; no network reclaim/IP moves. Files: `backend/ipam_demo/lifecycle.py`, `backend/ipam_demo/workflow.py`.

  Prerequisites: T030; owner: DeepSeek backend under Terra; FR-003 FR-004. Completion: Before/after lineage and retry/refusal preserved; no contradictory/pending external effect.

- [ ] T032 [US2] Integrate settled optional local release/reassignment APIs with existing scoped guards/errors and independent local/ticket outcomes. Files: `backend/ipam_demo/app.py`, `backend/ipam_demo/models.py`.

  Prerequisites: T031; owner: Terra in Codex; FR-003 FR-004 FR-009. Completion: No unchecked admin bypass, network side effect or stale reuse.

- [ ] T033 [P] [US2] Show optional local release/reassignment exact before/after service history and local-only labels; unsupported IP moves unavailable. Files: `frontend/src/Workflow.tsx`, `frontend/src/workflowApi.ts`.

  Prerequisites: T032; owner: DeepSeek UI under Terra; FR-003 FR-004. Completion: Tier A remains intact; no subscriber provisioning claim.

- [ ] T034 [US2] Freeze one isolated synthetic DHCP create-reservation fixture/authority/payload/readback contract; five-minute pending attention, no vendor API guess. Files: `specs/001-postmeeting-bridge/delivery/tier-b-dhcp-contract.md`.

  Prerequisites: T025; owner: Grok 4.7 requirements/integration sublead; FR-007 FR-009. Completion: Optional operation selected by lead; provider fixture distinct from local-static authority.

- [ ] T035 [US2] Before optional DHCP leaf, core owner reserves the next actual schema and persists isolated provider reservation/effect/attempt/readback state with stopped backup compatibility. Use schema_v8.sql if no optional prior migration, schema_v9.sql only if release migration T030 already accepted; touch only selected file, record predecessor SHA/task. This task does not require selecting allocated release. Files: `backend/ipam_demo/schema_v8.sql`, `backend/ipam_demo/schema_v9.sql`, `backend/ipam_demo/schema.sql`, `backend/ipam_demo/store.py`, `backend/ipam_demo/seed.py`, `backend/ipam_demo/state_ops.py`.

  Prerequisites: T034; owner: Terra in Codex; FR-007 FR-011 FR-016. Completion: Explicit recognized migration/fresh initialization and recovery contract complete before leaf. If release is selected first, add T030 as a prerequisite; otherwise no release dependency.

- [ ] T036 [US2] Implement only isolated synthetic provider reservation with durable correlation/readback, pending attention after five minutes; no generic connector or real network client. Files: `backend/ipam_demo/dhcp_simulator.py`.

  Prerequisites: T035; owner: DeepSeek backend under Terra; FR-007 FR-011. Completion: Intent/observed lease/provider fixture remain separate; pending is not success.

- [ ] T037 [US2] Integrate settled synthetic DHCP API with scoped independent approval and exact fixture authority; live mode unavailable. Files: `backend/ipam_demo/app.py`, `backend/ipam_demo/models.py`.

  Prerequisites: T036; owner: Terra in Codex; FR-007 FR-009. Completion: No static-pool relabeling; explicit simulated outcome only.

- [ ] T038 [P] [US2] Render optional synthetic DHCP reservation/readback/pending states with scope/provenance and five-minute attention. Files: `frontend/src/Workflow.tsx`, `frontend/src/workflowApi.ts`.

  Prerequisites: T037; owner: DeepSeek UI under Terra; FR-007. Completion: Ticket/HTTP response alone never establishes provider result.

- [ ] T039 [P] [US3] If lead selects lowest-priority stretch, show missing-child-prefix proposal through existing safe geometry/permission path; no expansion/resize/removal/new approval engine. Files: `frontend/src/InventoryEditor.tsx`, `frontend/src/inventoryCommandsApi.ts`.

  Prerequisites: T025; owner: DeepSeek UI under Terra; FR-008. Completion: Existing child editing semantics intact; optional UI only.


## Optional Tier B review

- [ ] T040 For selected completed optional branches only, add their task IDs as prerequisites and independently assess affected Tier A/optional invariants after validation authority; lead decides integration. Files: `specs/001-postmeeting-bridge/delivery/tier-b-review.md`.

  Prerequisites: T025; owner: Luna independent verifier; FR-001 FR-003 FR-004 FR-007 FR-008 FR-016. Completion: No optional branch integrated without independent exact-SHA evidence and lead approval.

## Dependencies and execution order

Core path: T001 → T003 → T004 → T005/T006 → T007 → T008 → T009 → T011 →
T012/T013 → T014 → T015/T016 → T017/T018 → T023/T024 → T025 → T028.
Full CSV includes operator/API/gap prerequisites. T019/T020 run alongside core. T022
needs usable assessment/change contracts; final recipient values refresh at exact candidate.
FABLE-DESIGN reviews the locked design/dispatch after T001. T027 waits for T024 and T025 on the exact candidate; both calls use authorized Claude Code Fable.

Parallel examples: T005 with T006; T009 API with T010 UI on frozen C-M; T012 routes with
T013 ticket leaf; T016 aging with T015 UI; T019/T020 documents with core. Terra serializes
all its shared-file edits. UI serializes Workflow.tsx work including T033/T038/T039.
T040 must append selected completed optional branch tasks as prerequisites before execution;
its fixed T025 edge alone never authorizes premature optional acceptance.

## Incremental delivery

US1 alone is useful but not the Q099 complete bridge. Tier A requires US1/US2 and required
US3/US4 controls. Preserve 20% reserve after integration. Tier B requires explicit selection
after T025; live vendors and HA/scale are excluded outright. If Tier A cannot fit, report
partial/bridge incomplete instead of lowering the passing bar. Commit coherent changes;
push after three or earlier for interruption/handoff. Lead coordinates merges/acceptance.

Conditional schema edge: T035 adds T030 only if the allocated-release migration was selected first; its recorded predecessor/schema SHA must be accepted before any write. Otherwise DHCP independently takes the next reserved revision. T040 adds completed selected branch task IDs before review.
