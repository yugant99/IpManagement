# Native local demo — completed rehearsal record

**Focused agent procedural evidence completed on 2026-09-19/20 and accepted within bounds.** F4 native presentation readiness includes the separate-copy agent reproduction below. This runbook records the actual native candidate, paths, IDs and evidence. It is not human presenter acceptance or portable deployment acceptance.

Stage 5 owns this native demo procedure and focused evidence. Main Lead 2.0 accepts the candidate. Stage 4 owns shared schema/migration; Foundation owns state-command compatibility. Spencer retains packaging, `docs/RUNNING.md`, `scripts/ops/` and portable recipient delivery. An unregistered package checkpoint is a visibility gap, not proof that Spencer has done no work.

## Record before using this runbook

| Item | Required value / current state |
|---|---|
| Reviewed application SHA and PRs | Candidate `289f53c7c5db1bd414c938add1ea207d591f9e64`; acceptance base `94a34b8a35d631b3b9b5bb987ba458f73484c324`; docs PR #47 |
| Presenting Mac and operator | macOS 14.5 arm64; Codex Luna agent procedural operator |
| `DEMO_CHECKOUT` | `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-acceptance` |
| `DEMO_ROOT` | `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/ready-cycle1-with-preset-v2` for presenter-ready cycle 1; final evidence remains in `final-rehearsal` |
| `DEMO_NODE_BIN` | Existing supported Node 22.14.0 installation on PATH; no reinstall performed |
| `DEMO_PORT` | `18892` for the prepared ready copy; loopback only |
| Python / Node / npm / uv paths and versions | Python `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/environment/bin/python` 3.12.10; Node 22.14.0; npm 10.9.2; uv 0.7.13 |
| Installed package origin, locks, compiled UI | Frozen environment at the exact Python path above; static candidate `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-acceptance/frontend/dist`; identity hashes retained in `final-rehearsal/identity.json` |
| Schema version / migration compatibility | Schema v5; restore reported `migration_required:false` |
| Historical initial snapshot path and SHA256 | `final-rehearsal/snapshots/demo-initial-cycle1.sqlite3`; `8f652f649c36af0a0d515098e3c2c32fea1a8a437eec3e2599b6978fea5e0239`; preserved unchanged and has no preset |
| Presenter-ready cycle-1 snapshot path and SHA256 | `ready-cycle1-with-preset-v2/snapshots/demo-ready-cycle1-with-preset.sqlite3`; `ee8134aa583dbf4711251f8bcd23e9bec6305ce77672e40e7cd3def91f655b37`; contains one cycle-1 run and one pinned preset |
| Final evidence snapshot path and SHA256 | `final-rehearsal/snapshots/demo-final-evidence-cycle7.sqlite3`; `e5e50c01b4a7bc8a561b9ba4c2bcc96f317e165e3385b8e7ce39457148946a2d` |
| Ready-state schedule | Observed disabled, config version 1, null due, no in-flight work, cycle 1 at `2026-09-01T06:00:00.000Z` |
| Run IDs | Cycle 1 `004246ef`; cycle 2 `e25f6397`; cycle 3 `c8101c55`; cycle 4 `5b1e253c`; cycle 5 `efadc3fa`; cycle 6 `82e4a57f`; cycle 7 `ab3ae7bd`; full IDs in the evidence handoff |
| Report preset | Presenter-ready cycle-1 revision `147f2054b8edf4f186bc3c8ac8b11d86bed4f08972f20e47da7cba763d6c71c6`; primary final revision `fffa8447...57831`; all eight supported columns and empty filters |
| Correction / finding / audit / exception IDs | Exact IDs are recorded in `docs/handoffs/luna-final-rehearsal.md` and raw HTTP records; no IDs are invented here |
| Native rehearsal / independent walkthrough | Primary evidence complete; presenter-ready copy prepared; independent browser/API/recovery verification complete with saved-run selector locator limitation |
| Spencer checkpoint / portable acceptance | Not established by native success; remains separate |

