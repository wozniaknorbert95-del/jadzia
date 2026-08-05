# SELF-AUDIT — PUNCH LISTA C (2026-08-05, drugi przebieg)

**Zlecenie Dowódcy:** dogłębna weryfikacja co zostało "na później" + gdzie poszedłem na skróty — uczciwie, z planem naprawczym, wykonana autonomicznie.
**Metoda:** każdy DoD z planu 10 kroków zweryfikowany ponownie dowodem (komenda/log/plik), nie deklaracją z pamięci.

## A. Odroczone ŚWIADOMIE (decyzja udokumentowana — nie gapy)

| Item | Gdzie | Uzasadnienie |
|------|-------|--------------|
| S10 desk chip STALE_DAYS=7 vs per-rola limity | MT-9 zadanie 9-02 | wymaga wspólnego źródła prawdy (wave_check ↔ heartbeat_view) |
| S12 per-action heartbeats | by design | dopiero gdy cadence się rozjedzie |
| S13 GDrive | by design | czeka na GO + creds (jak GA4) |
| MT-9 zadania 1–10 | [`MASTER-TODO-9.md`](../ops/demand-os/MASTER-TODO-9.md) | 9-01 termin 2026-08-12 (tydzień pracy workera) |
| Live P0 unlock | PARKED | decyzja człowieka, nie narzędzia |

## B. GAPY I SKRÓTY ZNALEZIONE (uczciwie) + plan naprawczy

| # | Gap / skrót | Dowód znaleziska | Plan naprawczy | Status |
|---|-------------|------------------|----------------|--------|
| G1 | **Doctor staleness tylko advisory** — na prod (worker LIVE) brak hard gate; S1 zamknięte "połowicznie" | `doctor.py` `_ADVISORY = {"agents_staleness"}` hardcoded | env-aware severity: `DEMAND_OS_STALENESS_BLOCKING=1` w prod `.env` → check blokuje doctor.ok; default advisory (dev bez workera) · test 3-fazowy | **FIXED** (kod+test green; env+restart w deploy tej sesji) |
| G2 | **VPS za originem** — `0daca4a` (MT-9, S-register, close handoff) wypchnięty, nie zdeployowany | VPS HEAD `a84ddcd` vs origin `0daca4a` | ff-only deploy `sudo -u jadzia` + owner-verify + tip pointer | **FIXED w ship tej sesji** |
| G3 | **Lokalny stash pominięty w C4** — triage objęło 9 stashy VPS; lokalny `stash@{0}` (Revenue War Room era: brief_node revenue classification, db.py +190) nigdy nie zreviewowany | `git stash list` lokalnie ≠ pusta | review: kod **już w HEAD** (zweryfikowane grep: `KPI-eligible`, `unknown_count`, `revenue_classification_events` ×11; wersja HEAD nowsza — metrics dict); docs-zmiany z 2026-07-17 stale/superseded → **drop** | **FIXED** (`git stash list` pusta obie strony) |
| G4 | **docs/handoffs = 103 pliki vs zasada rolling ≤15** (własny README łamany) | `(Get-ChildItem docs/handoffs).Count = 103` | archiwum 87 najstarszych → `docs/archive/handoffs/` (konwencja istnieje, 301→388) · naprawa 4 linków (STATE.md UX-CLOSE, COM-AI-50 blast, +2 broken-ref: INC-SSH, VHQ-DI research → archive path) | **FIXED** (live: 15 handoffów + README) |
| G5 | **Kanoniczna komenda owner-verify zepsuta** — `python tools/demand_os_owner_verify.py` z OWNER-VERIFY-COMMANDS.md pada: `ModuleNotFoundError: agent` (brak sys.path bootstrap; hub ma, owner_verify nie) + na Windows crash na `print` (cp1252 vs `≠`) | traceback na VPS i lokalnie | bootstrap sys.path + dotenv (paritet z hub) + `sys.stdout.reconfigure(utf-8)` · test regresji runpy bez PYTHONPATH | **FIXED** — canonical run: **ok:true, 7/7** |
| G6 | **Screenshot E2E słabej jakości** — sekcja Agenci na krawędzi kadru, chipy nieczytelne; "dowód" niesprawdzalny wizualnie | review PNG v1 | retake: scroll-into-view, 9 kart × chip `dziś · bieg: 2026-08-05`, dash13 w stopce → `desk-agents-live-prod-v2.png` | **FIXED** |
| G7 | OWNER-VERIFY-COMMANDS bez uwagi o venv python na VPS (`python` nie istnieje na prod) | `bash: python: command not found` | +1 linia w doc + wiersz doctor opisuje advisory/blocking | **FIXED** |
| G8 | **Różnica liczników suite nieudokumentowana** — local 716 vs VPS 712 | VPS `-rs`: 21 skips (zzpackage brain assets, flexgrafik-inspire engine, vehicle template — assety zewnętrzne, nie logika Demand OS) | dokumentacja tutaj; bez akcji kodowej | **CLOSED (doc)** |

## C. Uczciwe noty procesowe (nie defekty, ale do jawności)

- Triage 3 mega-stashy line-ending (346/141/122/89 plików): `show --stat` + spot-diff, nie exhaustive per-file. Ryzyko przyjęte świadomie (normalizacja CRLF; treść kodu w HEAD).
- Kontrolowany dispatch sales na prod użył backdated heartbeat (−7h) jako prowokacji `due`; stan po teście nadpisany realnymi dispatchami — heartbeats dziś wszystkie z 2026-08-05 (zweryfikowane).
- E2E używało minted JWT + localStorage injection — testuje autentykowany render + API, **nie** realny login flow Telegram (ten zostaje manualny).
- LEDGER na prod: tylko sanitized rows, `publish=N` — zero fake `publish=Y` (zweryfikowane tail).

## D. Weryfikacja ponowiona (dowody tej sesji)

- VPS: HEAD/status/stash/root-owned=0 · service+timer active · journal cykle 10:23/10:38 `dispatched:0, errors:0` (due=[] poprawnie — cadence nieosiągnięte) · wave-check `heartbeat_staleness ok` z realnych biegów · **owner-verify ok:true 7/7** · **unit 712 passed / 21 skipped / 0 fail · tree po suite CZYSTE** · `git log --all -- secrets/ output/` = 0 · check-ignore aktywne.
- Lokalnie: 3 nowe testy green (G1×1, G5×2) · canonical owner-verify **ok:true** · suite pełny w ship (poniżej).

## E. Wykonanie (commity)

- A: code+tests+docs+archive → `9d0cff0`
- B: SoT sync + ten register → ten commit (tip)
- Deploy VPS + `DEMAND_OS_STALENESS_BLOCKING=1` w `/opt/jadzia/.env` + restart `jadzia` + owner-verify blocking green → dowody w sekcji F po ship.

## F. Ship verify (po deploy)

- TBD
