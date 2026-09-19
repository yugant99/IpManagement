# Stage 5 local acceptance ledger

**Authorized local execution completed; scoped evidence awaits project-lead review.** Date: 2026-09-19. Worker task `01a0baff-2143-7073-ad3d-4963a9cc0ca5`; persistent lead `01a0b845-6c8d-7021-a5c9-15e673db07c9`. This is runtime evidence for a synthetic local candidate, not portable acceptance or questionnaire credit.

Read [observed results](observed-results.md) for actual outcomes and limits, [run summary](run-summary.json) for compact identities/hashes, and [Stage 5 report](../../handoffs/stage-05-report.md) for the maintenance handoff. [Prepared steps](acceptance-steps.md) retain the original procedure; expected values there are not evidence.

## Candidate and execution authority

| Item | Recorded fact |
|---|---|
| Accepted application code | `54f8f8168108733d40d842263218f16b33df5868` |
| Exact application pickup | `117d05295473cf25d362adb320e6fef26ecdd74c`; PR #25 against Stage 3 |
| Acceptance checkout / branch | `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5`, `codex/stage-5-local-acceptance`, draft PR #27 |
| Earlier preparation | `d7e062179aa75cc5cafd732746c120e9c44e0041`, report `46c225defea8c933363354fe2d5bb6492ee67073`, accepted disabled-snapshot correction `7e37dde6ba18a08717b0ce56c4438522fc5f7008` |
| Authorization | User told lead **“lets go man tun the tests man”** on 2026-09-19; [published scope](../../handoffs/stage-05-execution-authorization.md) at `c4cccef8b2014c7bcb2740b9f26a683f3e9d26c6` |
| Authorization incorporation | History-preserving documentation merge `e7a84f32ab2f409493a205a7f8357d39831f8245` |
| Runtime | macOS 14.5/arm64, Python 3.12.10, uv 0.7.13, isolated Node 22.14.0, npm 10.9.2 |
| Source changes | No application, fixture, dependency-lock or shared-contract changes; no accepted candidate substitution |

The grant covers the 16 prepared scenarios, pinned installation/build, disposable localhost services/browser/API, derived synthetic controls, direct database comparisons, bounded controlled time/concurrency/fault/response loss, stopped backup/restore and representative recognized legacy migration. No renewed per-scenario permission was needed. Cloud/VM/Docker/deployment/spending/public exposure, existing user databases, unrelated processes, reset and exhaustive matrices remain excluded.

## Actual retained artifacts

Root: **`/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-artifacts/run-20260919-O8RVgx`**. Paths below are relative to it; data is disposable synthetic acceptance material and remains on disk.

| Path | Purpose |
|---|---|
| `rich-scheduler/` | Primary disabled, populated schema-v4 store at cycle 7; only nine pinned authorities |
| `primary/` | Exact HTTP/proxy payloads, table snapshots, observer scripts, summaries and browser captures |
| `source-control/` | Separate baseline arithmetic, derived invalid/static-DHCP inputs, negative workflow controls and stopped store |
| `scheduler-harness/` | Isolated controlled clock/concurrency/rollback/asset copies; all threads stopped; `contention-stop` intentionally retains enabled config in its stopped store |
| `setup-control/` | Empty-startup/repeated-seed control; service stopped |
| `legacy/` | Historical v3 archive/provenance, populated v3 source/snapshot, restored migrated v4 and semantic comparisons |
| `state-operations/`, `snapshots/`, `preservation/` | Primary populated snapshot, restored disposable copy, preserved newer state and S5-14 command/comparison records |
| `environment/`, `uv-cache/`, `node-runtime/`, `npm-cache/` | Isolated pinned dependencies/tool/cache artifacts |
| `logs/` | Install/build/primary CLI/proxy and observer outputs, including retained observer errors |

Compiled output is `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5/frontend/dist`; ignored dependencies live in that checkout's `frontend/node_modules`. Immutable source input is `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5/fixtures/v1`. Measured input hashes are in `primary/environment-inputs.json` and scheduler/source-control metadata. Nine feed hashes matched adapter pins. No expected-outcome manifest drove application detection or independent arithmetic. No raw database, environment, log or screenshot is committed.

## Scenario status

**14 OBSERVED_PASS, 2 PARTIAL, 0 OBSERVED_FAIL.** All 16 IDs were exercised. A pass is limited to the explicitly bounded observation; it is not exhaustive coverage. S5-09 and S5-15 retain material gaps from the prepared wording.

