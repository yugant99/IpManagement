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

# 4. Confirm liveness. Expect HTTP 200 with {"process_ready": true}.
scripts/ops/health.sh

# 4b. Confirm protected readiness (separate domain-Operator token file,
#     explicit domain, current configuration pins). Success requires HTTP
#     200 AND all six booleans true; liveness alone never suffices.
scripts/ops/health.sh --readiness --token-file <operator-token-file> --domain <domain>

# 5. Trigger the first manual acquisition (cycle 1) with the separately
#    provisioned coordinator token file. The script bootstraps without a
#    domain, verifies the coordinator identity, and POSTs the original
#    stable key AND reason with the current pins. No automatic retry and
#    no replacement key: an ambiguous transport outcome stays unknown
#    until the operator re-runs the exact command.
scripts/ops/acquire.sh --token-file <coordinator-token-file> \
    --key part6-initial-cycle1 --reason "Prepare initial rich demo"
```

`scripts/ops/acquire.sh` performs the manual coordinator acquisition
described above: bootstrap without domain, trusted coordinator identity,
explicit current configuration pins, then the original stable key AND
reason in `POST /api/schedule/run` with no domain header:

```sh
scripts/ops/acquire.sh --token-file <coordinator-token-file> \
    --key part6-initial-cycle1 --reason "Prepare initial rich demo"
