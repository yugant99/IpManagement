#!/usr/bin/env bash
# Explicit schema v1 → v2 migration under the same exclusive data lock.
# Preconditions:
#   - Image is built.
#   - Service is stopped.
# Effects:
#   - Adds Stage 2 tables to an existing v1 database. Never runs implicitly
#     at startup; the app refuses to serve a v1 store without this step.

source "$(dirname -- "$0")/common.sh"

log "Running explicit schema migrate. Service must be stopped."
compose run --rm --no-deps --entrypoint "" "${SERVICE_NAME}" \
  python -m ipam_demo migrate "$@"
log "Migration step complete."
