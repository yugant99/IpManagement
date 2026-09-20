#!/usr/bin/env bash
# Explicit, one-shot seed. Default scenario is `rich`, which is the accepted
# demo baseline: 60 prefixes plus policy and eight observation envelopes
# from /app/fixtures/v1. Pass `--scenario baseline` for the older 6-prefix
# foundation baseline.
#
# Preconditions:
#   - Image is built (scripts/ops/build.sh)
#   - Service is stopped (scripts/ops/stop.sh)
# Effects:
#   - Fresh store: creates /data/ipam_demo.sqlite3 with the requested
#     inventory. Rich seed uses the frozen inventory at
#     /app/fixtures/v1/inventory.json packaged into the image.
#   - Initialized store: refused with ALREADY_INITIALIZED. Never silently
#     overwrites persisted state; use scripts/ops/reset.sh + this wrapper
#     to intentionally rebuild an empty store.
#
# After seed, start the service and (for rich) trigger the first manual
# acquisition via POST /api/schedule/run. See docs/RUNNING.md.

source "$(dirname -- "$0")/common.sh"

# Split forwarded flags into an optional --scenario override and everything
# else. Default: rich. `--` ends option parsing for the caller.
scenario="rich"
passthrough=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scenario)
      shift
      scenario="${1:?--scenario requires a value (baseline|rich)}"
      shift
      ;;
    --scenario=*)
      scenario="${1#--scenario=}"
      shift
      ;;
    --)
      shift
      passthrough+=("$@")
      break
      ;;
    *)
      passthrough+=("$1")
      shift
      ;;
  esac
done

case "${scenario}" in
  rich)
    seed_args=(--scenario rich --inventory /app/fixtures/v1/inventory.json)
    ;;
  baseline)
    seed_args=(--scenario baseline)
    ;;
  *)
    echo "error: unknown scenario '${scenario}'. Expected 'rich' or 'baseline'." >&2
    exit 2
    ;;
esac

require_service_stopped

log "Seeding scenario=${scenario}. Service must be stopped."
compose run --rm --no-deps --pull never --entrypoint "" "${SERVICE_NAME}" \
  python -m ipam_demo seed "${seed_args[@]}" "${passthrough[@]}"
log "Seed complete. Start the service with scripts/ops/start.sh."
if [[ "${scenario}" == "rich" ]]; then
  log "For the rich demo, trigger one manual acquisition after start:"
  log "  scripts/ops/acquire.sh <idempotency-key>"
fi
