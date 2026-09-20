# Running the IPAM demo container

Owner: Part 6 (Spencer). Packaging now targets accepted main
`376dd52f9457dd0b7fecc8d83a3e0d6970bb487e` (runtime equivalent to
`289f53c7c5db1bd414c938add1ea207d591f9e64`) as one
Docker service: a compiled React UI and the Python FastAPI/Uvicorn
API in the same process, with SQLite persisted through `IPAM_DATA_DIR`.

**Status: source files only.** No image has been built, run, health-
checked, or otherwise executed from this branch. `PART6_READY` remains
`no` until package state-command procedures and recipient evidence
(startup, restart persistence, allocation/audit records) are completed.
Core already supplies schema-5 `reset`, `backup` and `restore`; the
remaining package work is recorded in [the lead review](handoffs/part-6-pr49-review.md).
See [Limitations](#limitations-and-unverified-behavior).

## Supported target

- Host OS/architecture: **Linux `amd64`** with Docker Engine ≥ 24 and
  the Compose plugin (`docker compose`).
- macOS `arm64` and Windows/WSL2 hosts are stretch and not exercised
  here. Cross-architecture builds must pass `--platform=linux/amd64`
  explicitly and accept the emulation penalty.
- Local filesystem or a local Docker named volume for persistent data.
  Network mounts (NFS, SMB, cloud object stores) are **not** supported;
  the app's exclusive `flock` lock is Unix-local.
- Loopback publishing only. No public URL, TLS termination, load
  balancer or authentication is provided by this package.

## Files owned by Part 6

| Path | Purpose |
|---|---|
| `Dockerfile` | Three-stage build: UI bundle → Python venv → runtime. |
| `compose.yaml` | Single service, loopback publish, named `/data` volume. |
| `.dockerignore` | Excludes locks-adjacent artifacts, VCS metadata and secrets from build context. |
| `scripts/ops/` | Thin wrappers around `docker compose` and `python -m ipam_demo`. |
| `docs/RUNNING.md` | This runbook. |
| `docs/handoffs/part-6.md` | Lane handoff and current state. |
| `docs/parts/06-portability.md` | Part 6 task page. |

The application module, its dependency locks and its fixtures remain
core-owned and are consumed unchanged.

The image installs `ipam_demo` and `ipam_synthetic_feed` as non-editable
packages. It includes the frozen rich inventory, policy and eight observation
envelopes under `/app/fixtures/v1`, with `IPAM_SYNTHETIC_FEED_DIR` pointing
there. Expected-answer files are not packaged. The baseline setup below is
still the older foundation scenario, not the accepted rich demo; Spencer's
remaining operator handoff must supply its explicit rich-seed/acquisition path.

## First-time setup

```sh
# 1. Build the linux/amd64 image from committed locks.
scripts/ops/build.sh

# 2. Seed the packaged baseline (creates /data/ipam_demo.sqlite3).
scripts/ops/seed.sh

# 3. Start the service, loopback-only on 127.0.0.1:8000.
scripts/ops/start.sh

# 4. Confirm readiness.
scripts/ops/health.sh
```

Open <http://127.0.0.1:8000/> for the UI, <http://127.0.0.1:8000/api/docs>
for the OpenAPI browser, and <http://127.0.0.1:8000/healthz> for the raw
readiness payload.

## Normal operation

| Action | Command |
|---|---|
| Start | `scripts/ops/start.sh` |
| Stop | `scripts/ops/stop.sh` (data volume kept) |
| Tail logs | `scripts/ops/logs.sh` |
| Poll readiness | `scripts/ops/health.sh` |

The service must be **stopped** before running any state command
(`seed.sh`, `migrate.sh`) because the app holds an exclusive
`.ipam_demo.lock` inside `IPAM_DATA_DIR`. Attempting a state command
against a running service returns `DATA_IN_USE` and exits non-zero
without touching the database.

## Health, readiness and restart

`GET /healthz` returns JSON with `process_ready`, `schema_ready`,
`data_ready`, `static_ready`, `code`, `reason`, `schema_version` and
`contract_revision`. HTTP `200` means the schema is present and the
baseline has been seeded. HTTP `503` with `code == "SETUP_NEEDED"`
means the schema exists but seed has not yet run — the UI surfaces
a setup-needed view instead of erroring out.

- The container `HEALTHCHECK` calls `/healthz` every 30 s. It reports
  unhealthy on `503`. Compose's `restart: unless-stopped` policy is
  intentionally **not** health-driven; the container is only restarted
  after a real process exit. There is no first-run restart loop before
  seed by design.
- `scripts/ops/health.sh` distinguishes `SETUP_NEEDED` (exit code 1)
  from other 5xx or transport failures (2 / 3) so operator scripts do
  not silently treat an unseeded service as healthy.

## Data location and persistence

- Container path: `/data` (writable, owned by uid/gid `10001`).
- Named volume: `ipam_demo_data` — managed by Docker on the host.
- Files under `/data`:
  - `ipam_demo.sqlite3` — the application database.
  - `.ipam_demo.lock` — advisory `flock` file. Its presence after a
    normal shutdown is expected; the kernel releases the lock on
    process exit. Do **not** delete the lock while the service is up.

To inspect the volume from the host: `docker volume inspect ipam_demo_data`.

To provide a bind mount instead of the named volume (development only),
override the `volumes:` entry in a local Compose override file and point
`/data` at an existing local directory that is writable by uid `10001`.
Missing/unwritable paths surface `DATA_PATH_UNAVAILABLE` or
`DATA_PATH_UNWRITABLE` with the resolved path and runtime UID — the
service never silently falls back to ephemeral storage.

## State commands

- **Seed** — `scripts/ops/seed.sh` runs `python -m ipam_demo seed
  --scenario baseline` in a one-shot container that mounts the same
  `/data` volume. Re-running is refused with `ALREADY_INITIALIZED`
  and never rewrites persisted rows.
- **Migrate** — `scripts/ops/migrate.sh` calls the current CLI's explicit
  recognized v1/v2/v3/v4 → v5 migration under the same exclusive lock.
  See [state operations](STATE_OPERATIONS.md) for supported inputs and
  the narrower set of migrations actually observed.

### Package procedures still pending

`reset --confirm`, `backup --output PATH` and `restore --input PATH --confirm`
already exist in core. Part 6 must finish matching wrappers/procedures,
including usable container/host snapshot paths, stopped-service operation,
explicit confirmation and preservation of the replaced database. Follow
[the core semantics](STATE_OPERATIONS.md); do not copy live SQLite files or
delete the volume as a substitute.

## Shutdown

```sh
scripts/ops/stop.sh
```

`stop.sh` runs `docker compose down --remove-orphans`. The
`ipam_demo_data` named volume is preserved. To fully discard local
state (development only), run
`docker volume rm ipam_demo_data` after `stop.sh`; recipient hosts
must not do this.

## Diagnostics

- Container logs — `scripts/ops/logs.sh` (follow) or
  `scripts/ops/logs.sh --no-follow -n 200`. Every request carries a
  server-generated `X-Request-ID`; grep the logs by that ID for a
  single request's trail.
- Health JSON — `scripts/ops/health.sh` prints the raw body and
  exits with a distinguishable code per state (see above).
- `DATA_IN_USE` — the lock file normally remains after exit; the kernel
  releases its lock when the holder exits, including after `SIGKILL`.
  Identify and stop the process/container holding this data volume, then
  retry. Never remove the lock file to bypass a lock: replacing its inode
  can allow two writers to operate on the same database.
- Symlinked database path — the app rejects a symlinked
  `ipam_demo.sqlite3` with `UNSAFE_DATABASE_PATH`. Store the SQLite
  file as a regular file directly on the mounted volume.

## Dependencies and licensing

The image consumes locks committed by core; Part 6 does not pick or
pin versions independently.

- Python runtime: `python:3.12.10-slim-bookworm` (Debian bookworm
  base).
- Python packages: exact set in `uv.lock`. Direct declarations in
  `pyproject.toml`: `fastapi==0.141.1`, `uvicorn==0.50.1`.
- Node build tooling: `node:22.12.0-bookworm-slim`. Frontend graph in
  `frontend/package-lock.json`; direct declarations in
  `frontend/package.json` include `react`/`react-dom` 19.3.0, Vite
  8.3.0, TypeScript 7.0.2 and `@vitejs/plugin-react` 6.1.1.
- Extra apt packages installed into the runtime image: `tini`
  (init/signal handling) and `curl` (HEALTHCHECK). Both are Debian
  main.
- Build helper: `ghcr.io/astral-sh/uv:0.7.13`, matching the accepted native
  rehearsal tool version, runs `uv sync --frozen --no-dev --no-editable`;
  not present in the runtime image. Application dependency locks are unchanged.

License review of every transitive dependency is out of scope for
this branch and needs a separate audit against `uv.lock` and
`frontend/package-lock.json`.

## Limitations and unverified behavior

- **Nothing has been executed.** No image has been built, run,
  seeded, health-checked or restarted. All behavior above is derived
  from source and current contracts; no container runtime evidence
  is claimed.
- Core state commands are available. Package wrappers/procedures and G27
  target-host persistence evidence (G21/G22 allocation/audit records surviving
  restart and snapshot recovery) remain pending. `PART6_READY` stays `no`.
- Cross-architecture (`arm64`), non-Linux hosts, network filesystem
  mounts, multi-worker deployments, TLS/authentication and public
  exposure are **not** supported by this package.
- The image runs as an unprivileged user (uid `10001`) with a
  read-only root filesystem and `/tmp` on `tmpfs`. If the app later
  gains features that require additional writable paths, that
  boundary must be widened deliberately, not relaxed to `read_only:
  false` implicitly.
- The `HEALTHCHECK` uses `curl` inside the container. Debian's
  `curl` is a small add; if the recipient security profile disallows
  it, replace with a `python -c urllib.request` invocation and note
  the change here.
