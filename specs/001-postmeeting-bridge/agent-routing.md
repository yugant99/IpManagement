# Agent routing and task-level handoff

> Current dispatch update, 2026-09-22: Terra uses native Codex gpt-5.6-terra; Astra
> remains the lead. Grok4.6 T002 has executed through OpenCode Go and Grok4.7 is reviewing
> its exact result. Fable has supplied one Claude Code design advisory; future substantial
> advice is supplied as a user-run prompt, not repeated autonomous invocation. The original
> specification-only statements below are retained phase history. Current grants, actual
> invocations and leases are in delivery/authorization-and-ownership.md and dispatch-manifest.md.

Routing requested by the user; no external model availability verified or paid model invoked.
The actual specification agents were local architecture collaborators, not impersonated
Grok/Terra/DeepSeek/Fable executions. This annex is future routing, not dispatch.

## Hierarchy and capacity

- Level 0: Astra / Main Lead 4.0, task 01a0cade-506f-7442-97da-0cc09b4f9929.
- Level 1a: Grok 4.7 requirements/integration sublead; one Grok 4.6 research/documentation scout.
- Level 1b: Terra in Codex implementation sublead; at most two leaves: DeepSeek backend
  and DeepSeek UI. Sol replaces a blocked leaf; it is never an extra concurrent worker.
- Level 1c: Luna independent verification/evidence sublead; Spencer occupies one coordinated
  operator lane. A second independent verifier slot may be used only if lead assigns a
  disjoint verification task; no default fixer role and no extra delegation level.
- Fable: bounded direct advisory call to the lead, no workers/authority; schedule without
  creating a fourth sublead. If platform concurrency is lower, queue work to its real limit.

At most three subleads, two workers each, two levels below the lead. Spencer remains human
operator owner, not a model spawn or core-schema agent. Main Lead owns final decisions,
shared-contract adoption, PR merge coordination and canonical status/row adjudication.
No worker modifies another checkout or assigns itself global completion. Use isolated
codex/ feature worktrees for later workers; each receives only assigned files/contracts.

## Dispatch contract (applies to every row)

Before spawn: explicit implementation authority, prerequisites accepted, exact base SHA,
contracts frozen, file lease free, owner/model available. No model substitution is silently
accepted; a missing external provider remains a routing gate. No paid calls in this task.
Validation additionally needs explicit permission. For Tier B, T025 must pass and lead must
select exact optional tasks while preserving reserve. Fable and human outcomes stay pending
until actual authorized participation, or explicit lead waiver where allowed.

Each row in task-graph.csv is the full machine-readable assignment: requirements, dependency,
owner, owned files, contracts, spawn condition, observable completion, evidence, non-claims,
escalation and exact handoff format. The table below maps every task to that same contract.
Runtime evidence always includes SHA, schema/config/target, source identities, sanitized
success/refusal/retry/unknown observations and limits. Documentary source review remains
labeled documentary. No step self-promotes a row or claims production/real vendor behavior.

Escalate immediately for authority/history/contract contradiction or overlapping ownership;
otherwise at 45 minutes without a defensible resolution path. Terra sends exact SHA/files,
failure evidence, attempted approaches and needed decision; Sol replaces the blocked leaf.
Grok 4.7 checks interface/schema impact; Main Lead alone changes shared scope. Luna reports
failures to the author rather than becoming the default fixer. Rerun only affected gates
when later authorized, never convert old candidate evidence to new evidence.

## Task-level routing

