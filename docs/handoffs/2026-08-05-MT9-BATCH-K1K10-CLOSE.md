---
status: DONE
date: 2026-08-05
pack: AGENTS-9
scope: MT-9 batch K1-K10 — wykonanie 10 kroków + weryfikacja końcowa + repo/VPS hygiene
prod_tip: f545dc4
---

# MT-9 BATCH K1–K10 CLOSE + FINAL VERIFICATION + HYGIENE

**CO:** Wykonanie pakietu 10 kroków MT-9 (9-01→9-10 wg kolumny Kolejność), senior-verification całości,
domknięcie skrótów, sync lokalny≡VPS, profesjonalne sprzątanie śmieci.
**DLACZEGO:** Dowódca: „wykonaj kompleksowo jak najwyższej klasy engineer + zadbaj o deploy i porządek w git",
następnie: „weryfikacja + ostatnie poprawki + to samo na serwerze co u nas + śmieci usunąć bez skrótów".

## Wynik batcha (10/10)

| Krok | MT-9 | Wynik | Dowód |
|------|------|-------|-------|
| K1 | 9-02 | DONE | Wspólna polityka staleness `heartbeat.STALE_LIMITS_H` + `stale_limit_hours()`; desk rows `stale_limit_h`; 3 testy |
| K2 | 9-04 | DONE | `diagnostics.agents_due` (read-only, try/except — nigdy nie psuje statusu); 3 testy |
| K3 | 9-03 | DONE | `tools/demand_os_worker_journal_export.py` + 3 testy; **pierwszy eksport na prod:** `docs/handoffs/evidence/worker/worker-journal-2026-08-05.md` (jadzia dopisany do grupy `systemd-journal`) |
| K4 | 9-05 | DONE | Coverage gate per-module floor; `worker.py` 90% → **100%**; evidence refresh |
| K5 | 9-06 | DONE | **OPT-B zaimplementowany** (nie tylko decyzja) — patrz sekcja canary |
| K6 | 9-07 | DONE | `SHELL-FALSE-EXIT-CRITERIA.md` (DECISION-READY; flip order blog→cf→tt→fb) |
| K7 | 9-08 | DONE | `MT9-08-SWEEP-2-FINDINGS.md` — 7 PASS / 0 FAIL / 8 N/A-prod, zero nowych znalezisk |
| K8 | 9-01 | INTERIM | 37 ticków, 0 failures, wszystkie role fresh; finał 2026-08-12 |
| K9 | 9-10 | DONE | tip convention + ownership rules w playbooku; S10 → FIXED |
| K10 | final | DONE | suity obie strony + owner-verify + deploy ff + SoT sync + hygiene (ten dokument) |

## Canary 9-06 (alert path) — PASS, okno 16:19–16:21 UTC

1. `systemctl start demand-os-agents-worker-alert.service` (dokładnie to, co zrobi `OnFailure=`) → linia w `/opt/jadzia/data/demand-os/set-now/ALERTS.jsonl`.
2. Doctor (blocking, prod env): `ok=False`, `worker_failures: 1 failure(s) <24h, last=16:21:16 [blocking]`.
3. Desk (`build_demand_os_status(with_full_doctor=True)` in-process, ta sama funkcja co route): `footer.doctor_ok=False`.
4. Restore (`rm ALERTS.jsonl`): doctor `ok=True`, desk `doctor_ok=True`. Serwis cały czas `active`, health 200.

## Weryfikacja końcowa — złapane skróty i poprawki (uczciwie)

