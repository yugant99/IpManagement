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

# Path inside the container where snapshots live. Kept under the data
# volume so backups persist alongside the database across host restarts
# and never need a second volume/bind-mount at Compose level.
SNAPSHOT_DIR_CONTAINER="/data/snapshots"

# Require Docker Compose v2 (`docker compose`). The legacy `docker-compose`
# binary is out of scope for this package: it uses different flag semantics
# and hasn't been exercised against the compose.yaml here.
compose() {
  if ! docker compose version >/dev/null 2>&1; then
    echo "error: Docker Compose v2 ('docker compose') is required and not on PATH." >&2
    echo "       Install Docker Engine 24+ with the Compose plugin." >&2
    return 127
  fi
  docker compose --file "${COMPOSE_FILE}" --project-name "${COMPOSE_PROJECT_NAME}" "$@"
}

# True when the ipam service has a running container in this project.
# Returns 0 running, 1 stopped-or-absent, other codes on docker failure.
service_is_running() {
  local state
  state="$(compose ps --status running --services "${SERVICE_NAME}")" || return 2
  [[ "${state}" == "${SERVICE_NAME}" ]]
}

# Fail fast when a state command would collide with the running service.
# The container's exclusive .ipam_demo.lock enforces this too; refusing
# early gives a clearer error and skips a wasted container start.
require_service_stopped() {
  local status
  if service_is_running; then
    echo "error: ${SERVICE_NAME} is running. Stop it first with scripts/ops/stop.sh." >&2
    return 1
  else
    status=$?
    if [[ ${status} -ne 1 ]]; then
      echo "error: could not establish that the service is stopped." >&2
      return "${status}"
    fi
  fi
}

# Uniform stderr logger — cheap, avoids clashing with command stdout used
# by pipelines.
log() { printf '[ipam-ops] %s\n' "$*" >&2; }
