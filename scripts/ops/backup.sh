#!/usr/bin/env bash
# Snapshot the complete SQLite database via `python -m ipam_demo backup`.
# The core state operation is documented in docs/STATE_OPERATIONS.md; this
# wrapper only handles container plumbing, stopped-service enforcement and
# a predictable destination path.
#
# Usage:
#   scripts/ops/backup.sh                  # timestamped default name
#   scripts/ops/backup.sh <name>.sqlite3   # custom filename (no path)
#
# Destination:
#   /data/snapshots/<name>.sqlite3   inside the container
#   which resolves to the named volume `ipam_demo_data` on the host.
# The parent /data/snapshots is created (0700) on first backup so the
# core command's "parent must exist" precondition is met.
#
# Preconditions:
#   - Image is built.
#   - Service is stopped (this wrapper enforces it — the container's
#     exclusive .ipam_demo.lock also refuses concurrent access).
# Preserved state:
#   - The active database is opened read-only during backup. Existing
#     files at the destination are refused (`OUTPUT_EXISTS`); the core
#     command never overwrites a prior snapshot.

source "$(dirname -- "$0")/common.sh"

if [[ $# -gt 1 ]]; then echo "usage: backup.sh [snapshot-filename]" >&2; exit 2; fi
require_service_stopped

filename="${1:-ipam-backup-$(date -u +%Y%m%dT%H%M%SZ).sqlite3}"

case "${filename}" in
  */*|""|.|..)
    echo "error: filename must be a plain name, not a path. Got: '${filename}'" >&2
    exit 2
    ;;
esac

output="${SNAPSHOT_DIR_CONTAINER}/${filename}"
log "Backing up to ${output} (container path)."

# Two steps in one one-shot container: ensure the snapshot directory
# exists with 0700 permissions (owned by the uid 10001 app user), then
# run the backup. `install -d -m 0700` is idempotent.
compose run --rm --no-deps --pull never --entrypoint "" "${SERVICE_NAME}" \
  sh -c 'if test -L "$1"; then echo "error: snapshot directory must not be a symlink" >&2; exit 1; fi
         install -d -m 0700 "$1" &&
         exec python -m ipam_demo backup --output "$2"' \
  sh "${SNAPSHOT_DIR_CONTAINER}" "${output}"

log "Backup written inside volume ipam_demo_data at ${output}."
log "Copy it off the host with: scripts/ops/snapshots.sh export '${filename}' /path/on/host"
