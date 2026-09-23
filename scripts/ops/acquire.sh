#!/usr/bin/env bash
# Manual coordinator acquisition via POST /api/schedule/run (bridge T021 §8.3).
#
# The caller is the separately provisioned evidence coordinator, authenticated
# by a coordinator token FILE. The script bootstraps WITHOUT a domain
# (GET /api/access-context, bearer only), verifies the trusted coordinator
# identity and captures the explicit current configuration pins
# (revision + digest), then POSTs the ORIGINAL stable key AND reason with
# those pins. The coordinator sends NO X-IPAM-Domain header (the server
# refuses a coordinator that selects a domain with 403).
#
# There is NO automatic write retry and NO replacement key: an ambiguous
# transport outcome stays UNKNOWN. Keep the same key and reason; only after
# an explicit operator-confirmed decision re-run this exact command and let
# the server return the original replay (HTTP 200 + X-Acquisition-Replay).
#
# Token custody: the token is read from a protected file (regular file, not
# a symlink), validated for exact 64-lowercase-hex shape BEFORE any network
# use, and passed to curl through a 0600 config file — never argv, URLs,
# logs, snapshots or browser storage. Loopback only; proxies off and
# redirects never followed. Malformed credential/header values fail closed
# with no request sent. Bootstrap and error output never include
# credential-bearing data (only principal id, revision and digest, which
# are not credentials).
#
# Usage:
#   scripts/ops/acquire.sh --token-file <coordinator-token-file> \
#       --key <idempotency-key> --reason "<reason>" [--api-url <base-url>]
#
# Exit codes:
#   0  acquired (201 fresh, or 200 replay of the original operation)
#   2  usage or local validation failure (no request sent, or refused before POST)
#   3  transport failure — outcome UNKNOWN, may or may not have committed
#   4  authentication/authorization refusal (401/403: revoked, expired,
#      unknown, disabled, or not the coordinator — do not retry blindly)
#   5  server refusal with guidance (409/422/503: busy, stale, conflict,
#      exhausted, rejected, or setup needed)
#
# Revoked/stale/unknown outcomes are reported exactly as the server stated
# them, never normalised into success.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

usage() {
  cat >&2 <<'USAGE'
usage: scripts/ops/acquire.sh --token-file <coordinator-token-file> --key <idempotency-key> --reason "<reason>" [--api-url <base-url>]

  --token-file   separately provisioned coordinator token file (64 lowercase hex, no domain)
  --key          original stable idempotency key (1..200 chars; retained across retries)
  --reason       original reason text (1..200 chars; retained across retries)
  --api-url      loopback base URL (default http://127.0.0.1:8000; loopback only)

Ambiguous transport outcome stays unknown: keep the same key and reason and,
only after an explicit operator decision, re-run this exact command.
USAGE
}

TOKEN_FILE=""
KEY=""
REASON=""
API_URL="${IPAM_API_URL:-http://127.0.0.1:8000}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --token-file) shift; TOKEN_FILE="${1:?--token-file requires a value}"; shift ;;
    --key)        shift; KEY="${1:?--key requires a value}"; shift ;;
    --reason)     shift; REASON="${1:?--reason requires a value}"; shift ;;
    --api-url)    shift; API_URL="${1:?--api-url requires a value}"; shift ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "error: unknown flag '$1'" >&2; usage; exit 2 ;;
  esac
done

[[ -n "${TOKEN_FILE}" && -n "${KEY}" && -n "${REASON}" ]] || { usage; exit 2; }

# Loopback only: refuse anything that is not an explicit loopback base URL.
case "${API_URL}" in
  http://127.0.0.1*|http://localhost*|"http://[::1]"*) ;;
  *) echo "error: refusing non-loopback --api-url '${API_URL}' (loopback only)." >&2; exit 2 ;;
esac

