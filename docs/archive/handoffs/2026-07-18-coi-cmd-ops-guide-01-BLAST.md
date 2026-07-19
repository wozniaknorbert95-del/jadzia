# BLAST — COI-CMD-OPS-GUIDE-01 (Commander ops handbook → VCMS study)

**Date:** 2026-07-18  
**Backlog:** `COI-CMD-OPS-GUIDE-01`  
**Class:** Feature (docs) — **no runtime Python**, no VPS jadzia deploy required  
**Primary repo:** `flex-vcms` (`docs/study/`)  
**SoT gate:** `jadzia-core/todo.json`  
**Evidence base:** UX-POLISH-01 LIVE tip `2ddc942` / SoT `ff67e27` + `UX-DOGFOOD-PHONE.md`

## B — Background

| Field | Value |
|-------|-------|
| Trigger | Dowódca: profesjonalna instrukcja obsługi systemu w VCMS study |
| Value | 5 scenariuszy CEO/ops — cold-open → akcja → hop; bez spekulacji |
| Why VCMS study | Operacyjny handbook ekosystemu (nie skill-map Vibe Coach) |
| Prior | UX-POLISH-01 LIVE; companion gate z BLAST polish |

**Data flow:** Agent czyta dogfood + CLOSE polish → pisze handbook PL (UI) w flex-vcms → linkuje `study-index` + `docs/index` NAUKA → CLOSE w jadzia-core.

## L — Limits (1-1-1 + PARK)

- **Jeden artefakt główny:** `flex-vcms/docs/study/coi-commander-ops-handbook.md`
- **Nie** regeneracja MBA W00–W52; **nie** fałszywy Dowódca PASS.
- **Nie** Gate D / Mollie / mint-recover / OS merge.
- **Nie** rewrite Vibe Coach skill-map — study-index zachowuje pointer do Vibe Coach + **nowa sekcja Ops System**.
- **Nie** deploy jadzia (docs VCMS; VCMS deploy tylko jeśli Dowódca GO osobno).
- Scenariusze **tylko** z dogfood evidence (POLISH + UX-03 + MOBILE-02 gdzie dotyczy).

## A — Actions (`/implement`)

### A1 Handbook (flex-vcms)

- [ ] Utwórz `docs/study/coi-commander-ops-handbook.md`:
  - Cel / URL prod / auth (TG `/commander` + JWT fallback; bez mint secrets)
  - IA 5 (Start…Ustawienia) + Audyt secondary
  - **5 scenariuszy** (krok → oczekiwany wynik → FAIL→co robić):
    1. Cold-open dnia (Start → 3 priorytety → jedna akcja)
    2. Lead hot (Potwierdź / Odłóż / Zamknij + toast)
    3. Nawigacja Start → Marketing (bez redesign Marketing)
    4. Delegat / Settings (eskalacja; SMTP już LIVE)
    5. Emergency no-laptop (PWA/JWT path; bez mint w docs)
  - Mapa hops (OS/VCMS Basic Auth OK; sesja JWT zostaje)
  - STOP list (Gate D, Mollie, sekrety)
  - Linki do jadzia handoffów / dogfood

### A2 VCMS index wiring

- [ ] `docs/study/study-index.md`: sekcja **Ops System** → handbook (+ zachowany Vibe Coach pointer)
- [ ] `docs/index.md` NAUKA: link „COI Commander — instrukcja obsługi”

### A3 SoT jadzia-core

- [ ] `todo.json`: `COI-CMD-OPS-GUIDE-01` → `in_progress` → `completed` po DoD
- [ ] CLOSE: `docs/handoffs/2026-07-18-coi-cmd-ops-guide-01-CLOSE.md`
- [ ] `AGENTS.md` / session-state

## S — Success criteria (DoD)

- [ ] Handbook istnieje i pokrywa 5 scenariuszy z evidence
- [ ] Linki z study-index + docs/index działają (ścieżki względne VCMS)
- [ ] Zero sekretów / mint / Gate D content
- [ ] Gate `completed` + CLOSE

## T — Test plan

| Layer | What |
|-------|------|
| Review | Każdy scenariusz ma URL lub tip evidence |
| Smoke | Otwórz markdown lokalnie — brak broken relative links do plików w tym repo; cross-repo = absolute path note |
| Human | Optional: Dowódca walkthrough 1× cold-open |

## STOP

- Multi-repo runtime changes  
- VCMS deploy bez GO  
- „Uzupełnij wszystko o systemie” poza 5 scenariuszami  

## Estimate

≤1 sesja `/implement` + `/handoff`.

---

```text
BLAST_ANCHOR: docs/handoffs/2026-07-18-coi-cmd-ops-guide-01-BLAST.md
BACKLOG_ID: COI-CMD-OPS-GUIDE-01
INVARIANTS_TO_PROTECT: Vibe Coach skill-map split; parks; MBA weeks; no jadzia runtime
SUCCESS_CRITERIA: handbook + study/index links + CLOSE
IMPLEMENTATION_PLAN: handbook → study-index Ops → docs/index NAUKA → CLOSE
```
