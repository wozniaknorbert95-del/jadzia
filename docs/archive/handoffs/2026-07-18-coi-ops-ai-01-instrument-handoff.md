# Handoff — COI-OPS-AI-01 instrumentacja (nie PASS)

**Date:** 2026-07-18  
**Gate:** `COI-OPS-AI-01` — **in_progress** (nie completed)  
**Local tip:** (uncommitted instrumentacja na master)  
**VPS tip SoT:** `8de8806`  
**VCMS / KNOW:** bez zmian (parked)

## DONE

1. **Re-measure 14d VPS** tip `8de8806`: **v1 = 11 AI / 13 human = 45.8%** (bez zmian vs baseline).
2. **Gap:** `widget_chat_sessions` bez `created_at` (7 sesji `updated_at` 14d); `cs_followup`×2 under-counted w v1.
3. **Instrumentacja v1.1 (kod lokalny):**
   - `agent/db.py`: kolumna `created_at` (set-once on insert) + migrate/backfill z `updated_at`
   - `deployment/_ops_ai_count_14d.py`: RATIO_V1 + RATIO_V11 + projekcja
   - tests: `test_widget_session_durability.py` — 7 passed
4. **Kontrakt v1.1:** AI = `brief_*` + `cs_followup` + leads created + widget `created_at`
5. Scorecard + todo + AGENTS zaktualizowane — **bez** completed / bez fałszywego PASS

## Liczby (VPS, świeże)

| Contract | AI | Human | Ratio | PASS? |
|----------|---:|------:|------:|-------|
| v1 | 11 | 13 | 45.8% | NO |
| v1.1 pre-migrate | 13 | 13 | 50.0% | NO (widget=0) |
| v1.1 **projected** po migrate | 20 | 13 | **60.6%** | YES projected |

## LEFT / BLOCKER

- **ready_for_human:** **GO deploy** tip z instrumentacją (Zasada 11) → restart → `python3 /tmp/_ops_ai_count_14d.py`
- Po SQL `PASS_GE_60 YES`: scorecard #9 LIVE + `COI-OPS-AI-01` completed + CLOSE
- Jeśli po deploy &lt;60%: osobna sesja safe AI volume (nie spam CRITICAL)
- PM ritual / Gate D — **parked**

## RISKS / DON'T

- Nie oznaczać completed bez świeżego SQL ≥60%
- Nie liczyć human publish jako AI
- Nie auto-approve CRITICAL / nie Gate D / nie deploy bez GO
- Nie commit `deployment/_mint_*` / `_recover_*`

## Changed files (local, uncommitted)

- `agent/db.py`
- `deployment/_ops_ai_count_14d.py`
- `tests/unit/test_widget_session_durability.py`
- `docs/ops/OPS-AI-SCORECARD.md`
- `docs/ops/SCORECARD-AI-OS-ZALICZENIE.md`
- `todo.json`, `AGENTS.md`, `brain.md`
- this handoff

## NEXT_SESSION

1. Human: **GO deploy** (lub commit+push najpierw jeśli chcesz review).  
2. Agent: deploy → re-measure → PASS only on number → handoff CLOSE.
