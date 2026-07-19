# Handoff — MB shadow eval-pack v2 (Telegram-first)

**Date:** 2026-07-19  
**Gate:** MKT-BRAIN-PRO  
**Status:** CODE READY — deploy needs Dowódca GO (Zasada 11)

## Co to jest eval-pack

Tygodniowy test zaufania: Dowódca ocenia decyzje shadow MB (agree/partial/disagree).  
Gate przed `MB_MODE=propose`: accuracy ≥70% **oraz** ≥20 scored na 14d (preferuj 2 tygodnie z rzędu).

## Werdykt (pro) — wdrożone w kodzie

| Element | v1 (stare) | v2 (teraz) |
|---------|------------|------------|
| Sample | dump last N | stratified ~10–12/tydz, cap/rule, skip HEU_NO_SIGNAL spam |
| Scoring | CSV blank | Telegram buttons + API |
| Persist | brak | `marketing_shadow_eval` |
| Gate | tylko doc | `compute_accuracy` + `GET …/shadow/accuracy` |

## Jak używać (po deploy)

1. Telegram: `/mb_eval` → karty ze score  
2. Lub `POST …/commander/marketing/shadow/eval-push`  
3. Progress: `GET …/shadow/accuracy`  
4. Backup CSV: `python scripts/mb_shadow_eval_export.py --format csv -o eval.csv`

## Pliki

- `agent/marketing/shadow_eval.py`
- `agent/marketing/telegram_proposals.py` (`mb_score_*`, `send_eval_pack_telegram`)
- `agent/db.py` (`marketing_shadow_eval`)
- `api/telegram.py` (`/mb_eval`)
- `api/routes/commander.py` (accuracy / eval-score / eval-push)
- `tests/unit/test_mb_shadow_eval.py` — 4 passed

## NIE zrobione

- Deploy VPS (czekaj GO)
- Flip `MB_MODE=propose`
