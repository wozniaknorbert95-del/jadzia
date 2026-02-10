#!/bin/bash
# DEPLOY FIX: WORKER_AWAITING_TIMEOUT_MINUTES = 24h
# Uruchom NA VPS (ssh root@185.243.54.115) po wgraniu kodu z PC (rsync) lub po git pull.
# Chmod: chmod +x deployment/deploy-timeout-fix-vps.sh

set -e

cd /root/jadzia

echo "=== 1. BACKUP ==="
cp interfaces/api.py "interfaces/api.py.backup.$(date +%Y%m%d_%H%M%S)"
echo "Backup: interfaces/api.py.backup.*"
ls -la interfaces/api.py.backup.* 2>/dev/null | tail -1
echo ""

echo "=== 2. UPDATE CODE ==="
# --- OPCJA A: Git (jeśli na VPS jest klon repozytorium) ---
# git fetch origin
# git pull origin main

# --- OPCJA B: Kod wgrywany z PC przez rsync (uruchom NA PC w katalogu projektu): ---
#   cd /path/do/Jadzia
#   ./deployment/deploy-to-vps.sh
# Po deploy-to-vps.sh kod jest już na VPS; na VPS wykonaj tylko: backup (1), restart (3), verify (4).
# Jeśli NIE używasz deploy-to-vps.sh w tej sesji, wgraj tylko zmieniony plik z PC:
#   scp -P 22 interfaces/api.py root@185.243.54.115:/root/jadzia/interfaces/api.py

# --- OPCJA C: Ręczna edycja na VPS (jeśli brak git i rsync) ---
# nano interfaces/api.py
# Zmień linię z WORKER_AWAITING_TIMEOUT_MINUTES na:
#   WORKER_AWAITING_TIMEOUT_MINUTES = int(os.getenv("WORKER_AWAITING_TIMEOUT_MINUTES", "1440") or "1440")

# Weryfikacja że zmiana jest w pliku (jeśli już wgrałeś kod)
if grep -q 'WORKER_AWAITING_TIMEOUT_MINUTES.*1440' interfaces/api.py; then
    echo "OK: WORKER_AWAITING_TIMEOUT_MINUTES=1440 (24h) w interfaces/api.py"
else
    echo "UWAGA: W pliku nie ma 1440. Wgraj nowy api.py (z PC: deploy-to-vps.sh lub scp), potem uruchom ten skrypt ponownie."
    exit 1
fi
echo ""

echo "=== 3. RESTART BOTA (graceful) ==="
if systemctl is-active --quiet jadzia 2>/dev/null; then
    sudo systemctl restart jadzia
    echo "OK: systemctl restart jadzia"
else
    # Fallback: bez systemd (uruchomienie ręczne)
    pkill -f "python main.py" 2>/dev/null || true
    sleep 2
    source venv/bin/activate
    nohup python main.py >> logs/jadzia.log 2>> logs/jadzia-error.log &
    echo "OK: uruchomiono przez nohup (brak systemd)"
fi
sleep 3
echo ""

echo "=== 4. WERYFIKACJA ==="
if systemctl is-active --quiet jadzia 2>/dev/null; then
    systemctl status jadzia --no-pager -l
else
    ps aux | grep "[p]ython main.py" || echo "Proces nie znaleziony!"
fi
echo "--- Ostatnie linie logu (jadzia.log) ---"
tail -25 logs/jadzia.log
echo ""
echo "--- Wartość timeoutu w kodzie (potwierdzenie) ---"
grep "WORKER_AWAITING_TIMEOUT" interfaces/api.py || true
echo ""

echo "=== 5. TEST WEBHOOK (opcjonalny) ==="
# Załaduj .env żeby mieć TELEGRAM_WEBHOOK_SECRET
set -a
source .env 2>/dev/null || true
set +a
if [ -n "$TELEGRAM_WEBHOOK_SECRET" ]; then
    echo "Wywołanie POST /telegram/webhook (pomoc)..."
    curl -s -X POST "https://api.zzpackage.flexgrafik.nl/telegram/webhook" \
      -H "Content-Type: application/json" \
      -H "X-Webhook-Secret: ${TELEGRAM_WEBHOOK_SECRET}" \
      -d '{"user_id":"6746343970","chat_id":"telegram_6746343970","message":"/pomoc"}' | head -c 500
    echo ""
else
    echo "TELEGRAM_WEBHOOK_SECRET nie ustawiony w .env - pomijam test webhook."
    echo "Ręczny test: curl -X POST https://api.zzpackage.flexgrafik.nl/telegram/webhook -H 'Content-Type: application/json' -H 'X-Webhook-Secret: TWOJ_SECRET' -d '{\"message\":\"/pomoc\", ...}'"
fi
echo ""

echo "=== GOTOWE ==="
echo "Timeout awaiting: 24h (1440 min). Aby wyłączyć: w .env ustaw WORKER_AWAITING_TIMEOUT_MINUTES=0"
echo "Rollback: cp interfaces/api.py.backup.<timestamp> interfaces/api.py && sudo systemctl restart jadzia"
