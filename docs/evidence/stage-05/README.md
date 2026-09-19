# Stage 5 local acceptance ledger

**Preparation only — no application scenario has been executed.** Date: 2026-09-19. Owner: task `01a0baff-2143-7073-ad3d-4963a9cc0ca5`. This ledger records pending observations against a pinned candidate, not accepted questionnaire coverage.

## Candidate and authority

| Item | Recorded source/Git fact |
|---|---|
| Accepted application code | `54f8f8168108733d40d842263218f16b33df5868` |
| Exact pickup publication | `117d05295473cf25d362adb320e6fef26ecdd74c`; PR #25 OPEN/draft against Stage 3 when inspected |
| Acceptance checkout | `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5` |
| Acceptance branch | `codex/stage-5-local-acceptance`, created at the exact pickup |
| Published lead documents | Main `07013a9f949863e2addae527901ed3f84c8e6000`, incorporated by merge `95f370713ecd2d983d76c15f9326cd9facac91b1` |
| Application delta at preparation | None; inherited merge changes only STATUS, CURRENT_HANDOFF, Stage 4 lead review and Stage 5 kickoff |
| Execution authorization | **Pending**, per lead `docs/STATUS.md` and `docs/handoffs/stage-05-kickoff.md` at main `07013a9` |
| Runtime/platform/dependency versions | Not inspected by execution; installed availability remains unknown |
| Service/port/database/run/operation IDs | None created by this task; no port bound |

The user supplied the approved preparation handoff. Its explicit gate is: “this handoff authorizes source/evidence preparation only until an explicit local execution decision is recorded.” The data-owner task already holds the pending question. Do not repeat it. No affirmative execution scope was present in the inspected lead permission record. Recent lead/data task reads returned empty turn items, so they did not establish any additional permission.

Before execution, append the actual affirmative user wording, originating task/turn, publication of the lead permission record, date and precise allowed operations. Record exclusions separately. A completion message, task title, elapsed time or this checklist cannot supply permission.

## Artifact separation

The following **proposed absolute paths have not been created**. At execution, create a fresh session directory without reusing an existing path and record its actual name. All children below are relative to proposed root `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-artifacts/acceptance-01`.

| Child / path | Purpose and boundary |
|---|---|
| `rich-scheduler/` | Primary rich store; only nine pinned source authorities; use manual acquisition to reach cycles 1–7 |
| `source-control/` | Separate rich store for invalid/competing-source and workflow contradiction inputs; never copy its evidence into the scheduler store |
| `state-operations/` | Store restored from a stopped, populated snapshot; mutations and restore comparison happen here |
| `setup-control/` | Disposable uninitialized store for setup/readiness refusal observations |
| `harness/`, `legacy/` | Only create if the recorded scope separately covers controlled clock/fault work or legacy fixture creation/migration |
| `snapshots/`, `logs/`, `browser/`, `requests/`, `observations/` | Whole-store snapshots, raw command/HTTP output, screenshots, exact retry payloads, and semantic before/after records; retained locally |
| `environment/` | If approved/needed, isolated Python environment and dependency caches |
| Candidate `frontend/node_modules/`, `frontend/dist/` | Ignored generated dependency/build output in this isolated checkout, outside tracked source |
| `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5/frontend/dist` | Planned `IPAM_STATIC_DIR`, not built |
| `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5/fixtures/v1` | Immutable `IPAM_SYNTHETIC_FEED_DIR`; rich seed is explicit `inventory.json` within it |

No databases, environments, installed dependencies, compiled output, raw logs or screenshots currently exist as artifacts of this task. No acceptance-owned service needs stopping. Retain later artifacts and stop only the service/process this task starts; no broad cleanup or unrelated process inspection/termination.

## Input identity

These are **Git blob IDs read from `117d052`**, not newly measured filesystem SHA-256 values or runtime validation:

