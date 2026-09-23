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
# Token custody: the token is read from a protected file by a Python
# reader that validates regular-file/no-symlink, owner-only mode and exact
# shape, then writes the bearer line straight into the 0600 curl config —
# the token never enters a shell variable, argv, URLs, logs, snapshots or
# browser storage. Tracing is disabled on entry (set +x/+v): inherited
# `bash -x/-v` debugging is unsupported for this wrapper because trace
# output would capture secrets; the script turns it off before any secret
# handling. Loopback only (structurally parsed exact numeric loopback
# authority, validated BEFORE any credential read or request); proxies off
# and redirects never followed. Malformed credential/header values fail
# closed with no request sent. Bootstrap and error output never include
# credential-bearing data (only principal id, revision and digest, which
# are not credentials).
#
# Usage:
#   scripts/ops/acquire.sh --token-file <coordinator-token-file> \
#       --key <idempotency-key> --reason "<reason>" [--api-url <base-url>]
#
# Exit codes:
#   0  acquired: exact evidence triple (201 + header false + body false,
#      or 200 + header true + body true)
#   2  usage or local validation failure (no request sent, or refused before POST)
#   3  transport failure — outcome UNKNOWN, may or may not have committed
#   4  authentication/authorization refusal (401/403: revoked, expired,
#      unknown, disabled, or not the coordinator — do not retry blindly)
#   5  server refusal with guidance (409/422/503: busy, stale, conflict,
#      exhausted, rejected, or not ready)
#   6  inconsistent success evidence (status/header/body disagree) — outcome
#      UNKNOWN, original key/reason preserved, no new cycle claimed
#
# Revoked/stale/unknown outcomes are reported exactly as the server stated
# them, never normalised into success.

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
usage: scripts/ops/acquire.sh --token-file <coordinator-token-file> --key <idempotency-key> --reason "<reason>" [--api-url <base-url>]

  --token-file   separately provisioned coordinator token file (64 lowercase hex, no domain)
  --key          original stable idempotency key (1..200 chars; retained across retries)
  --reason       original reason text (1..200 chars; retained across retries)
  --api-url      numeric loopback origin only, e.g. http://127.0.0.1:8000
                 (default http://127.0.0.1:8000; DNS names rejected)

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

# Loopback only, structurally parsed BEFORE any credential read or request:
# exact numeric loopback authority (127.0.0.1 or ::1 — no DNS names, so no
# suffix-host or resolver tricks), http scheme, no userinfo, a valid port,
# origin form only (no path beyond "/", no query, no fragment), and no
# control characters or quotable/injectable characters. This rejects e.g.
# http://localhost.example.invalid and http://127.0.0.1@example.invalid.
validate_origin_url() {
  python3 - "$1" <<'PY'
import sys, urllib.parse
url = sys.argv[1]
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
if parts.path not in ("", "/") or parts.query or parts.fragment:
    sys.exit("API base must be origin only (no path, query or fragment)")
PY
}
validate_origin_url "${API_URL}" || { echo "error: refusing non-loopback or malformed --api-url (loopback origin only)." >&2; exit 2; }
# A single trailing slash on the base is normalized away after validation
# (the wrapper appends paths such as /api/..., so a kept "/" would produce
# "//api/..."). The numeric loopback-only policy above is unchanged.
API_URL="${API_URL%/}"

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

WORKDIR="$(mktemp -d)"
trap 'rm -rf -- "${WORKDIR}"' EXIT
chmod 700 "${WORKDIR}"
CURL_CONFIG="${WORKDIR}/curl.conf"
HEADERS_OUT="${WORKDIR}/headers.txt"
BODY_OUT="${WORKDIR}/body.txt"
: > "${CURL_CONFIG}"; : > "${HEADERS_OUT}"; : > "${BODY_OUT}"
chmod 600 "${CURL_CONFIG}" "${HEADERS_OUT}" "${BODY_OUT}"

# Protected header delivery: base curl options plus Content-Type live in the
# 0600 config file; the bearer line is appended by the Python reader below.
# Proxies off, redirects never followed (--location is never passed, so the
# default of zero redirects holds).
printf '%s\n' "silent" "show-error" "max-time = 30" "noproxy = *" \
  "header = \"Content-Type: application/json\"" > "${CURL_CONFIG}"
chmod 600 "${CURL_CONFIG}"

# Credential file, enforced before any network use (and after URL
# validation, so no directive is parsed before the origin is known safe).
# The Python reader opens with O_RDONLY|O_NOFOLLOW|O_NONBLOCK (a swapped-in
# symlink fails the open itself — no lstat/open race — and a FIFO fails
# fast instead of blocking indefinitely; the fstat regular-file check then
# refuses anything that is not a regular file), then checks the open
# fstat: regular file, owner-only mode (any group/other bit refuses),
# owned by the current user. The read is bounded to 67 bytes (valid
# content is at most 65: 64 hex plus one terminal newline), so no
# unbounded read follows any size signal. Content must be exactly 64
# lowercase hex with at most one documented terminal newline; internal
# whitespace is rejected, never silently stripped. The reader writes the
# bearer line straight into the 0600 curl config, so the token never
# enters a shell variable or expansion. Any failure exits without a
# request and without secret output.
if ! python3 - "${TOKEN_FILE}" "${CURL_CONFIG}" <<'PY' 2>/dev/null; then
import os, re, stat, sys
token_path, config_path = sys.argv[1], sys.argv[2]
try:
    fd = os.open(token_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
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
# (Both pin values were regex-validated from bootstrap — numeric revision,
# hex digest — so no header or curl-directive injection is possible here.)

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
# Exact success evidence (app.py:521-528; offline-api §8.3): 201 carries
# X-Acquisition-Replay: false with body replay false (fresh acquisition),
# 200 carries X-Acquisition-Replay: true with body replay true (original
# replay). The header value must match ^(true|false)$ exactly and the body
# must parse as JSON with a boolean replay field; all three must agree.
# Missing, malformed or contradictory evidence is reported as UNKNOWN /
# inconsistent: the original key and reason are preserved, no new cycle is
# claimed, and nothing is retried automatically.
EVIDENCE="$(python3 - "${BODY_OUT}" <<'PY' 2>/dev/null || echo "BODY_UNPARSEABLE"
import json, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    body = json.load(handle)
replay = body.get("replay")
if not isinstance(replay, bool):
    sys.exit("body replay is not a boolean")
print("true" if replay else "false")
PY
)"
# X-Acquisition-Replay is parsed deliberately: the header field name
# matches case-insensitively, only trailing OWS/CR is trimmed from the
# value, exactly one occurrence must exist, and the value must be exactly
# "true" or "false" (no case folding, no inner-whitespace removal — a
# value like "t r u e" is malformed). Anything else yields empty output,
# which fails the triple check below as UNKNOWN/inconsistent.
REPLAY_HEADER="$(python3 - "${HEADERS_OUT}" <<'PY' 2>/dev/null || true
import sys
values = []
with open(sys.argv[1], "rb") as handle:
    for raw in handle.read().split(b"\n"):
        line = raw.decode("latin-1")
        if line.lower().startswith("x-acquisition-replay:"):
            values.append(line.split(":", 1)[1].strip(" \t\r"))
if len(values) == 1 and values[0] in ("true", "false"):
    print(values[0])
PY
)"
log "HTTP ${POST_STATUS}"

