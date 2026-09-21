# Running the IPAM demo container

Owner: Part 6 (Spencer). One Docker service serves the compiled React UI
and Python FastAPI/Uvicorn API, with SQLite persisted through `IPAM_DATA_DIR`.

**Bounded VM execution observed:** exact accepted source
`eab1d3376633bf3280ff7bd8834fe46c88353d9a` built and ran on Linux amd64
in the authorized September 21 experiment. Rich acquisition, representative
UI/API flows, same-ID restart, stopped backup, populated restore and isolated
same-host agent reproduction were observed. A new disposable macOS snapshot
also restored on that VM. See [exact evidence and limits](handoffs/vm-portability.md).
Human recipient acceptance, full outage recovery and sustained hybrid operation
are not established. The lead owns readiness/accounting decisions.

## Supported target

- Host OS/architecture: **Linux `amd64`** with Docker Engine ≥ 24 and
  the Compose plugin (`docker compose`). The experiment used Engine 29.8.1
  and Compose plugin 5.5.1; earlier source guidance specified v2, which was
  not exercised in this experiment. Legacy `docker-compose`
  is not exercised here and is not supported by these scripts.
- Container execution on macOS `arm64` and Windows/WSL2 is not exercised.
  The package fixes its build target to Linux amd64; other host
  architectures need separately authorized emulation evidence.
- Host tools: Bash, curl, Python 3.11+ (acquisition JSON and snapshot
  transfer metadata), and GNU coreutils for the Linux snapshot export.
- Local filesystem or a local Docker named volume for persistent data.
  Network mounts (NFS, SMB, cloud object stores) are **not** supported;
  the app's exclusive `flock` lock is Unix-local.
- Loopback publishing only. No public URL, TLS termination, load
  balancer or authentication is provided by this package.

## Files owned by Part 6

| Path | Purpose |
|---|---|
| `Dockerfile` | Three-stage linux/amd64 build: UI bundle → Python venv → runtime. |
| `compose.yaml` | Single service, loopback publish, named `/data` volume. |
| `.dockerignore` | Excludes VCS metadata, editor scratch, private material and build artifacts from the build context. |
| `scripts/ops/` | Operator wrappers around `docker compose` and the `python -m ipam_demo` CLI. |
| `docs/RUNNING.md` | This runbook. |
| `docs/handoffs/part-6.md` | Lane handoff and current state. |
| `docs/parts/06-portability.md` | Part 6 task page. |

The application module, its dependency locks and its fixtures remain
core-owned and are consumed unchanged. The image installs `ipam_demo`
and the `ipam_synthetic_feed` producer as non-editable packages,
packages the frozen `inventory.json`, `inventory-policy.json` and eight
observation envelopes under `/app/fixtures/v1`, and sets
`IPAM_SYNTHETIC_FEED_DIR=/app/fixtures/v1`. Expected-answer files are
not packaged.

## Rich-demo first-time setup

The accepted demo state is the rich scenario: 60 prefixes with policy
and eight observation envelopes. Automatic scheduling stays **disabled**;
the first cycle is acquired by an explicit manual action.

```sh
# 1. Build the linux/amd64 image from committed locks (one-time).
scripts/ops/build.sh

# 2. Seed the frozen rich inventory. Service must be stopped.
#    Defaults to --scenario rich --inventory /app/fixtures/v1/inventory.json.
scripts/ops/seed.sh

# 3. Start the service, loopback-only on 127.0.0.1:8000.
scripts/ops/start.sh

# 4. Confirm readiness. Expect HTTP 200 once seed has run.
scripts/ops/health.sh

# 5. Trigger the first manual acquisition (cycle 1). Retain the same
#    idempotency key across retries so a replay returns the committed
#    result rather than advancing another cycle.
scripts/ops/acquire.sh part6-initial-cycle1
```

`scripts/ops/acquire.sh` posts the accepted payload

```json
{
  "actor_id": "demo-approver",
  "reason": "Prepare initial rich demo",
  "idempotency_key": "part6-initial-cycle1"
}
```

to `POST /api/schedule/run`. On a fresh store this acquires cycle 1,
imports the nine source envelopes and saves the reconciliation run.
Do not enable the timer.

Open <http://127.0.0.1:8000/> for the UI, <http://127.0.0.1:8000/api/docs>
for the OpenAPI browser and <http://127.0.0.1:8000/healthz> for the raw
readiness payload.

### Foundation-baseline alternative

For the older 6-prefix Stage 1 scenario used by legacy fixtures, seed
with `scripts/ops/seed.sh --scenario baseline` instead. The rich
`acquire.sh` step then does not apply.

## Normal operation

