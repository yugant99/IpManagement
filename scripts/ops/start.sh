#!/usr/bin/env bash
# Start the IPAM demo container in the background with the loopback-only
# port binding declared in compose.yaml. Idempotent: re-running after a
# clean stop simply restarts the service and preserves the /data volume.

source "$(dirname -- "$0")/common.sh"

log "Starting ${SERVICE_NAME} (published on 127.0.0.1:8000)"
compose up --detach --no-build --wait-timeout 30 "${SERVICE_NAME}" "$@"
log "Service running. Data volume: ipam_demo_data → /data"
log "Next steps: seed once with scripts/ops/seed.sh, then scripts/ops/health.sh"
