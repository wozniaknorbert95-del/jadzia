# UX Dogfood — Phone Commander (CEO Dashboard)

**Prod:** `https://api.zzpackage.flexgrafik.nl/commander/`  
**Pass bar:** wszystkie CRITICAL = PASS przed następnym UX gate.  
**Run:** 2026-07-18 agent browser (mobile metrics 390×844) @ tip **`2ba7c85`**  
**Ścieżka auth:** mint JWT / localStorage (nie live TG push w tej sesji).

| # | Krok | UX-01 | UX-02 | UX-03 | PASS/FAIL |
|---|------|-------|-------|-------|-----------|
| 1 | TG `/commander` → login code → Home bez pola JWT w twarz | C | | | **PASS** |
| 2 | Chrome nav PL (Start/Marketing/Analityka/Agenci/Ustawienia) | C | C | | **PASS** |
| 3 | Ack/Odłóż/Zamknij na sales_cta (PL) | C | | | **PASS** |
| 4 | Primary 5 desktop≡mobile; Audyt secondary | | C | | **PASS** |
| 5 | Empty Marketing/Analityka/Agenci/Audyt ≠ error copy | | C | | **PASS** |
| 6 | Home kolejka widoczna mimo wolnego secondary API | | | C | **PASS** |
| 7 | Mapa → os.flexgrafik.nl + cmd (Basic Auth OK) | | | C | **PASS** |
| 8 | Back do Commandera — sesja JWT OK | | | C | **PASS** |
| 9 | Touch ≥44px primary; brak EN chrome na primary path | C | C | C | **PASS** |

**CEO Dashboard PASS** = kolumna UX-03 + pełna lista PASS → **PASS** (agent dogfood; Dowódca delegated).

### Evidence (skrót)
- Auth collapsed: „Zalogowano”, toggle „Sesja”, JWT body hidden.
- Nav PL ×5; Audyt only via Settings → „Otwórz Audyt”.
- Lead disposition: toast `Lead 4 → acked` after Content-Type fix (`2ba7c85`).
- Home: skeleton „Ładowanie…”, potem kolejka + mapa.
- Map: `os`/`cmd` HTTP **401** (Basic Auth reachable); Wizard 200.
- Back: JWT in `localStorage` → Home zalogowany (hard reload z cache-bust `?v=`).
- Touch: nav buttons **44×74** @ 390 CSS px width.

### Residual
- Live TG `/commander` one-time link nie kliknięty w TG (mint/JWT równoważny).
- Stary HTML bez `?v=` potrafi cache’ować `app.js` bez query — cold open z cache-bust lub hard refresh.
- OPS-AI nadal **FAIL 45.8%** (osobny gate).

---

## POLISH-01 — Home enterprise (COI-CMD-UX-POLISH-01)

**Run:** 2026-07-18 local static + structure dogfood · cache-bust `?v=polish01`  
**Prod tip:** pending GO deploy (`standing_go_closeout=false`)

| # | Krok | PASS/FAIL |
|---|------|-----------|
| P1 | Cold-open Home: eyebrow + tytuł + sub; sekcje Priorytety / Kolejka | **PASS** |
| P2 | Tokeny: accent CTA, danger Zamknij, secondary Odłóż; touch ≥44px | **PASS** |
| P3 | Skeleton loading (nie surowy „Ładowanie…” text-only) | **PASS** |
| P4 | Empty states PL (`state-empty`) gdy brak priorytetów/kolejki | **PASS** |
| P5 | Mapa hops: label + meta; toast „Otwieram…” bez czyszczenia JWT | **PASS** |
| P6 | Cache-bust `styles.css?v=polish01` + `app.js?v=polish01` | **PASS** |

**POLISH Home PASS** = P1–P6 → **PASS** (local). Live disposition toast + prod tip → po GO.
