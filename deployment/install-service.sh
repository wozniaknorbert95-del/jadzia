#!/bin/bash
# Jadzia V4 - Systemd Service Installation Script

set -e

PROJECT_DIR="/root/jadzia"
SERVICE_FILE="jadzia.service"

echo "=========================================="
echo "  Jadzia V4 - Service Installation"
echo "=========================================="

# Check if running as correct user
if [ "$USER" != "root" ]; then
    echo "❌ Must run as root"
    exit 1
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

# Check if service file exists
if [ ! -f "$PROJECT_DIR/deployment/$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $PROJECT_DIR/deployment/$SERVICE_FILE"
    exit 1
fi

echo "✅ Project directory found"
echo "✅ Service file found"

# Create logs directory if not exists
mkdir -p "$PROJECT_DIR/logs"
echo "✅ Logs directory ready"

# Copy service file to systemd
echo "📝 Installing systemd service..."
sudo cp "$PROJECT_DIR/deployment/$SERVICE_FILE" /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
echo "🚀 Enabling service..."
sudo systemctl enable jadzia.service

# Start service
echo "▶️  Starting service..."
sudo systemctl start jadzia.service

# Check status
sleep 2
echo ""
echo "=========================================="
echo "  Service Status"
echo "=========================================="
sudo systemctl status jadzia.service --no-pager

echo ""
echo "=========================================="
echo "✅ Installation complete!"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  sudo systemctl status jadzia    # Check status"
echo "  sudo systemctl restart jadzia   # Restart service"
echo "  sudo systemctl stop jadzia      # Stop service"
echo "  sudo journalctl -u jadzia -f    # View logs (live)"
echo "  tail -f $PROJECT_DIR/logs/jadzia.log  # View app logs"
echo ""
