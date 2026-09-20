#!/usr/bin/env bash
# Inspect and move snapshots that live inside the `ipam_demo_data` named
# volume, without giving the operator raw shell access into the container.
# Uses a throwaway helper container so it works whether the service is up
# or down. Read-only for the app database itself.
#
# Subcommands:
#   list                       list files under /data/snapshots
#   export <name> <host-path>  copy a snapshot out to the host
#   import <host-path> [name]  copy a snapshot in from the host
#   remove <name>              delete a snapshot (asks for --confirm)
#
# The core state commands (backup/restore/reset) never touch these files
# except for the specific active database, so this helper is safe alongside
# them as long as the service is stopped when the operator intends to
# restore what they just copied in.

source "$(dirname -- "$0")/common.sh"

usage() {
  cat >&2 <<'USAGE'
usage: scripts/ops/snapshots.sh <subcommand> [args]
  list
  export <snapshot-filename> <host-destination>
  import <host-source> [snapshot-filename]
  remove <snapshot-filename> --confirm
USAGE
}

if [[ $# -lt 1 ]]; then usage; exit 2; fi
subcommand="$1"; shift

# Run a short-lived helper inside the ipam service image with the same
# /data volume attached. Overrides the entrypoint and USER so busybox-style
# utilities are available and the file permissions match uid 10001.
volume_shell() {
  compose run --rm --no-deps --entrypoint "" "${SERVICE_NAME}" sh -c "$1"
}

case "${subcommand}" in
  list)
    volume_shell "install -d -m 0700 '${SNAPSHOT_DIR_CONTAINER}' && \
                  ls -lh '${SNAPSHOT_DIR_CONTAINER}' 2>/dev/null || \
                  echo '(no snapshots yet)'"
    ;;
  export)
    if [[ $# -ne 2 ]]; then usage; exit 2; fi
    name="$1"; host_dst="$2"
    case "${name}" in */*) echo "error: snapshot must be a plain filename." >&2; exit 2 ;; esac
    if [[ -e "${host_dst}" ]]; then
      echo "error: host destination already exists: ${host_dst}" >&2
      exit 2
    fi
    log "Exporting ${name} to ${host_dst}"
    # Compose cp copies from a service filesystem to the host without
    # requiring the container to be running.
    compose cp "${SERVICE_NAME}:${SNAPSHOT_DIR_CONTAINER}/${name}" "${host_dst}"
    log "Exported."
    ;;
  import)
    if [[ $# -lt 1 || $# -gt 2 ]]; then usage; exit 2; fi
    host_src="$1"; name="${2:-$(basename -- "${host_src}")}"
    case "${name}" in */*) echo "error: snapshot must be a plain filename." >&2; exit 2 ;; esac
    if [[ ! -f "${host_src}" ]]; then
      echo "error: host source does not exist or is not a regular file: ${host_src}" >&2
      exit 2
    fi
    log "Importing ${host_src} as ${name}"
    volume_shell "install -d -m 0700 '${SNAPSHOT_DIR_CONTAINER}'"
    compose cp "${host_src}" "${SERVICE_NAME}:${SNAPSHOT_DIR_CONTAINER}/${name}"
    log "Imported. Restore with: scripts/ops/restore.sh '${name}' --confirm"
    ;;
  remove)
    if [[ $# -lt 1 ]]; then usage; exit 2; fi
    name="$1"; shift
    case "${name}" in */*) echo "error: snapshot must be a plain filename." >&2; exit 2 ;; esac
    confirmed=0
    for arg in "$@"; do [[ "${arg}" == "--confirm" ]] && confirmed=1; done
    if [[ "${confirmed}" -ne 1 ]]; then
      echo "error: --confirm is required to delete a snapshot." >&2
      exit 2
    fi
    log "Removing ${name}"
    volume_shell "rm -- '${SNAPSHOT_DIR_CONTAINER}/${name}'"
    log "Removed."
    ;;
  *)
    usage
    exit 2
    ;;
esac
