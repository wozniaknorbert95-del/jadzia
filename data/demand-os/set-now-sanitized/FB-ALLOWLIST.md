---
todo: DOS-C2-01
os_target_section_ref: "C.2"
status: done
set_at: "2026-08-01"
agency: "ALLOWLIST-RESEARCH.md · max 10"
join_actor: "personal:Trebron Norbert"
---

# FB Allowlist — agency pack (max 10)

**Runtime SoT:** [`ALLOWLIST.json`](./ALLOWLIST.json)  
**Research:** [`ALLOWLIST-RESEARCH.md`](./ALLOWLIST-RESEARCH.md)  
**Join log:** [`JOIN-LOG.md`](./JOIN-LOG.md)

| id | nazwa | status | icp |
|----|-------|--------|-----|
| fb_own_page | FlexGrafik page | **active** | all |
| fb_g1 | ZZP’ers in de bouw vanaf €35 | join_requested | installateur |
| fb_g2 | ZZP BOUW – Werk & Opdrachten NL | **active** | installateur |
| fb_g3 | zzp'ers in de bouw | **active** | installateur |
| fb_g4 | Zzp projecten door heel Nederland | **active** | installateur |
| fb_g5 | ZZP Bouw & Construction | **active** | installateur |
| fb_g6 | Zzp opdrachten bouw en techniek | **active** | installateur |
| fb_g7 | ZZP opdrachten midden NL | join_requested | installateur |
| fb_g8 | ZZP Community Nederland | join_requested | multi |
| fb_g9 | Hoveniers gezocht NL | **active** | hovenier |
| fb_g10 | ZZP - Vraag en Aanbod | join_requested | installateur |

## Zakazy

- \>**10** grup → FAIL  
- Ten sam copy na wiele grup / dzień → FAIL (anti-spam F3)  
- Engage bez `active` (przed Join) → DENY  
- Fake trade answers (VCA / „jestem hovenier”) → STOP  

## Next

1. Await admin: g1, g7, g8, g10  
2. `python tools/demand_os_f3.py activate --target-id fb_gN` po approve  
3. Engage tylko z F2 gate + anti-spam  
