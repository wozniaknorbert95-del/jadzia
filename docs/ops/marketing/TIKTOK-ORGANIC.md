---
status: "[ACTIVE]"
title: "TikTok organic — dystrybucja assetu"
updated: "2026-07-26"
---

# TikTok organic (Jadzia channel)

**Gate SoT:** [FREE-TIKTOK.md](./FREE-TIKTOK.md)  
**GTM KPI:** [GTM-1PAGER.md](./GTM-1PAGER.md) — success = `wizard_starts` utm=tiktok, nie views.
**Design:** [2026-07-26-free-tiktok-jadzia-channel-design.md](../../superpowers/specs/2026-07-26-free-tiktok-jadzia-channel-design.md)  
**Konto:** [@flexgrafik.nl](https://www.tiktok.com/@flexgrafik.nl?lang=en)

**C1-01 TikTok Developer / API = PARK** do osobnego GO po gate 3/3 (**TT-PUB-01**).  
Ten plik = dystrybucja Asset Factory (jak FB organic HITL).

## Zasady

1. Ten sam master Reel co Meta — cut 15s hook na start (`tt_hook_15s.mp4`).  
2. Bio / link: Wizard z UTM `utm_source=tiktok&utm_medium=organic&utm_campaign=zzp_branding_check_v1`.  
3. Język: **NL**.  
4. Nie buduj osobnej „strategii TikTok” — mierz bio → Wizard starts (UTM).  
5. Cadence po gate: 2–3 clipy/tydz. z `MKT/YYYY-WW/`.  
6. **Brak IG** w stacku — TikTok zastępuje rolę „drugiego surface”, nie dual Meta.

## Checklist publish (HITL / agent-assist) — Studio path

Path LIVE: https://www.tiktok.com/tiktokstudio/upload

- [ ] `tt_hook_15s.mp4` (9:16 mp4) w folderze WW  
- [ ] Caption NL  
- [ ] **First comment** = Wizard pełny UTM (web Edit profile **nie ma** Website — verified 2026-07-26)  
- [ ] Wpis w kalendarzu Commander (`tiktok organic`, WW)  
- [ ] Po 7d: Studio Analytics + wizard_starts UTM tiktok  

**Nie zaliczaj** starego katalogu (≥12 video) jako nowego gate T2.

## Roadmapa Jadzia (parity FB)

| Gate | Co |
|------|-----|
| FREE-TIKTOK 3/3 | bio + 1 clip + nota |
| TT-PUB-01 | Content Posting API + `agent/publishers/tiktok.py` |
| TT-INS-01 | metrics → DTL |
| TT-CMT-01 | comment webhook → draft reply → bio (nie DM) |

## HARD STOP

RPA / Appium DM · phone farm · trend-scrape stack bez GO · secrets · fake PASS.
