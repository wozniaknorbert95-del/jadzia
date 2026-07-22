# Commander UX/UI Audit — 2026-07-22

**Target:** https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash05  
**Task:** CMD-DASH-COMPLETE-01 (post-deploy dogfood)  
**Auditor:** live browser walkthrough (Cursor IDE browser)  
**Chrome DevTools MCP (9222):** offline — console/axe/Lighthouse not instrumented  
**Verdict:** **FAIL** (Critical = 0, High ≥ 1)

---

## Persona Lock

| Field | Value |
|-------|--------|
| Role | Dowódca (CEO) |
| Device | telefon + desktop hub |
| Time pressure | ≤90 s na decyzję |
| Goal | 1 akcja: potwierdź / odłóż / zamknij; MB execute = Telegram (brak UI) |
| Emotional state | zero tolerancji na sprzeczne statusy |

Każdy finding poniżej jest broniony z tej perspektywy: *„czy w 90 s wiem, czy system jest OK i co robić?”*.

---

## Verdict (executive)

**To nie jest finalny dashboard 100%.** Wiring Waves A–D jest LIVE i klika się end-to-end, ale **High** semantyka statusów + touch &lt; 44px dyskwalifikują Pass.

| Scorecard | Wynik |
|-----------|--------|
| DoD wiring A–D | ~92% (rail, KPI, Agenci truth, Audyt secondary) |
| Trust / decision UX | ~70% (sprzeczne sygnały) |
| Mobile dogfood | ~75% (nav działa, target 40px) |
| Agency polish | **nie** — FAIL |

---

## Hard gates

| Gate | Result | Notes |
|------|--------|--------|
| Console errors | **n/m** | DevTools 9222 offline |
| Console warnings | **n/m** | j.w. |
| Network 5xx | **0** (observed) | Sample Resource Timing: leads/orders/agents/breakers/accuracy/settings → **200** |
| Auth 403/404 | **0** (observed) | JWT session OK |
| Layout collapse | **0** desktop; mobile OK | 1280×900 + 390×844 |
| axe Critical/Serious | **n/m** | not run |
| LCP / CLS / INP | **n/m** | not run |
| Interaction Manifest | **complete** (below) | real clicks, gaps &gt; 0.5s |

Brak pomiaru axe/perf **nie** podnosi werdyktu do Pass. Przy High findings werdykt = **FAIL**.

---

## Interaction Manifest

| # | UTC≈ | Viewport | Action | Result | Evidence |
|---|------|----------|--------|--------|----------|
| 1 | 05:16 | 1280×900 | Open Commander + JWT sesja | Start loaded, ops chips | prior session + #6 |
| 2 | 05:16 | desktop | Click **Marketing** | Decision Rail LIVE | `page-…05-16-44….png` |
| 3 | 05:16 | desktop | Open Forensic + **Odśwież draft** | Shadow 8× HEU_ATTRIBUTION_LOW; draft W30 | snapshot |
| 4 | 05:17 | desktop | Click **Analityka** | KPI tiles + freshness RED orders/leads | `page-…05-17-23….png` |
| 5 | 05:17 | desktop | Click **Agenci** | LIVE cards + AI OS map (no fake phase-c) | `page-…05-17-58….png` |
| 6 | 05:18 | desktop | Click **Ustawienia** | form + Audyt entry | `page-…05-18-21….png` |
| 7 | 05:18 | desktop | **Otwórz Audyt** → **Weryfikuj łańcuch** | `PASS — łańcuch OK` | CDP text |
| 8 | 05:18 | **390×844** | Emulate phone + **Start** (bottom nav) | Menu mobilne; ops conflict visible | `page-…05-18-55….png` |

**Celowo nie kliknięte (prod safety):** Potwierdź na real hot_lead, execute MB, publish/cofnięcie FB na żywych postach.

---

## Findings

### H1 — Sprzeczny sygnał Ops (freshness red vs chips healthy)
**Severity:** High  
**Persona impact:** Dowódca widzi jednocześnie „wszystko OK” i „red” → traci zaufanie w ≤5 s.  
**Repro:** Start → `#home-ops-rail`  
**Observed:** `Worker freshness: red · up 654s` + chips `OPS healthy / SSH ok / SQLITE ok / LOOP alive / GA4 ok` (+ `SLA 5` red).  
**Evidence:** `page-2026-07-22T05-18-55-885Z.png`  
**Suspected:** `commander-ui/app.js` (home ops summary vs chip severity mapping)  
**Fix:** jedna hierarchia — summary = worst chip; albo „freshness” = osobny chip z tą samą barwą co wiersz.

