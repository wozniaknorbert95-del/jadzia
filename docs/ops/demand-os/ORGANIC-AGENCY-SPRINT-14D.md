---
status: "[ACTIVE]"
title: "Organic Agency Sprint 14D — Ads PARK cash"
updated: "2026-08-01"
window: "2026-08-01 → 2026-08-14"
icp_role: "installateur"
ads: "PARKED_CASH"
deploy_vps: false
---

# Organic Agency Sprint 14D

**Problem #1:** nie ma klientów.  
**Narzędzia:** F1–F4 LOCAL DONE.  
**Ads:** PARK (brak kasy) — zero Meta/Google spend / boost.  
**Egzekucja:** organic TT + FB hunt + blog HITL + ledger.

Parent plan: Cursor plan *Organic Agency Sprint*.  
Set-now pack: [`set-now/`](./set-now/)

---

## Team pods (agency)

| Pod | Owner | Daily |
|-----|-------|-------|
| Growth Lead | Agent + Dowódca | priorytet dnia · Money Check Pon |
| Creative / TT | Agent_TT HITL + Dowódca shoot | Val → publish ≥3/tydz |
| Community Hunt | Agent_FB HITL (Trebron Norbert CDP) | 1 comment / dzień roboczy |
| Blog / SEO free | Dowódca HITL | 1 article ship (Tor3) |
| Sales / STL | Dowódca | hot → Wizard <15m |
| Sniper Val | F2 engine | 0 bypass |

**STOP 14d:** HQ · Agent OS desk · VPS · Ads · spam copy · generic AI blog.

---

## Tor 0 — LOCK (DONE 2026-08-01)

- [`set-now/ADS-FREEZE.md`](./set-now/ADS-FREEZE.md) = `parked_cash`
- `DOS-F5-01` = `parked`
- GO ORGANIC RESUME: [`set-now/GO-DAY-TODAY.md`](./set-now/GO-DAY-TODAY.md)

---

## Rytuał dzień-po-dniu

### D0 — 2026-08-01 (SoT + unfreeze) — AGENT DONE

- [x] Ads PARK cash
- [x] W1-03 → `in_progress`
- [x] W2-01 soft-start
- [x] Sprint pack + hunt/blog/trust playbooks
- [x] Val+calendar: `tt_w32_install_01/02/03` PASS · gate ALLOW #1
- [x] Hunt bank W32 + Val `fb_hunt_w32_d1` PASS
- [x] Hunt g2 attempt → **blocked** membership verify (logged)
- [ ] Dowódca: shoot / cut + publish TT #1 (human)


### D1 — 2026-08-02 (TT #1 + Hunt g2)

| Pod | Task |
|-----|------|
| TT | Val + publish `tt_w32_install_01` (caption z TT-CAPTIONS-W1) |
| FB | Hunt fb_g2 — [`FB-HUNT-DAILY.md`](./set-now/FB-HUNT-DAILY.md) |
| Ledger | 1 wiersz dnia (publish i/lub comments) |
| Trust | — |

CLI:

```bash
python tools/demand_os_utm.py build --channel tiktok --role installateur --asset-id tt_w32_install_01
python tools/demand_os_f2.py validate --channel tiktok --role installateur --asset-id tt_w32_install_01 --caption-file …
python tools/demand_os_f2.py gate --asset-id tt_w32_install_01
```

### D2 — 2026-08-03 (Pon Money Check + Hunt g3)

| Pod | Task |
|-----|------|
| Growth | Money Check W32 → `MONEY-CHECK-LOG.csv` |
| FB | Hunt fb_g3 |
| Blog | Start [`BLOG-HITL-SHIP.md`](./set-now/BLOG-HITL-SHIP.md) checklist |
| Ledger | daily row |

### D3 — 2026-08-04 (TT #2 + Hunt g4 + Blog ship)

