# Native local demo — preparation draft

**Not yet rehearsed or ready for presentation.** This draft supports the authorized F1–F7 response on the presenting Mac. Fill the candidate, paths, IDs and evidence below after reviewed integration; then perform one connected rehearsal. Commands here describe existing native interfaces, not actions performed while writing this document. New correction and exception UI labels remain pending inspection of the integrated candidate.

Stage 5 owns this native demo procedure and focused evidence. Main Lead 2.0 accepts the candidate. Stage 4 owns shared schema/migration; Foundation owns state-command compatibility. Spencer retains packaging, `docs/RUNNING.md`, `scripts/ops/` and portable recipient delivery. An unregistered package checkpoint is a visibility gap, not proof that Spencer has done no work.

## Record before using this runbook

| Item | Required value / current state |
|---|---|
| Reviewed application SHA and PRs | **Pending**; do not substitute a moving branch or mix worker heads |
| Presenting Mac and operator | **Pending**; record macOS/architecture and operator |
| `DEMO_CHECKOUT` | **Pending** absolute checkout of that exact candidate |
| `DEMO_ROOT` | **Pending** new absolute local directory for this demo's environment, data, snapshots and evidence |
| `DEMO_NODE_BIN` | **Pending** absolute directory containing supported Node/npm executables |
| `DEMO_PORT` | **Pending** unused loopback port; do not stop another owner's listener |
| Python / Node / npm / uv paths and versions | **Pending refresh**; historical working versions were 3.12.10 / 22.14.0 / 10.9.2 / 0.7.13 |
| Installed package origin, locks, compiled UI | **Pending** candidate paths and hashes; Python requires 3.12, Node 22.12+ within major 22 or major 24, npm 10.9.2 |
| Schema version / migration compatibility | Schema v5 specified in the lead contract; **pending** reviewed implementation and Foundation evidence |
| Initial prepared snapshot path and SHA256 | **Pending** `demo-initial-cycle1.sqlite3`, standalone, disabled, before corrections or allocation |
| Final evidence snapshot path and SHA256 | **Pending** distinct `demo-final-evidence-cycle7.sqlite3`, preserving the completed rehearsal before recovery |
| Ready-state schedule | **Pending observed** disabled, null due, no in-flight work, cycle 1; record config version and scenario clock |
| Run IDs | **Pending** every acquisition cycle 1–7 plus ordinary correction/metadata reconciliation runs |
| Report preset | **Pending** initial cycle-1 run/revision and later updated final cycle-7 run/revision; record name, filters and columns for both |
| Correction / finding / audit / exception IDs | **Pending** actual retained identities from the final candidate |
| Native rehearsal / independent walkthrough | **Pending** evidence paths, operator and result; human versus agent explicitly identified |
| Spencer checkpoint / portable acceptance | **Pending registration or refresh** / not established by native success |

Keep absolute machine paths, process IDs and raw synthetic stores in a local execution record. Public handoffs may reference sanitized evidence and synthetic IDs; do not commit databases, private assessment, customer material or credentials. Preserve historical Stage 5 evidence at `Ip_inventory-stage-5-artifacts/run-20260919-O8RVgx` unchanged. Never use one of its stores as the working demo directory, and do not start its enabled scheduler-harness stores.

## Prepare the reviewed candidate once

Set the four `DEMO_*` values from the completed table before using these templates. `DEMO_ROOT` must be a new demo directory, not a user store or historical evidence directory. Use a local supported filesystem.

```sh
: "${DEMO_CHECKOUT:?Set the reviewed candidate checkout}"
: "${DEMO_ROOT:?Set a new dedicated demo directory}"
: "${DEMO_NODE_BIN:?Set the supported Node and npm directory}"
: "${DEMO_PORT:?Set the recorded unused loopback port}"
export PATH="$DEMO_NODE_BIN:$PATH"
cd "$DEMO_CHECKOUT"
mkdir -p "$DEMO_ROOT/data" "$DEMO_ROOT/snapshots" "$DEMO_ROOT/evidence"
export UV_PROJECT_ENVIRONMENT="$DEMO_ROOT/environment"
export UV_CACHE_DIR="$DEMO_ROOT/uv-cache"
uv sync --frozen
npm --prefix frontend ci --cache "$DEMO_ROOT/npm-cache" --no-audit --no-fund
npm --prefix frontend run build
```

