#!/bin/bash
# Jadzia V4 - Automated VPS Deployment Script
# Run from LOCAL machine (Windows via Git Bash or WSL)

set -e

# VPS Configuration
VPS_HOST="185.243.54.115"
VPS_PORT="22"
VPS_USER="root"
VPS_PROJECT_DIR="/root/jadzia"
SSH_KEY="$HOME/.ssh/cyberfolks_key"
LOCAL_PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# WordPress Hosting Configuration (for reference)
WP_HOST="s34.cyber-folks.pl"
WP_PORT="222"
WP_USER="uhqsycwpjz"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  Jadzia V4 - VPS Deployment"
echo "=========================================="
echo -e "${BLUE}VPS:${NC} ${VPS_USER}@${VPS_HOST}:${VPS_PORT}"
echo -e "${BLUE}Local:${NC} ${LOCAL_PROJECT_DIR}"
echo -e "${BLUE}Remote:${NC} ${VPS_PROJECT_DIR}"
echo "=========================================="
echo ""

# Function: SSH command to VPS
run_ssh() {
    ssh -i "$SSH_KEY" -p "$VPS_PORT" -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" "$@"
}

# Function: SCP upload to VPS
upload_file() {
    scp -i "$SSH_KEY" -P "$VPS_PORT" -o StrictHostKeyChecking=no "$1" "${VPS_USER}@${VPS_HOST}:$2"
}

# Step 0: Check if running from correct directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: Run this script from Jadzia project root!${NC}"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Step 1: Check SSH connection
echo "🔑 Testing SSH connection to VPS..."
if ! run_ssh "echo 'SSH OK'" > /dev/null 2>&1; then
    echo -e "${RED}❌ SSH connection failed!${NC}"
    echo "Troubleshooting:"
    echo "  - Check SSH key: $SSH_KEY"
    echo "  - Check VPS is online: $VPS_HOST"
    echo "  - Try manual: ssh -i $SSH_KEY -p $VPS_PORT ${VPS_USER}@${VPS_HOST}"
    exit 1
fi
echo -e "${GREEN}✅ SSH connection successful${NC}"
echo ""

# Step 2: Ensure project directory exists (code-only update; never overwrites data/logs/.env)
echo "📁 Preparing project directory on VPS..."
run_ssh "mkdir -p $VPS_PROJECT_DIR"
# Optional: backup SQLite DB on VPS before deploy (safety)
run_ssh "test -f ${VPS_PROJECT_DIR}/data/jadzia.db && cp ${VPS_PROJECT_DIR}/data/jadzia.db ${VPS_PROJECT_DIR}/data/jadzia.db.bak.\$(date +%Y%m%d-%H%M%S) || true"
echo -e "${GREEN}✅ Project directory ready (data/logs/.env preserved)${NC}"
echo ""

# Step 3: Upload CODE only (never overwrites data/, logs/, .env; no --delete)
echo "📤 Uploading code to VPS (data/, logs/, .env excluded)..."
echo "This may take a few minutes..."

if command -v rsync &> /dev/null; then
    rsync -avz --progress \
        -e "ssh -i $SSH_KEY -p $VPS_PORT -o StrictHostKeyChecking=no" \
        --exclude 'venv/' \
        --exclude 'logs/' \
        --exclude 'data/' \
        --exclude '__pycache__/' \
        --exclude '*.pyc' \
        --exclude '.git/' \
        --exclude '.env' \
        --exclude '*.db-journal' \
        "${LOCAL_PROJECT_DIR}/" \
        "${VPS_USER}@${VPS_HOST}:${VPS_PROJECT_DIR}/"
else
    echo -e "${YELLOW}⚠️  rsync not found, using tar method...${NC}"
    tar -czf /tmp/jadzia-deploy.tar.gz \
        --exclude='venv' \
        --exclude='logs' \
        --exclude='data' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='.env' \
        .
    upload_file "/tmp/jadzia-deploy.tar.gz" "$VPS_PROJECT_DIR/"
    run_ssh "cd $VPS_PROJECT_DIR && tar -xzf jadzia-deploy.tar.gz && rm jadzia-deploy.tar.gz"
    rm /tmp/jadzia-deploy.tar.gz
fi
echo -e "${GREEN}✅ Code uploaded (data/logs/.env untouched)${NC}"
echo ""

# Step 4: Upload .env file
echo "🔐 Handling .env configuration..."
if [ -f ".env" ]; then
    echo "Local .env file found."
    read -p "Upload .env to VPS? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # Check if USE_SQLITE_STATE is set
        if grep -q "USE_SQLITE_STATE=1" .env; then
            echo -e "${GREEN}✅ USE_SQLITE_STATE=1 found in .env${NC}"
        else
            echo -e "${YELLOW}⚠️  Adding USE_SQLITE_STATE=1 to VPS .env${NC}"
        fi
        upload_file ".env" "${VPS_PROJECT_DIR}/.env"
        run_ssh "grep -q 'USE_SQLITE_STATE' ${VPS_PROJECT_DIR}/.env || echo 'USE_SQLITE_STATE=1' >> ${VPS_PROJECT_DIR}/.env"
        echo -e "${GREEN}✅ .env uploaded and configured${NC}"
    else
        echo -e "${YELLOW}⚠️  .env NOT uploaded - you must configure manually!${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No .env file found locally!${NC}"
    echo "You must create .env on VPS with required variables:"
    echo "  - ANTHROPIC_API_KEY"
    echo "  - SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY_PATH (for WordPress hosting)"
    echo "  - USE_SQLITE_STATE=1"
