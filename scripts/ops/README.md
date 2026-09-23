# scripts/ops — operator helpers

Thin wrappers around Docker Compose v2 and the `python -m ipam_demo`
CLI. Shell entrypoints source `common.sh` and work from any current
directory. State and transfer wrappers validate their own arguments.

Full runbook: [`docs/RUNNING.md`](../../docs/RUNNING.md). Core state
semantics: [`docs/STATE_OPERATIONS.md`](../../docs/STATE_OPERATIONS.md).
Scheduling contract for the manual acquisition:
[`docs/SCHEDULING_CONTRACT.md`](../../docs/SCHEDULING_CONTRACT.md).

## Lifecycle

| Script | Purpose |
|---|---|
| `build.sh` | Build the `ipam-demo:local` image for `linux/amd64`. |
| `start.sh` | Bring the service up detached (loopback publish on `127.0.0.1:8000`). Requires explicit `IPAM_DATA_VOLUME` and `IPAM_ACCESS_CONFIG` (see below). |
| `stop.sh` | Stop the service; the explicit data volume is kept. |
| `health.sh` | Anonymous `/healthz` liveness from the host (default), or protected `/api/readiness` with all six booleans (`--readiness` with a domain-Operator token file and explicit domain). Liveness alone never establishes readiness. |
| `logs.sh` | Follow (default) or one-shot inspect service logs. |

## State commands (require stopped service)

| Script | Wraps |
|---|---|
| `seed.sh` | `python -m ipam_demo seed --scenario rich --inventory /app/fixtures/v1/inventory.json` by default; pass `--scenario baseline` for the older 6-prefix foundation scenario. |
| `migrate.sh` | `python -m ipam_demo migrate` (recognized v1/v2/v3/v4 → current). |
| `backup.sh` | `python -m ipam_demo backup --output /data/snapshots/<name>.sqlite3`. |
| `restore.sh` | `python -m ipam_demo restore --input <path> --confirm`. |
| `reset.sh` | `python -m ipam_demo reset --confirm`. Never reseeds. |
| `snapshots.sh` | Manage snapshot files inside the data volume (`list`, `export`, `import`, `remove`). |

Every state wrapper and snapshot operation checks that the service is not running and refuses
with a clear message otherwise; the container's exclusive
`.ipam_demo.lock` enforces the same invariant server-side.

## Rich demo acquisition (coordinator credential, no auto-retry)

| Script | Purpose |
|---|---|
| `acquire.sh` | Manual `POST /api/schedule/run` with a separately provisioned coordinator token file: bootstrap without domain, verify the trusted coordinator identity, send the explicit current configuration pins with the original stable key and reason. No automatic write retry and no replacement key — an ambiguous transport outcome stays unknown until the operator re-runs the exact command. |

The coordinator sends no `X-IPAM-Domain` header and no `actor_id` (the
server derives the actor from the trusted bearer). Coordinator and
domain-Operator credentials are separately provisioned files with
enforced owner-only mode and exact 64-hex representation (at most one
trailing newline; internal whitespace refused); neither token ever
appears in shell variables, argv, URLs, logs, Compose environment,
images, snapshots or browser storage, and both wrappers disable
inherited shell tracing on entry. Success needs the exact
status/header/body evidence triple (201/false/false or 200/true/true);
anything inconsistent exits unknown without claiming a cycle.

## Snapshot storage (paired SQLite + sidecar)

Snapshots live inside the explicit data volume (`IPAM_DATA_VOLUME`) at
`/data/snapshots/` (created 0700 by the wrapper). Every backup writes a
pair: `<name>.sqlite3` plus its `<name>.sqlite3.recovery.json` manifest,
which binds the closed snapshot bytes (SHA-256, size, schema) to the
observed configuration identity — never the configuration itself or any
credential. Transfer and keep the PAIR together (one
`snapshots.sh export`/`import` run per file, matching names, checksums
checked on both). Restore treats the sidecar exactly per the frozen
wire: absent sidecar permits only explicit legacy/data-rescue
(`unverified`); a present malformed, unsafe or hash/size/schema-mismatched
manifest REFUSES before replacement; a present valid sidecar classifies
`like_for_like`, `changed_configuration` or `unverified` (either config
identity unknown). Neither classification is readiness: run
`health.sh --readiness` separately. Full handoff:
[`operator-handoff.md`](../../specs/001-postmeeting-bridge/delivery/operator-handoff.md).
To retrieve snapshots outside the volume, use `scripts/ops/snapshots.sh export <name>
<host-path>`; the reverse is `... import <host-path> [<name>]`. These
subcommands stream through a one-shot app-user container and take the core
app-data lock. They work after `stop.sh` removes the service container.
Existing destinations, linked files and SQLite companion files are refused;
imports verify size/SHA-256 before publication. Core restore owns database
validation. `snapshot_transfer.py` is the shared transport implementation,
passed into the helper as code; it is not another service or database layer.

## Assumptions

- Docker Engine ≥ 24 with the Compose plugin (`docker compose`).
  Legacy `docker-compose` is not exercised against this compose.yaml
  and is intentionally unsupported by `common.sh`.
- Host is Linux `amd64`, with Bash, curl, Python 3.11+ and GNU coreutils.
  Other architectures require separate emulation evidence; see
  `docs/RUNNING.md`.
- The compose file (`compose.yaml`) at the repo root is authoritative;
  do not copy it elsewhere and re-tag paths.
- Compose requires explicit environment: `IPAM_DATA_VOLUME` names the
  recorded disposable volume for this candidate (a new candidate records
  a NEW name; deliberate reuse is recorded; a different Compose project
  name alone does not isolate a globally named volume), and
  `IPAM_ACCESS_CONFIG` points at the separately provisioned reviewed
  configuration file, mounted read-only. No token belongs in Compose
  environment, images, CLI arguments, logs or snapshots.
