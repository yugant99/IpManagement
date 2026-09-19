# Architecture grill: 75 explicit agent-to-agent questions

Status: **complete: 75 numbered questions and 75 answers**. This records actual messages between interviewer `/root/grill_architecture` and proposer `/root/coverage_20h`, under the user's explicit instruction to deepen the agent-to-agent review. The earlier two-round discussion remains historical; it was not a 75-question review. Wording below normalizes spacing for readability without inventing questions or answers.

Method: three batches of 25; each batch's answers are received before dispatching the dependent next batch. The current user request overrides the earlier two-round/ten-minute default for this pass. No user interview, application build, tests, installations or infrastructure actions are part of this review.

Completed groups: scope 5; data identity/time 9; imports 11; rules 10; capacity 8; API 7; UI 4; workflow 8; portability 7; parallel/Git 3; evidence 3. Total: 75. All questions reached confirmed or decided status; none remains an unresolved blocker. A decision is an implementation contract, not runtime evidence.

## Batch 1 — answered before batch 2 was dispatched

### Scope — 5 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q01 | At what hour of the 20-hour lead budget do we freeze new core features to protect integration and recipient handoff? | Freeze new feature work at hour 14; the remaining six hours cover integration repairs, authorized acceptance, packaging and handoff. Broken core paths may still be repaired. | decided |
| Q02 | If 22 core goals are not complete at freeze, what status/counting treatment prevents a reduced denominator or partly built goal becoming done? | Keep denominator 30 and binary pending/done goals with evidence. Incomplete goals stay pending without fractional credit; a broken release gate blocks a ready claim regardless of score. | confirmed |
| Q03 | Which public fixture domain labels should replace customer-specific topology/naming from source documents? | Use fictional North, Coastal, Central and Lab domains with `scope-north`, `scope-coastal`, `scope-central`, `scope-lab`. These labels assert no customer topology/geography. | decided |
| Q04 | What scale cap should bound the default synthetic dataset so the app and recipient package remain lightweight? | Four scopes, 60 prefixes, eight pools, 2,000 lease intervals and 200 route observations over 30 days. This is a demo sizing budget, not scale evidence. | decided |
| Q05 | Which document wins if an implemented API example contradicts CONTRACTS.md before the lead reconciles them? | CONTRACTS.md remains interface authority; the lead resolves and updates it before another lane relies on divergent code. Record the mismatch as drift rather than silently adopting it. | decided |

### Data identity and time — 9 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q06 | How should a noncanonical CIDR with host bits set be handled on import? | Reject it and retain the original value with an actionable error. Canonical text compression/case is permitted only after strict network parsing; never silently change the supplied network. | decided |
| Q07 | What typed value is required for scope identity when a source gives only a human region/domain label? | Require a string `scope_id` foreign key from the declared scope registry. Quarantine an unmapped row; do not infer isolation from a region label. | decided |
| Q08 | Must a declared parent-child relation exist before same-scope containment counts as legitimate hierarchy? | Yes: require `parent_id` and verified same-scope/address-family containment. Otherwise report unresolved overlap. | decided |
| Q09 | How do we represent overlapping sibling pools without a uniqueness constraint hiding the conflict? | Preserve separate pool/source records with stable IDs and emit overlap evidence; do not globally deduplicate raw observations by CIDR. An invalid intended pool cannot allocate until resolved. | decided |
| Q10 | What interval convention makes a lease ending exactly when another starts sequential reuse? | Use half-open intervals `[start,end)`. Equal end/start boundaries do not overlap. | decided |
| Q11 | What timezone/timestamp representation do we accept and persist? | Accept RFC3339/ISO8601 with explicit timezone offsets, normalize to UTC, and persist millisecond epoch values while raw evidence retains original text. Reject timezone-naive timestamps. | decided |
| Q12 | What happens to a DHCP lease interval with no expiry? | Retain the raw record but reject it from occupancy with a missing-expiry reason and mark affected coverage incomplete. Do not invent a lifetime or treat it as active forever. | decided |
| Q13 | How is static versus DHCP management declared, and what happens to DHCP evidence on a static pool? | Each pool has `management_mode` of `dhcp` or `static`. Leases on a static pool produce a policy/data discrepancy without activating DHCP inactivity/reclaim rules. | decided |
| Q14 | Can assignable ranges exceed or overlap the pool prefix/exclusions? | Ranges must lie within the pool prefix without overlapping each other; exclusions must lie within their union. Invalid configuration makes capacity unavailable and blocks allocation, percentages and forecasts. | decided |

