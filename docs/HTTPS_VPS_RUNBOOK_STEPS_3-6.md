# HTTPS VPS runbook – steps 3–6 (run on VPS)

**When:** After steps 1–2 are done (nginx + certbot installed, ufw configured).  
**Where:** Run these on the VPS after `ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115`.

---

## Step 3: Create nginx server block

**Option A – from local project (copy file to VPS):**
```bash
# From your LOCAL machine (PowerShell/terminal):
scp -i ~/.ssh/cyberfolks_key C:\Users\FlexGrafik\Desktop\projekty\Jadzia\jadzia-nginx.conf root@185.243.54.115:/etc/nginx/sites-available/jadzia
```

Then on the VPS:
```bash
ln -sf /etc/nginx/sites-available/jadzia /etc/nginx/sites-enabled
```

**Option B – create file directly on VPS:**
```bash
cat > /etc/nginx/sites-available/jadzia << 'EOF'
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
EOF
ln -sf /etc/nginx/sites-available/jadzia /etc/nginx/sites-enabled
```

**PASS:** `cat /etc/nginx/sites-available/jadzia` shows the server block; `ls -la /etc/nginx/sites-enabled/jadzia` shows symlink.

---

## Step 4: Test nginx config and reload

```bash
nginx -t && systemctl reload nginx
```

**PASS:** Output shows `syntax is ok` and `test is successful`; reload completes with no error.

---

## Step 5: Obtain SSL cert

```bash
certbot --nginx -d api.zzpackage.flexgrafik.nl
```

- Enter email when prompted.
- Agree to terms.
- Choose “Redirect HTTP to HTTPS” (recommended: Yes).

**PASS:** Message “Successfully received certificate” / “Congratulations! … HTTPS is enabled”.

**FAIL:** “Challenge failed” → check DNS (api.zzpackage.flexgrafik.nl → 185.243.54.115). For testing only, use `--staging`.

---

## Step 6: Verify HTTPS

```bash
curl -sI https://api.zzpackage.flexgrafik.nl/worker/health
```

**PASS:** `HTTP/2 200` or `HTTP/1.1 200`; no SSL errors.

```bash
curl -s https://api.zzpackage.flexgrafik.nl/worker/health
```

**PASS:** JSON response from Jadzia (e.g. `{"status":"ok"}`).
