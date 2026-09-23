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
# Token custody mirrors acquire.sh: a Python reader validates the token
# file (regular file, no symlink, owner-only mode, exact shape) and writes
# the bearer line straight into the 0600 curl config — the token never
# enters a shell variable, argv, URLs, logs, snapshots or browser storage.
# Tracing is disabled on entry (set +x/+v): inherited `bash -x/-v`
# debugging is unsupported for this wrapper. URLs are structurally parsed
# BEFORE any credential read or request: exact numeric loopback authority
# (127.0.0.1 or ::1, no DNS), no userinfo, valid port; the API base must
# be origin only while the liveness URL must carry exactly the /healthz
# path. The domain allowlist is deliberately narrower than the server's
# text rule (no controls, quotes or backslashes) so no header line or curl
# directive is injectable; malformed values fail before any network use.
# Error output carries no credential-bearing data.
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
# Tracing (including an inherited `bash -x/-v`) would capture secrets into
# trace output, so it is disabled here, before any secret handling. Caller
# debugging of this wrapper is unsupported; diagnose via its stderr/log
# lines and the server's X-Request-ID instead.
set +x +v

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
  --domain       explicit selected domain: 1..200 [A-Za-z0-9._-] chars, never '*'
                 (deliberately narrower than the server text rule for header safety)
  --api-url      numeric loopback origin only, e.g. http://127.0.0.1:8000
                 (default http://127.0.0.1:8000; DNS names rejected)
  --health-url   numeric loopback liveness URL with exactly the /healthz path
                 (default http://127.0.0.1:8000/healthz)
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

# Loopback only, structurally parsed BEFORE any credential read or
# request. Shared rules: http scheme, exact numeric loopback authority
# (127.0.0.1 or ::1 — no DNS names), no userinfo, valid port, no controls
# or injectable characters. The API base must be origin only; the liveness
# URL must carry exactly the /healthz path (no query or fragment).
validate_loopback_url() {
  python3 - "$1" "$2" <<'PY'
import sys, urllib.parse
url, kind = sys.argv[1], sys.argv[2]
if any(ord(char) < 32 or ord(char) == 127 for char in url):
    sys.exit("control character in URL")
if any(char in url for char in (' ', '"', '\\', '<', '>', '^', '`', '{', '}', '|')):
    sys.exit("injectable character in URL")
try:
    parts = urllib.parse.urlsplit(url)
    port = parts.port
except ValueError:
    sys.exit("invalid authority or port")
if parts.scheme != "http":
    sys.exit("scheme must be http")
if "@" in (parts.netloc or ""):
    sys.exit("userinfo forbidden")
if (parts.hostname or "") not in ("127.0.0.1", "::1"):
    sys.exit("authority must be exactly 127.0.0.1 or [::1]")
if port is not None and not 1 <= port <= 65535:
    sys.exit("invalid port")
if kind == "liveness":
    if parts.path != "/healthz" or parts.query or parts.fragment:
        sys.exit("liveness URL must carry exactly the /healthz path")
elif parts.path not in ("", "/") or parts.query or parts.fragment:
    sys.exit("API base must be origin only (no path, query or fragment)")
PY
}
if [[ "${MODE}" == "liveness" ]]; then
  validate_loopback_url "${HEALTH_URL}" liveness || { echo "error: refusing non-loopback or malformed --health-url (numeric loopback with exactly /healthz)." >&2; exit 2; }
else
  validate_loopback_url "${API_URL}" origin || { echo "error: refusing non-loopback or malformed --api-url (loopback origin only)." >&2; exit 2; }
  # A single trailing slash on the base is normalized away after validation
  # (the wrapper appends paths such as /api/..., so a kept "/" would
  # produce "//api/..."). The numeric loopback-only policy is unchanged.
  API_URL="${API_URL%/}"
fi

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

# Domain header value: deliberately narrower than the server's text rule.
# Only dot/dash/underscore alphanumerics (1..200 chars, never "*") reach
# the raw header argument and the curl config file, so embedded CR/LF,
# other controls, quotes and backslashes — and therefore header splitting
# or curl-directive injection — are rejected BEFORE any request.
if ! [[ "${DOMAIN}" =~ ^[A-Za-z0-9._-]{1,200}$ && "${DOMAIN}" != "*" ]]; then
  echo "error: --domain must be 1..200 [A-Za-z0-9._-] characters (never '*'); failing closed before any request." >&2
  exit 2
fi

# Credential file, enforced exactly as in acquire.sh and after URL/domain
# validation: O_NOFOLLOW open (no lstat/open symlink race), descriptor
# fstat (regular file, owner-only mode, current-user ownership), read
# bounded to 67 bytes, exact 64-lowercase-hex content with at most one
# documented terminal newline. The Python reader writes the bearer line
# straight into the 0600 curl config; the token never enters a shell
# variable or expansion.
printf '%s\n' "-silent" "-show-error" "max-time = 10" "noproxy = *" > "${CURL_CONFIG}"
chmod 600 "${CURL_CONFIG}"
if ! python3 - "${TOKEN_FILE}" "${CURL_CONFIG}" <<'PY' 2>/dev/null; then
import os, re, stat, sys
token_path, config_path = sys.argv[1], sys.argv[2]
try:
    fd = os.open(token_path, os.O_RDONLY | os.O_NOFOLLOW)
except OSError:
    sys.exit("open refused")
try:
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode):
        sys.exit("not a regular file")
    if info.st_mode & 0o077:
        sys.exit("group/other permissions")
    if info.st_uid != os.geteuid():
        sys.exit("ownership")
    with os.fdopen(fd, "rb") as handle:
        raw = handle.read(67)
    fd = -1
finally:
    if fd != -1:
        try:
            os.close(fd)
        except OSError:
            pass
if len(raw) > 66:
    sys.exit("too large")
try:
    text = raw.decode("ascii")
except UnicodeDecodeError:
    sys.exit("non-ascii content")
if text.endswith("\n"):
    text = text[:-1]
if not re.fullmatch(r"[0-9a-f]{64}", text):
    sys.exit("shape")
with open(config_path, "a", encoding="ascii") as handle:
    handle.write('header = "Authorization: Bearer %s"\n' % text)
PY
  echo "error: --token-file refused (must be a regular non-symlink file owned by the current user, owner-only mode, bounded size, exactly 64 lowercase hex with at most one trailing newline). Failing closed without contacting the service." >&2
  exit 2
fi

# Bootstrap WITH the explicit domain (optional on this route; sent here so
# the selected domain is confirmed before readiness).
log "GET ${API_URL}/api/access-context (bootstrap for domain '${DOMAIN}')"
BOOT_STATUS="$(curl_call GET "${API_URL}/api/access-context" -H "X-IPAM-Domain: ${DOMAIN}")" || {
  log "Transport error — is the service running? (scripts/ops/start.sh)"
  exit 3
}
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

# Protected readiness with explicit domain and explicit pins. All three
# values were shape-validated above (restricted domain charset, numeric
# revision, hex digest), so no header splitting or curl-directive
# injection is possible here.
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