### H2 — Preflight NO/BLOCKED przy MB_MODE=propose + accuracy 100%
**Severity:** High  
**Persona impact:** wygląda jak awaria cutoveru, choć runtime jest propose (HITL).  
**Repro:** Marketing → Decision Rail  
**Observed:** summary `MB propose · preflight BLOCKED · fail: mb_mode, breakers` + chip `PREFLIGHT NO` + `ACCURACY 100%` + `BREAKERS ALLOW`.  
**Evidence:** `page-2026-07-22T05-16-44-591Z.png`  
**Suspected:** copy/mapping preflight cutover vs runtime mode  
**Fix:** w trybie `propose` pokaż `PREFLIGHT N/A (propose)` / „cutover gate” osobno od „runtime health”; nie maluj NO jak incident.

### H3 — Touch target nav = 40px (&lt; 44px dogfood)
**Severity:** High (mobile primary persona)  
**Repro:** viewport 390×844 → `nav[aria-label=Menu mobilne] button`  
**Measured:** height **40px**, width ~74px  
**Fix:** min-height 44px (+ safe-area padding) w `commander-ui/styles.css`.

### M1 — KPI tile overflow: `insights_scope missing`
**Severity:** Medium  
**Repro:** Analityka → Organic tile  
**Observed:** surowy enum wylewa się z tile (czytelność + polish).  
**Evidence:** `page-2026-07-22T05-17-23-162Z.png`  
**Fix:** human label + truncate; raw code w `title`/forensic.

### M2 — Agenci: STATUS LIVE + Last/Next `—` + SLA breach
**Severity:** Medium  
**Persona:** „LIVE bez Last” = szum, nie decyzja.  
**Evidence:** Agenci screenshot  
**Fix:** LIVE wymaga last_run **lub** status `configured` / `unknown`; SLA breach tylko gdy next_expected istnieje.

### M3 — Analityka: DTL overall OK vs Orders/Leads freshness RED (dni)
**Severity:** Medium  
**Observed:** GA4 OK; Orders ~4d RED; Leads ~3.7d RED; DTL overall ok.  
**Fix:** DTL overall nie może być OK gdy critical freshness red — albo wyraźny split „pipeline OK / facts stale”.

### M4 — Marketing kolejka: gęstość smoke + zduplikowany FB strip
**Severity:** Medium  
**Observed:** wiele „Prod smoke entry” / test posts; FB health w rail + strip poniżej.  
**Fix:** filtry default `Nieudane`+`Zaplanowane`; smoke tag; jeden FB status.

### L1 — Shadow lista: 8× ten sam `HEU_ATTRIBUTION_LOW`
**Severity:** Low  
**Fix:** group-by action + count.

### L2 — Desktop top nav truncate `Analityk…`
**Severity:** Low  
**Fix:** skróty / overflow menu już istnieje na mobile — desktop ≥1280 też 5 etykiet pełnych lub ikony.

---

## Co działa (PASS slices)

- Marketing Decision Rail podpięty live (propose / breakers / accuracy / held / memory).
- Forensic L2 (shadow + brain-bus) otwiera się i czyta.
- Analityka KPI + freshness + DTL ładują się po JWT.
- Agenci: brak fake „phase-c LIVE”; mapa AI OS z hopami.
- Audyt secondary (D0.15): wejście z Ustawień; **Weryfikuj łańcuch → PASS**.
- Mobile bottom nav przełącza widoki.
- Brak execute UI MB (zgodnie z hard STOP).

---

## Czy to finalny dashboard?

**NIE.**

Blokery do „final 100%”:

1. H1 freshness vs healthy  
2. H2 preflight semantics w propose  
3. H3 touch ≥44px  
4. (zalecane) M1–M3 + phone dogfood re-walk + axe/console po Chrome `:9222`

---

## Next (1-1-1)

**CMD-DASH-UX-FIX-01** — tylko H1+H2+H3 (CSS + copy/mapping), potem re-audit Start+Marketing+mobile. Bez deployu bez osobnego GO.

---

## Appendix — API sample (200)

`api/v1/leads`, `api/v1/orders`, `api/v1/agents`, `commander/marketing/*`, `marketing/shadow/accuracy`, `v1/commander/settings` — durations ~50–390 ms, status 200 (Resource Timing, session walkthrough).
