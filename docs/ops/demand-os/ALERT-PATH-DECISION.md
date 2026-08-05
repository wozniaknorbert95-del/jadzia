# ALERT PATH DECISION — worker failure alerting na prod (MT-9/9-06)

**Status:** DECISION (rekomendacja: **OPT-B**) · **Data:** 2026-08-06 · **Repo:** jadzia-core
**Zakres:** wykrywanie i sygnalizacja awarii `demand-os-agents-worker.{timer,service}` na prod (`/opt/jadzia`, systemd). Tylko decyzja + szkic implementacji — bez zmian w kodzie w tym tasku.

---

## 1. Kontekst (stan faktyczny, z cytatami)

- Timer co 15 min odpala oneshot service → `venv/bin/python -m tools.demand_os_hub agents run-due --apply` (`deployment/demand-os-agents-worker.timer:6-8`, `deployment/demand-os-agents-worker.service:9-14`).
- `run_due` ma "honest envelope; never raises" i **zawsze zwraca `ok: True`** — per-role błędy lądują tylko w `runs[].status="error"` i liczniku `errors` (`agent/demand_os/agents/worker.py:61-104`, esp. `:96`, `:100-101`).
- Hub mapuje to na exit code `0 if out.get("ok") else 1` → **service wychodzi 0 nawet gdy wszystkie role się wysypały** (`tools/demand_os_hub.py:196-202`). systemd widzi "success".
- `registry.dispatch` łapie wyjątki runnerów i zwraca `ok=False` (`agent/demand_os/agents/registry.py:207-219`), ale heartbeat zapisuje tylko na ścieżce bez wyjątku (`registry.py:220-221`). Uwaga: na ścieżce bez wyjątku envelope ma **hardkodowane `ok: True`** niezależnie od `ok` runnera (`registry.py:222-223`) — dziś runnery wave1 sygnalizują awarie wyjątkami (`agent/demand_os/agents/wave1.py:30-44`), więc klasa "soft-fail" jest teoretyczna, ale strukturalnie niewidoczna.
- Detekcja dziś: doctor `agents_staleness` — RED gdy heartbeat roli cadence starszy niż limit (48h; sales 12h) (`agent/demand_os/agents/wave_check.py:174-218`); na prod BLOCKING via `DEMAND_OS_STALENESS_BLOCKING=1` (`agent/demand_os/doctor.py:336-350`).
- Doctor odpala się: (a) przy każdym loadzie deska — `GET /api/v1/commander/demand-os/status` woła `build_demand_os_status(with_full_doctor=True)` (`api/routes/commander.py:182-190`); (b) ręcznie w `owner-verify` (`tools/demand_os_owner_verify.py:71-77`). **Brak schedulowanego doctora i brak kanału push.**
- Unity są wersjonowane w repo i kopiowane na VPS (`deployment/install-service.sh:38-44`) → zmiana unitów = zmiana w repo + deploy.
- Telegram: `TELEGRAM_BOT_TOKEN` jest w `.env.example:14`, ale autopush ma kill-switch **domyślnie OFF** (`agent/telegram_autopush.py:12-20`; kontrakt opisany w `.env.example:15-17`), a `TELEGRAM_ADMIN_CHAT_ID` / `ALLOWED_TELEGRAM_USERS` w ogóle nie występują w `.env.example` (resolver: `agent/marketing/telegram_proposals.py:242-248`).

## 2. Macierz: tryb awarii × detekcja dziś

