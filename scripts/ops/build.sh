#!/usr/bin/env bash
# Build the ipam-demo image for linux/amd64. Consumes committed locks
# (uv.lock and frontend/package-lock.json); does not modify them.

source "$(dirname -- "$0")/common.sh"

log "Building ipam-demo:local for linux/amd64"
compose build "$@" "${SERVICE_NAME}"
