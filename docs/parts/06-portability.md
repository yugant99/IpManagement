# Part 6: portable delivery — Spencer

Owner: Spencer and his agent. Budget: approximately 6–8 hours. Core goals: G26–G28 and G30. Stretch: G29.

Lane label: `codex/part-6-portability`. Feature branches follow `codex/part-6-<feature>`. Delivered so far: `codex/part-6-container-startup` (PR #49, packaging skeleton), superseded on packaging plumbing by `codex/part-6-build-compat-fix` (PR #50, Main Lead 2.0 compat repair with the rich feed producer and inventory packaging). The current branch `codex/part-6-operator-handoff` adds the rich-seed wrapper, state-command wrappers and the corrected runbook on top of PR #50.

Start at [the pickup handoff](../handoffs/part-6.md). No presentation work is assigned. Parts 1–5 belong to the core team.

Questionnaire revision keeps this lane's 6–8-hour scope unchanged. Packaging, state operations and diagnostics supply concrete deployment evidence; they do not automatically supply HA, hybrid networking, tenant isolation or scale evidence. The lead owns the added delivery-method/roadmap pack; Spencer supplies accurate operator and dependency facts from the actual package.

## Win

Another person can start the same application, preserve its data, reset the synthetic scenario deliberately, and resume development without the original chat or a permanently rented host.

## Inputs

Consume the exact runtime/build/data contract in `docs/CONTRACTS.md`. Core supplies the actual app module, committed locks, UI build, health response and seed/reset/backup/restore commands. Read `PART6_READY` in status before treating the app as runnable.

## Owned files and output

Own root `Dockerfile`, `compose.yaml`, `.dockerignore`, `scripts/ops/`, this task page, `docs/handoffs/part-6.md` and `docs/RUNNING.md`. Package one service with compiled UI and external writable SQLite storage. Document supported host, startup, health, seed/reset, backup/restore, failure diagnosis and dependency/license inventory.

Do not modify schema, business rules, app module names, dependency versions/locks or shared frontend wiring without the lead. Package the existing contract instead of inventing a second application entrypoint.

## Acceptance and limits

On the declared target, documented startup serves UI and API. Restart preserves allocations/audit. Reset is explicit; backup/restore is consistent. Missing or unwritable data produces an actionable error. Record actual evidence and any unverified platform claims.

G27 persistence acceptance needs actual G21/G22 workflow records; seed-only restart is insufficient. Core owns readiness/setup behavior, SQLite backup and stopped-service reset/restore correctness. Part 6 wraps these interfaces and uses local filesystem mounts, with no silent ephemeral fallback. See the Core and Part 6 section of `docs/IMPLEMENTATION_DECISIONS.md`.

Primary packaged target is Linux amd64. The development Mac is arm64; cross-architecture support and a second host are stretch until exercised. No paid cloud dependency, VM rental, public URL, GPU, HA/DR promise or presentation responsibility.

## Timebox

0.5–1 hour context/contracts; 1–2 hours packaging/startup; 1–2 hours persistence/backup/reset; 0.5–1 hour health/diagnostics; 0.5–1 hour operator/agent docs; remainder integration repairs. If core entrypoints are missing, prepare files/docs and report the exact blocker. Do not claim startup succeeds against a placeholder service.

## Current state on `codex/part-6-operator-handoff`

Source and documentation only, unrun. On top of PR #50 this branch adds:

- `scripts/ops/seed.sh` defaults to the accepted rich scenario (`--scenario rich --inventory /app/fixtures/v1/inventory.json`); `--scenario baseline` remains available.
- New `scripts/ops/acquire.sh` for the first manual acquisition against `POST /api/schedule/run`, preserving the caller's idempotency key across retries.
- New `scripts/ops/backup.sh`, `restore.sh`, `reset.sh` wrappers around the core state commands, with stopped-service enforcement, explicit `--confirm` handling and snapshots under `/data/snapshots/`.
- New `scripts/ops/snapshots.sh` (`list`/`export`/`import`/`remove`) for moving snapshots in and out of the data volume via `docker compose cp`.
- `scripts/ops/common.sh` enforces Docker Compose v2 (drops the unverified `docker-compose` legacy fallback) and exposes `require_service_stopped`.
- `scripts/ops/start.sh` and `migrate.sh` corrected: no more "seed after start" implication; migrate advertises the real v1/v2/v3/v4 → current range.
- `docs/RUNNING.md` rewritten around the rich demo, manual acquisition, state commands, snapshot storage and dependency/license inventory. Handoff and this task page updated.

`Dockerfile`, `compose.yaml` and `.dockerignore` are left exactly as PR #50 delivered them; this branch does not duplicate those fixes. No image was built, run, seeded, migrated, backed up or restored. `PART6_READY=no`. Questionnaire accounting unchanged.
