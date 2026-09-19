# Stage 1 native foundation

**Implemented source; runtime evidence pending.** This page records the core team's app/dependency interfaces, not Spencer's portable recipient runbook. `docs/RUNNING.md`, containers and state-operation wrappers remain Part 6 ownership. No commands in this page were executed as installation, build or runtime acceptance.

## Native setup

Python 3.12 is required; `.python-version` selects 3.12.10. `pyproject.toml` uses Hatchling 1.29.0 to install `backend/ipam_demo`, including its SQL and JSON resources. `uv.lock` pins the runtime graph. FastAPI is 0.141.1 and Uvicorn 0.50.1. React/React DOM 19.3.0, TypeScript 7.0.2, Vite 8.3.0 and its React plugin 6.1.1 are exact pins; npm's complete graph is in `frontend/package-lock.json`.

Use Node 22.12+ within major 22, or Node 24, with npm 10.9.2. The author's shell has Node 23.11.0; lock generation returned `EBADENGINE` for that unsupported major. A successful lock write does not establish build compatibility. No Node runtime was installed or switched during Stage 1.

From the repository root, the intended native setup is:

```sh
uv sync --frozen
source .venv/bin/activate
npm --prefix frontend ci
npm --prefix frontend run build
export IPAM_DATA_DIR="$PWD/data"
export IPAM_STATIC_DIR="$PWD/frontend/dist"
mkdir -p "$IPAM_DATA_DIR"
python -m ipam_demo seed --scenario baseline
python -m ipam_demo serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` after startup. API documentation is at `/api/docs`; OpenAPI is `/api/openapi.json`. The backend is installed into the environment, so the module and packaged seed do not depend on running inside the source checkout. Keep environment paths absolute when changing working directory.

For frontend development, `npm --prefix frontend run dev` binds loopback and proxies `/api` and `/healthz` to the API at `127.0.0.1:8000`. The delivered runtime design remains one API process serving compiled UI assets; the development server is not a packaging prerequisite.

## Data, static assets and readiness

- `IPAM_DATA_DIR` defaults to the resolved `./data`. The directory must already exist and be writable; failures show a safe reason plus directory/runtime UID in diagnostics. No temporary-store fallback. Local macOS/Linux filesystems only; no network mounts or Windows-native claim.
- SQLite file: `ipam_demo.sqlite3`; schema version 1, application ID `0x4950414D`. Startup creates an empty schema only when the database is absent. Unrecognized/unsupported databases are preserved and refused. No automatic migration, seed or reset.
- Both CLI commands hold `.ipam_demo.lock` using nonblocking Unix `flock`; one API process/seed operation at a time. Stop the service before seeding. A stale lock **file** after exit is normal: the kernel releases the lock. Do not remove a live lock file to bypass the guard. All later core state commands must use this same exclusive lock.
- Seed validates scoped CIDRs, declared hierarchy, pool ranges/exclusions and assignment containment, then commits inventory and initialization together. Repeating seed returns a nonzero `ALREADY_INITIALIZED` error without overwriting data. Seed content/IDs/clock are deterministic; `ingested_at` records real setup time.
- `IPAM_STATIC_DIR` has no implicit checkout default. Set it to the built `frontend/dist` or the future package's asset directory. Missing assets yield an explicit setup-needed page at `/`; API data and static readiness are separately reported.
- `/healthz` returns process/schema/data booleans and 200 only when data is initialized, otherwise 503 with `code` and `reason`. `static_ready` is an independent asset signal, not part of the data-ready HTTP criterion. A data-ready response alone does not prove UI/package readiness or evidence freshness.
- An unseeded but initialized schema serves the React setup state if assets exist, otherwise the fallback setup page. Inventory routes return 503 `SETUP_NEEDED`. Fixing a startup configuration error requires restart. Never use unseeded readiness failure as a restart-loop trigger.
- API errors use `error.code/message/details/request_id` plus `X-Request-ID`. Validation is 422, missing objects 404, store contention 503 after at most the configured three-second SQLite busy timeout. Unexpected failures return safe errors and server logs. No fake successful empty responses on database failure.

The inventory API is read-only in Stage 1. It has no production authentication. The default network binding is loopback; public exposure is outside this assignment.

## Schema and baseline

The schema contains `app_meta`, `scopes`, `prefixes`, `pools`, `allocations`. Scoped foreign keys prevent cross-scope prefix/pool/assignment associations. Prefix identity includes scope/family/CIDR; allocation uniqueness includes scope/family/address. Parent containment and pool arithmetic are validated before the packaged seed transaction. Network integers use fixed-width hexadecimal text for ordering; API counts use decimal strings to preserve IPv6 precision.

`app_meta` stores `baseline_version=1`, fixed demo clock, setup timestamp and the original seed envelope. Current rows carry source/run/record references. Future edits must preserve the immutable seed envelope and increment appropriate versions; no schema changes or mutation interfaces are delegated implicitly to later lanes.

Packaged seed: `backend/ipam_demo/data/baseline.json`:

| Item | Authored contents |
|---|---|
| Source/run | `synthetic-baseline` / `baseline-v1` |
| Fixed clock | `2026-09-01T00:00:00.000Z` |
| Scopes | 2: North (`vrf-north`) and Lab (`vrf-lab`) |
| Prefixes | 6: North IPv4 /16 with /24 and /28 children; North IPv6 /48 with /64 child; isolated Lab /24 |
| Pools | North DHCP range `.1–.254`, exclusions `.1–.9`; North static range `.1–.14`, exclusion `.1` |
| Intended assignments | One: North static `10.40.2.2` |

North and Lab both include `10.40.1.0/24`; their distinct scope IDs make this valid isolation, not an observed conflict. All entities are fictional. Configured pool capacity is not occupancy, unused space or recoverability. No lease, routing observation, finding or expected-answer label is part of this seed. The independent richer data task owns `fixtures/`; it must preserve baseline UUIDs and use distinct source/run identities for changed envelopes.

See [FOUNDATION_API.md](FOUNDATION_API.md) for concrete payloads/filters and paginated endpoints. The UI displays persisted response data, source references and intended IP assignments with explicit loading/empty/setup/error/retry states. It clears earlier results during refresh rather than presenting them as current.

## Remaining gates

`PART6_READY=no`. Core still needs real reset/backup/restore behavior before Spencer can validate state operations. `frontend/dist` has not been built; no Python package was installed/built and no service/database was started. No import, typed observation storage, rules/findings, capacity history, inventory editing, allocation workflow or audits are implemented yet.

Actually performed: repository/source inspection, dependency registry reads, `uv lock`, `npm install --package-lock-only --ignore-scripts --no-audit --no-fund`, coherent Git integration/commits, and bounded source review. No application tests were added or run. No syntax/type/build checks, smoke checks, browser checks, service/seed commands, containers, VMs or deployment were run. Essential runtime/negative-path evidence remains pending an explicit user request, including install/resource packaging, first-run readiness, seed refusal, scope/family/search/detail behavior, filesystem/schema errors and compiled UI serving. This pending evidence is not a feature completion percentage.
