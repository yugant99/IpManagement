#!/usr/bin/env bash
# Trigger one manual scheduled acquisition via POST /api/schedule/run. The
# scheduling contract (docs/SCHEDULING_CONTRACT.md) requires that the same
# idempotency key be retained across ambiguous retries so a replay returns
# the committed result without advancing the cycle a second time.
#
# Usage:
#   scripts/ops/acquire.sh <idempotency-key>
#     [--actor demo-approver] [--reason "text"]
#
# Defaults match the accepted rich-demo runbook:
#   actor_id  = demo-approver
#   reason    = "Prepare initial rich demo"
#
# Requires the service to be running and reachable at the loopback port
# published in compose.yaml (127.0.0.1:8000 by default). Emits the raw JSON
# response so the operator can record run/cycle/operation IDs for evidence.

source "$(dirname -- "$0")/common.sh"

if [[ $# -lt 1 ]]; then
  cat >&2 <<'USAGE'
usage: scripts/ops/acquire.sh <idempotency-key> [--actor <id>] [--reason <text>]
Retain the same idempotency key across retries — a replay returns the
already-committed result without acquiring another cycle.
USAGE
  exit 2
fi

key="$1"; shift
actor="demo-approver"
reason="Prepare initial rich demo"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --actor)  shift; actor="${1:?--actor requires a value}"; shift ;;
    --reason) shift; reason="${1:?--reason requires a value}"; shift ;;
    *)
      echo "error: unknown flag '$1'" >&2
      exit 2
      ;;
  esac
done

URL="${IPAM_API_URL:-http://127.0.0.1:8000}/api/schedule/run"

payload=$(python3 - "${actor}" "${reason}" "${key}" <<'PY'
import json, sys
print(json.dumps({
    "actor_id": sys.argv[1],
    "reason": sys.argv[2],
    "idempotency_key": sys.argv[3],
}))
PY
)

log "POST ${URL}"
log "  actor_id=${actor} reason=${reason} idempotency_key=${key}"

response="$(curl --silent --show-error --max-time 30 \
  --write-out '\n%{http_code}' \
  -H "Content-Type: application/json" \
  -X POST --data "${payload}" "${URL}")" || {
  echo "error: transport failure. Is the service running (scripts/ops/start.sh)?" >&2
  exit 3
}

body="${response%$'\n'*}"
status="${response##*$'\n'}"

printf '%s\n' "${body}"
log "HTTP ${status}"

case "${status}" in
  200|201) exit 0 ;;
  409)     log "409: another acquisition/reconciliation is in progress or replay conflict."; exit 4 ;;
  *)       exit 2 ;;
esac
