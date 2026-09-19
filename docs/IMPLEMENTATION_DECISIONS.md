# Bounded implementation decisions

Status: agent-decided design, **not implemented or runtime-verified**. This is the detailed companion to [CONTRACTS.md](CONTRACTS.md), integrated after the [75-question exchange](GRILL_75.md). Read only sections relevant to your lane. The lead resolves any contract/code mismatch before another lane depends on it.

These choices bound the weekend demo; they are not customer scale, operational freshness or production guarantees. Retain one app, one SQLite database and direct functions. Do not translate every concept below into a new table, service or abstraction.

## Parts 1–2: identity and fixtures

- Initial sizing budget: four fictional scopes (North, Coastal, Central, Lab), 60 prefixes, eight pools, 2,000 lease intervals and 200 routing observations over 30 days. No customer topology is implied.
- Require registry `scope_id` and address family; reject unmapped scope and CIDRs with host bits set. Preserve rejected raw values. Declared parent/child containment can be legitimate; otherwise retain unresolved overlap evidence.
- Use timezone-aware timestamps normalized to UTC milliseconds and half-open intervals `[start,end)`. A lease ending when another begins is sequential, not concurrent. Retain original source timestamp text.
- Pools declare `management_mode=dhcp|static`, assignable ranges and exclusions. Ranges must be disjoint and inside the pool; exclusions must be inside those ranges. Invalid capacity blocks percentages, forecasts and allocation.
- Missing lease expiry or route validity bounds is rejected for calculations and makes affected coverage incomplete. Future observation/start times cannot contribute at the selected demo clock; future expiry/end times may be valid.
- Routing input contains bounded validity intervals, not a BMP add/withdraw parser. Scopes declare independent `managed_cidrs`; detection must not derive that perimeter from the inventory being checked.

## Part 2: imports and eligibility

- Core accepts one versioned JSON envelope with source metadata and records. CSV input adapters are stretch; agreed report exports remain in scope. Reject over 10 MiB or 10,000 records before mutation.
- Receipt counts satisfy `input_rows = accepted_rows + rejected_rows + duplicate_rows`, with exclusive statuses. Retain reasons and references. Rejected required observations force effective completeness false even if the sender declared the batch complete.
- Whole-batch identity is `(source_id, source_run_id)` plus SHA256 of canonical normalized-envelope JSON. Same identity/hash returns the original receipt with no new rows/effects; changed content under the same identity is 409.
- Select the latest accepted ingestion sequence per source and declared scope. Do not silently stitch coverage or fall back to an older complete batch after a newer partial one. Changed IPAM inventory remains staged as described in the main contract.
- Coverage includes scope, window start/end, snapshot/interval kind, declared completeness and validation result. The default illustrative freshness limits are DHCP 30 minutes and routing five minutes, measured from the covered/snapshot end against the run's fixed `demo_clock_at`.
- Show the demo clock separately from wall-clock ingestion time. Positive observations may remain usable in incomplete batches; absence conclusions require complete applicable evidence.

## Parts 3–4: one calculation, then rules and views

Part 4's calculation owner first supplies one backend occupancy/forecast function using G01/G05/G06 inputs. Part 3 invokes eligibility, occupancy/forecast and rules, then persists their output together. G09 consumes the calculation portion of G17, not its UI. The G17 chart consumes the saved result. No dependency cycle, second algorithm or additional goal is needed.

The immutable saved result includes `run_id`, demo clock, ledger revision, selected source-run IDs, rule version, pool capacity, occupancy, p95 value/status/window/sample counts, forecast value/status/basis and findings with evidence references. Retain old runs and their inputs for pinned reads; G16's historical comparison UI is still stretch.

| Calculation | Decision |
|---|---|
| Occupancy | Distinct active assignable IPv4 addresses at a sample time; renewals do not inflate counts. Out-of-range/excluded observations remain discrepancies, not denominator adjustments |
| 30-day p95 | 720 hourly samples from window start through end minus one hour; nearest-rank sorted item `ceil(0.95*n)` with one-based indexing. All 720 must be eligible; never fill missing samples with zero |
| Sampling claim | Hourly demo approximation to the source's minute occupancy/five-minute state model; always expose interval, window and coverage |
| Forecast | Ordinary least squares of daily p95 occupied-address counts against elapsed days, over 14–30 consecutive complete days through the last completed demo day; each day needs 24 eligible samples |
| Exhaustion basis | Latest complete daily p95 and positive slope estimate days to 100% assignable capacity; show current occupancy separately |
| Forecast states | Invalid capacity/missing current evidence → unavailable; current or baseline full → exhausted; insufficient/inconsistent history → unavailable; nonpositive growth → no positive growth; otherwise compute estimate |
| Distant estimate | Beyond 365 days, show beyond the illustrative one-year horizon without inventing/clamping a calendar date; retain mathematical basis |
| Scope/capacity change | Invalidate the fit until a consistent minimum history exists |
| Candidate totals | Union assignable candidate IPv4 intervals per scope after exclusions. Label addresses in candidate pools, never proven recoverable addresses. Keep IPv6 prefix counts separate |