| Tryb | Co się dzieje | Wykrywa dziś | Widoczne gdzie / kiedy | Luka |
|---|---|---|---|---|
| **F1** crash ticka (traceback, zły venv, import error) | exit≠0 → unit `failed`; heartbeat nie rośnie | systemd (biernie), doctor dopiero po oknie staleness 12–48h | `journalctl` od razu; desk footer / owner-verify po 12–48h **i dopiero gdy ktoś spojrzy** | brak sygnału w chwili crasha; doctor nie rozróżnia "crash 10 min temu" od "martwy timer" |
| **F2** timer martwy / service down | nic nie ticknie → heartbeaty stygną | doctor `agents_staleness` RED (BLOCKING na prod) | desk footer (`doctor_ok`) przy najbliższym loadzie deska; owner-verify przy ręcznym odpaleniu | **ludzka latencja** — nikt nie patrzy, dopóki nie spojrzy (rituał dzienny deska) |
| **F3** dispatch roli pada cyklicznie (wyjątek w runnerze) | per-role `error` w JSON run-due; exit wciąż 0; heartbeat roli zamrożony | journal (errors>0); doctor po 12–48h przez staleness tej roli | `journalctl` od razu; doctor przy następnym spojrzeniu | jak F1/F2 + klasa soft-fail (gdyby runner zwracał `ok=False` bez wyjątku) **niewidoczna strukturalnie** — envelope spłaszcza do `ok=True` (`registry.py:223`) |

**Kluczowa luka (jedna linia):** wszystko co wykrywalne schodzi się do doctora, a doctor odpala się tylko gdy człowiek patrzy (desk / owner-verify) — nie ma żadnego zapisu awarii w chwili zdarzenia ani kanału push.

Ocena akceptowalności: rituał "Dowódca ładuje desk codziennie" domyka F2 z latencją ≤ ~24h, co mieści się w oknach staleness (12–48h) i w realiach tool-only loop (role są read/upsert, brak publish — awaria nie pali pieniędzy). Latencja ludzka sama w sobie jest więc akceptowalna; **nieakceptowalny jest brak dowodu z chwili zdarzenia dla F1/F3** (dziś: tylko journal, ulotny, bez przejścia przez żaden check).

## 3. Opcje

### OPT-A — nic więcej (doctor blocking + desk footer wystarczą)
- **Plusy:** zero pracy, zero nowych zależności; ścieżka już dziś udowodniona canary; pełna zgodność z no-fake-evidence.
- **Minusy:** F1/F3 widać dopiero po 12–48h okna staleness (nie w chwili awarii); klasa soft-fail F3 niewidoczna w ogóle; diagnoza "dlaczego RED" zawsze zaczyna się od grzebania w journalctl.

### OPT-B — `OnFailure=` → alert unit dopisuje do `ALERTS.jsonl` + doctor check `worker_failures` ← **REKOMENDACJA**
- **Plusy:** zamyka F1 w chwili zdarzenia (linia w jsonl = realny event systemd); z 1-linijkową zmianą exit code w hubie łapie też F3; **całość wyłazi przez ISTNIEJĄCĄ ścieżkę** doctor → desk footer / owner-verify (zero nowych kanałów, zero sekretów, zero sieci); alert unit jest głupi jak but (system python, stdlib) — nie zależy od venv, który może być właśnie przyczyną crasha.
- **Minusy:** nie zamyka ludzkiej latencji F2 (celowo — patrz §2); +2 unity, +1 moduł, +1 check do utrzymania; wymaga jednego deploya unitów (Zasada 11 — GO Dowódcy).

### OPT-C — Telegram push z alert unit
- **Plusy:** jedyny wariant z latencją ~real-time; Dowódca dowiaduje się bez otwierania deska.
- **Minusy:** potrzebuje `TELEGRAM_BOT_TOKEN` + `TELEGRAM_ADMIN_CHAT_ID` w env unitu — ten drugi **nie jest nigdzie udokumentowany w repo** (`.env.example` go nie ma); autopush kill-switch jest domyślnie OFF i wszystkie istniejące pushy go respektują (`telegram_autopush.py:12-20`) — alert musiałby albo leżeć martwy pod kill-switchem, albo łamać ustalony kontrakt; zależność od sieci/TG API dokładnie w momencie awarii; nowe failure modes (curl/httpx w `OnFailure`) i sekret w dodatkowym unicie.

