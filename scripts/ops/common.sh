# Shared helpers for scripts/ops/*.sh. Source this from every operator
# script so behavior stays uniform. Never executed on its own.

set -euo pipefail

# Locate the repo root regardless of the caller's working directory. This
# keeps `scripts/ops/start.sh` valid from any shell prompt.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

# Compose file lives at the repo root.
COMPOSE_FILE="${REPO_ROOT}/compose.yaml"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ipam-demo}"
SERVICE_NAME="ipam"

# Detect the compose CLI variant. Prefer the modern `docker compose`
# subcommand; fall back to the legacy `docker-compose` binary.
compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose --file "${COMPOSE_FILE}" --project-name "${COMPOSE_PROJECT_NAME}" "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose --file "${COMPOSE_FILE}" --project-name "${COMPOSE_PROJECT_NAME}" "$@"
  else
    echo "error: docker compose (or docker-compose) is required and not on PATH" >&2
    return 127
  fi
}

# Uniform stderr logger — cheap, avoids clashing with command stdout used
# by pipelines.
log() { printf '[ipam-ops] %s\n' "$*" >&2; }
