# HTTPS setup – infrastructure analysis (plan only)

**Context:** VPS 185.243.54.115 (Ubuntu 24.04), hosting CyberFolks (s34.cyber-folks.pl:222), existing domain zzpackage.flexgrafik.nl (WordPress on hosting). Goal: HTTPS for Telegram webhook (e.g. `https://api.zzpackage.flexgrafik.nl/telegram/webhook`).

---

## Infrastructure analysis

| Item | Status |
|------|--------|
| **Existing domain** | In use: zzpackage.flexgrafik.nl points to WordPress on CyberFolks (s34.cyber-folks.pl). Root and current DNS are working. |
| **DNS control** | **Where:** Either (1) **CyberFolks client panel** (panel.cyberfolks.pl) if the domain uses CyberFolks nameservers (ns1.cyberfolks.pl etc.), or (2) **Registrar / DNS provider** for flexgrafik.nl if the domain uses external NS. **How:** Log in to the panel that manages the zone for flexgrafik.nl and use the DNS / "Rekordy DNS" or "Zarządzanie domeną" section. |
| **Subdomain feasible** | **Yes, in normal setup.** Adding an A record for a new subdomain (e.g. `api.zzpackage.flexgrafik.nl`) to `185.243.54.115` is standard and does not require moving the main site. The apex (zzpackage.flexgrafik.nl) can keep pointing to CyberFolks; only the subdomain hostname points to the VPS. If the panel does not allow adding A records for subdomains (rare), use Option C (Cloudflare Tunnel). |

**Verification to do:** Log in to panel.cyberfolks.pl (or the registrar for flexgrafik.nl), open DNS for flexgrafik.nl, and confirm you can add an A or CNAME record. Look for "Dodaj rekord" / "Add record", type A, name `api.zzpackage` (or `api` if the zone is zzpackage.flexgrafik.nl).

---

## Comparison

| Option | DNS setup | Time | Cost | Production grade | Risk |
|--------|-----------|------|------|------------------|------|
| **A: Subdomain on existing domain (api.zzpackage.flexgrafik.nl) → VPS, nginx + Let's Encrypt** | One A record in current DNS: `api.zzpackage.flexgrafik.nl` → `185.243.54.115`. No new domain. | ~25–40 min (DNS + nginx + certbot) | €0 | Yes | Low: single domain, one cert; main site unchanged. |
| **B: New domain → VPS (nginx + Let's Encrypt)** | New domain registered and A (or CNAME) to `185.243.54.115`. | ~30–50 min + domain purchase | Domain fee (~€8–15/year for .nl/.com) | Yes | Low; slightly more to maintain (two domains). |
| **C: Cloudflare Tunnel** | Domain (existing or new) on Cloudflare; no A to VPS; cloudflared on VPS. | ~30–45 min | €0 | Yes | Low; dependency on Cloudflare; no open 80/443 on VPS. |

---

## RECOMMENDATION

**Recommendation: Option A – subdomain on existing domain (api.zzpackage.flexgrafik.nl) with nginx + Let's Encrypt on the VPS.**

**Why:**

1. **Same provider, one domain** – You already use zzpackage.flexgrafik.nl on CyberFolks. Adding a subdomain that points to your VPS is the minimal change: no new domain, no extra cost, and clear naming (e.g. api.zzpackage.flexgrafik.nl for the Jadzia API).
2. **DNS is standard** – As long as you can edit DNS for flexgrafik.nl (in CyberFolks panel or at the registrar), you can add one A record. That does not affect the existing A/CNAME for the main site.
3. **Aligns with existing docs** – [HTTPS_SETUP_OPTIONS.md](HTTPS_SETUP_OPTIONS.md) recommends nginx + Let's Encrypt; this only fixes the hostname to your real domain and subdomain.
4. **Production-ready** – Let's Encrypt + certbot is widely used; certbot handles renewal. Single hostname for the webhook simplifies OPERATIONS and any future n8n/Telegram config.
5. **Option C as fallback** – If your current DNS does not allow an A record for a subdomain (unusual), use Cloudflare Tunnel with the same or another domain.

---

## Next steps for human (Option A)

### 1. Confirm where DNS for flexgrafik.nl is managed

- Log in to **panel.cyberfolks.pl** and check "Domeny" / "DNS" for flexgrafik.nl or zzpackage.flexgrafik.nl.
- If the domain is not there, check the registrar where flexgrafik.nl was registered and use their DNS / "Manage DNS" section.

### 2. Add A record for the API subdomain

- In that DNS panel, add a record:
  - **Type:** A
  - **Name:** `api.zzpackage` (or the label that yields api.zzpackage.flexgrafik.nl; some panels use "api" if the zone is already zzpackage.flexgrafik.nl).
  - **Value / Target:** `185.243.54.115`
  - **TTL:** 300–3600 (default is fine).
- Save and wait for propagation (often 5–15 min; up to 24–48 h in worst case). Check with: `dig A api.zzpackage.flexgrafik.nl` or an online DNS lookup.

### 3. On VPS: nginx + certbot

- SSH: `ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115`
- Install:
  ```bash
  sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx
  ```
- Firewall:
  ```bash
  sudo ufw allow 'Nginx Full'
  ```
  (and `sudo ufw enable` if needed).
- Create site config `/etc/nginx/sites-available/jadzia`:

```nginx
server {
    listen 80;
    server_name api.zzpackage.flexgrafik.nl;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- Enable and reload:
  ```bash
  sudo ln -s /etc/nginx/sites-available/jadzia /etc/nginx/sites-enabled
  sudo nginx -t && sudo systemctl reload nginx
  ```
- Certificate:
  ```bash
  sudo certbot --nginx -d api.zzpackage.flexgrafik.nl
  ```
  (agree to terms, give email, choose redirect HTTP→HTTPS if offered.)

### 4. Set Telegram webhook and health-check

- Webhook URL: `https://api.zzpackage.flexgrafik.nl/telegram/webhook`
- Quick check:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" https://api.zzpackage.flexgrafik.nl/worker/health
  ```
  (expect 200 if Worker API is up; may require JWT for other endpoints.)

### 5. Time estimate and production risks

- **Time:** ~25–40 min once DNS is editable and propagated (VPS steps ~15–20 min).
- **Risks:** (1) Wrong DNS panel or no permission to add A – fix by using the correct panel or Option C. (2) Certbot rate limits – use staging only for testing (`--staging`). (3) Nginx or firewall misconfig – test with `nginx -t` and `curl` from outside. (4) Jadzia not listening on 127.0.0.1:8000 – already the case per main.py (API_PORT 8000); no change needed.

---

**STOP after PLAN.** No edits or commands are executed; the human performs the steps above.
