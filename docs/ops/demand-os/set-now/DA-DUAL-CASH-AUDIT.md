---
todo: DOS-INS-03
os_target_section_ref: "B.7 · STRATEGY Path D"
status: done
set_at: "2026-08-01"
---

# Design Agent — Dual Cash Kill Audit

## Reguła

Każdy lead DA → Wizard deeplink &lt;24h **albo** leave. Offerte ≠ sukces.

## Audit log

Plik: [`DA-AUDIT-LOG.csv`](./DA-AUDIT-LOG.csv)

| Werdykt | Warunek |
|---------|---------|
| PASS | Wizard push &lt;24h **lub** explicit leave |
| FAIL | Offerte/WA/mail bez Wizard w &lt;24h |

## Tydzień 2026-W31 (baseline)

| lead_id | outcome | Wizard &lt;24h | notes |
|---------|---------|--------------|-------|
| _(brak leadów w oknie)_ | N/A | N/A | 0 dual-cash FAIL · audit window open |

**DoD met (agent):** audit rytm + log LIVE · 0 FAIL w oknie. Runtime: każdy nowy lead DA = wiersz w DA-AUDIT-LOG.
