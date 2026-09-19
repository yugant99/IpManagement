# Stage 1 foundation interface

Contract: `demo-v2-questionnaire`, additive inventory API revision 1. Stage 1 source contract; runtime evidence pending. Implementation owner: `codex/part-1-foundation`. The persistent project lead retains acceptance and merge authority.

## Ownership and scope

Core owns `backend/ipam_demo/` (except delegated baseline data), root Python metadata/lock, frontend dependency metadata/lock, this contract and Stage 1 documentation. The UI lane owns `frontend/` excluding `package.json` and `package-lock.json` in its own worktree. The baseline lane owns `backend/ipam_demo/data/baseline.json` in its own worktree. The separate richer-data task owns `fixtures/`. Spencer retains all Part 6 packaging/runbook files. The persistent lead owns global `STATUS.md` and `CURRENT_HANDOFF.md`; this worker submits proposed updates in its report.

Stage 1 supplies intended inventory only: no import, observations, findings, allocation writes, inventory editing or live integrations. Those remain later-stage work. No test/runtime/build execution is authorized in this stage request. Dependency resolution generates lock artifacts; it is not runtime evidence.

## HTTP

All URLs are relative to the API origin. All lists return `{items, total, limit, offset}`, default 50, maximum 200. Read-only endpoints:

- `GET /healthz`: 200 only when process, schema and initialized data are ready; otherwise 503. Body: `{status, process_ready, schema_ready, data_ready, static_ready, code, reason, schema_version, contract_revision}`. `status` is `ready`, `setup_needed` or `error`; `code` is null when ready. `static_ready` is independent of data readiness. UI uses health even on HTTP 503; no restart loop or automatic seed.
- `GET /api/scopes`: scopes in stable name/ID order.
- `GET /api/prefixes`: filters `scope_id`, `family` (4/6), `owner`, `tag`, `q`; numeric network order within scope/family. Text searches CIDR, owner, purpose and tags case-insensitively; an IP finds containing prefixes and a CIDR finds intersecting prefixes. No scope filter means results may legitimately repeat private addresses.
- `GET /api/prefixes/{id}`: one prefix plus `pools` and `allocations` arrays for that prefix (direct associations, not recursive children).
- `GET /api/pools`: filters `scope_id`, `prefix_id`; intended ranges and exclusions, not occupancy.
- `GET /api/allocations`: filters `scope_id`, `prefix_id`, `pool_id`, `q` (address/owner/purpose or containing CIDR); intended IP assignments.

Inventory endpoints return 503 `SETUP_NEEDED` until explicit seed, or a visible store/schema error. Unknown API routes return JSON 404, never the UI HTML. Errors: `{error:{code,message,details,request_id}}`; response header `X-Request-ID` is server generated. Standard 422 input, 404 missing object, 503 store busy/readiness; no stack traces in responses.

## Payloads

IDs are stable UUID strings. Timestamps are UTC millisecond ISO strings. IPv6-sized address/capacity counts are decimal **strings**, never JavaScript numbers. `scope_id` is the isolation key; domain and region are display context only.

- Scope: `id, name, namespace, domain, region, managed_cidrs: string[], synthetic: true`.
- Prefix: `id, scope_id, scope_name, family, cidr, parent_id: string|null, owner, purpose, tags: string[], custom_fields: Record<string,string>, version: number, address_count: string, origin`.
- Pool: `id, scope_id, prefix_id, family, name, management_mode: dhcp|static, allocation_authority: local|external, ranges: {start,end}[], exclusions: {start,end}[], pool_version: number, capacity: string, origin`.
- Allocation: `id, scope_id, prefix_id, pool_id: string|null, family, address, owner, purpose, origin`.
- Origin: `source_id, source_run_id, source_record_id, observed_at, ingested_at, synthetic: true`. Original seed envelope remains stored separately from current ledger rows; no telemetry or current-use claim.
- Prefix detail adds `pools: Pool[]` and `allocations: Allocation[]` to the prefix object.

Seed envelope revision 1: `schema_version: 1, scenario: baseline, demo_clock_at, source_id, source_run_id, scopes, prefixes, pools, allocations`. Fixture records omit derived `scope_name`, counts and `origin`; each has `source_record_id`. Prefixes carry `version`, pools carry `pool_version`. App metadata tracks schema version and initial `baseline_version=1`. Scope fixture records use the same fields except `synthetic`, which the API derives. Pool fixture `family` derives from its prefix; allocation fixture explicitly includes `family`.

## UI states

Inventory reads persisted API data. Show synthetic intended-state labeling, scoped prefix list, scope/family/search filters, owner/purpose/tags and reachable detail including parent, metadata, source references, pools and IP assignments. Show loading, empty, setup-needed, error/retry and pagination explicitly. Never turn unavailable evidence into healthy/unused metrics. If a refresh fails, retain earlier visible data only with an explicit stale/error banner; clearing stale data is also valid.

## Runtime boundary

Root `pyproject.toml` installs `backend/ipam_demo` and packaged baseline. `uv.lock` pins the Python dependency graph; `frontend/package-lock.json` pins npm. Core supplies only `serve` and `seed` in Stage 1. `reset`, `backup`, `restore` remain unimplemented and fail CLI argument parsing if invoked; no placeholders claiming success. `PART6_READY=no`.

Create the configured local data directory explicitly. Startup creates only a recognized empty schema when the database is absent; it never seeds. Both serve and seed hold an exclusive `.ipam_demo.lock`, so stop the service before seeding and restart afterward. The lock uses Unix `flock` (native macOS/Linux only); it is not a distributed/network-filesystem lock. Failed startup remains diagnostic until restart. No Windows-native runtime or multi-worker support is claimed.
