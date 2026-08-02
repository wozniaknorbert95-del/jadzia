---
gate: DEMAND-OS-DESK-5C-00
status: CLOSE · IA CLEANUP · deploy desk-dash04
updated: 2026-08-02
parent: docs/handoffs/2026-08-02-DEMAND-DESK-5B-CLOSE.md
---

# CLOSE — Etap 5c Biuro Popytu IA/UX cleanup

## Werdykt

**IA naprawione:** `/commander/` domyślnie → **Biuro Popytu**; Marketing tylko **Więcej (legacy)**; nav desktop+mobile spójny.

## Zmiany

| Obszar | Było | Jest |
|--------|------|------|
| Boot `vhqBoot()` | VHQ Start default | `openDemandDeskView()` default |
| Desktop nav | Start · Desk · **Marketing** · … | **Biuro Popytu** · Start · … · Więcej |
| Mobile nav | Start · **Marketing** · … | **Biuro Popytu** · Start · … · Więcej |
| Marketing | Równorzędny tab | Tylko More → `data-legacy="1"` |
| Cache | desk-dash03 | **desk-dash04** |

## Pliki

- `commander-ui/index.html` · `app.js` · `styles.css` · `sw.js`
- `tests/unit/test_demand_desk_ui_contracts.py` · `test_commander_complete_ui.py` · `e2e/test_demand_desk_flow.py`

## Verify

```bash
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/e2e/test_demand_desk_flow.py tests/unit/test_commander_complete_ui.py tests/unit/test_vhq_firm_ia_contracts.py -q
```

Prod: `https://api.zzpackage.flexgrafik.nl/commander/?cb=desk-dash04` → Biuro Popytu bez `?view=`

## Dowódca

- [ ] Phone: bottom nav → Biuro Popytu first
- [ ] `/commander/` cold open → Desk (nie VHQ)
- [ ] Marketing tylko z Więcej
- [ ] §8 design checkboxes (po wizualnym PASS)

Marketing **PARKED_LAST** — bez zmian.
