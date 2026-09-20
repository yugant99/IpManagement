#!/usr/bin/env bash
# Tail service logs. Defaults to follow-mode; forward extra flags to
# `docker compose logs` for one-shot inspection (e.g. `-n 200 --no-follow`).

source "$(dirname -- "$0")/common.sh"

if [[ "$#" -eq 0 ]]; then
  set -- --follow --tail=200
fi
compose logs "$@" "${SERVICE_NAME}"
