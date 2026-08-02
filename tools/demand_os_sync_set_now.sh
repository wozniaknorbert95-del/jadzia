#!/usr/bin/env bash
# Sync sanitized set-now pack to VPS (run only with GO deploy).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/data/demand-os/set-now-sanitized/"
DEST="${1:-}"
if [[ -z "${DEST}" ]]; then
  echo "Usage: $0 user@host:/opt/jadzia/data/demand-os/set-now" >&2
  exit 1
fi
if [[ ! -d "${SRC}" ]]; then
  echo "FAIL: missing ${SRC}" >&2
  exit 1
fi
rsync -av --delete "${SRC}" "${DEST}/"
echo "OK: synced sanitized set-now to ${DEST}"