Keep absolute machine paths, process IDs and raw synthetic stores in a local execution record. Public handoffs may reference sanitized evidence and synthetic IDs; do not commit databases, private assessment, customer material or credentials. Preserve historical Stage 5 evidence at `Ip_inventory-stage-5-artifacts/run-20260919-O8RVgx` unchanged. Never use one of its stores as the working demo directory, and do not start its enabled scheduler-harness stores.

## Completed evidence boundary

The primary rehearsal used both browser and API evidence. Browser observations covered restored startup, `/healthz`, rendered inventory, the intended-inventory disclaimer and the 60-prefix listing; the named record is `browser-restored-observation.json`. Mutating workflow actions were recorded through the native API recorder under `http/`; this includes correction proposals/decisions, exception actions, metadata edit, reconciliations, acquisitions, allocation, presets and all three exports. The browser did not submit the mutating story, so this record must not claim that every action was clicked through the UI.

The private evidence root is `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/final-rehearsal`. It contains `identity.json`, `observations.json`, `cycles.json`, HTTP responses, command logs, semantic snapshots and restore records. The faithful restore output is `commands/final-restore.json`; the final evidence database was preserved by restore at `data/ipam_demo.before-restore-20260920T012552-1896cd02967a4e18a754b50ec0ca27ed.sqlite3`.

## Prepare the reviewed candidate once

Set the four `DEMO_*` values from the completed table before using these templates. For the presenter-ready recovery path, use the prepared `ready-cycle1-with-preset-v2` copy; do not overwrite the historical initial or final evidence snapshots. The exact supported Python environment is retained outside the demo root.

```sh
: "${DEMO_CHECKOUT:?Set the reviewed candidate checkout}"
: "${DEMO_ROOT:?Set a new dedicated demo directory}"
: "${DEMO_NODE_BIN:?Set the supported Node and npm directory}"
: "${DEMO_PORT:?Set the recorded unused loopback port}"
export PATH="$DEMO_NODE_BIN:$PATH"
cd "$DEMO_CHECKOUT"
mkdir -p "$DEMO_ROOT/data" "$DEMO_ROOT/snapshots" "$DEMO_ROOT/evidence"
export DEMO_PYTHON="/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/environment/bin/python"
# One-time candidate preparation was already completed for this reviewed candidate.
# Do not rebuild or reinstall for a presentation startup. If a future candidate changes,
# run the frozen setup/build once in a new disposable root and record its actual paths.
```

Record actual tool versions, command outputs/exit codes and candidate identity. Build once after relevant frontend changes; do not run another build on every presentation startup. The historical Python environment is an editable install pointing at the old Stage 5 checkout: do not repoint or silently reuse it. Reusing an immutable supported Node binary or download cache does not make old application code or old `frontend/dist` the new candidate.

For every subsequent shell, explicitly set these values using the same recorded checkout and root:

```sh
export IPAM_DATA_DIR="$DEMO_ROOT/data"
export IPAM_STATIC_DIR="$DEMO_CHECKOUT/frontend/dist"
export IPAM_SYNTHETIC_FEED_DIR="$DEMO_CHECKOUT/fixtures/v1"
```

The feed directory is `fixtures/v1`, containing policy and eight observation envelopes. The producer module is separately installed with the application. A SQLite snapshot contains neither the producer nor those assets. Do not use `fixtures/evolving` as the asset directory or alter committed fixture files.

## Presenter-ready cycle-1 copy

The historical `demo-initial-cycle1.sqlite3` is a recovery/source snapshot from before the later report-preset save, so its `report_preset` table is intentionally empty. The presenter-ready copy is separate and must be used for a pinned cycle-1 walkthrough:

```sh
export DEMO_PYTHON="/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/environment/bin/python"
export DEMO_ROOT="/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/ready-cycle1-with-preset-v2"
export DEMO_CHECKOUT="/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-acceptance"
export IPAM_DATA_DIR="$DEMO_ROOT/data"
export IPAM_STATIC_DIR="$DEMO_CHECKOUT/frontend/dist"
export IPAM_SYNTHETIC_FEED_DIR="$DEMO_CHECKOUT/fixtures/v1"
"$DEMO_PYTHON" -m ipam_demo serve --host 127.0.0.1 --port 18892
```