| Pod | Task |
|-----|------|
| TT | publish #2 Val PASS |
| FB | Hunt fb_g4 |
| Blog | HITL publish `blog_w31_install_bus50m` → LEDGER publish=Y |
| Trust | opcjonalnie GBP teaser |

### D4 — 2026-08-05 (Hunt g5)

| Pod | Task |
|-----|------|
| FB | Hunt fb_g5 |
| TT | cut / prep #3 |
| Ledger | daily |

### D5 — 2026-08-06 (TT #3 + Hunt g6) — Ads nadal PARK

| Pod | Task |
|-----|------|
| TT | publish #3 → **≥3/tydz soft W1** |
| FB | Hunt fb_g6 |
| Ads | spend €0 (PASS) |
| Trust | 1× Google review ask jeśli był job |

### D6 — 2026-08-07 (Hunt g9)

| Pod | Task |
|-----|------|
| FB | Hunt fb_g9 |
| Ledger | daily |
| Sales | STL drill jeśli hot |

### D7 — 2026-08-08 (buffer / reply own TT)

| Pod | Task |
|-----|------|
| TT | reply własne filmy <2h jeśli komentarze |
| FB | rotate lub deep thread value |
| Ledger | daily |

### D8 — 2026-08-09 (prep W33 assets)

| Pod | Task |
|-----|------|
| Creative | shoot / batch W33 |
| Ledger | daily |

### D9 — 2026-08-10 (Pon Money Check #2)

| Pod | Task |
|-----|------|
| Growth | Money Check W33 |
| Hunt | continue 1/dzień |
| Ledger | daily |

### D10–D13 — 2026-08-11 … 08-14

| Focus | Task |
|-------|------|
| TT | utrzymaj rytm (kolejne 3 w W33 jeśli okno wymaga W1-PASS formal) |
| Hunt | domknij 5 dni z rzędu comments → ścieżka W2-PASS |
| Ledger | **14 unikalnych dat** bez luki >48h |
| Gate | audit PASS sprintu (tabela niżej) |

---

## Gate PASS sprintu

| Gate | Kryterium | Status tip |
|------|-----------|------------|
| W1 soft | ≥3 TT/tydz w oknie + Val 100% | pending HITL |
| Hunt | ≥5 dni `comments_sent≥1` | pending HITL |
| Blog | 1 article live + ledger | ready_for_human |
| Ledger | 14d bez luki >48h | in_progress |
| Ads | spend €0 | **PASS** (PARK) |

Po PASS: formal `DOS-W1-PASS` / `DOS-W2-PASS` · Wave3 2. article — **nie** F5.

---

## Pliki operacyjne

| Plik | Po co |
|------|-------|
| [`set-now/GO-DAY-TODAY.md`](./set-now/GO-DAY-TODAY.md) | unfreeze tip |
| [`set-now/FB-HUNT-DAILY.md`](./set-now/FB-HUNT-DAILY.md) | hunt |
| [`set-now/BLOG-HITL-SHIP.md`](./set-now/BLOG-HITL-SHIP.md) | blog |
| [`set-now/FREE-TRUST-RITUAL.md`](./set-now/FREE-TRUST-RITUAL.md) | GBP / reviews |
| [`set-now/LEDGER.csv`](./set-now/LEDGER.csv) | prawda |
| [`set-now/LEDGER-OPS-14D.md`](./set-now/LEDGER-OPS-14D.md) | 14d window |
| [`set-now/MONEY-CHECK-OPS.md`](./set-now/MONEY-CHECK-OPS.md) | Pon |
| [`../marketing/OPERATOR-TODAY.md`](../marketing/OPERATOR-TODAY.md) | start dnia |

---

## CLI cheat-sheet

```bash
python tools/demand_os_f2.py rules
python tools/demand_os_f2.py validate --channel tiktok --role installateur --asset-id ASSET --caption "…"
python tools/demand_os_f3.py allowlist
python tools/demand_os_f4.py pipeline --role installateur --asset-id blog_w31_install_bus50m
```
