## Handoff: COI docs alignment

**Data:** 2026-06-26
**Autor:** Agent

### Cel

Synchronizacja dokumentacji jadzia-core i flexgrafik-meta z `module-jadzia-core.md` (COI charter). Bez implementacji P0 kodu.

### jadzia-core — zmienione pliki

| Plik | Zmiana |
|------|--------|
| `brain.md` | Przepisany: AS-IS ~40%, TO-BE Phase A, readiness matrix |
| `docs/PRD-core.md` | v2.0: custom pipeline, order_node P0, bez LangGraph/alembic |
| `AGENTS.md` | Linki COI + PLAN-COI-PHASE-A |
| `CLAUDE.md` | brain.md zamiast SYSTEM_BIBLE; widget flow |
| `Project-Instructions.md` | module spec + charter |
| `.agents/workflows/*` | agent/state/ paths, bez LangGraph default |
| `.cursor/skills/*` | idem |
| `.opencode/agents/jadzia-builder.yaml` | L0-L4, custom pipeline |
| `docs/plans/PLAN-COI-PHASE-A.md` | NOWY — aktywny plan |
| `docs/plans/PLAN-REMEDIACJI.md` | COMPLETED + pointer |
| `todo.json` | COI Phase A backlog (P0/P1/OPS) |

### flexgrafik-meta — zmienione pliki

| Plik | Zmiana |
|------|--------|
| `modules/module-jadzia-core.md` | §2 stack, §7 ~40%, §8 gaps DONE |
| `as-is-inventory.md` | §5 post-remediation |
| `integration-contracts.md` | INT-002 trusted_source paths |

### Grep audit (aktywne docs)

STALE refs ograniczone do archiwów (`docs/handoffs/`, `PLAN-REMEDIACJI.md` history).

### Git (sesja zamknięta)

- **Branch:** `master` (clean)
- **HEAD:** `24758f0` — docs(jadzia): align brain, PRD, and backlog with COI module spec
- **Poprzedni:** `c5e1021` A3-01, `e31a95e` remediation baseline
- **Pushed:** origin/master
- **flexgrafik-meta:** `e26775b` — module spec + as-is-inventory §5 (pushed main)

### Testy

304 passed, 1 skipped, 1 xfailed (2026-06-26)

### VPS (stan produkcji)

- Deploy remediacji wykonany wcześniej; health localhost OK
- Nadal: `root@/root/jadzia` (OPS-01 pending — docelowo `/opt/jadzia` + user `jadzia`)

### SESSION_VERDICT: SUCCESS (docs scope complete)