### Imports and source eligibility — 11 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q15 | Which input format is core: canonical JSON, CSV, or both? | One versioned canonical JSON envelope containing source metadata and records is core. CSV adapters are stretch; specified CSV/report exports remain core. | decided |
| Q16 | What upload size and row-count limits apply? | Refuse imports over 10 MiB or 10,000 records before mutation; report limits and observed size/count. API and UI show the same limits. | decided |
| Q17 | Can an import with bad rows be accepted partially and still claim completeness? | Accept valid rows while retaining rejected/duplicate statuses. Any rejected required observation row forces effective completeness false; positive evidence may remain usable, absence claims may not. | decided |
| Q18 | Which counts account for every input row when duplicates are skipped? | `input_rows = accepted_rows + rejected_rows + duplicate_rows`, with exclusive statuses. Identical whole-batch reimport returns the original receipt and adds no rows, runs or effects. | decided |
| Q19 | What makes whole-batch reimport idempotent without hiding changed content? | Use `(source_id, source_run_id)` plus SHA256 of canonical normalized-envelope JSON. Same key/hash returns the original receipt; same key/different hash returns HTTP 409. | decided |
| Q20 | Which of overlapping valid observation batches becomes active? | Latest accepted server ingestion sequence selects one batch per source and declared scope, retaining its coverage window. Never silently merge windows or fall back from an incomplete new active batch to an older apparently healthy result. | decided |
| Q21 | Is source completeness just a boolean? | Require scope, window start/end, snapshot/interval kind, declared complete flag, and validation outcome. A boolean alone cannot establish coverage. | decided |
| Q22 | What default freshness thresholds apply to DHCP and routing evidence? | Illustrative configured defaults are DHCP 30 minutes and routing five minutes, measured from covered/snapshot end. Display these as demo policies, not real operational requirements. | decided |
| Q23 | Does freshness use wall time or the demo clock? | Evaluate against fixed `demo_clock_at` saved with each calculation run. Display demo and ingestion/wall-clock time separately so replay cannot masquerade as live data. | decided |
| Q24 | What happens to observations dated after the selected demo clock? | Quarantine future start/observation timestamps; a lease expiry may extend beyond demo time. Such observations cannot contribute until a later explicit demo-clock calculation. | decided |
| Q25 | Do saved runs keep original evidence after newer source batches become active? | Yes: retain immutable source-run/record references, demo clock, rule version and intended-ledger revision. New batch selection affects only new calculations. | confirmed |

## Batch 2 — answered before batch 3 was dispatched

### Detection rules — 10 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q26 | What window/coverage condition makes the 30-day zero-DHCP candidate evaluable? | Evaluate `[demo_clock_at - 30 days, demo_clock_at)` only for a DHCP-managed intended/assigned pool, with eligible fresh routing presence and complete DHCP coverage of the entire window. Any positive-duration lease overlap disqualifies it; touching an excluded boundary does not. | decided |
| Q27 | What eligibility predicate and threshold define oversized-pool detection? | Final: an IPv4 DHCP-managed pool with valid capacity and complete 30-day coverage is oversized when p95 occupancy is strictly below 50%; emit a review candidate only. The original 10% proposal was corrected after the lead identified deck slide 15's 50% rule and the proposer reread the source assessment. | decided |
| Q28 | When can a covering aggregate route satisfy expected child announcement? | Store `route_match_policy` as `exact` or `covering`, defaulting to exact. Only explicitly configured covering mode accepts an eligible containing route. | decided |
| Q29 | How do we derive route presence without treating a historical add as permanent? | Core input uses explicit bounded half-open validity intervals rather than add/withdraw parsing. Presence requires `valid_from <= demo_clock_at < valid_until`; missing bounds cause rejection/incomplete evidence, while a future end is allowed. | decided |
| Q30 | Must all eligible routing peers agree on presence? | Any active observation in the configured eligible view establishes positive presence. Negative conclusions require complete view coverage; do not build peer consensus. | decided |
| Q31 | Where is the managed-space perimeter declared? | Each scope has fixed `managed_cidrs`, independent of the inventory being checked. Only prefixes inside that perimeter are eligible for unregistered-managed-route detection. | decided |
| Q32 | What if the configured routing view is absent or incomplete for a prefix expecting announcement? | Return unknown with the missing view named. Show the expected policy separately; do not call the prefix stranded. | confirmed |
| Q33 | What distinguishes duplicate copies from incompatible simultaneous assignments? | Equal scope/address/principal and identical validity bounds are duplicate copies, counted once with provenance retained. Overlapping intervals for different principals or contradictory ownership conflict; sequential reuse is valid. | decided |
| Q34 | Which severity defaults and capacity-pressure cutoff apply? | Final: pressure is p95 at least 80% OR valid days-to-full below 60, using the same forecast as G17; conflict is critical, capacity/route/scope discrepancy high, inactivity/oversized/metadata warning, insufficient evidence unknown. The original 90% proposal was corrected against deck slide 15; for the OR condition, known true wins, both known false yield no pressure, otherwise unknown. | decided |
| Q35 | Can an anomaly be resolved when a newer incomplete run no longer detects it? | No: current evaluation becomes unknown and prior anomaly remains last-known evidence. Only a complete eligible evaluation establishing absence of the rule condition can resolve it. | confirmed |

