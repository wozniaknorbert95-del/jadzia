---
status: DECISION-READY
updated: "2026-08-05"
task: MASTER-TODO-9 / 9-07
scope: "definicja kryteriów exit shell:false dla tt/cf/fb/blog — DOKUMENT DECYZJI, nie implementacja"
tool_first: marketing live P0 PARKED — żadne kryterium nie dotyczy live publish
---

# SHELL-FALSE EXIT — kryteria uczciwego flipa tt / cf / fb / blog

**Pytanie:** co musi istnieć technicznie, żeby `shell: false` dla ról `tt`, `cf`, `fb`, `blog`
było uczciwe — tak jak dziś jest uczciwe dla ról CADENCE (`growth_lead`, `icp_brain`,
`sales`, `validator`, `cre`)?

**Odpowiedź w jednym zdaniu:** rola przestaje być shell dopiero wtedy, gdy worker
(15-min timer na prod) wykonuje dla niej **mutującą akcję tool-side** (draft/queue,
nigdy publish) z dowodem w heartbeat + artefaktach, bramką jakości Validatora,
kontraktem pytest i zachowanym twardym zakazem live publish.

Istniejący zapis w `OS-TARGET-V5-AGENTS-COVERAGE.md` („Worker loop per rola → dopiero
wtedy `shell: false`", linia 57) ten dokument zamienia na sprawdzalną macierz.

---

## 1. Mechanika flagi `shell` — jak flip działa dziś

Flaga nie jest deklarowana per rola — jest **wyliczana** z listy ról worker-driven:

- `agent/demand_os/agents/registry.py:117` — `_WORKER_CADENCE_ROLES = frozenset({"growth_lead", "icp_brain", "sales", "validator", "cre"})`
- `agent/demand_os/agents/registry.py:145` — `"shell": role not in _WORKER_CADENCE_ROLES`
- Komentarz `registry.py:141-144`: shell=False oznacza „dispatcher live and proven on prod" — czyli **dowód prod jest częścią definicji**, nie opcją.

Konsekwencja: flip = dopisanie roli do `_WORKER_CADENCE_ROLES`, a to jest uczciwe tylko
gdy rola faktycznie jest w `worker.CADENCE` i worker ją dispatchuje. Desk/cockpit tile
czy ręczny `hub agents --role X` **nie flippują** markera — i nie powinny.

### Tarcia do rozwiązania przed jakimkolwiek flipem (fakt architektoniczny)

Worker dziś **kontraktowo wyklucza** role `live_gated`:

- `agent/demand_os/agents/worker.py:40-41` — `if spec.get("live_gated"): continue`
- `agent/demand_os/agents/worker.py:1-6` — docstring: „live_gated roles are never dispatched here, even after marketing unlock (live cadence = HITL)"
- `tests/unit/test_agents_worker.py:50-57` — test `test_cadence_map_covers_only_registry_actions` asertuje `not spec["live_gated"]` dla każdej roli CADENCE.

Wszystkie 4 role mają `live_gated: True` (registry.py:45, 72, 81, 90). Jednocześnie
**żadna akcja w registry nie wykonuje live publish** — `live_gated` oznacza dziś
„zaparkowana zdolność live", nie „akcja która publikuje". Exit wymaga więc jawnego
rozstrzygnięcia modelu gate'u (patrz §3, kryterium S1): CADENCE jako whitelist
akcji tool-side, `live_gated` zostaje markerem publish — oba sprzężone testem.

---

## 2. Co znaczy shell:true dziś — stan uczciwy per rola

### `tt` — TikTok (measure only)
Registry (`registry.py:39-47`): akcje `["queue"]`, `mutating_actions: []`, runner wave1.
Implementacja (`agent/demand_os/agents/wave1.py:91-106`) jedynie **czyta** `hitl_queue`
z commander status i filtruje `channel == "tiktok"`, zwracając `live_publish: False`.
Rola nie produkuje żadnego artefaktu: nie ma draftu TT, nie zapisuje kolejki, nie ma
akcji mutującej, nie ma wpisu w CADENCE. To jest świadomie uczciwy shell — „measure
only" w labelu jest literalne.

### `cf` — Content Factory
Registry (`registry.py:66-74`): akcje `["status", "brief", "assets", "proof"]`,
`mutating_actions: []`, runner wave2. Implementacja (`agent/demand_os/agents/wave2.py:33-70`):
`build_brief` liczy brief w pamięci i zwraca dict (`content_factory.py:40` — bez zapisu),
`assets` listuje lokalny CSV + stub GDrive, `proof` to check etykiety tier≥1. Wszystko
read-only/compute-only: brief znika po odpowiedzi, nie trafia do kalendara ani do
żadnego store. CF jest producentem inputu dla tt/fb/blog — ale dziś produkuje go
tylko „na żądanie, w próżnię".

### `fb` — Facebook Engage
Registry (`registry.py:75-83`): akcje `["allowlist"]`, `mutating_actions: []`, runner
wave2. Implementacja (`agent/demand_os/agents/wave2.py:73-99`) czyta allowlist targetów
i raportuje `engageable_count` z `live_comment: False`. Nie ma żadnego draftu
komentarza; jedyny ślad engage to mock `engage-dry` (nota w coverage §E) i writer
`engage_log` istniejący infrastrukturalnie (`wave_check.py:128`), ale nieużywany przez
rolę. FB jest najbardziej „pustym" shellem z czwórki.

### `blog` — Blog ICP
Registry (`registry.py:84-92`): akcje `["status", "pipeline"]`,
`mutating_actions: ["pipeline"]` — **jedyna rola z czwórki z deklarowaną akcją mutującą**.
Implementacja (`agent/demand_os/agents/wave3.py:28-49` → `blog_pipeline.py:333-363`)
realnie: generuje draft ICP → waliduje go przez Sniper Validator C.5
(`blog_pipeline.py:243-269`) → zapisuje do `BLOG-DRAFTS/` (`blog_pipeline.py:272-299`)
→ bind do content_calendar jako `validated`. Czego brakuje do shell:false: wpisu w
`worker.CADENCE`, bramki `dry_run` (pipeline dziś zapisuje zawsze — `persist=True`
domyślnie, `wave3.py:36`; worker podaje `dry_run` tylko akcjom z `_MUTATING`,
`worker.py:28,73-74`), limitu staleness w wave-check i testu ścieżki dispatch.

---

## 3. Macierz kryteriów exit

Kategorie: **(E) execution path** · **(D) evidence path** · **(Q) quality gate** ·
**(S) safety** · **(T) test contract**.

Kryteria wspólne (warunek wstępny dla WSZYSTKICH ról — bez tego flip jest nieuczciwy
niezależnie od roli):

| ID | Kryterium wspólne | Kotwica |
|----|-------------------|---------|
| S1 | Model gate'u rozstrzygnięty i zapisany w kodzie: CADENCE = whitelist akcji tool-side; `live_gated` dalej znaczy „publish parked"; worker NIE wyklucza już roli, tylko publish nigdy nie wchodzi do mapy (zasada z `worker.py:17-18` zachowana). Docstring `worker.py:1-6` zaktualizowany: „live cadence = HITL" → „live publish nigdy z workera; draft cadence = tool" | `worker.py:19-41` |
| S2 | Deploy na prod + dowód ≥7 dni ticków workera z rc=0 dla nowych ról (journal audit jak w 9-01) — marker mówi „proven on prod", więc sam kod nie wystarczy | `registry.py:141-144`, `deployment/demand-os-agents-worker.timer:7` |
| T0 | `test_cadence_map_covers_only_registry_actions` zaktualizowany: zamiast `not live_gated` asertuje „akcje CADENCE ⊆ akcje tool-side roli" + nowy test „publish/engage-live nigdy w CADENCE" (pin S1) | `tests/unit/test_agents_worker.py:50-57` |
| D0 | `_STALE_LIMITS_H` w wave-check uzupełnione o nowe role (kontrakt „must match worker.CADENCE" jest pinowany mechanicznie — bez tego test coherence pada) | `wave_check.py:172-180` |

### 3.1 `blog` — flip możliwy jako pierwszy

| Kat. | Kryterium (musi być TRUE) | Stan dziś / kotwica |
|------|---------------------------|---------------------|
| E1 | `blog.pipeline` w `worker.CADENCE` (rekomendowane `168.0h` = 1/tydz., zgodnie z KPI „1 article/tydz") | brak — `worker.py:19-25` |
| E2 | `dry_run` przewodzony przez całą ścieżkę: worker `_MUTATING += {"pipeline"}` → `wave3._blog` → `run_pipeline(persist=not dry, calendar=not dry)`; bez `--apply` zero zapisu | `dry_run` dziś ignorowany — `wave3.py:28-49`, `worker.py:28,73-74` |
| D1 | Auto-heartbeat po dispatch (działa z pudełka przez `registry._record_run_heartbeat`) + widoczność w `list_agents()` | mechanizm jest — `registry.py:154-169,220-221` |
| D2 | Artefakt-dowód po każdym apply: plik w `BLOG-DRAFTS/` (json+md) + slot `validated` w content_calendar + wpis decyzji w validator log | ścieżka istnieje — `blog_pipeline.py:272-330`; brak tylko triggera z workera |
| Q1 | Validator C.5 w pętli dla każdego draftu (PASS → `validated` + calendar; FAIL → `rejected`, brak bind) | **już jest** — `blog_pipeline.py:243-269,304-305` |
| Q2 | Publish/ship pozostaje HITL: człowiek w desk podejmuje draft → publish (test→delete do unlock) | poza kodem agenta — `UNLOCK-LIVE-P0.md` |
| S3 | `live_ship: False` w envelope zostaje; worker nigdy nie dostaje akcji publish (nie istnieje w registry — i nie może powstać bez osobnej decyzji) | `wave3.py:45,64` |
| T1 | Pytest: `run_due --apply` z seedowanym starym heartbeat tworzy draft + heartbeat + calendar slot; dry-run tworzy nic | wzorzec: `test_agents_worker.py:68-80` |
| T2 | Test kontraktu `wave3._blog`: `dry_run=True` ⇒ `persist=False`, zero plików w `BLOG-DRAFTS/` | nowy |

### 3.2 `cf` — najpierw musi powstać akcja mutująca

| Kat. | Kryterium (musi być TRUE) | Stan dziś / kotwica |
|------|---------------------------|---------------------|
| E1 | Nowa akcja mutująca `brief_persist` (lub `brief --persist`): brief zapisywany do trwałego store (JSON per brief) + propozycja slotu `draft` w content_calendar; dopiero potem wpis `cf.brief_persist` w CADENCE (rekomendowane `72-168h`) | dziś brief jest ulotny — `wave2.py:34-44`, `content_factory.py:40` |
| E2 | `dry_run` gate jak u bloga: `_MUTATING += {"brief_persist"}`; dry = zero plików | `worker.py:28` |
| D1 | Heartbeat + `list_agents()` | `registry.py:154-169` |
| D2 | Artefakt-dowód: rekord briefu w store + slot `draft` w calendar (nie `validated` — brief to nie asset) | do zbudowania; calendar writer istnieje — `blog_pipeline.py:302-330` jako wzorzec |
| Q1 | Proof gate w pętli: `proof_check` tier≥1 jako warunek zapisu (tier 0 = odrzut, brak persist) | mechanizm jest, nieużywany w zapisie — `content_factory.py:75` |
| Q2 | Pełny Validator C.5 nie jest wymagany na poziomie briefu (to nie caption); wymagany dopiero gdy brief staje się assetem — reguła zapisana w kodzie/komentarzu | decyzja tego dokumentu |
| S3 | CF nie ma żadnej ścieżki publish — status quo zachowane; envelope `note` o gating zostaje | `wave2.py:69` |
| T1 | Pytest ścieżki: apply → brief w store + heartbeat + slot draft; dry → pusto | wzorzec `test_agents_worker.py` |
| T2 | Pytest proof gate: tier-0 label ⇒ brak zapisu | nowy |

### 3.3 `tt` — producent kolejki HITL, nie publisher

| Kat. | Kryterium (musi być TRUE) | Stan dziś / kotwica |
|------|---------------------------|---------------------|
| E1 | Nowa akcja mutująca `draft`: generuje draft TT (skrypt/caption/UTM z briefu CF lub szablonu ICP jak blog) → Validator C.5 → zapis draftu + wpis do `hitl_queue`/calendar jako `draft`; potem `tt.draft` w CADENCE (rekomendowane `56h` ≈ 3/tydz. z coverage §H) | dziś tylko read `queue` — `wave1.py:91-106`, `registry.py:43-44` |
| E2 | `dry_run` gate: `_MUTATING += {"draft"}` | `worker.py:28` |
| D1 | Heartbeat + `list_agents()` | `registry.py:154-169` |
| D2 | Artefakt-dowód: plik draftu TT (json/md jak BLOG-DRAFTS) + widoczność slotu w istniejącym `hitl_queue` (dziś queue jest tylko czytana — musi też być zapisywana przez rolę) | `wave1.py:94-95` (read); write do zbudowania |
| Q1 | Validator C.5 w pętli dla każdego captiona (jak blog Q1) — `evaluate_publish_request` przed zapisem | wzorzec `blog_pipeline.py:243-269` |
| Q2 | Publish = zawsze człowiek (HITL execution packet jak `tt_w32_install_01` w UNLOCK-LIVE-P0); rola produkuje, człowiek publikuje | `UNLOCK-LIVE-P0.md:41-42` |
| S3 | `live_publish: False` zostaje w envelope; żaden kod roli nie dotyka transportu TT (`LiveTikTokTransport` zostaje stubem PARKED) | `wave1.py:101`, TOOL-PASS #5 |
| T1 | Pytest: apply → draft + wpis queue + heartbeat; dry → pusto; Validator FAIL → `rejected`, brak wpisu do queue | nowy, wzorzec blog T1 |

### 3.4 `fb` — drafty engage do logu, komentarz zostaje HITL

| Kat. | Kryterium (musi być TRUE) | Stan dziś / kotwica |
|------|---------------------------|---------------------|
| E1 | Nowa akcja mutująca `engage_draft`: dla engageable targetów z allowlist generuje **dry** draft komentarza → zapis do `engage_log` (writer już istnieje infrastrukturalnie) ze statusem `draft`; potem `fb.engage_draft` w CADENCE (rekomendowane `24h` — „comments daily" po unlock, drafty mogą być dzienne już teraz) | dziś tylko read allowlist — `wave2.py:73-99`, `registry.py:79-80`; writer `wave_check.py:128` |
| E2 | `dry_run` gate: `_MUTATING += {"engage_draft"}` | `worker.py:28` |
| D1 | Heartbeat + `list_agents()` | `registry.py:154-169` |
| D2 | Artefakt-dowód: rekordy `draft` w `engage_log` per target/dzień | do zbudowania na istniejącym writerze |
| Q1 | Walidacja draftu: allowlist `is_engageable` + anti-spam (limit 1+1 z coverage §H) jako bramka przed zapisem; Validator C.5 dla treści komentarza | allowlist check jest — `wave2.py:85`; reszta do zbudowania |
| Q2 | Live comment = człowiek po unlock; nigdy z workera | `UNLOCK-LIVE-P0.md`, worker docstring |
| S3 | `live_comment: False` zostaje; social connector live poza zakresem (coverage §E: parked) | `wave2.py:93` |
| T1 | Pytest: apply → drafty w engage_log tylko dla engageable targetów + heartbeat; dry → pusto; nie-engageable target ⇒ pominięty | nowy |

---

## 4. Decyzja: rekomendowana architektura docelowa per rola

Dla każdej roli rozważono dwie opcje: **(A) worker-dispatched producer** (CADENCE +
mutating action + artefakt) vs **(B) HITL desk action button** (człowiek klika, agent
wykonuje na żądanie). Opcja B jako *jedyna* ścieżka została odrzucona dla wszystkich
czterech: marker `shell` jest wyliczany z `_WORKER_CADENCE_ROLES` (`registry.py:117,145`)
i desk-button nie flipuje go uczciwie — rola zostałaby shell:true na zawsze. Desk
zostaje jako warstwa publish/ship (Q2 w macierzach).

| Rola | Decyzja | Uzasadnienie (1-2 linie) |
|------|---------|--------------------------|
| `blog` | **A — worker-dispatched draft generator** (`pipeline` w CADENCE, 168h; DRAFT autonomicznie, publish human) | Mutująca ścieżka z Validatorem C.5, persistencją i calendar bind **już istnieje** (`blog_pipeline.py:333-363`) — brakuje tylko dry_run gate + wpisu w CADENCE. Najtańszy uczciwy flip. |
| `cf` | **A — worker-dispatched brief generator** (nowa akcja `brief_persist`, 72-168h) | Brief to artefakt-wejście dla tt/fb/blog; bez jego persistencji reszta floty produkuje „z niczego". Proof gate tier≥1 jako bramka zapisu. |
| `tt` | **A — worker-dispatched queue producer** (nowa akcja `draft`, ~56h; publish zawsze HITL) | Publish TT nigdy nie może być autonomiczny (ryzyko platformowe + zasada tool-first), ale **produkcja** kolejki HITL to uczciwa praca agenta — dziś queue jest tylko czytana (`wave1.py:94`). |
| `fb` | **A — worker-dispatched engage-draft generator** (nowa akcja `engage_draft`, 24h; live comment HITL po unlock) | Writer `engage_log` i mock `engage-dry` już istnieją — draft do logu ma zerową powierzchnię live, a daje dzienną kadencję zgodną z KPI „comments/day". |

**Rekomendowana kolejność flipów:** `blog` → `cf` → `tt` → `fb`.
Uzasadnienie: blog wymaga najmniej nowego kodu (E2 + T1/T2 zasadniczo); cf odblokowuje
artefakt-input dla tt/fb; fb jako ostatni — najcieńsza istniejąca infrastruktura roli.

**Każdy flip to osobny commit + osobny dowód prod (S2)** — nigdy bundle 4 ról naraz.

---

## 5. Co NIE jest kryterium exit (anti-scope)

Poniższe **nie mogą** być warunkiem ani skutkiem flipa shell:false:

- Live TT/FB/blog publish, auto-reply, outbound engage — PARKED do `UNLOCK-LIVE-P0.md`;
  live cadence pozostaje pracą człowieka (HITL) nawet po unlock (`worker.py:1-6` duch zachowany).
- Ads / boost / jakikolwiek paid spend (freeze — STOP w MASTER-TODO-9).
- Social connectors live (coverage §E: `parked`, TO-BE z TARGET).
- Zmiana `live_gated: True → False` dla którejkolwiek z tych ról **jako cel sam w sobie** —
  gate dotyczy publish, nie draftów; flip live_gated bez unlock Dowódcy jest zakazany.
- Traktowanie `marketing_hitl_gate=READY` / env GO jako pozwolenia na cokolwiek live
  (`UNLOCK-LIVE-P0.md:11-13`).
- Test publish (publish→delete) — dozwolony tool-first jako odrębna aktywność, ale
  **nie jest** kryterium ani dowodem shell:false.

---

## 6. Sign-off Dowódcy (per rola, niezależnie)

Flip danej roli = wszystkie kryteria z §3 TRUE + poniższy podpis w handoffie.

| Rola | Kryteria spełnione (data / dowód) | Dowód prod ≥7 dni (handoff) | Podpis Dowódcy |
|------|-----------------------------------|-----------------------------|----------------|
| `blog` | ☐ | ☐ | ☐ |
| `cf` | ☐ | ☐ | ☐ |
| `tt` | ☐ | ☐ | ☐ |
| `fb` | ☐ | ☐ | ☐ |

Wzór wpisu do handoffu przy flipie:

```text
SHELL-FLIP <role>
Date: ___________
Criteria: §3.<x> all TRUE (links: tests, journal audit, artifacts)
Gate model: S1/T0 landed in commit <sha>
Live publish: UNTOUCHED — PARKED per UNLOCK-LIVE-P0.md
By: Dowódca
```

## STOP

- Live publish / ads / boost — poza zakresem, PARKED do unlock Dowódcy.
- Flip bez S1+T0 (gate model + test pin) = fake shell — zakazany.
- Bundle flipów (2+ role w jednym commicie) — zakazany.
