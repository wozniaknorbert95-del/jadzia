# Handoff — Weryfikacja maratonu MASTER-TODO 6/7/8 + rejestr skrótów (2026-08-03)

**Typ:** audyt końcowy sesji · **Zakres:** całość prac 2026-08-03 (3 iteracje, ~40 commitów od `5298667`).
**Metoda:** nic na słowo — każdy wiersz zweryfikowany komendą w tej sesji.

## A. Weryfikacja — co jest PRAWDA (zweryfikowane)

| # | Asercja | Dowód (świeży, ta sesja) | Status |
|---|---------|--------------------------|--------|
| A1 | Local unit suite | `714 passed, 0 failed, 17 skipped` | ✅ |
| A2 | Local root suite | `336 passed, 1 skipped, 1 xfailed` | ✅ |
| A3 | VPS unit suite (re-run) | `709 passed, 0 failed, 22 skipped` @ `0930ea6` | ✅ |
| A4 | Δ local↔VPS = 5 | env-skips by design (inspire sibling, GA4 creds) — spójne | ✅ |
| A5 | VPS owner-verify | `ok:true`, errors [] (doctor, pointer, pytest 114/0, footer, go_day, waves 1–4 tool_ready) | ✅ |
| A6 | VPS service | `systemctl is-active jadzia` = active, `/health` 200 | ✅ |
| A7 | Prod UI = dash13 | `curl /commander/index.html` → `desk-dash13`, `sw.js` → `coi-commander-desk-dash13` | ✅ |
| A8 | Wave-check prod | `heartbeat_staleness` ok (fresh) · `state_writers_resolvable` 9/9 | ✅ |
| A9 | run-due prod dry | ok, due=[] (heartbeats świeże) | ✅ |
| A10 | RBAC run-due | `DEMAND_OS_ROLE=viewer` → `missing demand_os:act` (CLI dogfood) | ✅ |
| A11 | Git local | master == origin/master @ `a81410b`(+handoff commit) | ✅ |
| A12 | Git VPS | HEAD = `0930ea6` == prod_tip w STATE | ✅ |
| A13 | Zero TODO/FIXME/HACK | w plikach 8-ki (worker, wave_check, gdrive, state_paths, hub) | ✅ |
| A14 | Brak `secrets/` w historii repo | `git log --all -- secrets/` puste | ✅ |
| A15 | Live marketing | PARKED — zero publish, zero ads; jedyny "publish path" = test→delete w przeszłości | ✅ |

## B. Rejestr skrótów i pominięć (szczerze, z severity)

| ID | Skrót / pominięcie | Severity | Werdykt |
|----|--------------------|----------|---------|
| S1 | 8-05 plan mówił "doctor check" → zrobione w `wave_check`. `doctor.py` nie ma staleness (owner-verify pokrywa przez wave-check, ale doctor sam w sobie nie) | niska | udokumentowane odchylenie; opcjonalny alias jutro |
| S2 | 8-07 plan mówił o skrypcie `tools/demand_os_coverage_check.py` + update `OWNER-VERIFY-COMMANDS.md` → zrobione jako pytest gate; **OWNER-VERIFY-COMMANDS.md nie zaktualizowany** | średnia | dokumentacja niespójna z realizacją — dopisać jutro |
| S3 | Worker: `run-due --apply` nigdy na prod (tylko dry); **timer nie zainstalowany na VPS** (units tylko w repo) → `shell:true` słusznie, ale "worker loop żyje" tylko manualnie | by design | **czeka na GO Dowódcy** — to jest główny punkt jutra |
| S4 | **VPS: 9 stashy** (drift aug3 ×2, line-ending, agent-temp, fb-scripts, queue-clean, pre-deploy ×3) — nigdy nie rozliczone | średnia | review każdego: drop lub apply; ryzyko zapomnianych zmian |
| S5 | **VPS untracked: `secrets/` (wordpress_key, ssh_known_hosts) NIE w .gitignore** — jedno `git add -A` na VPS od leaku. Plus `output/` (design-agent runtime) i katalog `" "` (spacja) z kopią MEMORY.json po typo | **wysoka** | gitignore na VPS-side + usunąć `" "`; prewencja przed jakimkolwiek add -A |
| S6 | Lokalne untracked: `.superpowers/sdd/` 19 plików, `assets/tt-upload/*.mp4`, **`docs/ops/demand-os/set-now/GROWTH-EVENTS.jsonl` (dogfood artifact, NOT ignored)** — jedno add -A od commita runtime pliku | średnia | usunąć artifact; rozważyć gitignore pattern dla set-now runtime (AGENTS-HEARTBEAT już jest) |
| S7 | **Owner-verify/testy na prod regenerują tracked evidence** (`k12-coverage*.json/txt`) → dirty tree po KAŻDYM verify → kolejne stash/merge problemy w przyszłości | średnia | evidence write tylko pod flagą (CI/local), na prod skip — fix w teście gate |
| S8 | **Deploy playbook (`.agents/workflows/jadzia-deploy.md`) bez noty `sudo -u jadzia git` / chown** — ten sam incydent 2× (D8-05 + deploy 8-10: 114 plików root-owned) | średnia | 5-min fix, pierwszy punkt jutra |
| S9 | RBAC run-due: enforcement działa (A10), ale **brak dedykowanego testu** viewer-blocked dla `agents-run-due` (jest tylko generyczny dla sync-db) | niska | 1 test jutro |
| S10 | Dwie skale staleness: desk chip (2d/7d) ≠ wave-check (2×cadence) — udokumentowane w handoffie, **nie w kodzie/UI** | niska | komentarz w kodzie + ewentualnie jedna skala |
| S11 | VPS 1 commit za originem (`a81410b` docs-only nie wdrożony) — prod_tip spójny, parity dojedzie przy następnym ff | kosmetyczna | domknięte przy deploy tego handoffa |
| S12 | Heartbeat per-rola, nie per-akcja (money_check+sync_starts współdzielą zegar) — świadome uproszczenie | niska | udokumentowane; per-action tylko jeśli cadence się rozjedzie |
| S13 | GDrive live nigdy z realnymi creds (fail-closed only) | by design | czeka na GO + creds (jak GA4) |
| S14 | Desk tile po dash13: brak E2E w przeglądarce na prod (tylko unit/golden/curl tag) | niska-średnia | jutro: browser check sekcji Agenci na prod |
| S15 | `.gitignore` ma `data/`, ale 21 plików `data/demand-os/set-now-sanitized/` tracked (przed ignore) — celowe (proof pack), ale koncepcyjna kolizja z runtime fallback `data/demand-os/` | niska | udokumentować w state_paths docstring |