### Capacity and forecast — 8 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q36 | What sampling window/interval and percentile definition define p95? | Use 720 hourly samples across the 30-day half-open window, from window start through end minus one hour. Nearest-rank p95 is sorted element `ceil(0.95*n)` using one-based indexing; display interval/window/count/definition. | decided |
| Q37 | What sample coverage is required, and are gaps filled as zero? | Require all 720 eligible samples for the published 30-day p95 component and oversized evaluation. Never zero-fill; the pressure rule's independent forecast branch may still establish pressure from its own eligible 14–30-day history when full-window p95 is unavailable. | decided |
| Q38 | What minimum/horizon supports forecasting? | At least 14 consecutive complete daily summaries through the latest completed demo day, using at most 30 days. A capacity/scope change invalidates the fit until a consistent minimum window exists. | decided |
| Q39 | Which daily statistic and fitting method define forecast growth? | Fit ordinary least squares to daily p95 occupied-address counts against elapsed days. Use latest complete daily p95 as baseline; show instantaneous occupancy separately. | decided |
| Q40 | Does exhaustion target the warning threshold or full assignable capacity? | Forecast 100% configured assignable capacity. Threshold-crossing forecasts are outside core; the warning cutoff itself must follow corrected Q34. | decided |
| Q41 | What ordering handles invalid/full/insufficient/no-growth forecast states? | First reject invalid capacity or missing current evidence; then report current occupancy at capacity as exhausted; then reject inconsistent/insufficient history; then report nonpositive slope as no positive growth. Otherwise compute remaining capacity from the latest daily p95 divided by positive slope, treating an already-full baseline as exhausted. | decided |
| Q42 | What if the mathematical exhaustion date is extremely distant? | Beyond 365 days, display “beyond the illustrative one-year horizon” without a calendar date. Retain the mathematical basis; never clamp the estimate and present the clamp as a prediction. | decided |
| Q43 | How do candidate totals avoid overlaps and IPv4/IPv6 mixing? | Union configured assignable IPv4 intervals per scope, subtract exclusions, and label the result addresses in candidate pools rather than proven recoverable space. IPv6 remains prefix/delegation counts and is never added to IPv4 address totals. | decided |

Hourly sampling is an explicitly bounded demo approximation: the source deck describes minute-level lease occupancy and five-minute block state. Complete 24-sample days can independently support the 14–30-day forecast even when the full 720-sample p95 is unavailable. Both interval and completeness must remain visible. Pressure consumes the same backend forecast output used by G17; the UI is not a calculation dependency and no second algorithm is introduced.