| ID | Actual observation / limit | Status | Artifact entry point | Defect owner |
|---|---|---|---|---|
| S5-01 | Frozen dependency install; one UI build; rich seed; ready API and rendered compiled UI | OBSERVED_PASS | `logs/`, `primary/ready.json`, `seeded-ui.*` | Foundation/core |
| S5-02 | Setup 503/UI; stopped repeated-seed and active seed/backup lock refusals | OBSERVED_PASS | `primary/setup-*.json`, `active-lock-*` | Core |
| S5-03 | First manual cycle at 06:00 scenario time; nine receipts, one run/operation | OBSERVED_PASS | `primary/cycle1-summary.json` | Stage 4 |
| S5-04 | Exact replay, changed-keyed-payload conflict; actual browser retry through navigation/reload | OBSERVED_PASS | `primary/browser-recovery-summary.json` | Stage 4 |
| S5-05 | Healthy/anomaly/unknown, scoped reuse/conflict and static-DHCP positive/silence controls | OBSERVED_PASS | `source-control/observations.json` | Stage 3/data |
| S5-06 | Independent arithmetic; pinned run/detail/export; representative rendered parity; preset CSV/revision guard | OBSERVED_PASS | `source-control/independent-arithmetic.json`, `primary/preset-summary.json` | Stage 3/data |
| S5-07 | North cycle 4 anomaly→5 unknown→6 healthy; Central cycle 7 complete acquisition but stale calculations | OBSERVED_PASS | `primary/evolution-summary.json` | Stage 4/Stage 3/data |
| S5-08 | Save/interval/disable/re-enable/manual due; stale version and forbidden actor | OBSERVED_PASS | `primary/evolution.py`, config HTTP records | Stage 4 |
| S5-09 | Controlled contention/config race/overdue-once/direct stop pass; timer's ordinary occupancy is harness-held guard; OS-signal-in-flight unrun | PARTIAL | `scheduler-harness/REPORT.md` | Stage 4 |
| S5-10 | One post-run/queue injected fault rolled back all acquisition effects; one failure audit; retry succeeds | OBSERVED_PASS | `scheduler-harness/observations.json` | Stage 4 |
| S5-11 | IPv4 create/resize, IPv6 preview/create, metadata and overlap guard; rendered search | OBSERVED_PASS | `primary/inventory-summary.json` | Stage 3 |
| S5-12 | Request/independent approval/allocation; four negative guards; browser creation/decision replay in mounted UI | OBSERVED_PASS | `primary/workflow-recovery-summary.json`, source-control records | Stage 3 |
| S5-13 | API transfer/recipient acknowledgement and audit; subsequent UI state; saved finding/run unchanged | OBSERVED_PASS | `primary/exception-summary.json` | Stage 3 |
| S5-14 | Disabled populated snapshot; copy advancement; restore/restart/table equality and retained-key replay | OBSERVED_PASS | `preservation/` | Core/Stage 4 |
| S5-15 | Invalid rows, foreign authority, missing/changed asset, altered rich geometry refused; asset cases only fresh initial state | PARTIAL | source-control and scheduler reports | Stage 4/data/core |
| S5-16 | Genuine populated v3 backup/restore, refused pre-migration startup, explicit v4 migration and preservation | OBSERVED_PASS — v3 only | `legacy/README.md` | Core |

Unrun: reset; v1/v2; enabled-snapshot backup/restore; active ordinary reconciliation versus due timer; OS signal during acquisition; first-path-specific refusal; prior-success preservation under asset refusal; unavailable-asset committed replay; cycle-1460/exhaustive cycles; failure-audit loss; deeper commit/filesystem/WAL/fsync/crash; browser storage denial; endurance/scale/HA; Docker/Compose/Linux/recipient startup. No broad suite or extra build was run.

## Candidate questionnaire links — lead assigns credit

Denominator **111**. No questionnaire row, global status or accepted total was changed by this worker.

| Scenarios | Candidate IDs | Evidence boundary |
|---|---|---|
| S5-01/02 | 007, 010, 012, 013, 022 | Local compiled UI/API/readiness; no production alert transport or HA |
| S5-03/04/07/08/09/10 | 033, 034, 037, 061, 063, 068, 069, 071 | Actual synthetic acquisition and controlled timer evidence; no real interval endurance, live discovery or fleet |
| S5-05/06 | 029, 062–066, 069, 071, 073–077 | Independent scoped/time-bound lease arithmetic; no traffic or reclaim claim |
| S5-06/11 | 006, 031 | Rendered search for created metadata plus one preset; versioned inventory/source fields. No arbitrary report designer/organization rollout |
| S5-03/15 | 036, 087 | Nine known source identities and canonical receipt counts/provenance; catalog UI separately unobserved, no automatic real-system discovery or arbitrary customer migration |
| S5-11 | 002, 003, 026–028, 030, 035, 084, 085, 095 | Prefix arithmetic/versioned metadata; no IPv6 subscriber allocation/tenant security |
| S5-12 | 001, 004, 005, 009, 053, 054, 059, 060, 078, 080, 084, 085 | Fixed demo actors; real local allocation/audit; external provisioning simulated; no SSO/release/reclaim |
| S5-13 | 072, 081, 082 | Observed fixed-team owner transfer and recipient acknowledgement; no external tickets/paging |
| S5-14/16 | 018 | Local whole-store preservation and recognized v3 schema migration; no customer migration or measured DR/RPO/RTO |
| Later Spencer/lead | 090, 091, 092, 104, 106 | Package, target recipient operation/training/transfer and dependency disclosure remain separate |

RFP-043 general import callback remains deferred; explicit ordinary imports did not automatically reconcile. PR #9 remains **NO MERGE**. Spencer's package checkpoint remains missing in the governing handoff (`PART6_READY=no`); local success does not substitute for its portable-delivery gate. The lead owns final review, acceptance and integration.
