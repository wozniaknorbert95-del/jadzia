#!/bin/bash
# Check that SSH key exists before connecting to VPS 185.243.54.115.
# If key is missing, exit with a clear error instead of waiting for interactive password.
# Usage: ./check_ssh_key.sh [key_path]
#   key_path defaults to /root/.ssh/cyberfolks_key (or $SSH_KEY if set)

set -e

SSH_KEY="${1:-${SSH_KEY:-/root/.ssh/cyberfolks_key}}"
VPS_HOST="${VPS_HOST:-185.243.54.115}"

if [ -z "$SSH_KEY" ]; then
    echo "ERROR: SSH key path not set. Use: $0 /path/to/key or set SSH_KEY." >&2
    exit 1
fi

if [ ! -f "$SSH_KEY" ]; then
    echo "ERROR: SSH key not found: $SSH_KEY" >&2
    echo "Cannot connect to $VPS_HOST without key. Add the key file or run from a host that has it." >&2
    echo "" >&2
    echo "To fix permissions for all keys in .ssh (run on the host that has the key):" >&2
    echo "  chmod 700 ~/.ssh" >&2
    echo "  chmod 600 ~/.ssh/cyberfolks_key" >&2
    echo "  # Or all private keys (excluding .pub): for f in ~/.ssh/*; do [ -f \"\$f\" ] && [ \"\${f%.pub}\" = \"\$f\" ] && chmod 600 \"\$f\"; done" >&2
    exit 1
fi

if [ -d "$SSH_KEY" ]; then
    echo "ERROR: Path is a directory, not a key file: $SSH_KEY" >&2
    exit 1
fi

echo "SSH key found: $SSH_KEY"
exit 0
