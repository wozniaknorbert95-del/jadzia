## Handoff: Remediation baseline — git commit + hygiene

**Data:** 2026-06-26
**Autor:** Agent

### Kontekst

Duży working tree z wielu sesji remediacji (PLAN-REMEDIACJI) był niezacommitowany na `master`. Testy: **304 passed** przed commitem.

### Co zrobiono w tej sesji

1. **Weryfikacja:** pełny `pytest tests/` — zielony
2. **Hygiene workflow:** usunięto martwe referencje do `/pre-flight` w:
   - `.agents/workflows/vibe-init.md`
   - `.cursor/skills/vibe-init/SKILL.md`
   - `.opencode/agents/jadzia-builder.yaml`
3. **Git hygiene:** `*.egg-info/` dodane do `.gitignore`, `jadzia.egg-info/` usunięte z trackingu
4. **todo.json:** A3-01 → `in_progress` (partial migration documented)
5. **Commit baseline:** jeden logiczny commit z całą remediacją S1-S4 (poza S1-01 blocked)

### Stan backlogu po commicie

| ID | Status |
|----|--------|
| S1-01 | blocked (rotacja sekretów — Dowódca) |
| A1-01, A2-01, A4-01 | completed |
| A3-01 | in_progress |
| A5-01, D1-03 | pending |

### Następny krok

**A3-01 finish:** przenieść `call_claude`, `detect_session_source`, `get_cost_stats` do `core/llm.py`; usunąć lazy importy z `core/agent.py`.

### Deploy note

Przed wdrożeniem na VPS: jeśli są sesje tylko w `data/sessions/*.json`, zaimportować do SQLite (A4-01).