**Decyzja: OPT-B.** Zamyka realną, dziś niewidoczną klasę (F1 crash-time + F3 error-storm) dowodem zapisywanym w chwili zdarzenia i raportowanym przez sprawdzoną ścieżkę doctora. Ludzka latencja odczytu (≤24h, rituał deska) jest świadomie akceptowana. OPT-C zostaje jako późniejszy, cienki add-on do tego samego alert unitu (jedno `ExecStartPost` wysyłające TG po dopisaniu linii) — bez przeróbki architektury, jeśli Dowódca kiedyś zechce push.

## 4. Szkic implementacji OPT-B (follow-up engineer, <1h)

### 4.1 Nowy unit: `deployment/demand-os-agents-worker-alert.service`

```ini
# Demand OS — worker failure sink (MT-9/9-06 OPT-B).
# Fires ONLY via OnFailure= from demand-os-agents-worker.service.
# Deliberately dumb: system python3 + stdlib — must survive a broken venv.
[Unit]
Description=Demand OS agents worker failure sink (ALERTS.jsonl)

[Service]
Type=oneshot
User=jadzia
Group=jadzia
Environment=ALERTS_PATH=/opt/jadzia/data/demand-os/set-now/ALERTS.jsonl
ExecStart=/usr/bin/python3 -c "import json,os,datetime,pathlib; p=pathlib.Path(os.environ['ALERTS_PATH']); p.parent.mkdir(parents=True,exist_ok=True); rec={'ts':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'unit':'demand-os-agents-worker.service','kind':'onfailure','source':'systemd','resolved':False}; f=p.open('a',encoding='utf-8'); f.write(json.dumps(rec)+'\n'); f.close()"
# Brak [Install] — nigdy nie enable'ować standalone (jak K13 pattern).
```

Dlaczego `/usr/bin/python3` a nie `venv/bin/python`: jeśli crash worker'a wziął się z zepsutego venv, alert unit na tym samym venv też padnie i alert przepadnie. System python = zero wspólnych przyczyn awarii. Unit worker'a nie ma `ProtectSystem=strict` (to ma tylko `jadzia.service:38-42`), więc zapis do `/opt/jadzia/data/...` przejdzie.

### 4.2 Jedna linia w `deployment/demand-os-agents-worker.service`

```ini
[Unit]
Description=Demand OS agents worker (run-due dispatch)
After=network.target
OnFailure=demand-os-agents-worker-alert.service
```

### 4.3 (Zalecane) Exit code odzwierciedla per-role errors — `tools/demand_os_hub.py`

Dziś `cmd_agents_run_due` zwraca 0 mimo `errors>0` (`tools/demand_os_hub.py:196-202`). Zmiana:

```python
out = run_due(dry_run=not args.apply)
_print(out)
if not out.get("ok"):
    return 1
return 2 if int(out.get("errors") or 0) > 0 else 0   # F3 → OnFailure też strzela
```

Efekt: rola padająca cyklicznie (F3-wyjątki) generuje alert co tick — doctor pokaże RED w ≤24h zamiast czekać na okno staleness 12–48h. Klasa soft-fail (envelope spłaszcza `ok` runnera, `registry.py:223`) zostaje udokumentowanym residuum — runnery dziś rzucają wyjątki, więc pokryta przez exit 2.

### 4.4 Reader + resolver — `agent/demand_os/agents/alerts.py` (nowy, ~40 linii)

```python
ALERTS_MAX_AGE_H = 24.0

def default_alerts_path() -> Path:
    from agent.demand_os.state_paths import resolve_writable_path
    return resolve_writable_path("ALERTS.jsonl", env_var="DEMAND_OS_ALERTS_LOG")

def active_alerts(*, path=None, now=None) -> list[dict]:
    """Tolerantny parse jsonl; zwraca linie z resolved=False młodsze niż 24h.
    Brak pliku / złe linie = brak alertów (nigdy nie wywala doctora)."""
```

Resolver celowo idzie przez `resolve_writable_path` — ten sam kontrakt co heartbeat (`agent/demand_os/agents/heartbeat.py:24-28`, `agent/demand_os/state_paths.py:25-50`); na prod `.env` dopina `DEMAND_OS_ALERTS_LOG=/opt/jadzia/data/demand-os/set-now/ALERTS.jsonl` (zgodnie z `.env.example:134`).

