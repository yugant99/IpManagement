# Spencer's agent: start here for Part 6

Repository: https://github.com/yugant99/IpManagement

Assignment: **portable delivery**, approximately 6–8 hours. No presentation work. This supersedes earlier planning that assigned Spencer the allocation workflow.

## Current pickup state

The accepted application is on main at `376dd52f9457dd0b7fecc8d83a3e0d6970bb487e`. Core schema-5 state commands and feed interfaces exist. Read `docs/STATUS.md` and the latest lead instruction on pickup; `PART6_READY=no` denotes missing portable runtime/recipient evidence, not missing core source.

This source/operator handoff does not authorize VM provisioning or container execution. Runtime evidence requires a separate authorization.

## Read order

1. `AGENTS.md` and `DEVELOPMENT_RULES.md`.
2. `docs/STATUS.md` and `docs/ARCHITECTURE.md`.
   The architecture/deployment section of `docs/QUESTIONNAIRE_PRIORITIES.md` identifies what packaging can substantiate and what remains a production gap. No need to read every application row.
3. `docs/CONTRACTS.md`, especially runtime, file ownership and readiness.
   Its companion `docs/IMPLEMENTATION_DECISIONS.md` has a short **Core and Part 6** section; no need to reread the full grill transcript.
4. `docs/parts/06-portability.md` and goals G26–G28/G30 in `docs/GOALS.csv`.
5. The Part 6 row in `docs/SKILLS.md`.

Do not require the previous chat, source customer files or a separate planning interview. Facts come from the repo; missing core interfaces go to the lead.

Main Lead 3.0 (`01a0c0c1-3952-7720-93c8-ff49192b8e13`) is the user-authorized lead; prior leads are reference-only. Report pushed branch/SHA/PR, implemented versus observed behavior, gaps and blockers through the repository handoff. The lead reviews acceptance, global status and main integration; Spencer's agent does not replace this ownership. External agent conversations need not be accessible. See `docs/PROJECT_OVERSIGHT.md`.

## Branch and ownership

Historical PR #49 began at Stage 2 `8a1a1227`. PR #50 incorporated accepted main and compatibility fixes; PR #51 includes both exact histories and the operator handoff. Current source review must use that combined candidate, not the old Stage 2 application.

Use isolated `codex/part-6-...` branches for further changes and preserve the existing coherent commits.

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

These core interfaces exist in the accepted source; their presence does not establish container runtime success.

## Minimum deliverable

- One app image with compiled UI; no frontend development server at runtime.
- Compose configuration for ordinary Docker hosts, local published port bound to loopback and explicit persistent writable volume/path.
- Dependency installation follows committed locks. No developer absolute paths, bundled credentials or accidental source-document copies.
- Initial data setup is explicit and deterministic. Unseeded readiness is 503 with setup-needed UI; do not create health-driven restart loops before seed. Normal restart must retain requests, allocations, findings and audit.
- Reset requires the explicit confirmation flag, stopped service and exclusive app-data access; touch only recognized app state. Never delete the entire mounted directory.
- Wrap/document core's SQLite-backup-API entrypoint and validated stopped-service restore. Core implements app identity/schema/integrity checks and database correctness. Do not implement a competing persistence layer or copy a live SQLite main file.
- Support local filesystem mounts/volumes only; fail visibly for unwritable data without silent ephemeral fallback. State unsupported schema and target-platform limits plainly.
- `docs/RUNNING.md` gives supported target, prerequisites, exact startup/shutdown/state commands, data location, errors, dependency/license list and next-agent pickup.
- Record what was actually run and observed, and what remains unverified. Runtime checks follow current user authorization and lean-verification rules.

## Suggested work order and stop rules

1. Spend 30–60 minutes reading the contract and checking which prerequisites actually exist.
2. Implement package/startup files against the declared interfaces. Report missing paths/commands to the lead, without renaming the core app to fit your template.
3. Connect persistence and explicit state commands. Keep the app operationally simple.
4. Add diagnostics and short recipient documentation; use the remaining time for integration repairs.
5. When the core is ready and runtime checks are authorized, obtain the decisive startup/restart/state evidence on the declared target. G27 needs actual G21/G22 allocation/audit records for persistence evidence; a successful seed-only restart is insufficient. Do not repeatedly run broad application suites.

If blocked around 15 minutes, send the lead: missing interface, expected contract, observed state, impact, and work you can continue. Do not rent infrastructure, pull an unrelated platform or create a mock success to remove the blocker.

Second CPU architecture, second host or Sunday VM are stretch. No cloud resource or public deployment is authorized by this handoff.

## Paste-ready task for Spencer's agent

> Work on Part 6 of yugant99/IpManagement: portable delivery, within 6–8 hours, with no presentation assignment. Read AGENTS.md, DEVELOPMENT_RULES.md, docs/STATUS.md, docs/CONTRACTS.md, docs/parts/06-portability.md and docs/handoffs/part-6.md. Confirm current authorization and PART6_READY before runtime work. Use a separate codex/part-6-feature branch for each feature and respect owned paths. Package the existing application into one portable service with persistent data and documented explicit seed/reset/backup/restore. Do not change the architecture, application schema or dependency locks independently; do not provision a VM. Commit each coherent change and push after three or before handoff. Use the Part 6 skill mapping without setup/telemetry/full-suite pipelines. Report exact branch/commit, what works, simulated/unverified behavior, actual checks, blocker and next action. Open a focused PR for lead-coordinated review and merge.