| Action | Command |
|---|---|
| Start | `scripts/ops/start.sh` |
| Stop | `scripts/ops/stop.sh` (data volume kept) |
| Tail logs (follow) | `scripts/ops/logs.sh` |
| Last N lines, no follow | `scripts/ops/logs.sh --tail 200` |
| Poll readiness | `scripts/ops/health.sh` |

The service must be **stopped** before running any state command
(`seed.sh`, `migrate.sh`, `backup.sh`, `restore.sh`, `reset.sh`)
and all `snapshots.sh` operations.
The wrappers check this and refuse with a clear message; the app's
exclusive `.ipam_demo.lock` inside `IPAM_DATA_DIR` enforces the same
invariant server-side and returns `DATA_IN_USE`.

## Health, readiness and restart

`GET /healthz` returns JSON with `process_ready`, `schema_ready`,
`data_ready`, `static_ready`, `code`, `reason`, `schema_version` and
`contract_revision`. HTTP `200` means the schema is present and the
store has been seeded. HTTP `503` with `code == "SETUP_NEEDED"` means
the schema exists but seed has not yet run — the UI surfaces a
setup-needed view instead of erroring out.

- The container `HEALTHCHECK` polls `/healthz` every 30 s and reports
  unhealthy on `503`. Compose's `restart: unless-stopped` policy is
  intentionally **not** health-driven; the container is only restarted
  after a real process exit. There is no first-run restart loop before
  seed by design.
- `scripts/ops/health.sh` distinguishes `SETUP_NEEDED` (exit code 1)
  from other 5xx (2) and transport failures (3) so operator automation
  does not silently treat an unseeded service as healthy.

## Data location and persistence

- Container path: `/data` (writable, owned by uid/gid `10001`).
- Named volume: `ipam_demo_data` — managed by Docker on the host.
  This name is global to the engine: a different Compose project name does
  **not** isolate data. Before first use, establish that this volume is absent
  on a dedicated engine or select a separate disposable source copy and change
  only `volumes.ipam_data.name` to a unique name. Record the diff/hash and use
  a distinct `COMPOSE_PROJECT_NAME` too. The wrappers set their Compose file
  explicitly, so an environment-only `COMPOSE_FILE` override is insufficient.
  Some wrapper log messages name the default volume literally; use the rendered
  Compose configuration and actual mount inspection as the identity evidence.