### 4.5 Doctor check `worker_failures` — `agent/demand_os/doctor.py`

Wzorzec 1:1 z `agents_staleness` (`doctor.py:336-350`), ta sama flaga severity:

```python
try:
    from agent.demand_os.agents.alerts import active_alerts
    act = active_alerts()
    detail = "no active worker failures" if not act else f"{len(act)} failure(s) <24h, last={act[-1]['ts']}"
    checks.append(_check("worker_failures", not act, detail))
    if staleness_blocking and act:
        errors.append("worker_failures FAIL (blocking mode)")
except Exception as exc:
    checks.append(_check("worker_failures", False, str(exc)[:160]))
    if staleness_blocking:
        errors.append("worker_failures error (blocking mode)")
```

Semantyka resolve: **auto-expire po 24h** (okno w readerze), bez workflow ręcznego domykania — zero ryzyka fake-green, zero operacji. Jeśli awaria trwa >24h, alert unit i tak dopisuje nową linię co tick (exit≠0) → okno się przewija → RED trwa uczciwie.

### 4.6 Test plan

1. **pytest readera** (nowy `tests/test_demand_os_worker_alerts.py`): brak pliku → `[]`; zła linia → pominięta; linia 25h → poza oknem; `resolved=True` → pominięta; monkeypatch `DEMAND_OS_ALERTS_LOG` na `tmp_path`.
2. **pytest doctora**: advisory vs blocking — kopiuj wzorzec `tests/test_demand_os_coherence_etap1.py:137-178` (setenv/delenv `DEMAND_OS_STALENESS_BLOCKING`, asercje na `checks` + `errors`).
3. **pytest exit code**: monkeypatch `run_due` → `errors=1` → `cmd_agents_run_due` == 2; `errors=0` → 0.
4. **Lokalny systemd (dry):** `systemd-analyze verify deployment/demand-os-agents-worker-alert.service`.
5. **Canary na prod (po GO Dowódcy na deploy unitów):** `sudo systemctl start demand-os-agents-worker-alert.service` (to dokładnie to, co zrobi `OnFailure`) → linia w `ALERTS.jsonl` → `python -m tools.demand_os_hub doctor` pokazuje `worker_failures` RED (blocking) → desk footer `doctor_ok=false` → usunąć linię testową → GREEN. Zapisać canary w handoffie (uczciwie: test/deleted).
6. **Pełny:** `python tools/demand_os_owner_verify.py` exit 0. Uwaga: owner-verify celowo czyści `DEMAND_OS_STALENESS_BLOCKING` tylko dla subprocesu pytest (`tools/demand_os_owner_verify.py:62-66`) — check doctora w kroku 1 biegnie in-process z env proda, więc nowy check jest tam objęty bez zmian.

### 4.7 Deploy (Zasada 11 — tylko z GO)

`sudo cp deployment/demand-os-agents-worker{,-alert}.service /etc/systemd/system/ && sudo systemctl daemon-reload` + canary z §4.6 pkt 5. Bez `enable` dla alert unitu (oneshot wywoływany wyłącznie przez `OnFailure=`).

## 5. Residua (świadomie nie zamykane w tym tasku)

- **F2 push:** latencja odczytu ≤24h (rituał deska) — akceptowana; OPT-C jako późniejszy add-on do alert unitu.
- **F3 soft-fail:** envelope `dispatch` spłaszcza `ok=False` runnera do `ok=True` (`registry.py:223`) — dziś klasa pusta (runnery rzucają), ale przy przyszłych runnerach rozważyć propagację `ok` z `out.get("ok")`.
- **Scheduled doctor** (np. timer co 1h zapisujący wynik) — zbędny pod OPT-B: check i tak odpala się przy każdym loadzie deska, a dowody awarii leżą trwale w `ALERTS.jsonl`.
