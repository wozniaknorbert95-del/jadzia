# Deploy fix timeout (24h) – komendy na VPS

Fix: `WORKER_AWAITING_TIMEOUT_MINUTES = 1440` (24h) w `interfaces/api.py`.

---

## Sposób 1: Z PC (rsync) – zalecany

**Krok A – na swoim PC (Windows), w katalogu projektu Jadzia:**

```powershell
cd c:\Users\FlexGrafik\Desktop\projekty\Jadzia
# Wgraj kod na VPS (rsync przez Git Bash lub WSL)
bash deployment/deploy-to-vps.sh
```

Skrypt `deploy-to-vps.sh` wgra kod (w tym zmieniony `api.py`) i zrestartuje usługę na VPS.

**Krok B – opcjonalnie na VPS (weryfikacja):**

```bash
ssh root@185.243.54.115
cd /root/jadzia
grep "WORKER_AWAITING_TIMEOUT" interfaces/api.py
sudo systemctl status jadzia
tail -30 logs/jadzia.log
```

---

## Sposób 2: Wszystko na VPS (po wgraniu pliku)

Jeśli `api.py` jest już na VPS (scp/git/rsync), wklej na VPS:

```bash
# === DEPLOYMENT SCRIPT (run on VPS) ===
cd /root/jadzia

# 1. Backup
cp interfaces/api.py "interfaces/api.py.backup.$(date +%Y%m%d_%H%M%S)"

# 2. Update code (wybierz jedną opcję)
# --- GIT ---
# git pull origin main

# --- LUB wgraj z PC: scp (na PC): ---
# scp -P 22 interfaces/api.py root@185.243.54.115:/root/jadzia/interfaces/api.py

# 3. Restart (systemd)
sudo systemctl restart jadzia
sleep 3

# 4. Verify
systemctl status jadzia --no-pager
tail -20 logs/jadzia.log
grep "WORKER_AWAITING_TIMEOUT" interfaces/api.py

# 5. Test webhook (po ustawieniu .env)
source .env 2>/dev/null
curl -s -X POST "https://api.zzpackage.flexgrafik.nl/telegram/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: ${TELEGRAM_WEBHOOK_SECRET}" \
  -d '{"user_id":"6746343970","chat_id":"telegram_6746343970","message":"/pomoc"}' | head -c 300
echo ""
```

---

## Sposób 3: Skrypt na VPS

Na VPS (po wgraniu kodu):

```bash
cd /root/jadzia
chmod +x deployment/deploy-timeout-fix-vps.sh
./deployment/deploy-timeout-fix-vps.sh
```

Skrypt: backup → sprawdzenie 1440 w pliku → restart (systemd lub nohup) → logi → opcjonalny test webhook.

---

## Rollback

```bash
cd /root/jadzia
ls -la interfaces/api.py.backup.*
cp interfaces/api.py.backup.20260209_HHMMSS interfaces/api.py
sudo systemctl restart jadzia
```

---

## Podsumowanie

| Etap        | Akcja |
|------------|--------|
| 1. Backup  | `cp interfaces/api.py interfaces/api.py.backup.$(date +%Y%m%d_%H%M%S)` |
| 2. Update  | Z PC: `./deployment/deploy-to-vps.sh` **lub** na VPS: `git pull origin main` / scp `api.py` |
| 3. Restart | `sudo systemctl restart jadzia` |
| 4. Verify  | `systemctl status jadzia` + `tail -20 logs/jadzia.log` + `grep WORKER_AWAITING interfaces/api.py` |
| 5. Test    | `curl -X POST https://api.zzpackage.flexgrafik.nl/telegram/webhook ...` (z X-Webhook-Secret z .env) |