This prepared copy was created from the historical snapshot, then the cycle-1 preset was saved through `POST /api/report-preset` and read back through `GET /api/report-preset`. It contains run `004246ef-9089-40ac-b029-a412d5c2d38d`, Central finding `60409eed-4098-48eb-8cb6-c0defaf227a3`, preset revision `147f2054b8edf4f186bc3c8ac8b11d86bed4f08972f20e47da7cba763d6c71c6`, disabled scheduling, and one saved run. The backup command and hash are recorded under the ready-copy evidence directory.

The primary cycle-7 final evidence snapshot and the historical initial snapshot remain separate and must not be overwritten by presenter preparation.

For a fresh empty demo directory only, explicitly seed rich inventory while stopped:

```sh
"$DEMO_PYTHON" -m ipam_demo seed --scenario rich --inventory "$DEMO_CHECKOUT/fixtures/v1/inventory.json"
```

Do not reseed an initialized store to recover the presentation. Restore the prepared snapshot instead. If a recognized older-schema copy needs migration, stop its service and use the reviewed explicit migration procedure from [state operations](STATE_OPERATIONS.md); startup and restore must not silently migrate it. Never migrate a retained original acceptance database.

## Start and prepare the presentation state

```sh
"$DEMO_PYTHON" -m ipam_demo serve --host 127.0.0.1 --port "$DEMO_PORT"
```

Keep this foreground terminal and record its PID. Open `http://127.0.0.1:<recorded-port>/` and `/healthz`. Require initialized/schema readiness, `static_ready:true`, rendered inventory and the reviewed new controls. HTTP 200 data readiness alone does not establish UI readiness or source freshness.

Keep automatic scheduling **disabled**. Prepare only cycle 1 with one explicit manual acquisition, recording its returned run/cycle/operation ID and retaining the idempotency key until its outcome is known. Do not pre-advance to cycle 6: the rehearsal first resolves and closes the original ghost case, then demonstrates its recurrence. Scenario time advances six hours per acquisition; the configurable wall schedule interval does not change that step. An ordinary reconciliation evaluates the current scenario clock without acquiring the next cycle.

| Cycle plan | Presentation purpose |
|---|---|
| Cycle 1, initial prepared state | Fresh capacity/forecast reference and persistent Central ghost `.240.10`; save initial preset and snapshot before mutations |
| Cycle 1, ordinary reconciliation after correction | Actual healthy ghost result after approved `.240.0/24` registration; close the evidence-resolved case |
| Cycles 2 and 3, acquired during rehearsal | Record each manual advancement and retained case history; do not skip the intermediate acquisitions |
| Cycle 4 | North missing-route anomaly; retain its exact run ID |
| Cycle 5 | North incomplete evidence; 4→5 comparison must not claim resolution |
| Cycle 6 | North recovery; new Central ghost `.243.10` renews the notice and reopens the previously resolved case |
| Cycle 6, ordinary reconciliation after second correction | Approved `.243.0/24` registration followed by actual healthy comparable ghost evidence |
| Cycle 7, acquired deliberately at the end | Complete acquisition with stale Central observations; update the preset to this final run and preserve a separate final evidence snapshot |

Inspect the actual selected observations before proposing a correction. At cycle 1, the chosen registration is top-level `10.80.240.0/24` for persistent `10.80.240.10`. At cycle 6 that lease still exists, but its approved prefix now covers it; the new `10.80.243.10` episode requires a separate `.243.0/24` registration. Both addresses must be accounted for before claiming the ghost perimeter healthy. Persistent unregistered routing `.241.0/24` is a separate discrepancy: correcting ghosts does not establish that all Central rules are healthy. These examples are not rule inputs or substitutes for checking actual saved findings.

Save the initial report preset from the UI, pinned to the cycle-1 acquisition run; retain its displayed revision, filters and columns. The final rehearsal later updates this singleton preset to the current cycle-7 run and records a different explicit revision. Confirm the selected run and displayed scenario clock after loading completes. Merely finding a run ID among dropdown options does not prove that it is selected.

Before creating the ready-state snapshot, explicitly save disabled scheduling using the current configuration version. Read it back: disabled, null next due and no operation in progress. Record this state and its configuration audit, then stop with Ctrl-C and wait for the owned process to exit before backup.

