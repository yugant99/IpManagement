#!/usr/bin/env bash
# Operator liveness and readiness view from the host (bridge T021 §7).
#
# Two separate checks, never conflated:
#
#   Liveness (default): anonymous GET /healthz. The server returns only
#   {"process_ready": true} while the process serves HTTP. This proves
#   NOTHING about readiness, schema, data, configuration or business state.
#
#   Readiness (--readiness): a SEPARATE domain-Operator token FILE, an
#   explicit domain, bootstrap (GET /api/access-context) with the current
#   configuration pins, then the protected GET /api/readiness. Success
#   requires HTTP 200 AND all six exact booleans true: process_ready,
#   schema_ready, data_ready, static_ready, configuration_ready and
#   domain_state_compatible. HTTP 200 alone is insufficient. Six true
#   booleans still prove nothing about business-state recovery, which needs
#   its own separate comparison, nor about human acceptance.
#
# Token custody mirrors acquire.sh: protected token file (regular file, no
# symlink, exact 64-lowercase-hex shape), bearer delivered through a 0600
# curl config file — never argv, URLs, logs, snapshots or browser storage.
# Loopback only; proxies off, redirects never followed. Malformed values
# fail closed. Error output carries no credential-bearing data.
#
# Usage:
#   scripts/ops/health.sh [--health-url <url>]                       # liveness only
#   scripts/ops/health.sh --readiness --token-file <operator-token-file> \
#       --domain <domain> [--api-url <base-url>]
#
# Exit codes:
#   0  liveness confirmed, or readiness with all six booleans true
#   1  readiness answered but NOT all six true (reasons printed), or
#      liveness answered an unexpected shape (treated as not-ready, not healthy)
#   2  usage or local validation failure
#   3  transport failure (service not reachable)
#   4  authentication/authorization refusal (401/403 on bootstrap or readiness)

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/common.sh"

usage() {
  cat >&2 <<'USAGE'
usage:
  scripts/ops/health.sh [--health-url <url>]                              # anonymous liveness only
  scripts/ops/health.sh --readiness --token-file <operator-token-file> --domain <domain> [--api-url <base-url>]

  --readiness    protected readiness: Operator token file + explicit domain + pins,
                 requiring HTTP 200 and all six booleans true
  --token-file   separately provisioned domain-Operator token file (64 lowercase hex)
  --domain       explicit selected domain the Operator principal holds
  --api-url      loopback base URL (default http://127.0.0.1:8000; loopback only)
  --health-url   liveness URL (default http://127.0.0.1:8000/healthz; loopback only)
USAGE
}

MODE="liveness"
TOKEN_FILE=""
DOMAIN=""
API_URL="${IPAM_API_URL:-http://127.0.0.1:8000}"
HEALTH_URL="${IPAM_HEALTH_URL:-http://127.0.0.1:8000/healthz}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --readiness)  MODE="readiness"; shift ;;
    --token-file) shift; TOKEN_FILE="${1:?--token-file requires a value}"; shift ;;
    --domain)     shift; DOMAIN="${1:?--domain requires a value}"; shift ;;
    --api-url)    shift; API_URL="${1:?--api-url requires a value}"; shift ;;
    --health-url) shift; HEALTH_URL="${1:?--health-url requires a value}"; shift ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "error: unknown flag '$1'" >&2; usage; exit 2 ;;
  esac
done

# Loopback only for every URL this script contacts.
for candidate in "${API_URL}" "${HEALTH_URL}"; do
  case "${candidate}" in
    http://127.0.0.1*|http://localhost*|"http://[::1]"*) ;;
    *) echo "error: refusing non-loopback URL '${candidate}' (loopback only)." >&2; exit 2 ;;
  esac
done

