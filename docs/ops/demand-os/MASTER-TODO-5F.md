---
gate: DEMAND-OS-DESK-5F-00
status: ACTIVE
updated: "2026-08-02"
owner: agent-orchestrator
human_gate: "Dowódca §8 prod → Hard DoD 15/15"
supersedes_gate: DEMAND-OS-DESK-5B-00
close_target: "tool_100 SEALED · Commander dashboard 100% per surface"
---

# MASTER TODO — Etap 5f (Commander Dashboard 100%)

> **Jedyny aktywny backlog egzekucji UI.** Nie twórz równoległych planów.  
> Domykaj po kolei: **P0 → P1 → P2 → SEAL**. Jedno zadanie = jeden commit-worthy deliverable.

## Hierarchia SoT (czytaj w tej kolejności)

| Priorytet | Plik | Rola |
|-----------|------|------|
| 1 | **Ten plik** | Master TODO — co robić teraz |
| 2 | `docs/ops/demand-os/STATE.md` | Faza programu · prod_tip · Hard DoD |
| 3 | `.cursor/current-task.md` | **Jedno** aktywne zadanie bieżącej sesji |
| 4 | `todo.json` → `active_gate` | Gate maszyny · musi = `DEMAND-OS-DESK-5F-00` |
| 5 | `docs/ops/demand-os/DEMAND-CONTROL-PANEL-DESIGN.md` | Design v2.1 · §8 acceptance |
| 6 | `docs/ops/demand-os/DESK-UI-HANDOFF.md` | Kontrakt UI |
| 7 | `docs/handoffs/` | Dowód CLOSE (≤15 rolling) |

**Zakaz:** nowy gate bez CLOSE poprzedniego · fałszywy SEAL · commit `docs/ops/demand-os/set-now/` z `pass_token`.

---

## Stan wejścia (post audit enterprise 2026-08-02)

| Surface | Ocena | Bloker |
|---------|-------|--------|
| Biuro Popytu | ~75% | banner MIXED, Ponów ghost, hunt SENT UI |
| Kolejka | ~30% | VHQ console + 20× CEO stub |
| Analityka | ~40% | wieczne „Ładowanie…” |
| Agenci | ~20% | rejestr nie ładuje |
| Marketing legacy | ~20% | 3× loading |
| VHQ (Więcej) | ~50% | cały DOM w tle na Desk |
| Ustawienia / Audyt | ~80% | OK |
| Hard DoD | **14/15** | #12 Dowódca §8 prod |

**Prod:** `https://api.zzpackage.flexgrafik.nl/commander/?cb=desk-dash08` · tip post-deploy

---

## Role agentów (przydział na sesję)

| ID | Rola | Scope | Output obowiązkowy |
|----|------|-------|-------------------|
| **A** | SoT / BPM | STATE, todo, current-task, handoff | Zero rozjazdów gate |
| **B** | UI Engineer | `commander-ui/` | Diff + cache bump |
| **C** | QA / Proof | pytest + browser | PASS/FAIL per surface |
| **D** | Ops | set-now sync, deploy | prod_tip + verify curl |

**Orchestrator:** wybiera **jeden** item P0, deleguje B+C, A domyka docs, D tylko na GO.

---

## Definition of Done — surface 100%

Surface jest **DONE** gdy **wszystkie** punkty:

- [ ] Cold open = właściwy widok (bez teatru VHQ w tle / DOM noise)
- [ ] Każda sekcja: dane **albo** honest empty + „co zrobić” — **nigdy** stuck „Ładowanie…”
- [ ] Każdy przycisk przeklikany → oczekiwany efekt
- [ ] Każde przekierowanie → właściwy target
- [ ] pytest gate PASS (lista w workflow)
- [ ] Browser proof (prod lub local) w handoff
- [ ] Brak regresji: JWT, refresh, 375px

**Anti-ściema:** grep-only ≠ E2E · kod istnieje ≠ done · SEAL bez §8 = FAIL.

---

## MASTER BACKLOG

Legenda status: `open` · `in_progress` · `done` · `blocked` · `ready_for_human`

### P0 — Blokery (max 1–2 na sesję)

| ID | Zadanie | Owner | Status | DoD skrót | Verify |
|----|---------|-------|--------|-----------|--------|
| **5F-P0-01** | VHQ lazy/off-DOM — mount tylko po Więcej→VHQ | B | `done` | Desk bez 1000+ ukrytych node VHQ w a11y | browser: Desk-only snapshot <400 interactive refs VHQ hidden |
| **5F-P0-02** | Kolejka = czysta queue (bez Director Brief, filtr CEO stub) | B | `done` | Tab Kolejka: CRITICAL/ACTION + CS, zero stub spam | browser Kolejka tab |
| **5F-P0-03** | URL hygiene — Desk czyści `?vhq=` | B | `done` | Powrót Desk → URL bez vhq; brak ghost state | browser URL assert |
| **5F-P0-04** | Banner MIXED/FIXTURE prominent | B | `done` | §8: żółty banner przy data_mode≠REAL | browser + test |
| **5F-P0-05** | Hunt dry → SENT badge w UI | B | `done` | Po dry: SENT + disabled; reload OK | browser + `test_hunt_dry_updates_queue.py` |
| **5F-P0-06** | Connection banner hide on 200 | B | `done` | Brak „Ponów” gdy API OK | browser refresh Desk |

### P1 — Zakładki wypełnione

