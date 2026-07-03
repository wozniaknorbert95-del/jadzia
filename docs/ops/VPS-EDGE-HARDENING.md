# VPS Edge Hardening Runbook (optional — Phase 6)

**Scope:** Infrastructure in front of jadzia `:8000`  
**Owner:** Dowódca (manual)  
**Repo:** jadzia-core (docs only)

## Current state (post S2-01 deploy)

- jadzia binds `0.0.0.0:8000` with JWT on admin routes
- `JADZIA_ENV=production` enforces required secrets at boot
- Public by design: widget chat, portal qualify, health probes, WC webhook (HMAC)

## Recommended nginx front

```nginx
# /etc/nginx/sites-available/jadzia-api
limit_req_zone $binary_remote_addr zone=widget:10m rate=30r/m;
limit_req_zone $binary_remote_addr zone=portal:10m rate=20r/m;

server {
    listen 443 ssl http2;
    server_name api.jadzia.example;  # or IP-only TLS

    location /api/v1/widget/chat {
        limit_req zone=widget burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/v1/portal/qualify {
        limit_req zone=portal burst=5 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }

    location / {
        # Deny public internet; allow office IP only
        allow 1.2.3.4;   # Dowódca IP
        deny all;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## Firewall (ufw)

```bash
ufw default deny incoming
ufw allow 22/tcp
ufw allow from TRUSTED_IP to any port 8000
ufw enable
```

## Bind jadzia to localhost only (alternative)

In `jadzia.service` change to `--host 127.0.0.1` and expose only via nginx.

## Verification

- External scan: admin routes not reachable without VPN/IP allowlist
- Widget still works from `zzpackage.flexgrafik.nl` origin (CORS)
- `curl -X POST /chat` from internet → timeout or 403 (not 401 with open port)
