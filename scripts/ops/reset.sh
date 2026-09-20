#!/usr/bin/env bash
# Remove the recognized application database via `python -m ipam_demo reset`.
# The core state operation is documented in docs/STATE_OPERATIONS.md; this
# wrapper handles container plumbing, stopped-service enforcement and
# refuses to run without --confirm.
#
# Usage:
#   scripts/ops/reset.sh --confirm
#
# Effects:
#   - Removes /data/ipam_demo.sqlite3 (and exact removable empty sidecars)
#     after identity/schema/integrity checks. Reset never reseeds.
#   - Snapshots under /data/snapshots, preserved pre-restore databases and
#     the lock file are NOT touched.
#   - After reset, the store is empty and unseeded; run scripts/ops/seed.sh
#     to create a new baseline or scripts/ops/restore.sh to bring back an
#     earlier snapshot.
#
# Preconditions:
#   - Image is built.
#   - Service is stopped.
# Explicit destruction:
#   - --confirm is required by the core command; wrapper refuses without it
#     rather than silently forwarding a partial argument list.

source "$(dirname -- "$0")/common.sh"

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
  echo "error: --confirm is required. Reset removes the active database and does not reseed." >&2
  exit 2
fi

require_service_stopped

log "Removing recognized application database. Snapshots and lock file will remain."
compose run --rm --no-deps --pull never --entrypoint "" "${SERVICE_NAME}" \
  python -m ipam_demo reset --confirm "${passthrough[@]}"
log "Reset complete. Run scripts/ops/seed.sh or scripts/ops/restore.sh before starting the service."
