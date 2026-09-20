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
| `start.sh` | Bring the service up detached (loopback publish on `127.0.0.1:8000`). |
| `stop.sh` | Stop the service; persistent volume `ipam_demo_data` is kept. |
| `health.sh` | Poll `/healthz` from the host with an interpreted exit code. |
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

## Rich demo acquisition

| Script | Purpose |
|---|---|
| `acquire.sh` | Trigger one manual acquisition via `POST /api/schedule/run` with the operator-supplied idempotency key. Retain the same key across retries so a replay returns the committed result without advancing another cycle. |

## Snapshot storage

Snapshots live inside the `ipam_demo_data` named volume at
`/data/snapshots/` (created 0700 by the wrapper). To retrieve them
outside the volume, use `scripts/ops/snapshots.sh export <name>
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
