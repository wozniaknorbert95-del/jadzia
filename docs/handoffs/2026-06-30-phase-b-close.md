# Handoff: Phase B close + deploy script OPS fix

**Date:** 2026-06-30  
**Task:** Close COI Phase B; align deploy scripts with `/opt/jadzia`  
**Status:** COMPLETED  
**Executor:** Agent

## What changed

1. **Phase B COMPLETE** — archived to `docs/archive/plans/PLAN-COI-PHASE-B.md`; stub in `docs/plans/`
2. **B3.1–B3.3** → `deferred` in `todo.json` (Dowódca decision)
3. **`deployment/deploy-to-vps.sh`** — `/opt/jadzia`, `chown jadzia:jadzia`, pip as `jadzia`
4. **`deployment/install-service.sh`** — `PROJECT_DIR=/opt/jadzia`
5. **`brain.md`**, **`todo.json`** — sprint `coi_phase_b: completed`, `active_plan: null`

## Token

Rotacja FB Page Access Token — **jutro, Dowódca** (nie blokuje dalszej pracy).

## Następna sesja (wybór modułu)

| Opcja | Repo | Task | Impact |
|-------|------|------|--------|
| **A (revenue)** | `zzpackage.flexgrafik.nl` | Wizard konwersja / checkout flow | Priorytet #1 ekosystemu |
| **B (growth)** | `flexgrafik-nl` | `FX-PORTFOLIO-PAGE-01` | HIGH UX — brak strony portfolio |
| **C (COI)** | `jadzia-core` | GA4 snapshot persist → weekly brief | Filar 4 charter |

## Regression

Brak zmian kodu runtime — tylko docs + deploy scripts. Nie wymaga redeploy VPS.