### API contracts — 7 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q44 | What list pagination and deterministic ordering apply? | Offset pagination defaults to 50, caps at 200, and returns items/total/limit/offset. Inventory sorts by scope, family, numeric network, prefix length and ID; findings by severity, rule, subject and finding ID. | decided |
| Q45 | What identifier belongs in prefix detail URLs? | Stable opaque UUID `prefix_id`: deterministic for seeded objects, generated for new objects. CIDR text is data, not path identity. | decided |
| Q46 | What error envelope/status mapping applies? | Use `{error:{code,message,details,request_id}}` with safe actionable detail. Map invalid input 422, forbidden 403, missing object 404, conflict 409, upload limits 413, processing failure 500; no UI stack traces. | decided |
| Q47 | How does reconciliation run and reject concurrent triggers? | Run synchronously in the single API process with a nonblocking in-process lock. A competing trigger receives 409 `RUN_IN_PROGRESS`; multiple Uvicorn workers would require revisiting this contract. | decided |
| Q48 | How does the client avoid mixing different calculation runs? | Fetch the latest run ID, then pin subsequent overview/detail/export reads with a `run_id` parameter. Responses echo that ID and evidence metadata; new runs never mutate old output. | decided |
| Q49 | What does a partially rejected import return? | Return a receipt: 201 for a new batch, 200 for identical replay, with `application_status=partial` and explicit row counts. Link paginated rejected rows/reasons; transport success is not evidence completeness. | decided |
| Q50 | What does readiness report separately from source quality? | `/healthz` returns 200 only when process, schema and initialized data are ready; otherwise 503 with separate booleans and `status=not_ready`. Source freshness belongs in source-quality APIs, not app readiness. | decided |

## Batch 3 — answered after both prerequisite batches

### User interface — 4 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q51 | What does the dashboard display while rerunning or after refresh failure? | Retain the previous pinned output with a “Previous result” banner, original run/time, and current running/failed refresh state. Never update its timestamp or imply it is new output. | decided |
| Q52 | Which filters are core and should exports inherit them? | Inventory: scope, address family, owner/tag, text/IP/CIDR search; findings: scope, rule/type, severity, evidence state. Exports inherit selected filters and run ID and record these in metadata. | decided |
| Q53 | How is unknown distinguished from healthy and severity without color alone? | Use explicit “Unknown / insufficient evidence” and “Healthy / evaluated” labels, distinct icons, and an unknown reason. Severity and evidence state are separate fields. | decided |
| Q54 | What minimum responsive behavior keeps tables usable? | Use one responsive layout: desktop tables, horizontal overflow when narrow, wrapping evidence panels and reachable detail actions. No separate mobile app, gesture system or unreadable column compression. | decided |

### Allocation workflow — 8 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q55 | Which management mode and eligibility checks apply to the allocation pool? | Use one small static IPv4 pool with explicitly authoritative local ledger. Exclusions, out-of-range candidates, active assignments/reservations, conflicts and observed active DHCP claims make an address ineligible; DHCP silence alone never proves availability. | decided |
| Q56 | Which changes invalidate the reviewed concurrency token? | Increment pool version for ranges/exclusions/assignment state/policy changes; baseline version changes only with intended-authority change. Imports and reruns do not increment those tokens, but approval rechecks current conflicting evidence. | decided |
| Q57 | What makes request creation safe to retry? | Store a client idempotency key unique with actor ID and a canonical payload hash. Same key/payload returns the original request; changed payload returns 409. | decided |
| Q58 | Can terminal requests be edited or reused? | Approved/rejected records are immutable; a stale/conflicted proposal cannot silently become a different one. Renewed review creates a fresh request with `supersedes_request_id` and current candidate/versions. | decided |
| Q59 | How does a client recover from an approval timeout? | Read the persisted request by ID or retry the same action for that request. Return the committed outcome without another allocation/success-audit effect; timeout alone establishes neither success nor failure. | decided |
| Q60 | What if simulated provisioning fails after local allocation commits? | Keep the allocation and display local success and simulated external failure separately. Do not silently roll back or claim external success. | confirmed |
| Q61 | Which fields are mandatory decision audit evidence? | Event/request/actor IDs, server-derived role, action/outcome, UTC time, nonempty decision reason, scoped pool/address, reviewed/current versions and before/after references. Failed attempts also carry safe error details; allocation and success audit commit together. | decided |
| Q62 | How are store-busy and failure-audit errors handled? | Use a three-second SQLite busy timeout, then 503 `STORE_BUSY` with retry guidance and no success claim. If failure audit also fails, preserve the main error, return `audit_recorded=false`, and log the loss without indefinite retries. | decided |