## C. Punch lista na jutro (kolejność = priorytet)

1. **[GO Dowódcy]** Aktywacja workera: `sudo cp deployment/demand-os-agents-worker.{service,timer} /etc/systemd/system/ && systemctl enable --now …timer` → potem `shell:false` w registry + pierwszy realny przebieg (verify staleness green po 15 min). (S3)
2. **[bezpieczeństwo]** VPS: `.gitignore` += `secrets/`, `output/`; usunąć katalog `" "`; zweryfikować `git status` czyste po. (S5)
3. **[playbook]** `jadzia-deploy.md`: reguła "każdy git checkout/merge/stash na VPS = `sudo -u jadzia`", po merge `find ! -user jadzia` musi dać 0. (S8)
4. **[stashe]** Review 9 stashy na VPS → drop/apply każdy, zero na wyjściu. (S4)
5. **[evidence drift]** Test gate: evidence write tylko gdy `JADZIA_EVIDENCE_WRITE=1` (lokalnie/CI), na prod skip → koniec dirty tree po owner-verify. (S7)
6. **[higiena lokalna]** usunąć `set-now/GROWTH-EVENTS.jsonl` artifact; decyzja: gitignore pattern dla set-now runtime; `.superpowers/` i `assets/` → gitignore lub commit-decyzja. (S6)
7. **[docs]** OWNER-VERIFY-COMMANDS.md += coverage gate agents; doctor alias staleness (S1/S2); test RBAC run-due (S9); browser E2E desk Agenci (S14).
8. **[następnie]** MASTER-TODO-9: weryfikacja 8-ki po pierwszym tygodniu workera + decyzje z dnia.

## D. Stan końcowy sesji

- Local/origin: `a81410b` + ten handoff (commit poniżej) · VPS: ff-only do tego samego tipu (deploy docs-only, jako `jadzia` — lekcja S8 zastosowana od razu).
- prod_tip w STATE: sync z VPS HEAD po ff (commit 2-stopniowy jak w 8-10).
- Live P0: **PARKED** — bez zmian. Ads: PARK cash.
- Testy końcowe: A1–A3 świeże z tej sesji (nie z pamięci).

## E. Start prompt na jutro

```text
Kontynuacja jadzia-core. Wczytaj w tej kolejności:
1. .cursor/current-task.md
2. docs/ops/demand-os/STATE.md
3. docs/handoffs/2026-08-03-MARATON-678-VERIFICATION-AUDIT.md (ten plik) — sekcje B i C to plan dnia.

Zadanie: wykonaj punch listę C w kolejności 1→8. Punkt 1 wymaga mojego GO
(aktywacja timera workera) — zapytaj mnie na starcie: GO albo skip do punktu 2.
Reguły bez zmian: tool-first, live P0 PARKED, deploy tylko z GO, VPS git zawsze
sudo -u jadzia (S8). Każdy punkt domykaj testem lub dowodem, nie deklaracją.
```