- Files under `/data`:
  - `ipam_demo.sqlite3` — the application database.
  - `snapshots/` — populated by `scripts/ops/backup.sh` (0700, uid 10001).
  - `ipam_demo.before-restore-<UTC-timestamp>-<uuid>.sqlite3` — created
    by `restore` before replacing the current database. Preserved
    indefinitely; retrieve or delete explicitly if you need to discard.
  - `.ipam_demo.lock` — advisory `flock` file. Its presence after a
    normal shutdown is expected; the kernel releases the lock on
    process exit. Do **not** delete the lock file while the service is
    up. See [Diagnostics](#diagnostics) for the correct
    `DATA_IN_USE` recovery.

To inspect the volume from the host: `docker volume inspect ipam_demo_data`.

For an unverified development-only bind-mount variant, edit the service
`volumes:` entry in a separate disposable source copy's `compose.yaml` and
point `/data` at an existing local directory writable by uid `10001`. The
wrappers do not automatically consume a Compose override file. Record the
exact source-copy diff, rendered configuration, runtime UID and actual mount
before using such a variant; this experiment used named volumes only.
Missing/unwritable paths surface `DATA_PATH_UNAVAILABLE` or
`DATA_PATH_UNWRITABLE` with the resolved path and runtime UID — the
service never silently falls back to ephemeral storage.

## State commands

All state commands require a stopped service, run under the exclusive
`.ipam_demo.lock` and touch only the recognized app database and its
own sidecars inside `IPAM_DATA_DIR`. Full semantics are in
[`docs/STATE_OPERATIONS.md`](STATE_OPERATIONS.md).

### Seed

```sh
scripts/ops/seed.sh                     # rich (default, accepted demo)
scripts/ops/seed.sh --scenario baseline # older foundation scenario
```

Refuses `ALREADY_INITIALIZED` on an initialized store. To rebuild a
new empty demo, run `scripts/ops/reset.sh --confirm` first.

### Migrate

```sh
scripts/ops/migrate.sh
```

Advances a recognized v1/v2/v3/v4 database to the current schema. The
service never migrates implicitly; state operations never migrate at
all.

### Backup

```sh
scripts/ops/backup.sh                    # ipam-backup-YYYYMMDDTHHMMSSZ.sqlite3
scripts/ops/backup.sh my-snapshot.sqlite3
```

Writes a standalone snapshot to `/data/snapshots/<name>` using
SQLite's backup API. Existing files at that destination are refused
(`OUTPUT_EXISTS`); the core command never overwrites a prior snapshot.

To copy a snapshot out of the volume (service still stopped; use a new
host filename in an existing directory):

```sh
scripts/ops/snapshots.sh list
scripts/ops/snapshots.sh export my-snapshot.sqlite3 /host/path/my-snapshot.sqlite3
```

### Restore

```sh
scripts/ops/restore.sh my-snapshot.sqlite3 --confirm
```

Validates identity/schema/integrity, then atomically replaces the
current database. The pre-restore database is preserved as
`ipam_demo.before-restore-<UTC-timestamp>-<uuid>.sqlite3` inside
`/data`; it is never deleted automatically. Restore output includes
`database_replaced`, `preserved_database` and `migration_required` —
inspect these fields before retrying. If `migration_required` is
`true`, run `scripts/ops/migrate.sh` (still stopped) before starting.

Restoring a v1/v2/v3/v4 snapshot keeps that snapshot's schema
version; current v5 restore returns `migration_required: false`.

### Reset

```sh
scripts/ops/reset.sh --confirm
```

Removes only the recognized application database and its exact
removable empty sidecars. Snapshots under `/data/snapshots`, any
preserved pre-restore databases and the lock file are untouched.
Reset never reseeds; run `scripts/ops/seed.sh` or
`scripts/ops/restore.sh` before starting again.

### Bringing a snapshot back in

`scripts/ops/snapshots.sh import /host/path/foo.sqlite3` copies a
standalone snapshot from the host into `/data/snapshots/` inside the
volume. Stop the service first. Transfer uses a one-shot container running
as the app user, so it works after `stop.sh` has removed the service
container. All snapshot operations take the existing app-data lock.
Import/export refuse symlinks, multi-link files and SQLite companion files;
import checks source size/SHA-256 before publishing a new mode-0600 file.
Existing destinations are never overwritten. Export stages a private host
file and publishes it only after the transfer exits successfully. An
interrupted import may leave a `.import-*` scratch file; it is not a usable
snapshot and is never promoted automatically. This is file transport, not
an additional SQLite implementation: core restore validates application
identity, schema and integrity. Keep the source unchanged during transfer.
Follow with `scripts/ops/restore.sh foo.sqlite3 --confirm` to bring it
online.

## Offline recipient handoff

On an authorized Linux amd64 build host, build the reviewed source once.
Record the full source commit and image ID, then save the already-built
image. Use a new output directory. The linked experiment followed this procedure
using a distinct source copy and volume on the same host; it was agent
reproduction, not a human recipient session:

```sh
mkdir part6-transfer
git rev-parse HEAD > part6-transfer/source-commit.txt
git archive --format=tar --output=part6-transfer/source.tar HEAD
docker image inspect ipam-demo:local --format '{{.Id}}' > part6-transfer/image-id.txt
docker image save --output part6-transfer/image.tar ipam-demo:local
(cd part6-transfer && sha256sum source-commit.txt source.tar image-id.txt image.tar > SHA256SUMS)
```

Transfer that directory through the approved local/offline channel. The
recipient must already have Docker Engine/Compose and the host tools
listed above. Check the checksums, extract the source into a fresh directory,
load the image, and compare its ID with `image-id.txt` before using it:

```sh
(cd part6-transfer && sha256sum -c SHA256SUMS)
mkdir recipient-source
tar -xf part6-transfer/source.tar -C recipient-source
docker image load --input part6-transfer/image.tar
docker image inspect ipam-demo:local --format '{{.Id}}'
```

Use the extracted scripts. Skip `build.sh`: startup and one-shot wrappers
use `--pull never` and require the loaded `ipam-demo:local` image. For a new
demo follow seed → start → health → acquire. For saved state, transfer an
exported standalone snapshot separately with its checksum, then import →
restore (explicit confirmation) → migrate only if required → start → health.
Do not seed a restored database. Snapshot restoration also restores schedule
settings; an enabled overdue schedule may acquire on startup. Use a known
disabled snapshot for the bounded manual demo; enabled-snapshot recovery
remains unverified. The image archive does not contain the data volume.
Source/image checksums identify the transfer; they do not establish runtime
acceptance, signatures, license clearance or customer readiness.

## Shutdown

```sh
scripts/ops/stop.sh
```

Runs `docker compose down --remove-orphans`. The `ipam_demo_data`
named volume is preserved. To fully discard local state (development
only), run `docker volume rm ipam_demo_data` after `stop.sh`;
recipient hosts must not do this.

## Diagnostics

- Container logs — `scripts/ops/logs.sh` (follow) or
  `scripts/ops/logs.sh --tail 200` (one-shot). Every request carries
  a server-generated `X-Request-ID`; grep the logs by that ID for a
  single request's trail.
- Health JSON — `scripts/ops/health.sh` prints the raw body and
  exits with a distinguishable code per state (see above).
- `DATA_IN_USE` — the lock file normally remains after exit; the
  kernel releases its lock when the holder exits, including after
  `SIGKILL`. Identify and stop the process/container holding this
  data volume, then retry. Never remove the lock file to bypass a
  live lock — replacing its inode can allow two writers on the same
  database.
- Symlinked database path — the app rejects a symlinked
  `ipam_demo.sqlite3` with `UNSAFE_DATABASE_PATH`. Store the SQLite
  file as a regular file directly on the mounted volume.
- State command refusals — inspect the JSON error `code` first.
  Typical values are `CONFIRMATION_REQUIRED`, `DATA_IN_USE`,
  `STATE_FILE_MISSING`, `UNSAFE_STATE_FILE`, `OUTPUT_EXISTS`,
  `UNSAFE_INPUT`, `UNSAFE_OUTPUT`, `UNRECOGNIZED_DATABASE`,
  `UNSUPPORTED_SCHEMA`, `INVALID_SCHEMA`, `DATABASE_INTEGRITY_FAILED`,
  `SNAPSHOT_NOT_STANDALONE`, `STATE_RECOVERY_REQUIRED`,
  `STATE_CHANGED`, `STORE_BUSY` and `STATE_OPERATION_TIMEOUT`. Read
  `details` for retained scratch/preserved paths before retrying.

## Dependencies and licensing

The image consumes locks committed by core; Part 6 does not pick or
pin versions independently.

- Python runtime: `python:3.12.10-slim-bookworm` (Debian bookworm base).
- Python packages: exact set in `uv.lock`. Direct declarations in
  `pyproject.toml`: `fastapi==0.141.1`, `uvicorn==0.50.1`. Transitive
  dependencies (from `uv.lock`) include `starlette`, `pydantic`,
  `pydantic-core`, `anyio`, `sniffio`, `idna`, `h11`, `click`,
  `annotated-doc`, `annotated-types`, `typing-extensions` and
  `typing-inspection`.
- The internal `ipam_synthetic_feed` producer is installed alongside
  `ipam_demo` from the same lockfile; it is a first-party module, not
  a third-party dependency.
- Node build tooling: `node:22.12.0-bookworm-slim`. Frontend graph in
  `frontend/package-lock.json`; direct declarations in
  `frontend/package.json` include `react`/`react-dom` 19.3.0, Vite
  8.3.0, TypeScript 7.0.2 and `@vitejs/plugin-react` 6.1.1.
- Extra apt packages installed into the runtime image: `tini`
  (init/signal handling) and `curl` (HEALTHCHECK). Both are Debian
  main.
- Build helper: `ghcr.io/astral-sh/uv:0.7.13` — matches the accepted
  native rehearsal tool version — runs
  `uv sync --frozen --no-dev --no-editable`. Not present in the
  runtime image.

A per-package SPDX license inventory is not published on this branch:
the license text lives in each package's site-packages metadata after
`uv sync` and has not been extracted here. If a recipient needs a
formal notices file, generate it against the locked graph on the
target host with `uv pip list --format=json` plus a metadata scan
(e.g. `pip-licenses` in a disposable environment reading `/opt/ipam-venv`).
Frontend dependency notices have not been extracted or verified either;
do not assume the compiled bundle contains a complete notices file.

## Limitations and unverified behavior

- The [VM handoff](handoffs/vm-portability.md) records one baseline build and
  bounded runtime observations. No runtime source repair or rebuild was needed.
  Its timing starts with a prepared host, loaded image and imported snapshot;
  it does not measure provisioning, transfer or full business recovery.
- Core state commands have separate bounded native evidence in
  [STATE_OPERATIONS.md](STATE_OPERATIONS.md). This VM experiment adds stopped
  backup/restore, populated prior-state preservation and missing-confirmation
  refusal. It does not add reset, hot backup, corrupt-file, bad-mount,
  crash/endurance or enabled-schedule recovery coverage.
- Same-host image/source/snapshot reproduction does not establish a second
  independent engine or human recipient acknowledgement/practice/training.
  Native macOS-to-Linux snapshot transfer does not establish an ARM container
  or sustained hybrid-cloud networking and operation.
- Cross-architecture (`arm64`), non-Linux hosts, network filesystem
  mounts, multi-worker deployments, TLS/authentication and public
  exposure are **not** supported by this package.
- The image runs as an unprivileged user (uid `10001`) with a
  read-only root filesystem and `/tmp` on `tmpfs`. If the app later
  gains features that require additional writable paths, that
  boundary must be widened deliberately, not relaxed to
  `read_only: false` implicitly.
- The `HEALTHCHECK` uses `curl` inside the container. Debian's
  `curl` is a small add; if the recipient security profile disallows
  it, replace with a `python -c "urllib.request..."` invocation and
  note the change here.
- The lead owns `PART6_READY` and the questionnaire accounting in
  [STATUS.md](STATUS.md). This operator runbook does not adjudicate either.
