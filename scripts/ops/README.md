# scripts/ops — operator helpers

Thin wrappers around `docker compose` and the `python -m ipam_demo`
CLI. Every script sources `common.sh`, works from any current directory,
and forwards trailing flags to the underlying command.

Full runbook: [`docs/RUNNING.md`](../../docs/RUNNING.md).

| Script | Purpose |
|---|---|
| `build.sh` | Build the `ipam-demo:local` image for `linux/amd64`. |
| `start.sh` | Bring the service up detached (loopback publish on `127.0.0.1:8000`). |
| `stop.sh` | Stop the service; persistent volume `ipam_demo_data` is kept. |
| `health.sh` | Poll `/healthz` from the host with an interpreted exit code. |
| `logs.sh` | Follow (default) or one-shot inspect service logs. |
| `seed.sh` | Explicit one-shot baseline seed. Requires stopped service. |
| `migrate.sh` | Explicit schema v1 → v2 migration. Requires stopped service. |

## Deliberately absent

`reset`, `backup` and `restore` are core state commands and are owned
outside Part 6. The current core checkpoint (Stage 2, commit
`8a1a1227`) does not implement them; the CLI parser will reject the
subcommands. This directory will only gain matching wrappers **after**
core lands the commands and they are recorded in `docs/CONTRACTS.md`
as implemented.

## Assumptions

- Docker Engine ≥ 24 with the Compose plugin (`docker compose`). The
  scripts fall back to a legacy `docker-compose` binary if that is what
  is on `PATH`.
- Host is Linux `amd64`. Other host architectures require a stretch
  build with `--platform=linux/amd64` and emulation; see
  `docs/RUNNING.md`.
- The compose file (`compose.yaml`) at the repo root is authoritative;
  do not copy it elsewhere and re-tag paths.
