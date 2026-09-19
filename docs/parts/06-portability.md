# Part 6: portable delivery — Spencer

Owner: Spencer and his agent. Budget: approximately 6–8 hours. Core goals: G26–G28 and G30. Stretch: G29. Branch: `codex/part-6-portability`.

Start at [the pickup handoff](../handoffs/part-6.md). No presentation work is assigned. Parts 1–5 belong to the core team.

## Win

Another person can start the same application, preserve its data, reset the synthetic scenario deliberately, and resume development without the original chat or a permanently rented host.

## Inputs

Consume the exact runtime/build/data contract in `docs/CONTRACTS.md`. Core supplies the actual app module, committed locks, UI build, health response and seed/reset/backup/restore commands. Read `PART6_READY` in status before treating the app as runnable.

## Owned files and output

Own root `Dockerfile`, `compose.yaml`, `.dockerignore`, `scripts/ops/`, this task page, `docs/handoffs/part-6.md` and `docs/RUNNING.md`. Package one service with compiled UI and external writable SQLite storage. Document supported host, startup, health, seed/reset, backup/restore, failure diagnosis and dependency/license inventory.

Do not modify schema, business rules, app module names, dependency versions/locks or shared frontend wiring without the lead. Package the existing contract instead of inventing a second application entrypoint.

## Acceptance and limits

On the declared target, documented startup serves UI and API. Restart preserves allocations/audit. Reset is explicit; backup/restore is consistent. Missing or unwritable data produces an actionable error. Record actual evidence and any unverified platform claims.

Primary packaged target is Linux amd64. The development Mac is arm64; cross-architecture support and a second host are stretch until exercised. No paid cloud dependency, VM rental, public URL, GPU, HA/DR promise or presentation responsibility.

## Timebox

0.5–1 hour context/contracts; 1–2 hours packaging/startup; 1–2 hours persistence/backup/reset; 0.5–1 hour health/diagnostics; 0.5–1 hour operator/agent docs; remainder integration repairs. If core entrypoints are missing, prepare files/docs and report the exact blocker. Do not claim startup succeeds against a placeholder service.
