#!/usr/bin/env bash
# OPS-01: Migrate Jadzia from root@/root/jadzia → jadzia@/opt/jadzia
# Usage: bash migrate-to-opt.sh
# Must be run as root (or sudo) on the VPS.
# Idempotent: safe to re-run if partially completed.

set -euo pipefail

# ===== Config =====
APP_NAME="jadzia"
SERVICE_FILE="/etc/systemd/system/jadzia.service"
SRC_DIR="/root/jadzia"
DEST_DIR="/opt/jadzia"
BACKUP_DIR="/root/jadzia-backup-$(date +%Y%m%d-%H%M%S)"
SERVICE_NAME="jadzia"

# ===== Color output =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[OPS-01]${NC} $*"; }
warn() { echo -e "${YELLOW}[!OPS-01]${NC} $*"; }
err()  { echo -e "${RED}[ERR OPS-01]${NC} $*" >&2; }

# ===== Pre-flight checks =====
preflight() {
    log "Running pre-flight checks..."

    # Must be root
    if [[ $EUID -ne 0 ]]; then
        err "This script must be run as root (or with sudo)."
        exit 1
    fi

    # Source must exist
    if [[ ! -d "$SRC_DIR" ]]; then
        warn "Source dir $SRC_DIR does not exist."
        if [[ -d "$DEST_DIR" ]]; then
            log "$DEST_DIR already exists, migration may already be complete."
            check_current_state
            exit 0
        fi
        err "Neither $SRC_DIR nor $DEST_DIR found. Nothing to migrate."
        exit 1
    fi

    # Destination must not exist (or be empty)
    if [[ -d "$DEST_DIR" ]] && [[ -f "$DEST_DIR/main.py" ]]; then
        warn "$DEST_DIR/main.py already exists. Assuming migration is complete."
        check_current_state
        exit 0
    fi

    # Service file must exist in repo and be deployed
    if [[ ! -f "$SERVICE_FILE" ]]; then
        warn "Service file not found at $SERVICE_FILE."
        warn "Deploy jadzia.service first: sudo cp deployment/jadzia.service $SERVICE_FILE"
        warn "Continuing anyway — service restart will need manual service file deployment."
    fi

    log "Pre-flight checks passed."
}

# ===== Create system user =====
create_user() {
    if id "$APP_NAME" &>/dev/null; then
        log "User '$APP_NAME' already exists. Skipping creation."
    else
        log "Creating system user '$APP_NAME'..."
        adduser --system --group --no-create-home "$APP_NAME"
    fi
}

# ===== Backup =====
backup() {
    log "Creating backup of $SRC_DIR → $BACKUP_DIR"
    cp -a "$SRC_DIR" "$BACKUP_DIR"
    if [[ -d "$BACKUP_DIR" ]]; then
        log "Backup created: $BACKUP_DIR"
    else
        err "Backup failed! Aborting."
        exit 1
    fi
}

# ===== Migrate =====
migrate() {
    log "Migrating $SRC_DIR → $DEST_DIR..."

    if [[ -d "$DEST_DIR" ]]; then
        log "$DEST_DIR exists but is incomplete. Merging..."
        # Copy only missing files
        rsync -a --ignore-existing "$SRC_DIR/" "$DEST_DIR/" 2>/dev/null || \
            cp -a "$SRC_DIR/." "$DEST_DIR/"
    else
        log "Moving $SRC_DIR → $DEST_DIR..."
        mv "$SRC_DIR" "$DEST_DIR"
    fi

    # Set ownership
    chown -R "${APP_NAME}:${APP_NAME}" "$DEST_DIR"
    chmod 750 "$DEST_DIR"

    # Protect .env
    if [[ -f "$DEST_DIR/.env" ]]; then
        chmod 640 "$DEST_DIR/.env"
    fi

    # Ensure logs dir exists
    mkdir -p "$DEST_DIR/logs"
    chown "${APP_NAME}:${APP_NAME}" "$DEST_DIR/logs"

    log "Migration complete. Ownership set to $APP_NAME:$APP_NAME."
}

