#!/usr/bin/env bash
# Explicit stopped-service schema migration under the exclusive data lock.
# The current CLI migrates recognized v1, v2, v3 and v4 stores forward to
# the schema version supplied by the installed application (v5 at time of
# writing). Startup refuses to serve an older-schema store without this
# step; state operations refuse to advance a schema themselves.
#
# Preconditions:
#   - Image is built.
#   - Service is stopped (this wrapper checks and fails visibly).
# Effects:
#   - Adds the newer-schema tables/columns to an existing recognized
#     legacy database. See docs/STATE_OPERATIONS.md for supported input
#     versions and the narrower set of migrations actually exercised by
#     core focused checks.

source "$(dirname -- "$0")/common.sh"

require_service_stopped

log "Running explicit schema migrate. Service must be stopped."
compose run --rm --no-deps --pull never --entrypoint "" "${SERVICE_NAME}" \
  python -m ipam_demo migrate "$@"
log "Migration step complete."