Record actual tool versions, command outputs/exit codes and candidate identity. Build once after relevant frontend changes; do not run another build on every presentation startup. The historical Python environment is an editable install pointing at the old Stage 5 checkout: do not repoint or silently reuse it. Reusing an immutable supported Node binary or download cache does not make old application code or old `frontend/dist` the new candidate.

For every subsequent shell, explicitly set these values using the same recorded checkout and root:

```sh
export DEMO_PYTHON="$DEMO_ROOT/environment/bin/python"
export IPAM_DATA_DIR="$DEMO_ROOT/data"
export IPAM_STATIC_DIR="$DEMO_CHECKOUT/frontend/dist"
export IPAM_SYNTHETIC_FEED_DIR="$DEMO_CHECKOUT/fixtures/v1"
```

The feed directory is `fixtures/v1`, containing policy and eight observation envelopes. The producer module is separately installed with the application. A SQLite snapshot contains neither the producer nor those assets. Do not use `fixtures/evolving` as the asset directory or alter committed fixture files.

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

Complete the candidate/ID table and replace pending new-control descriptions with their observed labels before handing this to a presenter. Capture real UI/API actions and outcomes; do not invent routes or claim a planned action ran.

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

Stop only the owned demo service, wait for exit and keep the terminal result. Stop other tools holding its database. A leftover `.ipam_demo.lock` file is normal; never remove it to bypass a live lock. After retaining final evidence, use the same absolute environment values and the recorded **initial cycle-1** snapshot:

```sh
"$DEMO_PYTHON" -m ipam_demo restore --input "$DEMO_ROOT/snapshots/demo-initial-cycle1.sqlite3" --confirm
```

Require a successful restore result; retain `database_replaced`, schema, `migration_required` and the `preserved_database` path. If restoration reports a partial failure, inspect these fields rather than blindly retrying. The previous populated demo state is preserved by the command. Do not delete it or use reset as a shortcut.

Compare restored logical rows/IDs with the initial disabled cycle-1 baseline before further mutation, then start with the same command. Confirm disabled/null-due state, cycle-1 cursor/clock, initial saved run and initial preset revision. Rehearsal corrections, later runs and actions must be absent from this reset store and remain available in the separate final evidence and pre-restore preservation snapshots. SQLite file bytes may differ while logical content is equal. Only replay keys present in the restored history retain their deduplication meaning; post-snapshot operations are no longer present.

## Independent walkthrough and remaining gates

Give a second operator this completed runbook, the reviewed candidate/toolchain paths and **initial cycle-1** snapshot. Use a separate new data directory, restore while stopped, and record startup, initial pinned-run/preset selection, one assigned demo path and stopped recovery. Identify the final evidence snapshot separately so it cannot be mistaken for the starting state. Record elapsed time and every undocumented intervention. An independent **agent procedural check** can establish that the documented sequence is machine-reproducible; label it separately from an observed **human presenter/recipient walkthrough**. Neither establishes a portable Linux/container deployment.

Before declaring native readiness, link the reviewed merged candidate, focused F1–F5/schema/state results, final rehearsal and actual walkthrough evidence. Keep remaining unverified clauses explicit. Spencer's exact package SHA/PR and target-host/recipient evidence remain separate gates; this Mac demo does not wait on or imply unobserved portability. Preserve the historical Stage 5 result of 14 passes/two partial cases and append new results. The 15 catalog scenarios, 16 Stage 5 cases and 111 questionnaire requirements remain separate accounting sets.
