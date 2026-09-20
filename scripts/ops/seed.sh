#!/usr/bin/env bash
# Run the explicit, one-shot baseline seed. This wraps
# `python -m ipam_demo seed --scenario baseline` and refuses to run
# alongside a live service (the exclusive .ipam_demo.lock enforces this).
#
# Preconditions:
#   - Image is built (scripts/ops/build.sh)
#   - Service is stopped (scripts/ops/stop.sh)
# Effects:
#   - Creates /data/ipam_demo.sqlite3 with the packaged baseline the
#     first time. Repeating the seed is refused with ALREADY_INITIALIZED
#     and never overwrites persisted inventory.

source "$(dirname -- "$0")/common.sh"

log "Running one-shot seed (--scenario baseline). Service must be stopped."
compose run --rm --no-deps --entrypoint "" "${SERVICE_NAME}" \
  python -m ipam_demo seed --scenario baseline "$@"
log "Seed step complete. Start the service with scripts/ops/start.sh."