# ===== Reload & restart service =====
restart_service() {
    log "Reloading systemd daemon..."
    systemctl daemon-reload

    log "Restarting $SERVICE_NAME..."
    systemctl restart "$SERVICE_NAME"

    log "Waiting 5s for service to stabilize..."
    sleep 5
}

# ===== Verify =====
verify() {
    log "Verifying service status..."

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "Service is ACTIVE."
    else
        err "Service is NOT active!"
        systemctl status "$SERVICE_NAME" --no-pager || true
        warn "Check logs: journalctl -u $SERVICE_NAME --no-pager -n 50"
        warn "Rollback available at: $BACKUP_DIR"
        return 1
    fi

    # Verify running user
    RUN_USER=$(ps -o user= -p $(pgrep -f "python.*main.py" | head -1) 2>/dev/null || echo "UNKNOWN")
    if [[ "$RUN_USER" == "$APP_NAME" ]]; then
        log "Process running as '$APP_NAME' (not root). ✓"
    else
        warn "Process running as '$RUN_USER' instead of '$APP_NAME'. Check service file."
    fi

    # Quick health check
    if command -v curl &>/dev/null; then
        HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health 2>/dev/null || echo "N/A")
        log "Health endpoint: $HEALTH"
    fi

    # Source dir cleanup (only if migration succeeded)
    if [[ -d "$SRC_DIR" ]] && [[ -f "$SRC_DIR/main.py" ]]; then
        log "Old $SRC_DIR still has files. Consider removing after verification:"
        log "  rm -rf $SRC_DIR"
    fi

    log "Migration OPS-01 COMPLETE."
}

# ===== Check current state =====
check_current_state() {
    log "Current state check:"
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        local svc_user
        svc_user=$(systemctl show "$SERVICE_NAME" --property=User --value 2>/dev/null || echo "check")
        log "Service: active (User=$svc_user)"
    else
        warn "Service: inactive"
    fi

    if [[ -d "$DEST_DIR" ]] && [[ -f "$DEST_DIR/main.py" ]]; then
        log "App directory: $DEST_DIR (exists)"
    else
        warn "App directory: $DEST_DIR (missing or incomplete)"
    fi

    if [[ -d "$SRC_DIR" ]]; then
        warn "Old directory still exists: $SRC_DIR"
    else
        log "Old directory removed: $SRC_DIR"
    fi
}

# ===== Rollback =====
rollback() {
    warn "Rolling back OPS-01 migration..."
    warn "This will restore $BACKUP_DIR → $SRC_DIR and restart as root."

    if [[ ! -d "$BACKUP_DIR" ]]; then
        err "No backup found at $BACKUP_DIR. Cannot rollback."
        exit 1
    fi

    # Stop service
    systemctl stop "$SERVICE_NAME" 2>/dev/null || true

    # Move back
    if [[ ! -d "$SRC_DIR" ]]; then
        mv "$BACKUP_DIR" "$SRC_DIR"
    else
        cp -a "$BACKUP_DIR/." "$SRC_DIR/"
    fi

    # Restore root ownership
    chown -R root:root "$SRC_DIR" || true

    # Update service file to root (revert to original)
    # You'll need to redeploy the original service file or edit manually
    warn "Service file still points to $DEST_DIR. To fully rollback:"
    warn "  1. Edit $SERVICE_FILE: User=root, WorkingDirectory=$SRC_DIR"
    warn "  2. systemctl daemon-reload && systemctl restart $SERVICE_NAME"

    log "Rollback complete. Verify with: systemctl status $SERVICE_NAME"
}

# ===== Main =====
main() {
    case "${1:-migrate}" in
        rollback)
            rollback
            ;;
        status)
            check_current_state
            ;;
        *)
            preflight
            create_user
            backup
            migrate
            restart_service
            verify
            ;;
    esac
}

main "$@"
