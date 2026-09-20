#!/usr/bin/env bash
# Transfer standalone snapshots through a one-shot container, even after down.
# All operations take the app lock; stop the service first. Core restore owns
# database identity/schema/integrity validation. Imports never replace files.
source "$(dirname -- "$0")/common.sh"

usage() {
  cat >&2 <<'USAGE'
usage: scripts/ops/snapshots.sh <subcommand> [args]
  list
  export <snapshot-filename> <new-host-destination>
  import <host-source> [snapshot-filename]
  remove <snapshot-filename> --confirm
USAGE
}

if [[ $# -lt 1 ]]; then usage; exit 2; fi
subcommand="$1"; shift
transfer() {
  compose run --rm --no-deps --pull never -T --entrypoint "" "${SERVICE_NAME}" \
    python -c "$(cat "${SCRIPT_DIR}/snapshot_transfer.py")" "$@"
}
require_service_stopped

case "${subcommand}" in
  list)
    if [[ $# -ne 0 ]]; then usage; exit 2; fi
    transfer list
    ;;
  export)
    if [[ $# -ne 2 ]]; then usage; exit 2; fi
    name="$1"; host_dst="$2"
    if [[ -e "${host_dst}" || -L "${host_dst}" ]]; then
      echo "error: host destination already exists: ${host_dst}" >&2
      exit 2
    fi
    for suffix in -wal -shm -journal; do
      if [[ -e "${host_dst}${suffix}" || -L "${host_dst}${suffix}" ]]; then
        echo "error: host destination has a SQLite companion: ${host_dst}${suffix}" >&2
        exit 2
      fi
    done
    # Stage beside the requested destination. Link publication refuses even
    # raced-in names, and a failed transfer never becomes the final snapshot.
    temporary="$(mktemp "$(dirname -- "${host_dst}")/.ipam-export.XXXXXXXX")"
    trap 'rm -f -- "${temporary}"' EXIT
    transfer export "${name}" > "${temporary}"
    # -T is supported on the declared Linux host and refuses a raced directory.
    ln -T -- "${temporary}" "${host_dst}"
    log "Exported to ${host_dst}."
    ;;
  import)
    if [[ $# -lt 1 || $# -gt 2 ]]; then usage; exit 2; fi
    host_src="$1"; name="${2:-$(basename -- "${host_src}")}"
    metadata="$(python3 "${SCRIPT_DIR}/snapshot_transfer.py" describe "${host_src}")"
    read -r size digest <<< "${metadata}"
    transfer import "${name}" "${size}" "${digest}" < "${host_src}"
    log "Imported without overwrite. Restore with: scripts/ops/restore.sh '${name}' --confirm"
    ;;
  remove)
    if [[ $# -ne 2 || "$2" != "--confirm" ]]; then usage; exit 2; fi
    transfer remove "$1"
    log "Removed snapshot $1."
    ;;
  *) usage; exit 2 ;;
esac