```sh
"$DEMO_PYTHON" -m ipam_demo backup --output "$DEMO_ROOT/snapshots/demo-initial-cycle1.sqlite3"
```

The destination must be new; do not overwrite an earlier snapshot. Record the exact path, SHA256 and command result. Retain a semantic baseline for every finalized application table, including new correction/history/exception fields, saved runs, preset, audits, clock/cursor and committed replay records. Do not hardcode the historical 15-table count. This is the initial cycle-1 recovery target, before live corrections and allocation. The later final evidence snapshot has a different filename and purpose.

## One integrated rehearsal after review

For a future human presenter, use the completed candidate/ID table above and the observed labels below. Capture any additional UI/API actions and outcomes; do not invent routes or claim a planned action ran.

1. **Orient and handle the original case.** Start the prepared state, confirm disabled cycle 1, open the pinned fresh run and inspect Central `.240.10` source provenance. Show original saved evidence separately from latest evidence. On that case exercise owner escalation, handoff and recipient acknowledgement with refreshed versions and reasons; retain audit and ownership history.
2. **Approve the first correction and establish resolution (F1/F5).** As requester, propose top-level `10.80.240.0/24` from the actual anomalous finding, supplying owner, purpose, reason and reviewed inventory version. Pending must leave inventory unchanged; a different authorized actor approves. Inspect prefix/decision/audit, then reconcile at the same cycle-1 clock. Show original, first subsequent result and latest result distinctly. Close as current owner only after the latest comparable finding is actually healthy, with current version and reason. Demonstrate explicit owner reopen without inventing anomalous evidence, then close again while evidence is still healthy so the cycle-6 recurrence starts from a closed case. Refresh the version after each action or reconciliation.
3. **Correct metadata and preserve history (F2/F3).** Show Lab `10.40.15.0/24` metadata-gap evidence, correct actual missing values with an audit reason, and reconcile to inspect the healthy comparison. On the designated pool-bearing control, demonstrate that metadata edits preserve eligible p95/forecast while concurrency versions still advance. Older runs remain unchanged. A newly registered prefix without intended route policy remains appropriately unknown.
4. **Advance deliberately and observe recurrence.** Manually acquire cycles 2, 3, 4, 5 and 6 in order, recording every request key, operation/run ID, clock and outcome. Keep scheduling disabled. Inspect North anomaly at 4, unknown at 5 and healthy at 6; compare 4→5 and 4→6. At cycle 6 inspect the new Central `.243.10` discrepancy: the previously resolved case reopens, renews its notice and clears acknowledgement while retaining owner and operational history. Generated IDs or a changed run alone must not be described as a new incident. Retained focused evidence covers unchanged-anomaly notification deduplication and new material members within an unresolved episode.
5. **Correct the new episode.** Propose `.243.0/24` from the new actual anomalous finding, approve independently, then perform ordinary reconciliation without advancing beyond cycle 6. Verify both `.240.10` and `.243.10` are covered by their persisted prefixes and the latest comparable ghost finding is healthy before owner closure. Account for any additional actual observations; do not hide a remaining discrepancy. Keep the separate `.241.0/24` routing finding and unknown new-prefix policy outcomes visible. Confirm feed eligibility remains compatible; do not enable the timer.
6. **Approve a local allocation.** Select the actual free candidate and current reviewed versions, request as one actor, approve as the other, then inspect allocation and audit IDs. Pending does not reserve addresses. Distinguish the persisted local allocation from explicitly simulated external provisioning; reuse focused stale/self/unauthorized/contradictory-evidence guard observations.
7. **Show outputs and final uncertainty.** Export the initial pinned cycle-1 preset using its displayed revision before changing it. Deliberately acquire cycle 7 once, inspect complete acquisition alongside stale/unavailable Central evidence, then stop advancing. Historical healthy results remain saved, but current correction/case resolution must reflect the latest uncertain evidence rather than falling back to an older healthy result. Update the preset explicitly to the final cycle-7 run; retain its new revision, filters and columns and export against that revision. Findings CSV, run JSON and audit CSV are distinct outputs, not a complete customer assessment report. Rule thresholds remain fixed; acquisition scheduling is configurable.
8. **Preserve final evidence, then recover.** Capture the final state, create the distinct stopped final evidence snapshot below, then restore the initial cycle-1 snapshot. Verify the initial run/preset revision, disabled schedule, clock/cursor and complete baseline. Keep the completed rehearsal's final snapshot, restore-preserved newer state and evidence.