# Key/reason shape matches the server's strict text rules (1..200 chars,
# non-blank, no surrounding whitespace). Fail closed before any network use.
valid_text() {
  local value="$1"
  [[ -n "${value}" && ${#value} -le 200 ]] || return 1
  [[ "${value}" != " "* && "${value}" != *" " ]] || return 1
  [[ "${value}" != $'\t'* && "${value}" != *$'\t' ]] || return 1
}
valid_text "${KEY}" || { echo "error: --key must be 1..200 non-blank characters without surrounding whitespace." >&2; exit 2; }
valid_text "${REASON}" || { echo "error: --reason must be 1..200 non-blank characters without surrounding whitespace." >&2; exit 2; }

# Credential file: regular file only (symlinks refused, as for the reviewed
# configuration), then exact 64-lowercase-hex shape. Anything else fails
# closed with no request sent and no credential material echoed.
if [[ -L "${TOKEN_FILE}" || ! -f "${TOKEN_FILE}" ]]; then
  echo "error: --token-file must be a regular file, not a symlink or missing path." >&2
  exit 2
fi
if [[ -n "$(find "${TOKEN_FILE}" -perm -0044 2>/dev/null)" ]]; then
  log "WARNING: token file is readable beyond its owner; restrict it (chmod 600)."
fi
TOKEN="$(tr -d '[:space:]' < "${TOKEN_FILE}")"
if ! [[ "${TOKEN}" =~ ^[0-9a-f]{64}$ ]]; then
  echo "error: token file does not hold exactly 64 lowercase hex characters; failing closed without contacting the service." >&2
  exit 2
fi

WORKDIR="$(mktemp -d)"
trap 'rm -rf -- "${WORKDIR}"' EXIT
chmod 700 "${WORKDIR}"
CURL_CONFIG="${WORKDIR}/curl.conf"
HEADERS_OUT="${WORKDIR}/headers.txt"
BODY_OUT="${WORKDIR}/body.txt"
: > "${CURL_CONFIG}"; : > "${HEADERS_OUT}"; : > "${BODY_OUT}"
chmod 600 "${CURL_CONFIG}" "${HEADERS_OUT}" "${BODY_OUT}"

# Protected header delivery: the bearer travels in a 0600 curl config file,
# never in argv, URLs or logs. Proxies off, redirects never followed
# (--location is never passed, so the default of zero redirects holds).
printf '%s\n' "-silent" "-show-error" "max-time = 30" "noproxy = *" \
  "header = \"Authorization: Bearer ${TOKEN}\"" \
  "header = \"Content-Type: application/json\"" > "${CURL_CONFIG}"
TOKEN=""

# curl_call <METHOD> <URL> [extra curl args...]: response body lands in
# BODY_OUT, response headers in HEADERS_OUT; echoes the HTTP status.
# Returns 3 with nothing sent-or-unknown on transport failure.
curl_call() {
  local method="$1" url="$2"
  shift 2
  local status
  if ! status="$(curl -q -K "${CURL_CONFIG}" -D "${HEADERS_OUT}" -o "${BODY_OUT}" \
      --write-out '%{http_code}' -X "${method}" "$@" "${url}")"; then
    return 3
  fi
  printf '%s' "${status}"
  return 0
}

# Step 1 — bootstrap WITHOUT a domain: trusted coordinator identity plus the
# explicit current configuration pins. Only the non-credential fields are
# ever reported; the bootstrap body itself is never dumped.
log "GET ${API_URL}/api/access-context (bootstrap, bearer only, no domain)"
BOOT_STATUS="$(curl_call GET "${API_URL}/api/access-context")" || {
  echo "error: transport failure during bootstrap. Nothing was written by this step — check the service (scripts/ops/start.sh)." >&2
  exit 3
}
if [[ "${BOOT_STATUS}" == "401" ]]; then
  echo "error: bootstrap 401 AUTHENTICATION_REQUIRED — token unknown, disabled, expired or revoked. Clear this credential and do not retry with it." >&2
  exit 4
fi
if [[ "${BOOT_STATUS}" == "503" ]]; then
  echo "error: bootstrap 503 — reviewed access configuration unavailable/invalid on the server. Provision IPAM_ACCESS_CONFIG before acquiring." >&2
  exit 5
fi
if [[ "${BOOT_STATUS}" != "200" ]]; then
  echo "error: bootstrap unexpected HTTP ${BOOT_STATUS}; failing closed without acquiring." >&2
  exit 5
fi
BOOT_FIELDS="$(python3 - "${BODY_OUT}" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    body = json.load(handle)
for field in ("principal_id", "is_evidence_coordinator",
              "configuration_revision", "configuration_digest"):
    print(f"{field}={body.get(field)}")
PY
)" || { echo "error: bootstrap body unparseable; failing closed without acquiring." >&2; exit 5; }
PRINCIPAL_ID="$(printf '%s\n' "${BOOT_FIELDS}" | sed -n 's/^principal_id=//p')"
IS_COORDINATOR="$(printf '%s\n' "${BOOT_FIELDS}" | sed -n 's/^is_evidence_coordinator=//p')"
CONFIG_REVISION="$(printf '%s\n' "${BOOT_FIELDS}" | sed -n 's/^configuration_revision=//p')"
CONFIG_DIGEST="$(printf '%s\n' "${BOOT_FIELDS}" | sed -n 's/^configuration_digest=//p')"
if [[ "${IS_COORDINATOR}" != "True" ]]; then
  echo "error: bootstrap identity '${PRINCIPAL_ID}' is not the evidence coordinator. Refusing acquisition; use the separately provisioned coordinator credential." >&2
  exit 4
fi
if ! [[ "${CONFIG_DIGEST}" =~ ^[0-9a-f]{64}$ && "${CONFIG_REVISION}" =~ ^[0-9]+$ ]]; then
  echo "error: bootstrap pins malformed; failing closed without acquiring." >&2
  exit 5
fi
log "Bootstrap: principal '${PRINCIPAL_ID}' (evidence coordinator), configuration revision ${CONFIG_REVISION}, digest ${CONFIG_DIGEST:0:12}…"

# Step 2 — manual acquisition with the ORIGINAL stable key AND reason, the
# explicit pins, and NO domain header. Key/reason reach the payload builder
# through the environment (never argv); the JSON body travels in a 0600
# file via --data. No actor_id is sent: the server derives the actor from
# the trusted bearer, so no mismatch is possible.
export IPAM_ACQUIRE_KEY="${KEY}" IPAM_ACQUIRE_REASON="${REASON}"
python3 - "${WORKDIR}/payload.json" <<'PY'
import json, os, sys
with open(sys.argv[1], "w", encoding="utf-8") as handle:
    json.dump({"idempotency_key": os.environ["IPAM_ACQUIRE_KEY"],
               "reason": os.environ["IPAM_ACQUIRE_REASON"]}, handle)
PY
unset IPAM_ACQUIRE_KEY IPAM_ACQUIRE_REASON
KEY=""; REASON=""
chmod 600 "${WORKDIR}/payload.json"

printf '%s\n' "header = \"X-IPAM-Configuration-Revision: ${CONFIG_REVISION}\"" \
  "header = \"X-IPAM-Configuration-Digest: ${CONFIG_DIGEST}\"" >> "${CURL_CONFIG}"

log "POST ${API_URL}/api/schedule/run (original key, pinned configuration, no domain)"
POST_STATUS="$(curl_call POST "${API_URL}/api/schedule/run" --data "@${WORKDIR}/payload.json")" || {
  cat >&2 <<'UNKNOWN'
error: transport failure during POST /api/schedule/run. Outcome is UNKNOWN:
the acquisition may or may not have committed. Keep the SAME key and reason;
do NOT invent a replacement key. Only after an explicit operator-confirmed
decision, re-run this exact command and let the server return the original
replay (HTTP 200 with X-Acquisition-Replay: true).
UNKNOWN
  exit 3
}

cat "${BODY_OUT}"
REPLAY="$(grep -i '^X-Acquisition-Replay:' "${HEADERS_OUT}" | tr -d '[:space:]' | cut -d: -f2 | tr '[:upper:]' '[:lower:]' || true)"
log "HTTP ${POST_STATUS}"

case "${POST_STATUS}" in
  201)
    log "Acquired fresh cycle (replay=${REPLAY:-false}). Record run/cycle/operation IDs from the body above."
    exit 0 ;;
  200)
    log "Replay of the original operation (replay=${REPLAY:-true}). No new cycle was advanced."
    exit 0 ;;
  401)
    echo "error: 401 AUTHENTICATION_REQUIRED — credential revoked, expired or disabled mid-session. Clear it; do not retry with the old token." >&2
    exit 4 ;;
  403)
    echo "error: 403 FORBIDDEN — coordinator grant or identity refused. See the server code above; do not retry blindly." >&2
    exit 4 ;;
  409)
    cat >&2 <<'GUIDE'
error: 409 conflict. Read the server code above and keep the SAME key:
  RUN_IN_PROGRESS      — busy; retry this exact command after the conflicting work finishes.
  ACCESS_CONTEXT_STALE — configuration changed; bootstrap again for the new pins, then re-run this exact command (same key and reason).
  IDEMPOTENCY_CONFLICT — same key, changed content; investigate, never silently send a new key.
  STALE_SCHEDULE / FEED_EXHAUSTED — cursor moved or feed complete; do not force a new key.
GUIDE
    exit 5 ;;
  422)
    echo "error: 422 — the whole cycle was rolled back (e.g. FEED_IMPORT_REJECTED). See the server code above; keep the same key." >&2
    exit 5 ;;
  503)
    echo "error: 503 — service not ready (e.g. SETUP_NEEDED: stop, seed, restart first). See the server code above." >&2
    exit 5 ;;
  *)
    echo "error: unexpected HTTP ${POST_STATUS}; see the body above. Outcome for a 5xx may be ambiguous — keep the same key." >&2
    exit 5 ;;
esac
