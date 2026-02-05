#!/bin/bash
# Jadzia V4 - Systemd Service Uninstall Script

set -e

echo "=========================================="
echo "  Jadzia V4 - Service Uninstall"
echo "=========================================="

# Stop service
echo "⏹️  Stopping service..."
sudo systemctl stop jadzia.service || true

# Disable service
echo "🔓 Disabling service..."
sudo systemctl disable jadzia.service || true

# Remove service file
echo "🗑️  Removing service file..."
sudo rm -f /etc/systemd/system/jadzia.service

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "✅ Service uninstalled successfully!"
