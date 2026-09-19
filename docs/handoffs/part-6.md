# Spencer's agent: start here for Part 6

Repository: https://github.com/yugant99/IpManagement

Assignment: **portable delivery**, approximately 6–8 hours. No presentation work. This supersedes earlier planning that assigned Spencer the allocation workflow.

## Current pickup state

The repository currently contains planning/coordination documents. There is no application to run yet. Read `docs/STATUS.md` first on every pickup; the lead will set `PART6_READY` when actual runtime prerequisites exist.

During the present planning stage, this document is a handoff specification, not a request to provision a VM or execute containers. During an authorized implementation turn, you can prepare packaging against the frozen contract while core finishes the app.

## Read order

1. `AGENTS.md` and `DEVELOPMENT_RULES.md`.
2. `docs/STATUS.md` and `docs/ARCHITECTURE.md`.
3. `docs/CONTRACTS.md`, especially runtime, file ownership and readiness.
4. `docs/parts/06-portability.md` and goals G26–G28/G30 in `docs/GOALS.csv`.
5. The Part 6 row in `docs/SKILLS.md`.

Do not require the previous chat, source customer files or a separate planning interview. Facts come from the repo; missing core interfaces go to the lead.

## Branch and ownership

Start each distinct feature from current `main` on a separate branch. First feature: `codex/part-6-container-startup`. Later backup/operator improvements can use a separate `codex/part-6-...` branch after their prerequisite is merged. Use an isolated worktree if another agent shares the checkout.

Own root `Dockerfile`, `compose.yaml`, `.dockerignore`, `scripts/ops/`, `docs/RUNNING.md`, this handoff and the Part 6 task page. Coordinate small README runtime updates with the lead. Do not edit business rules, shared schemas, application entrypoints, frontend dependencies or locks independently.

One coherent change per commit; push after three changes/commits, earlier on handoff. Open a focused PR. The lead coordinates review and merge; preserve coherent commit history.

## Core prerequisites — do not guess these

| Required input | Canonical contract |
|---|---|
| Installed backend module | `backend/ipam_demo`, importable as `ipam_demo` |
| Server | `python -m ipam_demo serve --host 0.0.0.0 --port 8000` |
| Built frontend | React/Vite `frontend/dist`; relative `/api` URLs; served by API |
| Static path | `IPAM_STATIC_DIR`, set by the package |
| Persistent data | `IPAM_DATA_DIR`; image `/data`; database `ipam_demo.sqlite3` |
| Health | `/healthz`, plus source-catalog freshness through core API |
| State commands | Core-provided `seed`, `reset`, `backup`, `restore` per `CONTRACTS.md` |
| Dependencies | Core-committed backend lock/install metadata and frontend lock |
| First packaged target | Ordinary Linux amd64; report additional platform evidence separately |

These are planned interfaces until status marks them implemented. A placeholder web server or fabricated health response cannot satisfy Part 6.

## Minimum deliverable

- One app image with compiled UI; no frontend development server at runtime.
- Compose configuration for ordinary Docker hosts, local published port bound to loopback and explicit persistent writable volume/path.
- Dependency installation follows committed locks. No developer absolute paths, bundled credentials or accidental source-document copies.
- Initial data setup is explicit and deterministic. Normal restart must retain requests, allocations, findings and audit.
- Reset requires the explicit confirmation flag and targets only configured demo state.
- Wrap/document the core's consistent backup/restore entrypoints. Do not implement a competing schema-aware persistence layer or naïvely copy a live SQLite file.
- `docs/RUNNING.md` gives supported target, prerequisites, exact startup/shutdown/state commands, data location, errors, dependency/license list and next-agent pickup.
- Record what was actually run and observed, and what remains unverified. Runtime checks follow current user authorization and lean-verification rules.

## Suggested work order and stop rules

1. Spend 30–60 minutes reading the contract and checking which prerequisites actually exist.
2. Implement package/startup files against the declared interfaces. Report missing paths/commands to the lead, without renaming the core app to fit your template.
3. Connect persistence and explicit state commands. Keep the app operationally simple.
4. Add diagnostics and short recipient documentation; use the remaining time for integration repairs.
5. When the core is ready and runtime checks are authorized, obtain the decisive startup/restart/state evidence on the declared target. Do not repeatedly run broad application suites.

If blocked around 15 minutes, send the lead: missing interface, expected contract, observed state, impact, and work you can continue. Do not rent infrastructure, pull an unrelated platform or create a mock success to remove the blocker.

Second CPU architecture, second host or Sunday VM are stretch. No cloud resource or public deployment is authorized by this handoff.

## Paste-ready task for Spencer's agent

> Work on Part 6 of yugant99/IpManagement: portable delivery, within 6–8 hours, with no presentation assignment. Read AGENTS.md, DEVELOPMENT_RULES.md, docs/STATUS.md, docs/CONTRACTS.md, docs/parts/06-portability.md and docs/handoffs/part-6.md. Confirm current authorization and PART6_READY before runtime work. Use a separate codex/part-6-feature branch for each feature and respect owned paths. Package the existing application into one portable service with persistent data and documented explicit seed/reset/backup/restore. Do not change the architecture, application schema or dependency locks independently; do not provision a VM. Commit each coherent change and push after three or before handoff. Use the Part 6 skill mapping without setup/telemetry/full-suite pipelines. Report exact branch/commit, what works, simulated/unverified behavior, actual checks, blocker and next action. Open a focused PR for lead-coordinated review and merge.

## Current lane handoff

Owner: Spencer / Part 6. Branch/commit: not started; choose the current integration baseline at pickup. Pushed implementation: none. Working application: none yet. Next action: read status and contracts, then take the first authorized packaging feature once assigned. This line must be replaced with actual branch/commit/results when work starts.