| File | Git blob |
|---|---|
| `fixtures/v1/inventory.json` | `c8c8093177ebee70768274b80b55d988148f4f66` |
| `backend/ipam_demo/feed_adapter.py` | `e7f137a4c0dd517f56f584acfc9fabefc5a09e8d` |
| `uv.lock` | `56671dad30939e0e1df3fdf0e44105316f15a3d1` |
| `frontend/package-lock.json` | `dbbecd811d7145e89f80aac002e17f870b5ecde6` |
| `pyproject.toml` | `931397380ed4f4cfa46e1c7737b0bcb5706faad8` |
| `frontend/package.json` | `f0c279228c2c07074ba37ce3d9a11a097f297cdc` |

The exact nine source asset names and expected byte SHA-256 values are pinned in [`feed_adapter.py`](../../../backend/ipam_demo/feed_adapter.py), `_ASSETS`. At authorized execution, record measured input hashes with absolute paths and compare to those pins. Do not treat `pack.json` or expected-answer labels as runtime inputs; expected manifests are comparison-only. Source pins do not establish that installation packaged or loaded the assets.

## Scenario status

Status vocabulary: `PENDING_PERMISSION`, `NOT_RUN`, `OBSERVED_PASS`, `OBSERVED_FAIL`, `PARTIAL`. No row below has observed output; all runtime ID/time/evidence fields are **not generated**. A group is not a pass until each claimed observation has its own evidence. Procedures are in [acceptance-steps.md](acceptance-steps.md).

| ID | Required observation | Store | Current status / additional gate | Defect owner |
|---|---|---|---|---|
| S5-01 | Locked install if needed; one frontend build; explicit rich setup; ready API and rendered compiled UI | setup-control, rich-scheduler | PENDING_PERMISSION | Foundation/core; build owner through lead |
| S5-02 | Uninitialized setup state; repeated seed refusal; active-data-lock refusal | setup-control, rich-scheduler | PENDING_PERMISSION | Core |
| S5-03 | First manual cycle: index 1, nine receipts, one run/operation, scenario `2026-09-01T06:00:00.000Z` | rich-scheduler | PENDING_PERMISSION | Stage 4 |
| S5-04 | Exact retry has no new effects; changed payload conflicts; UI recovery retains exact key/payload through navigation/reload | rich-scheduler | PENDING_PERMISSION; response-loss manipulation only if covered | Stage 4 |
| S5-05 | Representative healthy/anomaly/unknown; cross-scope reuse and static DHCP discrepancy | rich-scheduler, source-control | PENDING_PERMISSION | Stage 3/data |
| S5-06 | Independent fixture arithmetic; saved run detail/export and older-run agreement; preset export | source-control baseline, rich-scheduler evolution | PENDING_PERMISSION | Stage 3/data |
| S5-07 | Phase 5 incomplete North routing; phase 7 stale Central evidence; intermediate/restoration results retained | rich-scheduler | PENDING_PERMISSION | Stage 4, Stage 3/data |
| S5-08 | Schedule save/disable/re-enable, interval and stale/actor controls | rich-scheduler | PENDING_PERMISSION | Stage 4 |
| S5-09 | Timer/manual/ordinary-run contention; old six-hour failure versus new one-hour configuration; overdue restart once; clean stop | separate harness copy | PENDING_PERMISSION; controlled time/concurrency harness separately scoped | Stage 4 |
| S5-10 | Controlled failed cycle rolls back clock/import/run/queue/cursor/replay; separate failure audit outcome | separate harness copy | PENDING_PERMISSION; fault injection separately scoped | Stage 4 |
| S5-11 | IPv4/IPv6 child planning/persistence and safe edit; overlap refusal | rich-scheduler after calculations; new children only | PENDING_PERMISSION | Stage 3 |
| S5-12 | Request/review/allocation; current DHCP contradiction; stale/self-approval refusal; ambiguous retry | rich-scheduler for success; source-control for contradictions | PENDING_PERMISSION; record any needed derived input/response-loss scope | Stage 3 |
| S5-13 | Actual exception transfer to fixed recipient, then recipient acknowledgement and audit | rich-scheduler or source-control | PENDING_PERMISSION | Stage 3 |
| S5-14 | Stopped populated backup; advance/change restored copy; restore/restart; compare full saved state and retained replay | state-operations | PENDING_PERMISSION | Core; Stage 4 restart |
| S5-15 | Invalid/foreign source, missing/changed asset and altered-rich refusal, preserving prior success | source-control and isolated asset copies | PENDING_PERMISSION; no edits to original fixtures | Stage 4/data/core |
| S5-16 | Recognized legacy snapshot restore/migrate on separate copies | legacy | PENDING_PERMISSION; legacy fixture creation/migration separately scoped | Core |