case "${POST_STATUS}" in
  201)
    if [[ "${REPLAY_HEADER}" == "false" && "${EVIDENCE}" == "false" ]]; then
      log "Acquired fresh cycle (201 + replay header false + body replay false). Record run/cycle/operation IDs from the body above."
      exit 0
    fi
    cat >&2 <<'INCONSISTENT'
error: 201 without exact fresh-acquisition evidence (need X-Acquisition-Replay: false AND body replay false). Outcome is UNKNOWN/inconsistent:
a cycle may or may not have advanced. Keep the SAME key and reason; do NOT
invent a replacement key and do NOT claim success. Only after an explicit
operator-confirmed decision, re-run this exact command and validate the
replay triple again.
INCONSISTENT
    exit 6 ;;
  200)
    if [[ "${REPLAY_HEADER}" == "true" && "${EVIDENCE}" == "true" ]]; then
      log "Replay of the original operation (200 + replay header true + body replay true). No new cycle was advanced."
      exit 0
    fi
    cat >&2 <<'INCONSISTENT'
error: 200 without exact replay evidence (need X-Acquisition-Replay: true AND body replay true). Outcome is UNKNOWN/inconsistent:
no new cycle may be claimed. Keep the SAME key and reason; do NOT invent a
replacement key. Only after an explicit operator-confirmed decision, re-run
this exact command and validate the replay triple again.
INCONSISTENT
    exit 6 ;;
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
    echo "error: 503 — service or configuration not ready (see the server code above: SETUP_NEEDED, ACCESS_CONFIGURATION_* or STORE_*). Diagnose the concrete code first: seed only deliberately fresh, uninitialized disposable data, never as a generic recovery step." >&2
    exit 5 ;;
  *)
    echo "error: unexpected HTTP ${POST_STATUS}; see the body above. Outcome for a 5xx may be ambiguous — keep the same key." >&2
    exit 5 ;;
esac