WORKDIR="$(mktemp -d)"
trap 'rm -rf -- "${WORKDIR}"' EXIT
chmod 700 "${WORKDIR}"
CURL_CONFIG="${WORKDIR}/curl.conf"
HEADERS_OUT="${WORKDIR}/headers.txt"
BODY_OUT="${WORKDIR}/body.txt"
: > "${CURL_CONFIG}"; : > "${HEADERS_OUT}"; : > "${BODY_OUT}"
chmod 600 "${CURL_CONFIG}" "${HEADERS_OUT}" "${BODY_OUT}"

base_curl_config() {
  printf '%s\n' "-silent" "-show-error" "max-time = 5" "noproxy = *" > "${CURL_CONFIG}"
  chmod 600 "${CURL_CONFIG}"
}

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

if [[ "${MODE}" == "liveness" ]]; then
  # Anonymous minimal liveness. The container HEALTHCHECK uses the same
  # endpoint; Docker labels (Dockerfile) record that it is liveness only.
  log "GET ${HEALTH_URL} (anonymous liveness only — not readiness)"
  base_curl_config
  # --write-out separates HTTP status from body; --fail is NOT used because
  # a non-200 body is evidence, not a masked error.
  if ! response_status="$(curl_call GET "${HEALTH_URL}")"; then
    log "Transport error — is the service running? (scripts/ops/start.sh)"
    exit 3
  fi
  body="$(cat "${BODY_OUT}")"
  printf '%s\n' "${body}"
  log "HTTP ${response_status}"
  if [[ "${response_status}" == "200" ]] && python3 - "${BODY_OUT}" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    body = json.load(handle)
assert body == {"process_ready": True}, "unexpected liveness shape"
PY
  then
    log "Liveness confirmed: process serves HTTP. This says nothing about readiness — use --readiness."
    exit 0
  fi
  log "Liveness NOT confirmed (status ${response_status} or unexpected shape)."
  exit 1
fi

# --- Protected readiness -------------------------------------------------
[[ -n "${TOKEN_FILE}" && -n "${DOMAIN}" ]] || { usage; exit 2; }