| ID | Zadanie | Owner | Status | DoD skrót | Verify |
|----|---------|-------|--------|-----------|--------|
| **5F-P1-01** | Analityka — KPI scoreboard load/empty | B | `done` | Koniec „Ładowanie analityki…” | browser Analityka |
| **5F-P1-02** | Agenci — rejestr z API | B | `done` | Lista agentów status/SLA | browser Agenci |
| **5F-P1-03** | Marketing legacy — MB + draft + queue | B | `done` | 3 sekcje: data lub PARKED | browser Marketing |
| **5F-P1-04** | Gorące/STL — kontekst + CTA | B | `done` | breach z linkiem do checklist | browser Desk sekcja D |

### P2 — SEAL (human + agent)

| ID | Zadanie | Owner | Status | DoD skrót | Verify |
|----|---------|-------|--------|-----------|--------|
| **5F-P2-01** | Dowódca §8 prod phone smoke | Human | `ready_for_human` | 7/7 checkbox design §8 | `DESK-PHONE-SMOKE-CHECKLIST.md` |
| **5F-P2-02** | Hard DoD 15/15 + tool_100 SEALED | A | `open` | STATE + handoff CLOSE | audit matrix |

### DONE (nie cofać — historia 5b→5e)

| Etap | Gate | Close handoff |
|------|------|---------------|
| 5b | DEMAND-OS-DESK-5B-00 | `2026-08-02-DEMAND-DESK-5B-CLOSE.md` |
| 5c | DEMAND-OS-DESK-5C-00 | `2026-08-02-DEMAND-DESK-5C-IA-CLOSE.md` |
| 5d | DEMAND-OS-DESK-5D-00 | `2026-08-02-DEMAND-DESK-5D-IA-CLOSE.md` |
| 5e | DEMAND-OS-DESK-5E-00 | `2026-08-02-DEMAND-DESK-5E-GAP-CLOSE.md` |

---

## Aktywne zadanie (pointer)

```
CURRENT: 5F-P2-01 (human)
NEXT:    5F-P2-02 SEAL after §8
BLOCKED: deploy — cleared (GO 2026-08-02)
```

Mirror: `.cursor/current-task.md` musi = ten ID + gate.

---

## Protokół sesji (1-1-1)

```text
1. READ  STATE + MASTER-TODO (ten plik) + current-task
2. SYNC  todo.json active_gate = DEMAND-OS-DESK-5F-00 (Agent A)
3. PICK  pierwsze open w P0 (nie P1 jeśli P0 open)
4. BUILD Agent B — minimal diff, commander-ui + tests
5. PROVE Agent C — pytest + browser prod ?cb=desk-dashXX
6. LOOP  max 3 fix attempts → else blocked + checklist
7. CLOSE Agent A — handoff + STATE + MASTER-TODO status=done + current-task next ID
8. COMMIT safe files only (gitleaks)
9. DEPLOY tylko GO / standing policy
```

---

## Protokół pętli (Cursor Automation / scheduled)

Workflow: `.agents/workflows/demand-os-master-loop.md`

```text
WHILE exists(open in P0|P1) AND NOT Hard DoD 15/15:
  RUN protokół sesji dla CURRENT pointer
  ADVANCE pointer to next open
IF P0+P1 done AND P2-01 pending:
  SET ready_for_human Dowódca §8
  STOP (no fake SEAL)
IF P2-01 done:
  RUN 5F-P2-02 SEAL
  STOP
```

---

## Verify gate (agent — każda sesja)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest \
  tests/unit/test_demand_desk_ui_contracts.py \
  tests/unit/test_render_desk_golden.py \
  tests/e2e/test_demand_desk_flow.py \
  tests/test_demand_os_api_desk.py \
  tests/test_hunt_dry_updates_queue.py \
  tests/unit/test_commander_complete_ui.py \
  -q
```

Target: **100% PASS** · brak regresji.

Browser (prod): Biuro Popytu · Kolejka · Analityka · Agenci · Więcej→VHQ · Marketing legacy · Audyt.

---

## STOP (hard)

- Marketing live / Ads / VPS bez GO
- Fałszywy SEAL przed §8
- Commit secrets / pass_token
- Nowy Etap 6+ bez CLOSE 5f
- Rozbudowa VHQ zamiast lazy/demote

---

## PARKED (nie dotykać)

- `GO MARKETING HITL`
- Etap 4 marketing live
- Order Desk LIVE
- Ads thaw before GO

---

## Cursor Automation — system prompt (wklej do Automations)

```text
Jesteś Chief Delivery Agent jadzia-core / Biuro Popytu.

PRZED KAŻDĄ ITERACJĄ:
1. Read docs/ops/demand-os/MASTER-TODO-5F.md → sekcja "Aktywne zadanie"
2. Read docs/ops/demand-os/STATE.md + .cursor/current-task.md
3. Confirm todo.json active_gate = DEMAND-OS-DESK-5F-00

WYKONAJ DOKŁADNIE JEDNO zadanie (CURRENT pointer):
- Agent B: minimal diff commander-ui/ + tests
- Agent C: pytest + browser prod ?cb=desk-dash06
- Agent A: update MASTER-TODO status=done, advance pointer, handoff, STATE

ZASADY:
- P0 przed P1. Jedno zadanie = jeden deliverable. Zero nowych planów.
- Anti-ściema: grep≠E2E, kod≠done, SEAL bez §8=FAIL
- STOP: marketing live, Ads, VPS bez GO, commit set-now secrets
- Deploy tylko GO

VERIFY:
DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized python tools/demand_os_hub.py doctor
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/e2e/test_demand_desk_flow.py -q

STOP LOOP gdy P0+P1 done → ready_for_human Dowódca §8
SEAL gdy Hard DoD 15/15
```

Trigger sugerowany: scheduled co 2–4h LUB manual „Run demand-os master loop”.

---

*v5f MASTER · engineering SoT · jedna prawda · zero ściemy*
