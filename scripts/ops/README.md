# scripts/ops — operator helpers

Thin wrappers around Docker Compose v2 and the `python -m ipam_demo`
CLI. Every script sources `common.sh`, works from any current directory,
and forwards trailing flags to the underlying command.

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

Every state wrapper checks that the service is not running and refuses
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
subcommands run `docker compose cp`; nothing is copied through the app.

## Assumptions

- Docker Engine ≥ 24 with the Compose plugin (`docker compose`).
  Legacy `docker-compose` is not exercised against this compose.yaml
  and is intentionally unsupported by `common.sh`.
- Host is Linux `amd64`. Other host architectures require a stretch
  build with `--platform=linux/amd64` and emulation; see
  `docs/RUNNING.md`.
- The compose file (`compose.yaml`) at the repo root is authoritative;
  do not copy it elsewhere and re-tag paths.
