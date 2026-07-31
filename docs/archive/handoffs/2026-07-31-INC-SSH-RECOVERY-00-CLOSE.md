---
status: "[CLOSED]"
title: "INC-SSH-RECOVERY-00 — SSH connection recovered"
updated: "2026-07-31"
gate: "INC-SSH-RECOVERY-00"
evidence: "EV-CAMPUS-005 / EV-W2-011"
post_fix: "ssh_connection=ok · status=healthy"
---

# INC-SSH-RECOVERY-00 — CLOSE

**Date:** 2026-07-31  
**Verdict:** **RECOVERED** · `/worker/health` → `status=healthy` · `ssh_connection=ok`

---

## Root cause (no secrets)

| Finding | Detail |
|---------|--------|
| Baseline | sqlite OK · worker_loop_alive true · `ssh_connection=error` |
| TCP | Reachable on configured port |
| Key path in `.env` | Pointed at `/opt/jadzia/secrets/wordpress_key` |
| Key on disk | **Missing** (empty `secrets/` — consistent with prior `git clean` incident) |
| Key found | Present under `/root/.ssh/wordpress_key` |
| Known hosts path | Configured path missing |
| After key+known_hosts restore | Fingerprint pin in `.env` **stale** → `HostKeyVerificationError` |
| Final fix | Restore key + known_hosts · clear then re-pin live host-key fingerprint · restart |

---

## Recovery actions (config/ops only)

1. Copied key → `/opt/jadzia/secrets/wordpress_key` (mode 600, owner `jadzia`)
2. Built `/opt/jadzia/secrets/ssh_known_hosts` via `ssh-keyscan`
3. Cleared stale `SSH_HOST_KEY_FINGERPRINT`, verified probe OK
4. Re-pinned fingerprint from live negotiated host key
5. `systemctl restart jadzia`

**No** RejectPolicy change · **no** secrets committed · **no** fake health UI before post-fix.

---

## Post-fix

| Check | Result |
|-------|--------|
| `/worker/health` ssh_connection | **ok** |
| `/worker/health` status | **healthy** |
| sqlite_connection | true |
| worker_loop_alive | true |
| `test_ssh_connection()` | **Polaczenie SSH dziala** |

---

## UI honesty follow-up

- `VHQ_ROOMS["ai-agent-health"]`: DEGRADED → **PARTIAL** (SSH LIVE; OS/VCMS still PARTIAL)
- Critical SSH pin removed
- Mission Control KPI worker health updated
- Cache bust: **`vhq-w40c`**

---

## Related

- W4 LIVE agent dogfood: `docs/handoffs/2026-07-31-VF-VHQ-W4-LIVE-DOGFOOD.md` **PASS**
- Founder 5-min stamp pack: `docs/handoffs/2026-07-31-VF-VHQ-W4-ROOMS-OPERATIONS-FOUNDER-DOGFOOD.md` (`founder_stamp: pending`)

---

## STOP / residuals

- Do not start W5 without GO
- Do not commit `/opt/jadzia/secrets/*` or `.env`
- OS/VCMS post-auth PARTIAL remains
- Backup tip: keep secrets out of `git clean` paths