Confirmed F3 contract: metadata edits do not advance `pools.capacity_history_version`; supported child creation or CIDR-bounds changes conservatively invalidate own/ancestor pool history while normal concurrency bumps remain. The editor receives `edit_context.history_impact` with `metadata:[]` and `structural:[{pool_id,name,cidr}]`. Migration conservatively retains previously invalidated history; metadata changes do not repair that history. Capture the affected-ancestor warning in focused acceptance. Keep structural controls on a separate disposable store. Do not describe current occupancy as necessarily unavailable, positive-lease zombie evidence as necessarily unknown, or old saved runs as erased.

F5 closure and operational disposition are separate: `closed_at` does not replace open/acknowledged/escalated history. Missing, unknown, not-applicable or incomparable latest evidence never establishes healthy resolution. New runs invalidate an older action version; refresh before closing or reopening. Exact immediate retries follow the reviewed canonical payload/current-version rule, not a blanket permission to reuse an old action after intervening runs.

## Preserve the final rehearsal evidence

After the final cycle-7 preset update, confirm disabled/null-due scheduling and no in-flight work with current saved configuration. Capture the final semantic state, selected run and preset revision. Stop the owned service and wait for exit before creating a second, new snapshot:

```sh
"$DEMO_PYTHON" -m ipam_demo backup --output "$DEMO_ROOT/snapshots/demo-final-evidence-cycle7.sqlite3"
```

Record its SHA256, schema, command result and logical-state evidence separately. This snapshot preserves approved corrections, original/first/latest outcomes, metadata changes, exception recurrence and actions, allocation/audit history, all acquired runs and the final cycle-7 preset. It is not the presentation reset target. Never overwrite the initial snapshot with this newer state.

## Stopped recovery

Stop only the owned demo service, wait for exit and keep the terminal result. Stop other tools holding its database. A leftover `.ipam_demo.lock` file is normal; never remove it to bypass a live lock. After retaining final evidence, use the same absolute environment values and the recorded **initial cycle-1** snapshot for final-rehearsal recovery:

```sh
"$DEMO_PYTHON" -m ipam_demo restore --input "$DEMO_ROOT/snapshots/demo-initial-cycle1.sqlite3" --confirm
```

For the current presenter-ready copy, recover the prepared ready snapshot from its own root instead of the historical final-rehearsal initial snapshot:

```sh
export DEMO_PYTHON="/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/environment/bin/python"
export DEMO_ROOT="/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/ready-cycle1-with-preset-v2"
export DEMO_CHECKOUT="/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-acceptance"
export IPAM_DATA_DIR="$DEMO_ROOT/data"
export IPAM_STATIC_DIR="$DEMO_CHECKOUT/frontend/dist"
export IPAM_SYNTHETIC_FEED_DIR="$DEMO_CHECKOUT/fixtures/v1"
"$DEMO_PYTHON" -m ipam_demo restore --input "$DEMO_ROOT/snapshots/demo-ready-cycle1-with-preset.sqlite3" --confirm
```

Require a successful restore result; retain `database_replaced`, schema, `migration_required` and the `preserved_database` path. If restoration reports a partial failure, inspect these fields rather than blindly retrying. The previous populated demo state is preserved by the command. Do not delete it or use reset as a shortcut.

Compare restored logical rows/IDs with the initial disabled cycle-1 baseline before further mutation, then start with the same command. Confirm disabled/null-due state, cycle-1 cursor/clock, initial saved run and initial preset revision. Rehearsal corrections, later runs and actions must be absent from this reset store and remain available in the separate final evidence and pre-restore preservation snapshots. SQLite file bytes may differ while logical content is equal. Only replay keys present in the restored history retain their deduplication meaning; post-snapshot operations are no longer present.