## Current lane handoff

Owner: Spencer / Part 6. Feature: operator handoff (rich-seed wrapper, state-command wrappers, corrected runbook). Branch: `codex/part-6-operator-handoff`, based on `codex/part-6-build-compat-fix @ 3e129d9` (PR #50, which itself packages current accepted main plus the Main Lead 2.0 compat fixes on top of the earlier PR #49 commits). Contract revision: `demo-v2-questionnaire`. Predecessor: `codex/part-6-container-startup` (PR #49, superseded by PR #50's compat fixes).

Implemented on this branch (source and documentation, unrun):

- `scripts/ops/seed.sh` now defaults to the accepted rich scenario (`python -m ipam_demo seed --scenario rich --inventory /app/fixtures/v1/inventory.json`); `--scenario baseline` remains available for the older foundation scenario. It checks that the service is stopped and refuses when it is not.
- New `scripts/ops/acquire.sh` posts the accepted rich-demo payload (`actor_id=demo-approver`, `reason="Prepare initial rich demo"`, operator-supplied `idempotency_key`) to `POST /api/schedule/run`, distinguishing 200/201 success, 409 in-progress and transport failures.
- New `scripts/ops/backup.sh`, `restore.sh`, `reset.sh` wrappers around the core state commands with stopped-service enforcement and explicit `--confirm` handling. Snapshots live under `/data/snapshots/` (0700, created on first backup) inside the existing `ipam_demo_data` named volume; the preserved pre-restore database and lock file are documented as never removed automatically.
- New `scripts/ops/snapshots.sh` covers `list`, `export`, `import` and `remove` for the snapshot subdirectory using locked one-shot container streams.
- `scripts/ops/common.sh` now enforces Docker Compose v2 and provides `service_is_running` / `require_service_stopped`; the previously claimed unverified `docker-compose` legacy fallback is removed.
- `scripts/ops/start.sh` no longer implies "seed after start" (seed needs the exclusive lock and refuses to run alongside the service). `scripts/ops/migrate.sh` describes v1/v2/v3/v4 → current, not the stale v1→v2 claim.
- `docs/RUNNING.md` rewritten: rich-demo first-time setup, manual acquisition procedure, corrected logs/tail example, full state-command section referencing `docs/STATE_OPERATIONS.md`, snapshot storage semantics, dependency and license notes, and clearly separated "unverified behavior" recipient checks.
- `scripts/ops/README.md` updated to list every wrapper and drop the "Deliberately absent" reset/backup/restore claim.

Not run: no image build, container start, seed, migrate, health check, restart, backup, restore or reset has been executed on this branch. No application logic, schema, fixture, dependency lock, `frontend/`, `backend/` file, or lead-owned status/handoff/task page (except this one and `docs/parts/06-portability.md`) was edited. `Dockerfile`, `compose.yaml` and `.dockerignore` are left as PR #50 delivered them; this branch does not duplicate those fixes.

Blockers: recipient/target-host evidence session — image build on linux/amd64, seed→start→health→acquire, restart preserving G21/G22 allocation/audit, backup→restore cycle and confirmed refusal paths — is not authorized in this turn. `PART6_READY` remains `no`. Questionnaire accounting stays 32 Demonstrated / 22 Partial / 10 Documentary / 47 Missing out of 111.

Next action: Main Lead 3.0 reviews the bounded correction candidate before a history-preserving source merge. The recipient session, when authorized, exercises the flow documented above and records results into a follow-up handoff.

## Independent source correction of PR #51

Reviewed original `7f79f38bbde62dd0b3c13f7892a48ccfb6a19038` against
`376dd52f9457dd0b7fecc8d83a3e0d6970bb487e`. The original build/module/feed
fixes are present. The correction branch `codex/part-6-review-fixes` retains
the exact #49/#50/#51 heads and fixes these source findings:

- Snapshot export/import used `compose cp` although `stop.sh` removes the
  service container. Imports could overwrite existing snapshots and copied
  ownership did not establish app-user readability. One-shot app-user streams
  now work independently of a retained service container; imports are private,
  hash/size checked and published without overwrite. All transfer actions use
  the core data lock; restore alone owns SQLite validation.
- Backup/remove interpolated unrestricted filenames into `sh -c`. Backup
  now passes positional arguments and transfers never interpolate filenames
  into executable shell text. Linked files/companion files are refused.
- Stopped-service detection hid Compose failures as stopped. It now fails
  visibly. Startup and one-shot operations refuse image pulls; offline
  save/load instructions record source/image identity and checksums.
- Pickup instructions incorrectly said main was documentation-only; those
  instructions now point to the accepted application and current lead.

Source inspection only: no application tests, helper execution, Docker
commands, image builds/pulls, containers, VM/cloud operations or runtime
checks were performed. The lead must review the corrective delta before
merge. Runtime/recipient evidence and dependency license/notices inventory
remain open; source merge does not change `PART6_READY=no`.
