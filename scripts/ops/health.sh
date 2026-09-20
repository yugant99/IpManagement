#!/usr/bin/env bash
# Poll the /healthz endpoint from the host. Exit codes:
#   0  → 200 Ready
#   1  → 503 SETUP_NEEDED (schema present, data not seeded)
#   2  → any other non-200 (schema / process / static problem)
#   3  → transport failure (service not reachable)
#
# The container also runs its own HEALTHCHECK; this script is the operator
# view used from the host without shelling into the container.

source "$(dirname -- "$0")/common.sh"

URL="${IPAM_HEALTH_URL:-http://127.0.0.1:8000/healthz}"

log "GET ${URL}"

# --write-out separates HTTP status from body; --fail is NOT used because
# we want to observe 503 bodies rather than mask them as errors.
if ! response="$(curl --silent --show-error --max-time 5 --write-out '\n%{http_code}' "${URL}")"; then
  log "Transport error — is the service running? (scripts/ops/start.sh)"
  exit 3
fi

body="${response%$'\n'*}"
status="${response##*$'\n'}"

printf '%s\n' "${body}"
log "HTTP ${status}"

case "${status}" in
  200) exit 0 ;;
  503)
    case "${body}" in
      *'"SETUP_NEEDED"'*) exit 1 ;;
      *) exit 2 ;;
    esac
    ;;
  *) exit 2 ;;
esac
