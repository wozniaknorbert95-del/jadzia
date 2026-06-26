# S1-03: Dedicated System User Setup

**Zasada 11: Commander executes on VPS.**

## Steps

1. **Create user:**
   ```bash
   sudo adduser --system --group --no-create-home jadzia
   ```

2. **Move app to /opt and set permissions:**
   ```bash
   sudo mv /root/jadzia /opt/jadzia
   sudo chown -R jadzia:jadzia /opt/jadzia
   sudo chmod 750 /opt/jadzia
   sudo chmod 640 /opt/jadzia/.env
   ```

3. **Update service file** (done — see jadzia.service):
   ```
   User=jadzia
   Group=jadzia
   ```

4. **Reload & restart:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart jadzia
   sudo systemctl status jadzia
   ```

5. **Verify:**
   ```bash
   ps aux | grep jadzia
   # Should show jadzia user, not root
   ```