# Domain header shape mirrors the server's strict rule (non-empty, no
# surrounding whitespace, at most 200 chars, never "*"). Fail closed.
if [[ -z "${DOMAIN}" || "${DOMAIN}" == "*" || ${#DOMAIN} -gt 200 \
      || "${DOMAIN}" != "${DOMAIN#"${DOMAIN%%[![:space:]]*}"}" \
      || "${DOMAIN}" != "${DOMAIN%"${DOMAIN##*[![:space:]]}"}" ]]; then
  echo "error: --domain is malformed (empty, '*', over 200 chars, or surrounding whitespace); failing closed." >&2
  exit 2
fi

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

printf '%s\n' "-silent" "-show-error" "max-time = 10" "noproxy = *" \
  "header = \"Authorization: Bearer ${TOKEN}\"" > "${CURL_CONFIG}"
chmod 600 "${CURL_CONFIG}"
TOKEN=""

# Bootstrap WITH the explicit domain (optional on this route; sent here so
# the selected domain is confirmed before readiness).
log "GET ${API_URL}/api/access-context (bootstrap for domain '${DOMAIN}')"
export IPAM_HEALTH_DOMAIN="${DOMAIN}"
BOOT_STATUS="$(curl_call GET "${API_URL}/api/access-context" -H "X-IPAM-Domain: ${IPAM_HEALTH_DOMAIN}")" || {
  log "Transport error — is the service running? (scripts/ops/start.sh)"
  exit 3
}
unset IPAM_HEALTH_DOMAIN
if [[ "${BOOT_STATUS}" == "401" ]]; then
  echo "error: bootstrap 401 AUTHENTICATION_REQUIRED — token unknown, disabled, expired or revoked. Clear this credential and do not retry with it." >&2
  exit 4
fi
if [[ "${BOOT_STATUS}" == "503" ]]; then
  echo "error: bootstrap 503 — reviewed access configuration unavailable/invalid on the server." >&2
  exit 4
fi
if [[ "${BOOT_STATUS}" != "200" ]]; then
  echo "error: bootstrap unexpected HTTP ${BOOT_STATUS}; failing closed without checking readiness." >&2
  exit 4
fi
BOOT_FIELDS="$(python3 - "${BODY_OUT}" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    body = json.load(handle)
for field in ("principal_id", "selected_domain",
              "configuration_revision", "configuration_digest"):
    print(f"{field}={body.get(field)}")
PY
)" || { echo "error: bootstrap body unparseable; failing closed." >&2; exit 4; }
PRINCIPAL_ID="$(printf '%s\n' "${BOOT_FIELDS}" | sed -n 's/^principal_id=//p')"
SELECTED="$(printf '%s\n' "${BOOT_FIELDS}" | sed -n 's/^selected_domain=//p')"
CONFIG_REVISION="$(printf '%s\n' "${BOOT_FIELDS}" | sed -n 's/^configuration_revision=//p')"
CONFIG_DIGEST="$(printf '%s\n' "${BOOT_FIELDS}" | sed -n 's/^configuration_digest=//p')"
if [[ "${SELECTED}" != "${DOMAIN}" ]]; then
  echo "error: bootstrap selected_domain '${SELECTED}' does not match --domain '${DOMAIN}'. Failing closed." >&2
  exit 4
fi
if ! [[ "${CONFIG_DIGEST}" =~ ^[0-9a-f]{64}$ && "${CONFIG_REVISION}" =~ ^[0-9]+$ ]]; then
  echo "error: bootstrap pins malformed; failing closed." >&2
  exit 4
fi
log "Bootstrap: principal '${PRINCIPAL_ID}', domain '${DOMAIN}', configuration revision ${CONFIG_REVISION}, digest ${CONFIG_DIGEST:0:12}…"

# Protected readiness with explicit domain and explicit pins.
printf '%s\n' "header = \"X-IPAM-Domain: ${DOMAIN}\"" \
  "header = \"X-IPAM-Configuration-Revision: ${CONFIG_REVISION}\"" \
  "header = \"X-IPAM-Configuration-Digest: ${CONFIG_DIGEST}\"" >> "${CURL_CONFIG}"

log "GET ${API_URL}/api/readiness (Operator + domain '${DOMAIN}' + pins)"
READY_STATUS="$(curl_call GET "${API_URL}/api/readiness")" || {
  log "Transport error during readiness — outcome unknown; re-check, do not assume readiness."
  exit 3
}
body="$(cat "${BODY_OUT}")"
printf '%s\n' "${body}"
log "HTTP ${READY_STATUS}"

if [[ "${READY_STATUS}" == "401" ]]; then
  echo "error: readiness 401 — credential revoked, expired or disabled. Clear it; do not retry with the old token." >&2
  exit 4
fi
if [[ "${READY_STATUS}" == "403" ]]; then
  echo "error: readiness 403 — principal lacks Operator rights in '${DOMAIN}', or sent a forbidden combination. See the server code above." >&2
  exit 4
fi
if [[ "${READY_STATUS}" == "409" ]]; then
  echo "error: readiness 409 ACCESS_CONTEXT_STALE — configuration changed. Bootstrap again for the new pins, then re-check." >&2
  exit 1
fi

# HTTP 200 alone is insufficient: all six exact booleans must be true.
if [[ "${READY_STATUS}" == "200" ]] && python3 - "${BODY_OUT}" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    body = json.load(handle)
required = ("process_ready", "schema_ready", "data_ready",
            "static_ready", "configuration_ready", "domain_state_compatible")
missing = [name for name in required if body.get(name) is not True]
if missing:
    raise SystemExit(f"not ready: {', '.join(missing)} is not true")
PY
then
  log "Readiness confirmed: HTTP 200 with all six booleans true. Business-state recovery still needs its own separate comparison."
  exit 0
fi
log "Readiness NOT confirmed (HTTP ${READY_STATUS}; reasons printed in the body above)."
exit 1