fi
echo ""

# Step 5: Upload SQLite database
echo "💾 Handling SQLite database..."
if [ -f "data/jadzia.db" ]; then
    DB_SIZE=$(du -h data/jadzia.db | cut -f1)
    echo "Local database found (size: $DB_SIZE)"
    read -p "Upload database to VPS? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        run_ssh "mkdir -p ${VPS_PROJECT_DIR}/data"
        upload_file "data/jadzia.db" "${VPS_PROJECT_DIR}/data/jadzia.db"
        echo -e "${GREEN}✅ Database uploaded${NC}"
    else
        echo -e "${YELLOW}⚠️  Starting with fresh database${NC}"
        run_ssh "mkdir -p ${VPS_PROJECT_DIR}/data"
    fi
else
    echo -e "${YELLOW}⚠️  No local database found - will start fresh${NC}"
    run_ssh "mkdir -p ${VPS_PROJECT_DIR}/data"
fi
echo ""

# Step 6: Install Python dependencies
echo "🐍 Installing Python dependencies on VPS..."
run_ssh "cd ${VPS_PROJECT_DIR} && python3 -m venv venv"
run_ssh "cd ${VPS_PROJECT_DIR} && source venv/bin/activate && pip install --upgrade pip setuptools wheel"
run_ssh "cd ${VPS_PROJECT_DIR} && source venv/bin/activate && pip install -r requirements.txt"
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 7: Create necessary directories
echo "📂 Creating required directories..."
run_ssh "cd ${VPS_PROJECT_DIR} && mkdir -p logs data/sessions"
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Step 8: Set up executable permissions
echo "🔧 Setting up file permissions..."
run_ssh "cd ${VPS_PROJECT_DIR}/deployment && chmod +x *.sh"
echo -e "${GREEN}✅ Permissions set${NC}"
echo ""

# Step 8b: Restart Jadzia service (so new code is loaded)
echo "🔄 Restarting Jadzia service..."
if run_ssh "systemctl is-active --quiet jadzia 2>/dev/null"; then
    run_ssh "sudo systemctl restart jadzia"
    echo -e "${GREEN}✅ Service restarted${NC}"
else
    echo -e "${YELLOW}⚠️  Service jadzia not active; skip restart${NC}"
fi
echo ""

# Step 9: Install and start systemd service
echo "⚙️  Installing systemd service..."
read -p "Install and start systemd service? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Running installation script..."
    run_ssh "cd ${VPS_PROJECT_DIR}/deployment && ./install-service.sh"
    echo -e "${GREEN}✅ Service installed and started${NC}"
else
    echo -e "${YELLOW}⚠️  Service NOT installed${NC}"
    echo "To install later, run on VPS:"
    echo "  cd ${VPS_PROJECT_DIR}/deployment && ./install-service.sh"
fi
echo ""

# Step 10: Health check
echo "🏥 Running health check..."
sleep 5
echo "Checking Jadzia API..."
if run_ssh "curl -s http://localhost:8000/worker/health" 2>/dev/null | grep -q '"status"'; then
    echo -e "${GREEN}✅ Jadzia is running!${NC}"
    echo ""
    echo "Health status:"
    run_ssh "curl -s http://localhost:8000/worker/health | python3 -m json.tool" || true
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Troubleshooting:"
    echo "  1. Check service status: ssh -i $SSH_KEY ${VPS_USER}@${VPS_HOST} 'sudo systemctl status jadzia'"
    echo "  2. View logs: ssh -i $SSH_KEY ${VPS_USER}@${VPS_HOST} 'tail -50 ${VPS_PROJECT_DIR}/logs/jadzia.log'"
    echo "  3. Check errors: ssh -i $SSH_KEY ${VPS_USER}@${VPS_HOST} 'tail -50 ${VPS_PROJECT_DIR}/logs/jadzia-error.log'"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "VPS Details:"
echo "  SSH: ssh -i $SSH_KEY ${VPS_USER}@${VPS_HOST}"
echo "  Project: ${VPS_PROJECT_DIR}"
echo "  API: http://${VPS_HOST}:8000"
echo ""
echo "Useful commands:"
echo "  # Check service status"
echo "  ssh -i $SSH_KEY ${VPS_USER}@${VPS_HOST} 'sudo systemctl status jadzia'"
echo ""
echo "  # View live logs"
echo "  ssh -i $SSH_KEY ${VPS_USER}@${VPS_HOST} 'tail -f ${VPS_PROJECT_DIR}/logs/jadzia.log'"
echo ""
echo "  # Restart service"
echo "  ssh -i $SSH_KEY ${VPS_USER}@${VPS_HOST} 'sudo systemctl restart jadzia'"
echo ""
echo "  # Test API"
echo "  curl http://${VPS_HOST}:8000/worker/health"
echo ""
echo "Next steps:"
echo "  1. Test API endpoint (from local machine)"
echo "  2. Create test task via Worker API"
echo "  3. Verify task persistence (restart service)"
echo "  4. Run field tests (4 scenarios)"
echo ""