## Independent walkthrough and remaining gates

### Primary rehearsal result

The primary agent rehearsal completed the documented path. Central `.240.10` finding `60409eed-4098-48eb-8cb6-c0defaf227a3` was corrected by request `dc4ef177-1b96-461c-906d-f7013f7c586b`, then reconciled healthy at the same scenario clock; the exception was escalated, handed off, acknowledged, closed, explicitly reopened and closed again. Lab `10.40.15.0/24` metadata was edited from the actual gap and reconciled; the original cycle-1 run remains immutable in the saved-run records. Cycle 6 produced material `.243.10` recurrence with notification reason `recurrence`; correction `0fc0e038-4632-453c-906d-f7013f7c586b` and reconciliation `ddd4afac-ca8a-435a-b60c-dee0586a3895` produced comparable healthy evidence for both ghost addresses before closure. Cycle 7 `ab3ae7bd-5ed1-454c-9cc1-80d07f96d210` was deliberately acquired at the latest clock and final preset; Central ghost evidence was `unknown` under stale/incomplete source evidence and did not reuse the older healthy result. The separate `.241.0/24` routing discrepancy stayed visible.

F3 metadata evidence is in the API records for `GET /api/prefixes/a1526294-9c3c-5588-98b5-c0fa7cae2aa9/edit-context` and the subsequent edit; the returned metadata impact was separate from structural impact, prefix version advanced, and saved calculation/run records were retained. The Lab edit-context does not by itself prove pool-history preservation. That narrower history claim reuses the accepted owner-3 focused history checks and shared-owner 27-HTTP North metadata evidence; the designated structural-ancestor control remains a separate disposable-store gate and was not silently folded into this rehearsal. The initial, final and restored semantic comparison is `snapshots/restored-semantic-comparison.json`: 16 application tables plus the SQLite bookkeeping table `sqlite_sequence` were compared, restored state matched the initial snapshot for every table, and the preserved final database differed as expected. The comparison is an artifact-level logical check; the faithful CLI restore response is separately named in `commands/final-restore.json`.

The three distinct exports are recorded in the HTTP evidence: final preset findings CSV, final run JSON and audit CSV. The initial preset revision was `7232911f9ebb408e473a951987667d00539ca8e3285aaa9128725431eef2b089`; final revision was `fffa84479ab3406d119f068a416921d53a7222eaa024fe314d5d70dcc2b57831`.

Give a second operator this completed runbook, the reviewed candidate/toolchain paths and **initial cycle-1** snapshot. Use a separate new data directory, restore while stopped, and record startup, initial pinned-run/preset selection, one assigned demo path and stopped recovery. Identify the final evidence snapshot separately so it cannot be mistaken for the starting state. Record elapsed time and every undocumented intervention. An independent **agent procedural check** can establish that the documented sequence is machine-reproducible; label it separately from an observed **human presenter/recipient walkthrough**. Neither establishes a portable Linux/container deployment.

The independent agent reproduction was run in `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-independent-ready-verification-20260919` and reported at `/Users/yuganthareshsoni/Documents/Codex/2026-09-19/luna-independent-reproduction-20260919/outputs/independent-agent-procedural-reproduction.md`. It restored the new ready snapshot, verified health, disabled cycle 1, the saved run, the pinned preset revision and the Central `.240.10` finding through API, and stopped/recovered cleanly with all 17 tables matching. One fresh browser attempt visibly showed 60 prefixes and the `Presenter ready cycle 1` preset pinned to the expected run; selecting the saved-run control hit a locator timeout, so no saved-run selection claim is made and no retry occurred. This is separate agent reproduction, not human presenter/recipient acceptance.

Before declaring native readiness, link the reviewed merged candidate, focused F1–F5/schema/state results, final rehearsal and actual walkthrough evidence. Keep remaining unverified clauses explicit. Spencer's exact package SHA/PR and target-host/recipient evidence remain separate gates; this Mac demo does not wait on or imply unobserved portability. Preserve the historical Stage 5 result of 14 passes/two partial cases and append new results. The 15 catalog scenarios, 16 Stage 5 cases and 111 questionnaire requirements remain separate accounting sets.