| # | Skrót/ominięcie | Fix |
|---|------------------|-----|
| V1 | **Desk chip UI miał własną skalę 2d/7d** ignorując backend `stale` — S10 domknięte w backendzie, ale kłamie w UI (sales 24h → „dziś" zamiast stale) | `commander-ui/app.js`: chip z `a.stale` (backend = jedyna prawda), tooltip `Limit: Nh`; 87 testów UI/alerts green |
| V2 | **Subagent side-effect:** `MEMORY.json` zmutowany (sync dedupe 15:51 UTC) poza zakresem tasków doc | Zweryfikowano diff: usunięcie literalnego duplikatu wpisu = prawda → **świadomie zostawiony** i zacommitowany; heartbeat/ledger nietknięte (sprawdzone) |
| V3 | **systemd unescapuje `\n`** w ExecStart → alert unit padał z SyntaxError | `chr(10)` zamiast `'\n'` w one-linerze; commit fix |
| V4 | **Resolver alertów:** brak `DEMAND_OS_ALERTS_LOG` na prod → doctor czytał repo set-now, unit pisał do data/ | Dopisany env do `/opt/jadzia/.env` (jak `DEMAND_OS_AGENTS_HEARTBEAT`) + restart jadzia + re-canary PASS |
| V5 | **Journal export jako jadzia:** brak uprawnień do system journal | `usermod -aG systemd-journal jadzia` (standard dla kont serwisowych) |
| V6 | Operator pack w sweep doc używał `.venv/bin/python` (nie istnieje — realne to `venv/`) | Poprawione 8 wystąpień + `env HOME=/home/jadzia` |
| V7 | `test_sot_tip_pointer` RED na VPS po ff (STATE wskazywał stary tip) | Oczekiwane — domknięte tym SoT syncem (prod_tip → f545dc4) |

## Hygiene — plan śmieci i wykonanie (z inwentarzem)

**Repo (tracked junk — `git rm`, commit f545dc4):** `archive/` (8 plików: Windows-era skrypty, stare tarball deploye, ngrok.exe 32M), `ngrok.zip` (12M), `jadzia-nginx.conf` + `nginx_jadzia.conf` (martwe kopie — live config to `/etc/nginx/sites-available/jadzia`, symlink z sites-enabled; zweryfikowane brak referencji).

**VPS `/opt/jadzia` (untracked junk, usunięte jako jadzia):** `venv.py312.bak.20260721-193005` (**305M**, stary backup venv — aktywny `venv/` działa), `scratch/` (pusty), `temp_export/` (styczeń extracts), 4× `deploy_*.tar.gz` (marzec, duplikaty z archive), `test-results*.log`, `__pycache__`, `.coverage`. Rozmiar: **6.5G → 6.2G**.

**VPS `/tmp`:** artefakty canary 9-09/9-06 (`canary-*`, `hb-backup-canary.json`, `ovparse.py`, skrypty pomocnicze) + **~200 plików `tmp*.db*` (SQLite temp z historycznych pytest runs)** — wyczyszczone, zero aktywnych referencji.

**Świadomie ZOSTAWIONE (nie śmieci):** `output/` + `logs/` (runtime), `secrets/` (live), `.env.backup` (lutowy safety net — decyzja Dowódcy czy usunąć), lokalne `.superpowers/sdd/*`, `assets/tt-upload/*.mp4`, `BLOG-DRAFTS/blog_w31_*` (artefakty workstreamu demand-os, poza 1-1-1 tej sesji).

**Git sync:** lokalny == origin == VPS @ tip poniżej · `git status --porcelain` puste po obu stronach · `find /opt/jadzia/.git ! -user jadzia` == 0.

## Weryfikacja końcowa (fakty)

- Lokalny pełny suite: **1075 passed, 18 skipped, 1 xfailed, 0 failed** (97s).
- VPS unit suite: **731 passed, 21 skipped** (Δ = env-skips, zgodne z A4).
- VPS owner-verify: **`ok:true`, `errors:[]`**, exit 0 (blocking mode, worker_failures check objęty).
- Canary 9-06: RED → GREEN udowodnione (wyżej). Canary 9-09: PASS wcześniej dziś.
- Worker: 37+ ticków, 0 failures; alert path LIVE (`OnFailure=` aktywny po daemon-reload).
- `test_sot_tip_pointer`: green po tym syncu (po obu stronach).

## Stan

- **prod_tip:** `f545dc4` (repo hygiene + journal evidence) · cache `desk-dash13` · worker timer LIVE 15 min · doctor staleness + worker_failures **blocking** na prod.
- **MT-9:** 9/10 DONE; otwarte tylko **9-01 finał 2026-08-12** (tygodniowa weryfikacja workera — narzędzie gotowe: journal export + sweep pack).
- **Live P0:** PARKED (bez zmian — TOOL FIRST).

## NASTĘPNY KROK (rekomendacja inżyniera)

1. **9-01 finał (2026-08-12):** journal export --since -7d + tabela cadence per rola + sweep pack z MT9-08 (komendy gotowe).
2. **Shell-flip `blog`** wg `SHELL-FALSE-EXIT-CRITERIA.md` §3.1 (najtańszy uczciwy flip; osobny commit + dowód prod ≥7 dni + sign-off).
3. Residual: decyzja Dowódcy re `.env.backup` na VPS.
