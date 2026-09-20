# S5-09 supplemental process observations

**Three targeted scenarios observed pass; accepted by Main Lead 2.0 after independent artifact review on 2026-09-19.** Candidate `a279f32df0ac7d2147b580dbff36dd88772bdeb2`, read-only worktree `/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-gap-process-checks`. Successful run: 2026-09-20 00:54:36–00:55:00 UTC (2026-09-19 local). The 35 assertions support these three scenarios, not additional questionnaire or catalog counts.

Local evidence root:

`/Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5-audit-artifacts/run-20260919-zzeadfai/process-gaps/`

Start with `compact-summary.json` and `REPORT.md`. `attempt-2/child.py`, `attempt-2/run.py`, JSONL events, HTTP results, process logs and `attempt-2/results.json` retain the actual proof. The large results file includes logical row manifests; select needed fields rather than printing it whole. Source hashes and imported module paths pin the code used.

## Method and evidence boundary

An external child wrapper invoked the real installed `ipam_demo.__main__.main()` and Uvicorn on the process main thread, using real HTTP routes and fresh rich stores. All injected instrumentation stayed outside repository source. It observed existing methods, controlled only `scheduler._now`, and held a bounded Event barrier at the specified real transaction boundary. The host clock and production interval bounds were unchanged. JSONL records contain real UTC, monotonic time and controlled scheduler time separately.

Controlled scheduler wall time starts at `2031-01-01T00:00:00.000Z`. This is bounded clock/trigger evidence, not an elapsed-hour endurance test. Synthetic scenario time remains the application clock, advancing six hours for each committed feed cycle.

## Actual ordinary reconciliation competing with a due timer

On port `18871`, an actual HTTP ordinary reconciliation calculated all eight pools inside the API's `BEGIN IMMEDIATE`, paused before its large saved-run write, and held the shared run guard. A due timer attempted acquisition and received `RUN_IN_PROGRESS`.

The ordinary SQLite writer blocked the separate failure-record transaction for its three-second busy timeout. Observed error details were `audit_recorded:false` and `failure_recorded:false`; the message explicitly disclosed the failure-status/audit loss. Persisted schedule status and due remained unchanged. GET schedule exposed `timer_error`; the process retry guard advanced to controlled `02:00` for configuration 2 / saved due `01:00`.

Releasing the ordinary barrier committed exactly one ordinary run (`9e8fd96b-d30a-4cbe-9370-cb338f45fe56`), with no source acquisition, cursor/clock advancement or operation record. A wake at the same controlled instant made no new timer attempt. Moving to the guarded later deadline yielded one cycle-2 acquisition (`5325993e-7ef9-4fe3-b986-642043a6529b`, run `a472938a-55bc-48ce-b5db-6254c1020432`), adding nine batches and one acquired run. This establishes forward recovery without falsely claiming the blocked audit was saved.

Scheduling was disabled and the owned process stopped; an independent process acquired its data lock after exit. Final state is disabled, configuration 3, cursor 2, null due. Its retained controlled-time store is evidence, not a presentation store.

## Actual OS signals during acquisition

Each signal used a separate process/store. A real due acquisition paused inside its transaction after nine imports, saved reconciliation and exception synchronization, before the final acquisition commit. The controller sent one actual OS signal to the known child PID. Uvicorn's actual handler ran on its main thread, then the API lifespan entered scheduler stop/join while acquisition was still active.

| Signal | PID / port | Actual exit | Committed operation / run |
|---|---|---|---|
| SIGTERM | `94268` / `18872` | `-15` after graceful completion and signal re-raise | `e185695b-299c-4f9b-affd-759ab2cb70b8` / `8431a92f-23dd-4792-9ed2-40c0b812dc35` |
| SIGINT | `94382` / `18873` | `0` after graceful completion | `e8f3f74f-810d-468c-9042-0fab4c9d4ea3` / `e7056849-b208-4621-beb2-c5fff8c72319` |

For both, an independent lock-probe process failed to acquire the data lock while shutdown waited. Only after the barrier released did the acquisition complete, scheduler thread join and process exit. A new independent lock probe then succeeded. Exit code alone was not used as the graceful-shutdown criterion.

Stopped logical state held exactly nine source batches, one saved run, one committed operation and cursor 1. Status, operation run ID, unique nine-batch references and scenario clock agreed. Each store restarted before its saved controlled due; all actual application-table hashes remained unchanged. Scheduling was explicitly disabled after the restart observation, and the restart service stopped.

These cases demonstrate the **finish-and-commit** shutdown branch. They do not claim SIGKILL/power-loss recovery, rollback caused by a signal, arbitrary termination points, multiple workers or every platform's signal behavior.

## Observer correction and limits

The first ordinary-run attempt paused after the large saved-run/queue writes. With those writes pending, SQLite also blocked the timer's initial status read, so it reported `STORE_BUSY` before reaching the expected acquisition/failure-record marker. The observer timed out waiting for that marker. This was an incorrect barrier assumption, not evidence of an application defect. The original attempt, logs, traceback and stopped process remain retained.

One fresh attempt moved the ordinary barrier earlier, after actual pool calculation within the same real API transaction. The three successful scenarios above then ran once. No application source was changed or broad passing suite rerun. All five successful-run child processes and the initial-attempt child are stopped; no broad process cleanup occurred. The three completed-case stores finish disabled/configuration 3/null due (ordinary cursor 2; signal cases cursor 1). **Do not start the retained first-attempt store:** it remains enabled/configuration 2/cursor 1 with controlled due `2031-01-01T01:00:00.000Z`.

Independent read-only review recounted 13 ordinary/timer, 11 SIGTERM and 11 SIGINT assertions; matched actual receipt IDs to operation and saved-run selected batches; and confirmed all 15 tables unchanged across each restart. `supporting-stopped-state.json` records final-state checks and `artifact-sha256.json` pins 31 retained artifacts. This review did not rerun application behavior.

Historical S5-09 remains recorded as partial in its original report. These specifically missing observations are a separate lead-review addendum, not evidence for all untested scheduler/filesystem/exhaustion/portable branches.
