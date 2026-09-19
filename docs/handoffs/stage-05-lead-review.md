# Stage 5 local acceptance review — 2026-09-19

**Accepted as a bounded local runtime checkpoint: 14 observed passes, two partial scenarios, no observed application defect.** This accepts the recorded observations and their limits. It does not accept every planned failure branch, the portable package, all questionnaire clauses or production readiness.

Persistent lead: `01a0b845-6c8d-7021-a5c9-15e673db07c9`. Existing Stage 5 owner: `01a0baff-2143-7073-ad3d-4963a9cc0ca5`, **Execute Stage 5 acceptance handoff**.

## Candidate and evidence

- Application pickup: `117d05295473cf25d362adb320e6fef26ecdd74c`; accepted application code `54f8f8168108733d40d842263218f16b33df5868`, PR #25.
- Evidence checkpoint: `278868ad17e79d7f17699a38f3b069ed4d89597f`; final report publication **`fe50cd6828016a25fee9086f499e2e865b4a16e4`**, Stage 5 branch `codex/stage-5-local-acceptance`, [PR #27](https://github.com/yugant99/IpManagement/pull/27) OPEN/draft against Stage 4. The lead read the final report and confirmed the exact pushed head; its final delta changes only the report.
- Authorization: [the user's local execution grant](stage-05-execution-authorization.md), docs commit `c4cccef8b2014c7bcb2740b9f26a683f3e9d26c6`, incorporated by worker merge `e7a84f32ab2f409493a205a7f8357d39831f8245`.
- Actual evidence: [scenario ledger](https://github.com/yugant99/IpManagement/blob/278868ad17e79d7f17699a38f3b069ed4d89597f/docs/evidence/stage-05/README.md), [observations and limits](https://github.com/yugant99/IpManagement/blob/278868ad17e79d7f17699a38f3b069ed4d89597f/docs/evidence/stage-05/observed-results.md), [compact run manifest](https://github.com/yugant99/IpManagement/blob/278868ad17e79d7f17699a38f3b069ed4d89597f/docs/evidence/stage-05/run-summary.json).
- Retained local artifact root: `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-artifacts/run-20260919-O8RVgx`. No raw databases, environments, logs or screenshots were published.
- Platform: macOS 14.5 arm64, Python 3.12.10, isolated Node 22.14.0, npm 10.9.2. Frozen dependency installation and one TypeScript/Vite UI build succeeded. Application, fixtures and dependency locks are unchanged from the pinned pickup.

## Reviewed observations

The lead directly inspected the build/startup records and compiled dashboard capture, first acquisition and replay records, response-loss proxy and browser recovery evidence, evolution/configuration results, and populated preservation scripts/results. Bounded independent reviewers inspected the completed raw-arithmetic/negative-workflow, scheduler/failure, representative legacy and primary workflow/export evidence. They reviewed existing artifacts without repeating application execution. No blocking evidence flaw was found. Minor observer labels and inferred port-error wording were clarified without rerunning successful mutations.

| Area | Accepted observed behavior |
|---|---|
| Setup and acquisition | Rendered compiled UI and ready API; empty-store setup and data-lock refusals; first cycle saves nine receipts/one run; exact retry makes no duplicate changes; altered keyed payload conflicts |
| Browser recovery | Schedule request survives navigation/reload after a controlled committed-response loss; creation and approval recover in the mounted workflow UI without duplicate allocations or audits |
| Calculations and findings | Independent raw-input arithmetic matches 58 comparisons across eight pools; scoped address reuse, real same-scope conflict and static-policy positive/unknown/healthy controls behave as recorded |
| Evolution and reports | Cycles 4/5/6 preserve anomaly/unknown/healthy transitions; cycle 7 stale sources keep calculations unavailable; old runs remain pinned; representative rendered detail and all 113 unfiltered CSV rows match saved results; stale preset revision refused |
| Scheduler and failures | Configuration/actor/version controls; controlled-time old-config race and overdue-once behavior; shared lock rejection; direct scheduler stop; one transaction fault rolls back acquisition effects and preserves a separate failure audit |
| Inventory and workflow | IPv4 create/resize and IPv6 child planning persist; overlap refused; independent approval creates one local allocation; fixed-team transfer and recipient acknowledgement preserve original finding/run evidence |
| Preservation | Disabled populated snapshot, copy advanced to cycle 8, restore over newer copy, restart and retained-key replay preserve all 15 application tables; replaced newer state is retained separately |
| Legacy | Genuine populated historical v3 backup/restore; startup refuses unsupported schema without implicit migration; explicit v4 migration preserves all original rows and adds disabled scheduling |

## Two partial scenarios and other limits

**S5-09 remains partial.** Timer-versus-ordinary-run occupancy used the real guard held by the harness, not an active ordinary reconciliation. Stop was exercised through scheduler/lifespan calls, not an OS signal during acquisition. Controlled scheduler time is not elapsed-hour endurance or an enabled-snapshot restore.

**S5-15 remains partial.** Missing/changed assets, foreign authority and altered-rich geometry were refused on fresh initial stores. Prior-success preservation under those asset refusals and a first-path-specific authority case were not exercised.

Other boundaries: v3 is the only legacy version exercised; workflow recovery does not establish reload/navigation retention; exception writes were API-driven with subsequent UI observation; preset content proof is the API-captured unfiltered/default-column CSV, while browser evidence confirms the download request. One injected rollback does not establish failure-audit-loss, filesystem/fsync/WAL/commit/crash safety. Reset, exhaustion, storage-denial, scale, HA, live discovery, real provisioning and customer migration remain unrun or outside scope.

All acceptance-owned services/proxies were stopped, harness threads joined, and browser tab closed. The worker recorded no listeners on ports 8765/8766/8767/8769/18768. Retain the synthetic stores, snapshots and evidence; no broad cleanup or process termination is needed. Some stopped harness stores intentionally retain enabled schedule configuration and are not recipient/demo startup stores.

## Integration and next ownership

Application code remains outside `main`. PRs #5/#7/#8/#10/#18/#19/#25/#27 remain open despite accepted inherited dependencies. Component merges into Stage 3/4 remain distinct from main integration. This review performs no application PR merge. PR #9 remains NO MERGE.

Spencer retains Part 6 packaging, read-only feed mounting, persistent data integration and recipient/operator handoff. No package checkpoint or target-host result is registered; `PART6_READY=no`. Local tests do not establish Docker/Compose/Linux or recipient portability. Existing core, Stage 3, Stage 4 and data tasks retain their defect ownership; there is no application fix to route from this run.

The denominator remains **111**. The updated worker ledger links observed evidence to 51 unique candidate rows, with overlapping IDs deduplicated; this is not 51 fully satisfied requirements. The earlier preparation mapping included 089, which is not in the final worker mapping; do not silently retain that credit. Final per-row demonstrated/partial/documentary/missing adjudication remains a lead deliverable. There is no 60%-complete claim from these 16 scenarios. RFP-043 remains deferred; synthetic scheduling and fixed-team handoff now have actual bounded runtime evidence for 068/081.

The source DOCX also remains in scope: [phase coverage and gaps](../PHASE_COVERAGE.md) maps these observations to its assessment and transformation sections. Engineering Stage 5 is not customer Phase 1/2 completion. The validated customer assessment report, live integrations, full lifecycle/reclamation, customer migration, adopted governance, training and production transition remain outstanding and must appear alongside final questionnaire accounting.

Next: lead integration and row-level evidence accounting; Spencer publishes the package checkpoint for its separate portable-delivery review. Keep the existing Stage 5 task for scoped evidence follow-ups. No new Stage 6 implementation task or repeated full run is required.
