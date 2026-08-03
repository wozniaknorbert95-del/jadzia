#!/usr/bin/env bash
# Sync sanitized set-now pack to DEST — SAFE by default (no --delete, runtime excluded).
# Usage:
#   tools/demand_os_sync_set_now.sh [--apply] user@host:/opt/jadzia/data/demand-os/set-now
# Default = dry-run (rsync -n). Pass --apply to write.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/data/demand-os/set-now-sanitized/"
APPLY=0
DEST=""

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --delete)
      echo "REFUSED: --delete is disabled (use manual ops if wipe required)" >&2
      exit 2
      ;;
    -*)
      echo "Unknown flag: $arg" >&2
      exit 2
      ;;
    *) DEST="$arg" ;;
  esac
done

if [[ -z "${DEST}" ]]; then
  echo "Usage: $0 [--apply] user@host:/path/to/set-now" >&2
  echo "Default: dry-run. Runtime excludes: LEDGER.csv MEMORY.json *.jsonl ENGAGE-LOG*" >&2
  exit 1
fi
if [[ ! -d "${SRC}" ]]; then
  echo "FAIL: missing ${SRC}" >&2
  exit 1
fi

EXCLUDES=(
  --exclude 'LEDGER.csv'
  --exclude 'MEMORY.json'
  --exclude '*.jsonl'
  --exclude 'ENGAGE-LOG*'
  --exclude 'CONTROL-AUDIT*'
  --exclude 'VALIDATOR-LOG.csv'
  --exclude '.write_probe'
)

RSYNC_FLAGS=(-av "${EXCLUDES[@]}")
if [[ "${APPLY}" -eq 0 ]]; then
  RSYNC_FLAGS+=(-n)
  echo "DRY-RUN (pass --apply to write). DEST=${DEST}"
else
  echo "APPLY sync (no --delete). DEST=${DEST}"
fi

echo "=== manifest (source phase0-ish) ==="
ls -1 "${SRC}" | head -40

rsync "${RSYNC_FLAGS[@]}" "${SRC}" "${DEST}/"
echo "OK: rsync finished (delete=OFF · runtime excluded)"