### Portable delivery — 7 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q63 | How does a fresh package remain usable before seeding despite readiness 503? | Start the service with a setup-needed page and `data_ready=false` readiness response. Document explicit seed as first-run action; health checks must not cause a restart loop, and startup never silently seeds/resets. | decided |
| Q64 | What backup mechanism handles SQLite WAL/journal state consistently? | Core uses `sqlite3.Connection.backup` into a new destination. Never copy the active main database file as the backup mechanism. | decided |
| Q65 | How does restore reject bad data before changing the current database? | Validate a temporary read-only candidate for app identity, supported schema and SQLite integrity first. Require stopped service plus exclusive app-data lock, preserve the old database, then atomically replace with the validated candidate; no speculative migration. | decided |
| Q66 | Which data-directory storage types are supported? | Local filesystem directories and local Docker volumes/bind mounts on declared supported hosts. Exclude NFS/SMB/network filesystem data mounts. | decided |
| Q67 | How does reset stay inside the application's own database? | Require `--confirm`, stopped-service exclusive lock and recognized app identity. Report and touch only `ipam_demo.sqlite3` and its own sidecars inside resolved `IPAM_DATA_DIR`; never recursively delete the directory or unknown files. | decided |
| Q68 | What happens to an unsupported schema on startup? | Refuse with an actionable unsupported-version error and preserve the database. No destructive downgrade or migration framework this weekend. | decided |
| Q69 | What happens when the data mount is missing or unwritable? | Create the data directory only if its parent allows it; otherwise exit nonzero with resolved path, runtime UID and mount guidance. Never silently use ephemeral storage or chmod arbitrary directories. | decided |

### Parallel work and Git — 3 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q70 | How do concurrent lanes coordinate dependency-lock/schema additions? | Lead owns shared schema/locks; lanes submit the smallest delta and wait for its integration commit before relying on it. Coordinate baseline updates instead of independently regenerating incompatible locks/migrations. | confirmed |
| Q71 | How does the three-change push rule work at an unfinished handoff? | Commit the coherent checkpoint and push immediately even with fewer than three commits. State unfinished/unverified behavior; no empty commits or artificial splitting. | confirmed |
| Q72 | What minimum handoff prevents stale/unmerged dependency assumptions? | Include repo URL, branch, exact pushed SHA, integration base SHA, contract revision, goal IDs, owned paths, current behavior, required branches, next action and blockers. State merged/unmerged dependencies and proposed commands still absent. | decided |

### Evidence and release claims — 3 questions

| ID | Question actually sent | Answer | Status |
|---|---|---|---|
| Q73 | What evidence pointer allows a goal to become done? | Tie observed acceptance to exact commit, fixture/scenario and run/clock, with limitations. A screenshot cannot establish hidden calculations/persistence, and authored criteria or code inspection cannot demonstrate runtime behavior. | decided |
| Q74 | Which release gates can block readiness despite achieving 22/30? | Broken provenance, false healthy/reclaim conclusions, inconsistent totals, failed/duplicate allocation or role enforcement, and unproved recipient startup/persistence block readiness. A numerical score cannot waive these gates or undisclosed simulation. | confirmed |
| Q75 | What happens when a later edit invalidates earlier evidence? | Mark only affected goals pending revalidation and earlier evidence superseded for the new commit, retaining history. Check changed behavior/direct dependencies; preserve unrelated valid evidence rather than rerunning everything. | decided |

## Correction trail and outcome

The proposer initially invented 10% oversized and 90% pressure cutoffs. The lead caught the conflict; the interviewer read the existing deck assessment, challenged the same Q27/Q34 answers, and the proposer explicitly corrected them to below 50% oversized and at least 80% OR fewer than 60 days to full for pressure. The correction is part of these same numbered questions, not additional questions counted toward 75.

Other numeric choices are labeled engineering/demo defaults where the source is not prescriptive: dataset/import caps, freshness windows, hourly approximation, forecast history/horizon, pagination, and busy timeout. The chosen thresholds do not convert hourly sampling into parity with minute-resolution source requirements.

No implementation or runtime result follows from this discussion. The lead integrated the resulting decisions into `CONTRACTS.md`, `IMPLEMENTATION_DECISIONS.md`, the goal dependencies and part handoffs. Those canonical documents govern implementation; this record preserves the exchange and its correction trail.