```

On a fresh store this acquires cycle 1, imports the nine source
envelopes and saves the reconciliation run. Success needs the exact
evidence triple (`201` + replay header false + body false for fresh,
`200` + true + true for the original replay); a transport failure — or
a missing/malformed/contradictory triple — leaves the outcome unknown
and keeps the same key. Do not enable the
timer. Do not pass a coordinator token on the command line or in the
environment of unrelated commands; the script reads it from the
protected file only.

Open <http://127.0.0.1:8000/> for the UI and
<http://127.0.0.1:8000/healthz> for the raw liveness payload
(`{"process_ready": true}` only — never readiness). The protected
OpenAPI reference at `/api/docs` requires a valid bearer sent as an
`Authorization` header from protected storage (never a URL or command
argument); plain browser navigation cannot attach it.

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
| Poll liveness | `scripts/ops/health.sh` (anonymous `/healthz`; never readiness) |
| Confirm readiness | `scripts/ops/health.sh --readiness --token-file <operator-token-file> --domain <domain>` |

The service must be **stopped** before running any state command
(`seed.sh`, `migrate.sh`, `backup.sh`, `restore.sh`, `reset.sh`)
and all `snapshots.sh` operations.
The wrappers check this and refuse with a clear message; the app's
exclusive `.ipam_demo.lock` inside `IPAM_DATA_DIR` enforces the same
invariant server-side and returns `DATA_IN_USE`.

## Reviewed access configuration and credentials

The reviewed access configuration is provisioned separately outside the
repository and snapshots. Export `IPAM_ACCESS_CONFIG` pointing at the
enabled file; Compose mounts it read-only at
`/run/ipam/access-config.json` and refuses to start without it. The
closed key set and provisioning procedure are in the T022 recipient
pack; the shape-only disabled example must never be enabled as shipped.

Two credentials are provisioned as separate protected files (exactly 64
lowercase hex characters each with at most one trailing newline;
owner-only mode enforced by the wrappers, internal whitespace refused;
never in shell variables, argv, URLs, logs, Compose environment, images,
snapshots or browser storage; wrapper shell tracing disabled on entry):

- Coordinator token file — evidence coordinator principal, no domain.
  Used only by `scripts/ops/acquire.sh` (bootstrap without domain, then
  the pinned acquisition POST).
- Domain-Operator token file — Operator principal in one explicitly
  selected domain. Used only by `scripts/ops/health.sh --readiness`.

A `401` means the token is unknown, disabled, expired or revoked: clear
it and never retry with it. A `409 ACCESS_CONTEXT_STALE` (or pins that
no longer match the server's current headers) means the configuration
changed: bootstrap again under the new pins.

## Health, readiness and restart

`GET /healthz` is minimal anonymous process liveness only: it returns
exactly `{"process_ready": true}` while the process serves HTTP. It
never discloses configuration, schema, data or domain state and proves
nothing about readiness or business state.

Protected readiness is `GET /api/readiness` with a domain-Operator
token file, an explicitly selected permitted domain and the current
configuration pins (`scripts/ops/health.sh --readiness`). Success
requires HTTP `200` AND all six booleans true — `process_ready`,
`schema_ready`, `data_ready`, `static_ready`, `configuration_ready`,
`domain_state_compatible` — with allowlisted reasons otherwise. Six
true booleans still do not establish business-state recovery, which
needs its own separate comparison, nor human acceptance.

- The container `HEALTHCHECK` polls `/healthz` every 30 s and reports
  unhealthy on `503`. Compose's `restart: unless-stopped` policy is
  intentionally **not** health-driven; the container is only restarted
  after a real process exit. There is no first-run restart loop before
  seed by design.
- `scripts/ops/health.sh` exits `0` for confirmed liveness or for
  readiness with all six booleans true, `1` when readiness answers but
  is not fully true (reasons printed), `2` for usage/local validation
  failures, `3` for transport failures and `4` for 401/403 credential or
  grant refusals — so operator automation never mistakes liveness,
  partial readiness or a stale credential for ready.

## Data location and persistence

- Container path: `/data` (writable, owned by uid/gid `10001`).
- Named volume: the explicit `IPAM_DATA_VOLUME` — managed by Docker on
  the host; Compose refuses to start when it is unset or empty. Record a
  NEW disposable volume name per candidate; deliberate reuse is recorded.
  This name is global to the engine: a different Compose project name does
  **not** isolate data. Before first use, establish that the recorded
  volume is absent, or record the deliberate reuse. The wrappers set
  their Compose file explicitly, so an environment-only `COMPOSE_FILE`
  override is insufficient. Wrapper log messages report the actual
  configured volume; use the rendered Compose configuration and actual
  mount inspection as the identity evidence.
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

To inspect the volume from the host: `docker volume inspect "${IPAM_DATA_VOLUME}"`.

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

Refuses `ALREADY_INITIALIZED` on an initialized store. Stop and inspect
the recorded volume identity; never reset or reseed as a readiness fallback.
A new candidate uses its own new disposable volume. Deliberate reset is
a separate explicitly confirmed operation, described below.

### Migrate

```sh
scripts/ops/migrate.sh
```

Advances a recognized schema 1–7 database to current schema 8. The
service never migrates implicitly; backup/restore preserve the source
schema until this explicit stopped-service migration.

### Backup

```sh
scripts/ops/backup.sh                    # ipam-backup-YYYYMMDDTHHMMSSZ.sqlite3
scripts/ops/backup.sh my-snapshot.sqlite3
```

Writes a standalone SQLite snapshot to `/data/snapshots/<name>` and
a paired `<name>.recovery.json` manifest bound to its closed bytes, size
and schema. The manifest records sanitized observed configuration identity
or explicit unavailability; it contains no configuration file or credentials.
Existing destinations are refused (`OUTPUT_EXISTS`), never overwritten.
If publication fails, inspect `output_published` and `manifest_published`
and retain any published files; do not report the pair complete or retry
automatically.

To copy a snapshot out of the volume (service still stopped; use a new
host filename in an existing directory):

```sh
scripts/ops/snapshots.sh list
scripts/ops/snapshots.sh export my-snapshot.sqlite3 /host/path/my-snapshot.sqlite3
scripts/ops/snapshots.sh export my-snapshot.sqlite3.recovery.json /host/path/my-snapshot.sqlite3.recovery.json
(cd /host/path && sha256sum my-snapshot.sqlite3 my-snapshot.sqlite3.recovery.json > snapshot-SHA256SUMS)
```

Keep both files and their checksum record together. A partial transfer is
incomplete; transfer and verify the missing member before ordinary restore.

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

Restoring a recognized schema 1–6 snapshot keeps that schema and requires
explicit migration; current schema 7 returns `migration_required: false`.

A present sidecar must be safe, well formed and match the snapshot hash,
size and schema; otherwise restore refuses before replacement. An absent
sidecar permits explicitly classified `unverified` legacy/data rescue. A
valid sidecar yields `like_for_like` only when saved and current observed
configuration identities are both known and equal; known unequal identities
yield `changed_configuration`; unavailable identity yields `unverified`.
These classify configuration evidence only. After start, require all six
protected readiness booleans and a separate selected-domain business-state
comparison, including schema 7 notice/receipt history; neither restore success
nor equal digests is business recovery or human acknowledgement.

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

Import both members of the verified pair into `/data/snapshots/` inside
the volume while the service is stopped:

```sh
(cd /host/path && sha256sum -c snapshot-SHA256SUMS)
scripts/ops/snapshots.sh import /host/path/my-snapshot.sqlite3
scripts/ops/snapshots.sh import /host/path/my-snapshot.sqlite3.recovery.json
```

The transfer helper accepts each standalone regular file; manifest content
and binding are validated by core restore. Stop if either transfer fails. Transfer uses a one-shot container running
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
Only after both members are present, use
`scripts/ops/restore.sh my-snapshot.sqlite3 --confirm`, inspect its result,
then migrate if required and start. Verify readiness and business state
separately. An intentionally absent legacy sidecar remains an explicitly
recorded unverified data-rescue exception, not a complete paired transfer.

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
demo follow seed → start → protected readiness → coordinator acquisition,
using the separate token files and explicit domain/pins described above.
For saved state, transfer the exported SQLite snapshot AND its deterministic
`.recovery.json` sidecar with both checksums. Verify and import both →
restore (explicit confirmation) → migrate only if required → start →
protected readiness → selected-domain business-state comparison.
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

Runs `docker compose down --remove-orphans`. The explicit data volume
(`IPAM_DATA_VOLUME`) is preserved. To fully discard local state
(development only), run `docker volume rm "${IPAM_DATA_VOLUME}"` after
`stop.sh`; recipient hosts must not do this.

## Diagnostics

- Container logs — `scripts/ops/logs.sh` (follow) or
  `scripts/ops/logs.sh --tail 200` (one-shot). Every request carries
  a server-generated `X-Request-ID`; grep the logs by that ID for a
  single request's trail.
- Liveness JSON — `scripts/ops/health.sh` prints the raw `/healthz`
  body (liveness only, never readiness). Readiness JSON —
  `scripts/ops/health.sh --readiness` prints the raw `/api/readiness`
  body; success needs HTTP 200 with all six booleans true. Both exit
  with a distinguishable code per state (see above).
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