| Task / tier | Owner | Prerequisites | Requirements / contract | Owned files | Completion/evidence gate |
|---|---|---|---|---|---|
| T001 / A | Astra / Main Lead 4.0 | Lead authority | FR-001 FR-005 FR-015 FR-021; C-A C-M C-L C-T C-O | `specs/001-postmeeting-bridge/delivery/authorization-and-ownership.md` | Explicit lead decision before dispatch; no inferred execution permission. Exact-candidate evidence required. |
| T002 / A | Grok 4.6 under Grok 4.7 | T001 | FR-009 FR-010 FR-012 FR-014 FR-018 FR-020; C-M C-T C-O | `specs/001-postmeeting-bridge/delivery/source-authority.md` | Every gap has a requirement, owner role and evidence gate. Exact-candidate evidence required. |
| T003 / A | Terra in Codex | T001 | FR-002 FR-003 FR-004 FR-005 FR-016; data-model.md C-M C-L C-T | `backend/ipam_demo/schema.sql`<br>`backend/ipam_demo/schema_v6.sql`<br>`backend/ipam_demo/store.py`<br>`backend/ipam_demo/seed.py` | Explicit recognized upgrade and fresh initialization; no destructive reseed or history loss. Exact-candidate evidence required. |
| T004 / A | Terra in Codex | T003 | FR-005 FR-015; C-A | `backend/ipam_demo/access.py`<br>`backend/ipam_demo/models.py` | Default-deny trusted context, fail-closed invalid authority and stopped/reload revocation. Exact-candidate evidence required. |
| T005 / A | Terra in Codex | T004 | FR-005 FR-009 FR-013 FR-015 FR-019; C-A | `backend/ipam_demo/app.py`<br>`backend/ipam_demo/inventory.py`<br>`backend/ipam_demo/reports.py`<br>`backend/ipam_demo/imports.py`<br>`backend/ipam_demo/source_catalog.py`<br>`backend/ipam_demo/scheduler.py`<br>`backend/ipam_demo/workflow.py`<br>`backend/ipam_demo/feed_adapter.py`<br>`backend/ipam_demo/inventory_commands.py` | Every route has allow/deny/projection classification and no global data leak. Exact-candidate evidence required. |
| T006 / A | DeepSeek UI under Terra | T004 | FR-005 FR-009 FR-015 FR-019; C-A | `frontend/src/api.ts`<br>`frontend/src/firstPathApi.ts`<br>`frontend/src/workflowApi.ts`<br>`frontend/src/inventoryCommandsApi.ts`<br>`frontend/src/correctionApi.ts`<br>`frontend/src/scheduleApi.ts`<br>`frontend/src/App.tsx`<br>`frontend/src/FirstPath.tsx`<br>`frontend/src/Schedule.tsx`<br>`frontend/src/CapacityReports.tsx`<br>`frontend/src/Corrections.tsx`<br>`frontend/src/InventoryEditor.tsx`<br>`frontend/src/Workflow.tsx` | No token in URL/localStorage/logs; browser uses trusted context everywhere. Exact-candidate evidence required. |
| T007 / A | Luna independent verifier | T005 T006 | FR-005 FR-015 FR-019; C-A | `specs/001-postmeeting-bridge/delivery/access-review.md` | No unresolved source/design access findings; runtime still requires T025. Exact-candidate evidence required. |
| T008 / A | DeepSeek backend under Terra | T007 | FR-002 FR-014; C-M | `backend/ipam_demo/migration_compare.py` | Exactly one class per accepted row; partial/conflicted/stale cannot sign; active state unchanged. Exact-candidate evidence required. |
| T009 / A | Terra in Codex | T008 | FR-002 FR-005 FR-009; C-A C-M | `backend/ipam_demo/app.py`<br>`backend/ipam_demo/models.py` | Only independent exact-current assessment sign-off; no cutover endpoint. Exact-candidate evidence required. |
| T010 / A | DeepSeek UI under Terra | T008 T006 | FR-002 FR-019; C-A C-M | `frontend/src/MigrationCompare.tsx`<br>`frontend/src/FirstPath.tsx`<br>`frontend/src/firstPathApi.ts`<br>`frontend/src/App.tsx` | Usable assessment against T009; visible complete accounting and immutable provenance. Exact-candidate evidence required. |
| T011 / A | DeepSeek backend under Terra | T009 | FR-003 FR-014; C-A C-L | `backend/ipam_demo/lifecycle.py`<br>`backend/ipam_demo/workflow.py` | No double hold, substitution, self-approval or free-on-expiry; local cancellation distinct from reclaim. Exact-candidate evidence required. |
| T012 / A | Terra in Codex | T011 | FR-003 FR-005 FR-009; C-A C-L | `backend/ipam_demo/app.py`<br>`backend/ipam_demo/models.py` | Exact versions and supported authority checked; unsupported pool/family/action refused. Exact-candidate evidence required. |
| T013 / A | DeepSeek backend under Terra | T011 | FR-004 FR-009 FR-011; C-A C-T | `backend/ipam_demo/ticket_handoff.py`<br>`backend/ipam_demo/workflow.py` | Effect-committed/response-lost recovers via same correlation; no duplicate or budget reset. Exact-candidate evidence required. |
| T014 / A | Terra in Codex | T012 T013 | FR-004 FR-005 FR-009 FR-011; C-A C-T | `backend/ipam_demo/app.py`<br>`backend/ipam_demo/models.py` | Unknown never success; no ticket approval grants local authority; old requests not tracked. Exact-candidate evidence required. |
| T015 / A | DeepSeek UI under Terra | T010 T014 | FR-003 FR-004 FR-019; C-A C-L C-T | `frontend/src/Workflow.tsx`<br>`frontend/src/workflowApi.ts` | Complete allocation and unused release path; downstream failure preserves visible local state. Exact-candidate evidence required. |
| T016 / A | DeepSeek backend under Terra | T013 | FR-003 FR-006 FR-008; C-L | `backend/ipam_demo/lifecycle.py`<br>`backend/ipam_demo/workflow.py` | One due episode, ack not clearance, no forged finding IDs or saved-run rewriting. Exact-candidate evidence required. |
| T017 / A | Terra in Codex | T014 T016 | FR-003 FR-006 FR-008; C-A C-L | `backend/ipam_demo/app.py`<br>`backend/ipam_demo/models.py` | All new reads/actions scoped and authority bounded. Exact-candidate evidence required. |
| T018 / A | DeepSeek UI under Terra | T015 T017 | FR-006 FR-008 FR-013 FR-019; C-A C-L | `frontend/src/Workflow.tsx`<br>`frontend/src/CapacityReports.tsx`<br>`frontend/src/workflowApi.ts` | No invented IPv6 delegation, hijack attribution or health monitoring; same metric identity across views. Exact-candidate evidence required. |
| T019 / A-documentary | Grok 4.6 under Grok 4.7 | T002 | FR-010 FR-012 FR-014 FR-016 FR-017 FR-018 FR-020 FR-022; C-O qualification.md | `specs/001-postmeeting-bridge/delivery/gaps-and-qualification.md` | Each exclusion has owner/evidence boundary/future gate; numeric cohorts are assumptions, not source requirement replacements. Exact-candidate evidence required. |
| T020 / A | Spencer under Luna coordination | T002 | FR-004 FR-007 FR-009 FR-010 FR-011 FR-012 FR-021; C-A C-M C-L C-T C-O | `specs/001-postmeeting-bridge/delivery/integration-matrix.md` | All integration clauses classified; no guessed endpoint or simulated-as-live entry. Exact-candidate evidence required. |
| T021 / A | Grok 4.7 requirements/integration sublead | T009 T014 T017 T020 | FR-009 FR-015 FR-019; C-A C-M C-L C-T | `specs/001-postmeeting-bridge/delivery/offline-api.md` | Source-accurate examples distinguish illustrative from observed; no secret/vendor invention. Exact-candidate evidence required. |
| T022 / A | Spencer under Luna coordination | T010 T015 T020 | FR-002 FR-014 FR-021; C-M C-O | `specs/001-postmeeting-bridge/delivery/recipient-validation.md`<br>`specs/001-postmeeting-bridge/delivery/configuration-example.json` | One Linux amd64 target declared or explicitly unavailable; no fabricated signoff/cutover. Exact-candidate evidence required. |
| T023 / A | Terra in Codex | T003 T017 | FR-005 FR-016 FR-021; C-A C-O | `backend/ipam_demo/state_ops.py`<br>`backend/ipam_demo/__main__.py` | Supported history survives recognized state operations; code/UI/config/secrets not assumed in snapshots. Exact-candidate evidence required. |
| T024 / A | Spencer under Luna coordination | T021 T022 T023 | FR-009 FR-016 FR-020 FR-021; C-A C-O | `scripts/ops/acquire.sh`<br>`scripts/ops/health.sh`<br>`scripts/ops/README.md`<br>`specs/001-postmeeting-bridge/delivery/operator-handoff.md`<br>`Dockerfile`<br>`compose.yaml` | Wrappers/docs match core auth contract; no token args/logging; no universal portability/license-clearance claim. Exact-candidate evidence required. |
| T025 / A | Luna independent verifier | T018 T019 T021 T022 T023 T024 | FR-001 FR-002 FR-003 FR-004 FR-005 FR-006 FR-008 FR-009 FR-013 FR-015 FR-016 FR-019 FR-021; All contracts quickstart.md | `specs/001-postmeeting-bridge/delivery/independent-evidence.md` | Every Tier A criterion has independent evidence or blocker; no reduced passing bar. Exact-candidate evidence required. |
| T026 / A-human-gate | Spencer under Luna coordination | T025 | FR-020 FR-021; C-O | `specs/001-postmeeting-bridge/delivery/human-rehearsal.md` | Human-handoff claim only with actual acknowledgement; agent reproduction not substitute. Exact-candidate evidence required. |
| T027 / A-advisory-gate | Fable via Claude Code CLI | T024 T025 | FR-001 FR-002 FR-003 FR-004 FR-005 FR-009 FR-016 FR-021; All contracts | `specs/001-postmeeting-bridge/delivery/fable-advisory.md` | Actual advice or explicit lead waiver before acceptance; Fable has no acceptance authority. Exact-candidate evidence required. |
| T028 / A | Astra / Main Lead 4.0 | T025 T026 T027 | FR-001 FR-020 FR-021; All contracts | `specs/001-postmeeting-bridge/delivery/lead-adjudication.md`<br>`docs/STATUS.md`<br>`docs/QUESTIONNAIRE_ROW_MAP.md` | Lead alone changes canonical ledger/status; no hidden external gate or92-completed claim. Exact-candidate evidence required. |
| T029 / B | Grok 4.7 requirements/integration sublead | T025 | FR-003 FR-004; C-L | `specs/001-postmeeting-bridge/delivery/tier-b-release-contract.md` | Accepted contract before optional code; no referenced allocation deletion. Exact-candidate evidence required. |
| T030 / B | Terra in Codex | T029 | FR-003 FR-004 FR-016; C-L tier-b-release-contract | `backend/ipam_demo/schema_v7.sql`<br>`backend/ipam_demo/schema.sql`<br>`backend/ipam_demo/store.py`<br>`backend/ipam_demo/inventory.py`<br>`backend/ipam_demo/reports.py`<br>`backend/ipam_demo/state_ops.py` | Historical requests remain valid; active uniqueness correct before reuse executable. Exact-candidate evidence required. |
| T031 / B | DeepSeek backend under Terra | T030 | FR-003 FR-004; C-L tier-b-release-contract | `backend/ipam_demo/lifecycle.py`<br>`backend/ipam_demo/workflow.py` | Before/after lineage and retry/refusal preserved; no contradictory/pending external effect. Exact-candidate evidence required. |
| T032 / B | Terra in Codex | T031 | FR-003 FR-004 FR-009; C-A C-L | `backend/ipam_demo/app.py`<br>`backend/ipam_demo/models.py` | No unchecked admin bypass, network side effect or stale reuse. Exact-candidate evidence required. |
| T033 / B | DeepSeek UI under Terra | T032 | FR-003 FR-004; C-A C-L | `frontend/src/Workflow.tsx`<br>`frontend/src/workflowApi.ts` | Tier A remains intact; no subscriber provisioning claim. Exact-candidate evidence required. |
| T034 / B | Grok 4.7 requirements/integration sublead | T025 | FR-007 FR-009; C-A C-T | `specs/001-postmeeting-bridge/delivery/tier-b-dhcp-contract.md` | Optional operation selected by lead; provider fixture distinct from local-static authority. Exact-candidate evidence required. |
| T035 / B | Terra in Codex | T034 | FR-007 FR-011 FR-016; tier-b-dhcp-contract C-O | `backend/ipam_demo/schema_v7.sql`<br>`backend/ipam_demo/schema_v8.sql`<br>`backend/ipam_demo/schema.sql`<br>`backend/ipam_demo/store.py`<br>`backend/ipam_demo/seed.py`<br>`backend/ipam_demo/state_ops.py` | Explicit recognized migration/fresh initialization and recovery contract complete before leaf. If release is selected first, add T030 as a prerequisite; otherwise no release dependency. Exact-candidate evidence required. |
| T036 / B | DeepSeek backend under Terra | T035 | FR-007 FR-011; tier-b-dhcp-contract | `backend/ipam_demo/dhcp_simulator.py` | Intent/observed lease/provider fixture remain separate; pending is not success. Exact-candidate evidence required. |
| T037 / B | Terra in Codex | T036 | FR-007 FR-009; C-A tier-b-dhcp-contract | `backend/ipam_demo/app.py`<br>`backend/ipam_demo/models.py` | No static-pool relabeling; explicit simulated outcome only. Exact-candidate evidence required. |
| T038 / B | DeepSeek UI under Terra | T037 | FR-007; tier-b-dhcp-contract | `frontend/src/Workflow.tsx`<br>`frontend/src/workflowApi.ts` | Ticket/HTTP response alone never establishes provider result. Exact-candidate evidence required. |
| T039 / B | DeepSeek UI under Terra | T025 | FR-008; C-A C-L | `frontend/src/InventoryEditor.tsx`<br>`frontend/src/inventoryCommandsApi.ts` | Existing child editing semantics intact; optional UI only. Exact-candidate evidence required. |
| T040 / B | Luna independent verifier | T025 | FR-001 FR-003 FR-004 FR-007 FR-008 FR-016; All selected contracts | `specs/001-postmeeting-bridge/delivery/tier-b-review.md` | No optional branch integrated without independent exact-SHA evidence and lead approval. Exact-candidate evidence required. |

