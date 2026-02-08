# VPS HTTPS setup options for Telegram webhook

**Context:** Jadzia runs on VPS at `http://185.243.54.115:8000` (systemd service, [deployment/jadzia.service](../deployment/jadzia.service)). Telegram requires an **https://** URL for the webhook ([OPERATIONS.md](OPERATIONS.md) section 7). Target endpoint: `POST /telegram/webhook`.

---

## Option 1: Cloudflare Tunnel (cloudflared)

**Steps (human executes on VPS and Cloudflare dashboard):**

1. Add your domain to Cloudflare and point nameservers to Cloudflare.
2. In Cloudflare One: **Networks > Connectors > Cloudflare Tunnels > Create a tunnel**. Choose **Cloudflared**, name the tunnel (e.g. `jadzia-vps`), save.
3. Copy the install command from the dashboard (e.g. for Linux) and run it on the VPS to install and authenticate `cloudflared`.
4. In the tunnel's **Published applications** tab: add a **Public Hostname** – subdomain (e.g. `jadzia`) and domain from dropdown; **Service type** HTTP, **URL** `http://localhost:8000`; save.
5. Run the connector command on the VPS so the tunnel stays up (or install cloudflared as a systemd service and start it).
6. Set Telegram webhook (or n8n) to `https://<subdomain>.<your-domain>/telegram/webhook`.

**Prerequisites:** Domain added to Cloudflare; nameservers at registrar pointing to Cloudflare; SSH to VPS; cloudflared installed and token from dashboard.

**Time:** ~30–45 min (first time; includes DNS propagation if needed).

**Production:** Yes. No open inbound ports 80/443 on VPS; TLS at Cloudflare edge; free tier suitable for this use case.

**Pros:** No direct exposure of VPS ports; free; automatic HTTPS; DDoS/mitigation at edge; optional Access for auth.

**Cons:** Requires a domain and Cloudflare; traffic goes through Cloudflare; dependency on Cloudflare availability.

---

## Option 2: nginx + Let's Encrypt (certbot)

**Steps (human executes on VPS):**

1. Point a domain (or subdomain) A record to `185.243.54.115`.
2. SSH to VPS. Install nginx and certbot:
   ```bash
   sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx
   ```
3. Open firewall: `sudo ufw allow 'Nginx Full'` (and `ufw enable` if not already).
4. Create a server block that proxies to the app, e.g. in `/etc/nginx/sites-available/jadzia`:
   ```nginx
   server {
       listen 80;
       server_name <your-domain-or-subdomain>;
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   Enable it: `sudo ln -s /etc/nginx/sites-available/jadzia /etc/nginx/sites-enabled/` and `sudo nginx -t && sudo systemctl reload nginx`.
5. Obtain and attach certificate: `sudo certbot --nginx -d <your-domain>`. Follow prompts (agree, email, redirect HTTP to HTTPS).
6. Set Telegram webhook to `https://<your-domain>/telegram/webhook`. Certbot sets up auto-renewal (systemd timer/cron).

**Prerequisites:** Domain with A record to VPS IP; root/sudo on VPS; ports 80 and 443 open and allowed in firewall.

**Time:** ~20–30 min (after DNS points to VPS).

**Production:** Yes. Standard, widely used; certificates from a trusted CA; full control on your server.

**Pros:** No third-party tunnel; free certificates and renewal; full control; no traffic through a tunnel provider.

**Cons:** VPS must have public 80/443; you manage nginx and cert renewal (certbot automates it); need a domain.

---

## Option 3: ngrok

**Steps (human executes):**

1. Create an ngrok account at ngrok.com and get an authtoken from the dashboard.
2. On the VPS (or a machine that can reach the app): install ngrok agent, then `ngrok config add-authtoken <token>`.
3. Expose the app: `ngrok http 8000` (or `ngrok http 8000 --domain=<your-ngrok-static-domain>` if using the free static domain). If running on your laptop, ensure the target is the VPS (e.g. SSH port-forward 8000 to localhost and run ngrok against that, or run ngrok on the VPS).
4. Use the shown https URL (e.g. `https://xxxx.ngrok-free.app`) and set Telegram webhook to `https://<ngrok-host>/telegram/webhook`.
5. For "always on" on the VPS: run ngrok as a service (ngrok docs: background service) or use a process manager so the tunnel stays up.

**Prerequisites:** ngrok account; ngrok agent on the machine that exposes port 8000 (VPS or tunnel from elsewhere to VPS).

**Time:** ~10–15 min for a working URL.

**Production:** Free tier: 1 static domain, 20k HTTP requests/month, 1 GB bandwidth; no interstitial for programmatic/API traffic (Telegram webhook is API, so no browser warning). Paid plans remove interstitial and increase limits; free is acceptable for low-volume webhook-only use.

**Pros:** Very fast to get an https URL; no domain required for free static subdomain; no nginx or cert management; optional webhook verification features on paid.

**Cons:** Free tier limits (requests/bandwidth); URL is ngrok-branded unless paid; dependency on ngrok; for production at scale, paid plan is more appropriate.

---

## RECOMMENDATION

**Recommendation: Option 2 (nginx + Let's Encrypt)** for production Telegram webhook.

**Why:**

- You already have a VPS and a public IP; adding nginx and certbot is a one-time, well-documented setup with no ongoing cost and no dependency on a tunnel provider for traffic.
- You get a proper domain and a trusted certificate (Let's Encrypt), which fits a "production" webhook and future integrations (e.g. n8n, other webhooks).
- OPERATIONS.md and the codebase assume a stable base URL; a fixed domain fits that model better than a tunnel URL that can change (ngrok free) or depend on Cloudflare (Option 1).
- If you already have or plan a domain for the project, Option 2 adds minimal complexity (one reverse proxy, cert renewal automated by certbot).

Use **Option 1 (Cloudflare Tunnel)** if you prefer not to open 80/443 on the VPS and are fine with Cloudflare in front (and already use or want Cloudflare for the domain). Use **Option 3 (ngrok)** for quick validation or very low volume when you do not yet have a domain or want zero server config.
