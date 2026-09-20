#!/usr/bin/env bash
# Bring the IPAM demo container up detached, with the loopback-only port
# binding declared in compose.yaml. Persistent data lives in the named
# volume `ipam_demo_data`; snapshots go under /data/snapshots inside it.
#
# Ordering (see docs/RUNNING.md):
#   1. scripts/ops/build.sh   — one-time or after code changes
#   2. scripts/ops/seed.sh    — REQUIRED before first start; service stopped
#   3. scripts/ops/start.sh   — this script
#   4. scripts/ops/health.sh  — expect HTTP 200 once seed has run
#
# Starting before seed is allowed and the service will surface a 503
# SETUP_NEEDED response; the earlier version of this file recommended
# seeding AFTER starting, which is wrong (seed needs the exclusive lock
# and refuses to run alongside a live service).

source "$(dirname -- "$0")/common.sh"

log "Starting ${SERVICE_NAME} (published on 127.0.0.1:8000)"
compose up --detach --no-build --wait-timeout 30 "${SERVICE_NAME}" "$@"
log "Service running. Data volume: ipam_demo_data -> /data"
log "If /healthz reports SETUP_NEEDED, stop the service and run scripts/ops/seed.sh."
