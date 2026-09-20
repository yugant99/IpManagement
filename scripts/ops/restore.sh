#!/usr/bin/env bash
# Restore a previous snapshot via `python -m ipam_demo restore`. The core
# state operation is documented in docs/STATE_OPERATIONS.md; this wrapper
# handles container plumbing, stopped-service enforcement and pointing at
# a filename inside the shared snapshots directory.
#
# Usage:
#   scripts/ops/restore.sh <name>.sqlite3 --confirm
#
# Input:
#   /data/snapshots/<name>.sqlite3   inside the container
#   which resolves to the named volume `ipam_demo_data` on the host.
# The snapshot must be a plain SQLite file with no -wal/-shm/-journal
# companion, produced by scripts/ops/backup.sh (or the equivalent core
# command). Absolute paths inside the container are also accepted for
# scenarios where a snapshot has been staged elsewhere first.
#
# Preconditions:
#   - Image is built.
#   - Service is stopped (this wrapper enforces it).
#   - --confirm is required by the core command; wrapper refuses without it
#     rather than silently forwarding a partial argument list.
# Preserved state:
#   - The current database is preserved by core as
#     /data/ipam_demo.before-restore-<UTC-timestamp>-<uuid>.sqlite3
#     before replacement. It is not removed automatically; retrieve or
#     archive it explicitly if you need to discard it.

source "$(dirname -- "$0")/common.sh"

if [[ $# -lt 2 ]]; then
  cat >&2 <<'USAGE'
usage: scripts/ops/restore.sh <snapshot-filename> --confirm

  <snapshot-filename>   plain filename inside /data/snapshots, or an
                        absolute path starting with / (must resolve
                        inside the container's mounted /data)
  --confirm             required by the core command; refuses otherwise
USAGE
  exit 2
fi

snapshot="$1"
shift

confirmed=0
passthrough=()
for arg in "$@"; do
  if [[ "${arg}" == "--confirm" ]]; then
    confirmed=1
  else
    passthrough+=("${arg}")
  fi
done

if [[ "${confirmed}" -ne 1 ]]; then
  echo "error: --confirm is required. Restore replaces the active database." >&2
  exit 2
fi

case "${snapshot}" in
  /*)
    input="${snapshot}"
    ;;
  */*)
    echo "error: snapshot must be a plain filename or absolute container path. Got: '${snapshot}'" >&2
    exit 2
    ;;
  *)
    input="${SNAPSHOT_DIR_CONTAINER}/${snapshot}"
    ;;
esac

require_service_stopped

log "Restoring from ${input} (container path). The current database will be preserved."
compose run --rm --no-deps --entrypoint "" "${SERVICE_NAME}" \
  python -m ipam_demo restore --input "${input}" --confirm "${passthrough[@]}"
log "Restore complete. Inspect JSON output for database_replaced/preserved_database/migration_required."
log "If migration_required is true, stop the service and run scripts/ops/migrate.sh."