## Handoff payload for every task

> READY FOR PROJECT-LEAD REVIEW — Stage N (lead supplies the actual stage).
> Task IDs and FR/RFP rows; base and final SHA/PR; owned files/contracts and scope;
> actual evidence with mode/target/revision; unrun checks and remaining gates;
> findings/escalations and bounded recommended next action; copyable next prompt.

Lead-only final prompt begins START A NEW IMPLEMENTATION CHAT. A worker does not issue it
as acceptance or rotate project ownership. This specification report instead uses
READY FOR PROJECT-LEAD REVIEW — SPECIFICATION.

## Shared-file leases

Terra alone owns app.py/models.py/access.py and schema/store/state integration across T003–T023.
The backend leaf receives workflow.py only after T005 ends, then serializes T011/T013/T016.
UI owns api.ts and App.tsx through T006/T010, then serializes Workflow/client work T015/T018.
Spencer Dockerfile/Compose and scripts/ops ownership starts only after T023 core contract; Terra does not edit those
packaging files/wrappers concurrently. Grok/Spencer evidence files are distinct. Global STATUS/ROW_MAP are
reserved to Main Lead at T028. Optional shared-file tasks queue behind all accepted Tier A
work and each other; the DAG does not override a lease.

## Main Lead 4.0 route and review amendment
The 2026-09-22 user clarifies Fable runs in Claude Code CLI and Sol in Codex.
Implementation routes remain OpenCode, with exact configured IDs verified before invocation.
See delivery/model-routes.md for observations and unresolved route mismatch. No silent
model/provider substitution. FABLE-DESIGN runs after spec/dispatch lock; T027 is a separate
final advisory after T024/T025 and cannot be completed by the earlier design review.
The T006 UI lease includes correction/inventory/workflow actor state and context-scoped
retry recovery. T005 includes inventory_commands.py for bounded correction authorization.
