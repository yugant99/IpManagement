# Bounded local acceptance steps — not executed

Use only after the [ledger's execution gate](README.md) is satisfied for the particular operation. These are source-derived instructions, not a test suite, executable harness or runtime evidence. All expected results below are **unobserved**. Run each group once on the pinned candidate; after a concrete owner correction, rerun only affected behavior.

## 1. Install, setup and readiness: S5-01/02

Read the actual environment after permission. Requirements from `pyproject.toml`, `.python-version`, and `frontend/package.json`: Python `>=3.12,<3.13` (pinned preference 3.12.10), Node `>=22.12.0 <23 || >=24 <25`, npm 10.9.2. Do not use a known unsupported Node 23 or upgrade locks to make installation pass. If the required environment is unavailable, record the concrete dependency blocker.

The existing locked setup interfaces are `uv sync --frozen`, `npm --prefix frontend ci` and **one** `npm --prefix frontend run build`. The build already includes TypeScript checking; do not add a second type-check/test run. Use an external isolated `UV_PROJECT_ENVIRONMENT` if needed, then its installed Python. Record exact tool paths/versions, full commands, output, exit codes and resulting dist path. Dependency/install/cache paths must be recorded; no existing user database is a setup target.

Create the actual fresh absolute store directories from the ledger's artifact plan. Export an absolute `IPAM_DATA_DIR` for each operation; never fall back to `./data`. Set the candidate's absolute `IPAM_STATIC_DIR` and immutable `IPAM_SYNTHETIC_FEED_DIR`. Proposed CLI examples, with the data directory already selected explicitly:

```sh
python -m ipam_demo seed --scenario rich --inventory /Users/yuganthareshsoni/Downloads/Ip_inventory-stage-5/fixtures/v1/inventory.json
python -m ipam_demo serve --host 127.0.0.1 --port 8765
```

Port 8765 is proposed, not reserved or observed. If occupied, select another unused loopback port without stopping its owner. The CLI sets `workers=1`. Record the owned session/PID, actual port, `/healthz` response, rendered `/` and API-backed inventory. Data-ready HTTP 200 alone is insufficient: `static_ready` and rendered compiled UI must also be observed.

For setup control, start a separate empty store without seeding: expect 503 `SETUP_NEEDED` and visible setup UI; stop it before explicit seed. On the rich store, repeated seed while stopped should refuse `ALREADY_INITIALIZED`; an attempted seed or backup while the owned service holds the data lock should refuse `DATA_IN_USE`. Capture outputs and unchanged state. Never delete the lock to force a result. Source: `__main__.py`, `app.py` lifespan/health, `store.py:exclusive_data_access`, `seed.py` and `STATE_OPERATIONS.md`.

## 2. Acquisition, receipts and retry: S5-03/04

On **rich-scheduler**, keep timer disabled while establishing the first manual cycle. Capture `/api/schedule`, `/api/imports?limit=1`, `/api/runs?limit=1`, `/api/audit?limit=1`. Read actual baseline totals; do not assume seed created imported receipts. Source defaults are interval 6, config 1, cursor 0 and no due/run/cycle ID.

POST `/api/schedule/run` with this exact retained payload:

```json
{"actor_id":"demo-approver","reason":"Stage 5 first acquisition","idempotency_key":"stage5-g2-cycle1"}
```

Expected first success: 201, `X-Acquisition-Replay:false`, `replay:false`, `cycle_index:1`, `cycle_id:evolving-v1-000001`, scenario clock `2026-09-01T06:00:00.000Z`, nine distinct batch IDs and one operation/run ID. Import count increases by nine, run count by one, and successful `schedule.acquire` audit count by one. These direct importer calls do **not** create nine ordinary `source.import` audit events.

For each batch read `/api/imports/{batch_id}` and its `/envelope`; preserve source identities/coverage/counts. Cycle 1 expects zero rejected/duplicate rows, accepted=input, nine distinct rich authorities and `source_run_id:evolving-v1-000001`. Read saved `/api/runs/{run_id}`, `/api/runs/{run_id}/export`, and `/api/audit?subject_id={operation_id}`. Record wall completion separately from scenario time.

Repeat the exact actor/reason/key: expect 200 replay with identical operation/run/batch/cycle/completion identities and no added imports/run/success audit/cursor advancement or changed due time. Direct `schedule_operations` count inspection is additional evidence only if disposable-store reads are covered; there is no HTTP list route for that table. Reuse the actor/key with a changed reason: expect 409 `IDEMPOTENCY_CONFLICT` without acquisition effects. A separate failure audit/status change is allowed; do not incorrectly require all audit/status fields to be unchanged.

Browser recovery is a separate observation, requiring an ambiguous response. Record the exact pre-submit sessionStorage payload at `ipam.schedule.manual-attempt.v1`; navigate/reload the same tab, then use “Retry exact Run now request.” Recover the same durable IDs with no extra cycle; validated success clears storage. If ordinary navigation does not produce response ambiguity, leave this branch pending unless response-loss manipulation is explicitly within scope. Do not infer recovery from an ordinary replay or screenshot. Closing the tab/storage clearing is outside this retention boundary. Source: `scheduler.py`, `Schedule.tsx`, `scheduleApi.ts`; existing client timeout is 12 seconds.

## 3. Findings, arithmetic and evolution: S5-05/06/07

Use raw persisted receipts/envelopes and their actual selected run IDs. Runtime inputs must never include expected-answer files. For a baseline-only numeric reference, use **source-control before its negative controls**: seed rich, POST the nine original envelopes to `/api/imports` as JSON, then explicitly POST `/api/runs`. Ordinary imports do not run reconciliation automatically; RFP-043 remains deferred.

Authored baseline comparisons from `fixtures/v1/expected-outcomes.json` are not measured results and must not be reused unchanged for later cycles:

| Subject | Authored comparison |
|---|---|
| Coastal growth pool `051ba42c-08ff-592d-a6dc-109a6bd35967`, `10.60.2.0/24` | Capacity 100, current 69, 30-day p95 68; daily p95 40…69, slope 1, forecast 31 days; pressure anomaly |
| North DHCP pool | Capacity 245, current/p95 150; no positive growth; healthy pressure control |
| North/Lab `10.40.1.10` | Legitimate reuse across separate scope IDs, not a cross-scope conflict |
| Lab `.100`, records `lease-lab-conflict-alpha`/`beta` | Concurrent incompatible claims; one distinct address for occupancy |

Independently compute from selected raw intervals: configured inclusive ranges minus exclusions; distinct scoped addresses active when `lease_start <= sample < lease_end`; 720 hourly samples in `[scenario_clock−30 days, scenario_clock)`; nearest-rank p95 at one-based position **684** after sorting 720 eligible samples. For each full UTC day use position **23** of 24 samples. Fit ordinary least squares over 14–30 consecutive complete days; forecast `(capacity−latest_daily_p95)/positive_slope`. Preserve independent arithmetic and source-record IDs. Missing/stale/incomplete coverage and scope/version changes must retain unavailable history/forecast states. Never use the app's calculation helper as the independent comparator.

On **rich-scheduler**, use a fresh retained key per actual next manual cycle, keeping all older runs. Only cycles needed to reach the named scenarios are required:

- North prefix `41aca2b0-ec1d-4f64-8d21-c5af0ab0b002`: cycles 4/5/6 correspond to route withdrawal, intentionally incomplete North routing, and restoration. Compare 4→5 (`resolution_unknown`) and 4→6 (`resolved_by_evidence`), using actual run IDs at `/api/run-comparison?before_run_id=...&after_run_id=...`.
- Cycle 7 keeps Central envelopes declared complete while their observations are stale. Acquisition may say `complete`; findings/calculations must disclose stale/unknown. Central episode `10.80.243.10` / `10.80.243.0/24` is a concrete reference. Cycle 8 recovery is optional beyond the seven-cycle bounded path; if observed, original Central discrepancies persist, so removal of one episode does not resolve the whole managed-perimeter finding.
- Static DHCP positive/healthy/unknown discrepancy controls use the separate workflow source-control inputs below. Static occupancy/pressure/forecast/inactivity remain not applicable. Fresh positive evidence in partial coverage can still establish a discrepancy; partial silence cannot establish health.

Compare the same run's dashboard, subject detail and JSON export. Then select an older run after later acquisition and verify its contents/clocks/source references remain pinned. Save one report preset using the UI's supported fields; export with its displayed `revision` and preserve `X-Run-ID`/`X-Preset-Revision`. A later changed preset should make the old revision return 409 `STALE_REPORT_PRESET`; unknown outcomes must not be counted as resolution. Source: `calculations.py`, `rules.py`, `reports.py`, both expected-outcome manifests and `STAGE3_API.md`.

## 4. Schedule configuration and failures: S5-08/09/10

Ordinary approved API interactions can save `/api/schedule` with:

```json
{"actor_id":"demo-approver","reason":"Stage 5 schedule acceptance","expected_config_version":1,"enabled":true,"interval_hours":6}
```

Replace version 1 with the **observed** current version. Save should increment config once and set due from wall save time without scenario advancement. Save interval 1 with the returned version; disable (null due); re-enable (new future due). Reusing an old version should return `STALE_SCHEDULE`; `demo-requester` should be forbidden. Record due after successful manual acquisition while enabled and ability to acquire while disabled. None of these observations establishes that a real timer interval elapsed.

Finish these ordinary configuration observations by disabling scheduling with the current configuration version and recording `enabled:false`, `next_due_at:null`. Leave it disabled through inventory/workflow work; use the separate authorized harness copy for enabled-timer cases. Group 6 establishes a fresh disabled-state preservation baseline before its snapshot.

The following require a **separately authorized disposable acceptance harness**, to be concretely scoped before use. No harness was created, no hook added to application code, and no host clock changed:

| Scenario | Smallest controlled observation |
|---|---|
| Contention | Hold an acquisition in preparation; attempt manual acquisition and ordinary `POST /api/runs`; expect busy and only one commit. Separately hold an ordinary reconciliation while a timer becomes due to observe durable busy/forward due. A timer rejected behind an active acquisition leaves status/deadline to that acquisition |
| Old configuration race | Pause old six-hour timer failure after guard release; save one-hour configuration; release old failure handler; at controlled new due, verify old retry tuple cannot suppress new attempt; retain config/due identities and interleaving |
| Overdue restart | Restart the owned service with authorized controlled time beyond multiple due intervals; expect at most one overdue acquisition and a future due, no catch-up burst |
| Transaction rollback | Inject one bounded failure after run/exception creation before commit; compare clock, imports, run, exceptions, cursor, committed replay and successful audit against prior state. Retain explicit error and separate failure audit/status; retry can reuse the uncommitted key |
| Stop | Stop during controlled in-flight work; record completion or rollback and timer join before lock release; after orderly shutdown, observe successful fresh lock acquisition |

Label controlled wall time explicitly. Do not change production intervals, wait hours, simulate an elapsed interval without disclosure, or imply one fault covers commit failure/failure-audit loss/filesystem branches. See `scheduler.py` and `app.py` lifecycle. Leave ungranted cases pending.

## 5. Inventory, allocation and team handoff: S5-11/12/13

Perform successful inventory/workflow/queue/preset operations on **rich-scheduler after arithmetic/evolution observations**, so the populated snapshot contains their IDs alongside scheduler/replay history. Append new child prefixes; do not alter original fixed feed geometry. Perform contradictory source and negative workflow controls on **source-control**.

North scope is `7d2075a0-6fd4-4d58-a26c-1e7d8cb0a001`; IPv4 parent is `41aca2b0-ec1d-4f64-8d21-c5af0ab0b001`. Fetch `/api/prefixes/{parent}/edit-context`. POST `/api/prefixes`, replacing sample versions with current values:

```json
{"actor_id":"demo-approver","reason":"Stage 5 bounded inventory acceptance","expected_baseline_version":1,"scope_id":"7d2075a0-6fd4-4d58-a26c-1e7d8cb0a001","parent_id":"41aca2b0-ec1d-4f64-8d21-c5af0ab0b001","expected_parent_version":1,"cidr":"10.40.250.0/24","owner":"Acceptance Planning","purpose":"Synthetic planning","tags":["acceptance"],"custom_fields":{"review_reference":"stage5"}}
```

Edit that returned empty child to `10.40.250.0/25` through `/api/prefixes/{id}/edit`, replacing scope/parent fields with `expected_version` and retaining baseline version/metadata. Attempt overlap `10.40.1.0/24` with fresh versions: expect 409 `PREFIX_OVERLAP`, unchanged intended prefix and visible audit outcome. IPv6 parent ends `b004`; call its `/child-preview?prefix_length=64&limit=10`, then persist one actual free result with fresh versions. Original fixture reference is 65536 total, 2 blocked, 65534 free; read actual state after any preceding edits. Never enumerate hosts.

Fetch `/api/workflow` and create a request at `/api/allocation-requests` with current pool/baseline versions and an actually available candidate:

```json
{"actor_id":"demo-requester","idempotency_key":"stage5-allocation-01","pool_id":"8821c420-18ea-4caa-9d97-83a331c0c002","candidate":"10.40.2.3","pool_version":1,"baseline_version":1,"owner":"Acceptance Planning","purpose":"Synthetic allocation","reason":"Stage 5 reviewed candidate"}
```

POST `/api/allocation-requests/{id}/decision`:

```json
{"actor_id":"demo-approver","action":"approve","reason":"Stage 5 independent approval","simulate_failure":false}
```

Capture the request, decision, allocation and successful audit IDs; external provisioning must be labeled simulated. Exact creation/decision replay should return the same effects with `X-Request-Replay`/`X-Decision-Replay`; changed keyed payload should conflict. Browser uncertain-response recovery needs its own authorized response-loss observation.

On source-control, use distinct candidates/keys and current versions for controls: requester decision → `FORBIDDEN`; approver self-approval → `SELF_APPROVAL_FORBIDDEN`; intended inventory change after request → `STALE_REVIEW`. For current-DHCP refusal, create the pending request **first**, then import a fresh eligible North DHCP claim for that candidate using a new `source_run_id`; approve without a reconciliation rerun → `CANDIDATE_OBSERVED`. No original fixture has that North static positive claim: preserve the separately authored synthetic input, its derivation, hash, coverage and explicit scope authorization. It must not enter rich-scheduler. Reconciliation on source-control supplies the static `pool_assignment_discrepancy` positive control. Missing DHCP alone does not forbid allocation when the local static ledger is authoritative; preserve its visible limitations.

For an actual anomaly in `/api/exceptions`, transfer with current version via POST `/api/exceptions/{id}`:

```json
{"actor_id":"demo-requester","version":1,"action":"handoff","reason":"Stage 5 transfer","recipient_actor_id":"demo-approver"}
```

Then fetch the new version and acknowledge as `demo-approver` with `action:acknowledge` and a reason. Record Access Planning → Network Operations owner/recipient state, transfer/ack audit IDs, and unchanged finding/run evidence. Team labels alone cannot substantiate RFP-081. Source: `inventory_commands.py`, `workflow.py`, `Workflow.tsx`, `STAGE3_API.md`.

## 6. Whole-store preservation and refusals: S5-14/15/16

Before the primary preservation snapshot, explicitly disable scheduling on the populated rich-scheduler store: GET `/api/schedule`, then POST `/api/schedule` as `demo-approver` with a preservation reason, that current `expected_config_version`, `enabled:false` and the observed interval. Require a successful save; if busy or stale, let the owned operation settle, reload and retry with the current version. Read back and record `enabled:false`, `next_due_at:null`, the returned config version and `in_progress:false`. A submitted disable request without confirmed saved state is not this prerequisite.

Capture semantic IDs/content **after that successful disable**, including its configuration audit: inventory, allocations, requests/decisions, audit, exceptions, preset, source receipts/records, saved runs, seed envelope/baseline version, scenario clock, schedule config/due/cursor and committed replay results. Stop the acceptance-owned primary service before backup. This recorded disabled/null-due state is the preservation baseline; an earlier enabled state is not the comparison target. Direct database inspection requires that the recorded acceptance scope covers it; a snapshot's existence alone cannot establish preservation.

With explicit absolute `IPAM_DATA_DIR`, use the existing stopped-service interfaces:

```text
python -m ipam_demo backup --output ABSOLUTE_NEW_SNAPSHOT_PATH
python -m ipam_demo restore --input ABSOLUTE_SNAPSHOT_PATH --confirm
```

These path labels are placeholders for **new, recorded paths under the acceptance artifact root**, never an existing user store. Back up rich-scheduler to a new file; restore it into empty state-operations; start that copy with scheduling still disabled, explicitly advance once with manual Run now/change an owned record, record newer IDs and stop it. Restore the original snapshot over this copy. Capture the command's `preserved_database` for the newer state, `database_replaced`, schema and `migration_required`. Compare all recorded logical content/IDs to the disabled snapshot baseline; file bytes can differ without a logical difference. Restart without enabling scheduling, read back disabled/null-due state and compare the restored clock/cursor/receipts/runs/audit before any further mutation. Replay a key retained in the snapshot; keys created after it should be absent, so do not blindly reuse them and call the result exactly-once recovery.

This primary round-trip does not establish preservation/startup behavior for an enabled schedule or saved due time. Keep enabled/due/overdue restore evidence on the separately authorized group 4 harness copy, where stopped snapshot state is compared before deliberately allowing controlled timer startup. A legitimate overdue acquisition must not be mistaken for restore corruption or allowed to change this primary comparison baseline.

Use dedicated source-control/asset copies for focused refusals: invalid batch rows with explicit receipt counts; foreign/first-path authority makes scheduled acquisition ineligible; missing/altered copied feed asset fails visibly; original rich structure changed in a copied seed must not become its own authority. The reviewed concrete structural case is Coastal prefix `3eb2272d-8d3e-5f5e-bb5c-7fc1045e6b48` changed from `10.60.11.0/24` to `10.60.12.0/24`. Do not modify committed fixtures. Preserve prior successful clock/run/cursor and record any failure audit separately.

Legacy snapshot creation/restore/migration and reset require their actual scoped permission. If legacy work is granted, use only separate recognized v1/v2/v3 copies, retain their provenance and populated IDs, observe startup refusal before explicit `python -m ipam_demo migrate`, then compare saved state after v4 migration. One legacy version does not cover all three. No legacy fixtures or fault cases have been created here. Deeper permission/copy/replace/fsync/WAL/crash, exhaustion and failure-audit-loss branches remain listed as unrun in the ledger.

Stop all acceptance-owned services on completion, retain snapshots/evidence, and report exact remaining artifacts/process state. Core owns state correctness; Spencer still owns Docker/Compose/mounts/recipient instructions and its later target-host evidence. Local acceptance does not complete that portable delivery gate.
