#!/usr/bin/env bash
# Bring the IPAM demo container up detached, with the loopback-only port
# binding declared in compose.yaml. Persistent data lives in the explicit
# IPAM_DATA_VOLUME named volume (Compose refuses to start when it is
# unset); snapshots go under /data/snapshots inside it. The reviewed
# access configuration comes from the separately provisioned
# IPAM_ACCESS_CONFIG file, mounted read-only.
#
# Ordering (see docs/RUNNING.md):
#   1. scripts/ops/build.sh   — one-time or after code changes
#   2. scripts/ops/seed.sh    — REQUIRED before first start; service stopped
#   3. scripts/ops/start.sh   — this script
#   4. scripts/ops/health.sh --readiness ... — protected readiness needs
#      HTTP 200 with all six booleans true; bare /healthz is liveness only.
#
# Starting before seed is allowed and the service will surface a 503
# not-ready response; the earlier version of this file recommended
# seeding AFTER starting, which is wrong (seed needs the exclusive lock
# and refuses to run alongside a live service).

source "$(dirname -- "$0")/common.sh"

log "Starting ${SERVICE_NAME} (published on 127.0.0.1:8000)"
compose up --detach --no-build --pull never "${SERVICE_NAME}" "$@"
log "Start requested. Data volume: ${IPAM_DATA_VOLUME:-(unset — compose refuses to start without it)} -> /data"
log "Readiness is GET /api/readiness (scripts/ops/health.sh --readiness ...); /healthz is liveness only."
log "If readiness is not fully true, read the allowlisted reasons first: seed only deliberately fresh, uninitialized disposable data — never as generic recovery (configuration, static-asset, schema or domain-incompatibility failures are not fixed by seeding)."
