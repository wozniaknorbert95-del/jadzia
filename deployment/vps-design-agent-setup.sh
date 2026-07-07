#!/bin/bash
# Design Agent — VPS setup (run ON VPS as root after jadzia code deploy)
# Installs VGE path, upload dir, nginx snippet, env placeholders.
set -euo pipefail

VGE_DIR="/opt/vge/image-generator"
UPLOAD_DIR="/var/www/design-agent-uploads"
SSOT="/opt/zzpackage/system/data/product-master-table.json"
JADZIA_ENV="/opt/jadzia/.env"

echo "=== Design Agent VPS setup ==="

mkdir -p "$VGE_DIR" "$UPLOAD_DIR"
chown -R jadzia:jadzia "$UPLOAD_DIR"
chmod 755 "$UPLOAD_DIR"

if [ ! -f "$SSOT" ]; then
  echo "WARN: SSoT missing at $SSOT — sync zzpackage system/ to VPS"
fi

# Append env keys if missing (operator fills secrets)
append_env() {
  local key="$1"
  local val="$2"
  if ! grep -q "^${key}=" "$JADZIA_ENV" 2>/dev/null; then
    echo "${key}=${val}" >> "$JADZIA_ENV"
    echo "Added ${key} to .env"
  fi
}

touch "$JADZIA_ENV"
chmod 640 "$JADZIA_ENV"
chown jadzia:jadzia "$JADZIA_ENV"

append_env "VGE_ROOT" "$VGE_DIR"
append_env "ZZPACKAGE_SSOT_PATH" "$SSOT"
append_env "DESIGN_AGENT_OUTPUT_DIR" "$UPLOAD_DIR"
append_env "DESIGN_AGENT_PUBLIC_URL" "https://api.zzpackage.flexgrafik.nl/uploads/design-agent"
append_env "DESIGN_AGENT_ENABLE_PHOTOREAL" "0"
append_env "DESIGN_AGENT_QA_STRICT" "1"

if [ -d "$VGE_DIR" ] && [ -f "$VGE_DIR/requirements.txt" ]; then
  echo "Installing VGE Python deps..."
  sudo -u jadzia bash -c "cd $VGE_DIR && python3 -m venv venv 2>/dev/null || true && source venv/bin/activate && pip install -q -r requirements.txt"
fi

echo "=== Reload nginx if config updated ==="
if nginx -t 2>/dev/null; then
  systemctl reload nginx || true
fi

systemctl restart jadzia
sleep 3
CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:8000/api/v1/design-agent/generate || true)
echo "design-agent route HTTP: $CODE (expect 401 or 422, not 404)"

echo "=== Done. Set FG_DESIGN_AGENT_KEY in $JADZIA_ENV then restart jadzia ==="