Explicitly **unrun and not covered**: all entries above; reset; all legacy versions; cycle-1460 exhaustion/replay; deeper filesystem/copy/replace/fsync/WAL failures; failure-audit loss; crash recovery; storage-denial browser branch; exhaustive producer cycles; carrier scale/concurrency; Docker/Compose/Linux recipient startup. S5-10's one eventual injected failure cannot silently cover every transaction/failure-record branch. Capture only the smallest granted set; keep the remainder explicit.

## Required observation record

For each attempted scenario, append a short record here or a small sanitized Markdown record in this directory. Never fill an unknown result with an expected label.

```text
Scenario ID / status / observed at UTC:
Exact execution authorization reference and allowed mechanism:
Application candidate / documentation SHA / any accepted correction SHA:
Actual OS/architecture, Python, uv, Node/npm; install/build command and exit:
Absolute worktree, data/static/feed/input/artifact paths and measured hashes:
Service PID or owned session / actual loopback port / stop outcome:
Actor, exact request payload/key, operation/cycle/run/batch/receipt IDs:
Wall start/completion/due time AND synthetic scenario clock:
Controlled time/network/fault mechanism (or real elapsed interval):
Before state/counts/IDs; expected result and independent source of expectation:
Actual HTTP/CLI status/body, request ID, after state/counts/IDs:
UI/detail/export agreement and screenshot path where useful:
Pass/fail/partial, limitations, exact evidence paths:
Owner, failing input/output, review-approved correction, affected rerun only:
```

## Candidate questionnaire links — no new credit

Denominator **111**. The lead decides final row status; these are evidence targets only. Current observed contribution is **zero**.

| Scenarios | Candidate IDs | Clause limits |
|---|---|---|
| S5-01/02 | 007, 010, 012, 013, 022 | Local compiled UI/API and readiness; no production alert transport or HA |
| S5-03/04/07/08/09/10 | 033, 034, 037, 061, 063, 068, 069, 071 | Scheduled synthetic acquisition, not network discovery; manual run alone cannot establish timer behavior; general import callback 043 stays deferred |
| S5-05/06 | 029, 062–066, 069, 071, 073–077 | Scope/time-specific calculations; hourly approximation; candidate space is not released or proven reclaimable; no traffic measurement |
| S5-11 | 002, 003, 026–028, 030, 035, 084, 085, 095 | Prefix arithmetic/metadata, no IPv6 subscriber allocation or tenant security |
| S5-12 | 001, 004, 005, 009, 053, 054, 059, 060, 078, 080, 084, 085 | Fixed demo roles and real local allocation/audit; external action simulated; no release/reclaim or SSO |
| S5-13 | 072, 081, 082 | Actual fixed-team transfer plus recipient acknowledgement required; no external ticket/paging integration |
| S5-14/15/16 | 018; 033/034/037/089 for applicable import refusals | Local whole-store preservation only; schema migration is not customer legacy-data migration; no measured RPO/RTO/DR |
| Later Spencer/lead gate | 090, 091, 092, 104, 106 | Package, recipient operation, training/transfer and actual dependency disclosure remain pending; local success cannot substitute |

PR #9 remains NO MERGE. No package branch/checkpoint was registered in the inspected lead documents or matching remote branch/open-PR inventory. `PART6_READY=no`. This ledger does not assign a new stage or replace the persistent lead.