The 14–30-day forecast can be eligible even when 30-day p95 is unavailable. Source thresholds are **pressure p95 >=80% OR valid days-to-full <60**, and **oversized 30-day p95 <50%**. A known-true pressure branch makes the OR true; two known-false branches make it false; otherwise return unknown. Exhausted is zero days; no positive growth makes the forecast warning branch false, while unavailable evidence makes it unknown. Do not reintroduce the rejected 90%/10% proposal.

Zombie candidates require a DHCP-managed intended/assigned pool, fresh eligible routing presence and complete 30-day DHCP coverage without any positive-duration lease overlap. They are investigation candidates only. Routing policy is `exact` by default or explicitly `covering`; any active eligible route establishes presence, but a missing expected route requires a complete declared view. Unknown new evidence cannot resolve a previous anomaly.

Severity and evidence state are separate. Initial severities: assignment conflict critical; capacity/route/scope discrepancies high; inactivity/oversized/metadata warning. Unknown is an evidence state, not a low-severity healthy result.

## Parts 1–5: API and UI

- Lists use offset pagination, default 50/max 200, returning items/total/limit/offset. Stable opaque UUIDs identify objects in URLs. Inventory sorts by scope/family/numeric network/prefix length/ID; findings by severity/rule/subject/ID.
- Errors use `{error:{code,message,details,request_id}}`. Input 422; forbidden 403; absent object 404; conflict 409; upload limit 413; processing failure 500; store busy 503. Safe details must be actionable without exposing stacks.
- New imports return 201; identical replay 200. Partial acceptance explicitly returns `application_status=partial`, counts and paginated rejects. HTTP success does not establish complete evidence.
- Reconciliation runs synchronously in one API worker with a nonblocking run lock; another trigger receives 409 `RUN_IN_PROGRESS`. No background queue or second worker is required.
- Overview, detail and export pin one `run_id`. A failed refresh retains the previous result with its original time and a clear failure/previous-result banner; it cannot relabel the old output as new.
- Inventory filters: scope, family, owner/tag and text/IP/CIDR. Finding filters: scope, rule, severity and evidence state. Exports inherit filters/run ID and record them.
- Explicit healthy/unknown labels and reasons accompany color. One responsive layout permits table overflow and reachable detail actions; no separate mobile app.

## Part 5: allocation details

- Use one small static IPv4 pool with an explicitly authoritative local ledger. A candidate must be within eligible ranges, outside exclusions, unassigned and without contradictory current assignments/reservations or eligible active DHCP claims. DHCP silence never proves availability.
- `pool_version` changes for relevant range/exclusion/policy/assignment mutations. Baseline version changes for intended-authority changes. Imports/reruns do not increment these tokens; approval still reads current eligible conflicting observations rather than old findings.
- Creation uses actor ID plus client idempotency key and canonical payload hash. Same payload returns the request; changed payload returns 409. Final requests are immutable; a fresh review uses a new request with `supersedes_request_id`.
- Approval checks actor/role, self-approval, exact candidate and reviewed/current versions in the allocation transaction. Success audit and allocation commit together. On timeout, fetch or retry the same request; never create another allocation to guess the outcome.
- Audit includes event/request/actor IDs, server-derived role, action/outcome, UTC time, nonempty reason, scoped address/pool, versions and before/after references. If failure audit cannot be written after rollback, return `audit_recorded=false` and log the loss visibly.
- SQLite busy timeout is three seconds, then 503 `STORE_BUSY`; no endless retries. A simulated downstream failure leaves the committed local allocation visible and reports local and simulated outcomes separately.

## Core and Part 6: state and recipient handoff

Core implements these behaviors; Spencer packages and documents them. Planned CLI names and paths remain in `CONTRACTS.md`.

- An unseeded service shows setup-needed UI; `/healthz` returns 503 with separate process/schema/data readiness booleans until initialized. Ready is 200; source freshness is a separate API concern. Do not configure readiness failures to cause a first-run restart loop.
- Seed is explicit and cannot overwrite initialized data. Normal startup never seeds/resets. Unsupported schema preserves the database and fails visibly without speculative migrations.
- Backup uses `sqlite3.Connection.backup` to a new destination. Reset and restore require stopped service and exclusive app-data access. Restore validates a temporary candidate's app identity, supported schema and SQLite integrity before replacing; preserve the old database and replace atomically.
- Reset requires `--confirm` and recognized app identity. Touch only the app database and its own sidecars within resolved `IPAM_DATA_DIR`; never recursively delete that directory or unrelated files.
- Support local filesystem data paths and local Docker volumes/bind mounts. Network filesystems are excluded. A missing/unwritable location fails with resolved path, runtime UID and useful guidance; never silently fall back to ephemeral storage.
- G27 restart/persistence acceptance requires G21/G22 allocation/audit records, as well as seed/package. Packaging can be prepared sooner; this does not make `PART6_READY` true.
- Handoffs include repo URL, exact pushed branch/SHA, integration base SHA, contract revision, goal IDs, owned paths, merged/unmerged dependencies, behavior, missing entrypoints, blocker and next action.

## Completion discipline

Freeze new features at lead hour 14. Keep the 30-goal denominator and binary evidence-backed completion; broken provenance, calculation consistency, allocation controls or recipient startup/persistence block release regardless of the score. Tie evidence to commit, fixture/scenario and run/clock. A later edit reopens affected goals and direct dependencies, not every unrelated passing behavior. No runtime checks have been performed during this planning work.
