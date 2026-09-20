#!/usr/bin/env bash
# Stop the running IPAM service without removing its persistent data.
# The named volume `ipam_demo_data` is intentionally left in place;
# use `docker volume rm ipam_demo_data` explicitly if you need to
# discard local state (development only — never for a recipient host).

source "$(dirname -- "$0")/common.sh"

log "Stopping ${SERVICE_NAME}"
compose down --remove-orphans "$@"
log "Stopped. Persistent volume ipam_demo_data is preserved."
