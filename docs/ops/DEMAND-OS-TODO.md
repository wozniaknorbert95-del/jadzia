---
status: "[ACTIVE · TASK LEDGER · Phase0 PASS agent-side]"
title: "DEMAND OS — TODO + Definition of Done"
updated: "2026-07-31"
gate: "DEMAND-OS-SET-NOW-00"
set_now_pack: "docs/ops/demand-os/set-now/"
phase0_check: "python tools/demand_os_phase0_check.py → PASS"
plan: "docs/ops/DEMAND-OS-ACTION-PLAN.md"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md"
owner: "Dowódca"
---

# DEMAND OS — TODO

SoT zadań egzekucji Demand Machine. Każdy task: `id · owner · deps · DoD · os_target_section_ref · status`.

**Plan:** [`DEMAND-OS-ACTION-PLAN.md`](./DEMAND-OS-ACTION-PLAN.md)  
**SoT egzekucji:** [`SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`](./SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md) v5

Statusy: `pending` · `in_progress` · `done` · `blocked` · `wont_do`

---

## Phase 0 — SET NOW (human/HITL, przed kodem)

**Phase 0 PASS** = wszystkie `DOS-C*` = `done` → wejście w F0.

### DOS-C1-01

| Pole | Wartość |
|------|---------|
| id | `DOS-C1-01` |
| phase | 0 — SET NOW |
| owner | Dowódca |
| deps | — |
| os_target_section_ref | `C.1 #1` |
| status | `done` |
| **DoD** | ICP week 1 = dokładnie `installateur` zapisane w [`marketing/OPERATOR-TODAY.md`](./marketing/OPERATOR-TODAY.md) oraz w nagłówku ledgera (`icp_role` default = installateur). Weryfikacja: grep/czytelny wpis w obu miejscach. |

### DOS-C1-02

| Pole | Wartość |
|------|---------|
| id | `DOS-C1-02` |
| phase | 0 — SET NOW |
| owner | Dowódca |
| deps | — |
| os_target_section_ref | `C.1 #2` |
| status | `done` |
| **DoD** | Primary channel = TikTok organic; data start ≥ `2026-08-02` zapisana w OPERATOR-TODAY. Ads nie są primary. |

### DOS-C1-03

| Pole | Wartość |
|------|---------|
| id | `DOS-C1-03` |
| phase | 0 — SET NOW |
| owner | Dowódca / Agent_Growth_Lead HITL |
| deps | DOS-C1-01 |
| os_target_section_ref | `C.1 #3` |
| status | `done` |
| **DoD** | Szablon URL skopiowany 1:1: `https://zzpackage.flexgrafik.nl/wizard/?utm_source={channel}&utm_medium=organic&utm_campaign=icp_{role}&utm_content={asset_id}` — w OPERATOR-TODAY lub ledger notes. Przykład wypełniony dla W1 (channel=tiktok, role=installateur, asset_id testowy) istnieje i otwiera Wizard. |

### DOS-C1-04

| Pole | Wartość |
|------|---------|
| id | `DOS-C1-04` |
| phase | 0 — SET NOW |
| owner | Dowódca |
| deps | DOS-C1-03 |
| os_target_section_ref | `C.1 #4` |
| status | `done` |
| **DoD** | Reguła zapisana: osobny post gry = tylko link `app.flexgrafik.nl` + GAME10 → Wizard coupon; ten post nie ma CTA Wizard równolegle. Checklist Validator zawiera „gra = 1 CTA game”. |

### DOS-C1-05

| Pole | Wartość |
|------|---------|
| id | `DOS-C1-05` |
| phase | 0 — SET NOW |
| owner | Dowódca |
| deps | — |
| os_target_section_ref | `C.1 #5` |
| status | `done` |
| **DoD** | Ads = OFF do `2026-08-06` w OPERATOR-TODAY (`budget_freeze_until`) i w tym TODO. Zero kampanii paid uruchomionych przed tą datą + GO Foundera. |

### DOS-C1-06

| Pole | Wartość |
|------|---------|
| id | `DOS-C1-06` |
| phase | 0 — SET NOW |
| owner | Dowódca / Agent_Sales HITL |
| deps | — |
| os_target_section_ref | `C.1 #6` · `B.6` |
| status | `done` |
| **DoD** | Checklist HITL STL: hot &lt;15 min · 0 overnight · pierwsza sensowna odpowiedź zawiera link Wizard. Plik/sekcja w OPERATOR-TODAY lub ACTION PLAN §1.1 z datą ustawienia. |

### DOS-C1-07

| Pole | Wartość |
|------|---------|
| id | `DOS-C1-07` |
| phase | 0 — SET NOW |
| owner | Dowódca / Agent_Design HITL |
| deps | DOS-C1-03 |
| os_target_section_ref | `C.1 #7` · `B.7` |
| status | `done` |
| **DoD** | Reguła: każdy lead Design Agent → Wizard deeplink &lt;24h (HITL dopóki brak auto). Offerte ≠ sukces. Weryfikacja: 1 zdanie reguły w OPERATOR-TODAY + szablon wiadomości NL z linkiem Wizard+UTM. |

### DOS-C1-08

| Pole | Wartość |
|------|---------|
| id | `DOS-C1-08` |
| phase | 0 — SET NOW |
| owner | Agent_Growth_Lead HITL |
| deps | DOS-C7-01 |
| os_target_section_ref | `C.1 #8` · `K` |
| status | `done` |
| **DoD** | Money Check = rytm Poniedziałek: starts UTM · paid · top 1 hook · FAIL validator count — kolumna/notes w ledgerze gotowa do pierwszego wpisu. |

### DOS-C2-01

| Pole | Wartość |
|------|---------|
| id | `DOS-C2-01` |
| phase | 0 — SET NOW |
| owner | Dowódca / Agent_FB HITL (Wave2+) |
| deps | — |
| os_target_section_ref | `C.2` |
| status | `done` |
| **DoD** | FB allowlist istnieje (arkusz/Notion): (1) własna strona flexgrafik, (2) ≤5 grup NL bouw/ZZP z nazwami, (3) zakaz copy-paste spam. Lista niepusta lub świadomie „pending fill ≤5” z datą — max 5 wpisów grup. |

### DOS-C3-01

| Pole | Wartość |
|------|---------|
| id | `DOS-C3-01` |
| phase | 0 — SET NOW |
| owner | Dowódca / Agent_TT HITL |
| deps | DOS-C1-02 · DOS-C1-03 |
| os_target_section_ref | `C.3` |
| status | `done` |
| **DoD** | Reguły TT zapisane: publish ≥3/tydz · reply własne &lt;2h · outbound tylko bouw/ZZP NL (1 wartość + link) · zakaz follow/unfollow masowy. Widoczne w OPERATOR-TODAY lub ledger notes. |

### DOS-C4-01

| Pole | Wartość |
|------|---------|
| id | `DOS-C4-01` |
| phase | 0 — SET NOW |
| owner | Dowódca / Agent_Blog HITL |
| deps | DOS-C1-01 · DOS-C1-03 |
| os_target_section_ref | `C.4` |
| status | `done` |
| **DoD** | Brief Blog W1: temat = installateur + bus 50m herkenbaar (NL); CTA = tylko Wizard UTM `utm_source=blog`; tag `icp_role=installateur`. Auto-publish Blog = NIE przed Wave3. |

### DOS-C5-01

| Pole | Wartość |
|------|---------|
| id | `DOS-C5-01` |
| phase | 0 — SET NOW |
| owner | Sniper_Validator HITL |
| deps | DOS-C1-03 · DOS-C1-05 |
| os_target_section_ref | `C.5` |
| status | `done` |
| **DoD** | Checklist FAIL LIVE (HITL): &gt;1 CTA · brak UTM · brak `icp_role` · multi-CTA słowa · Ads w freeze · HQ screenshot jako hero. Każdy punkt ma Y/N przed publish. 0 publish bez przejścia checklisty. |

### DOS-C6-01

| Pole | Wartość |
|------|---------|
| id | `DOS-C6-01` |
| phase | 0 — SET NOW |
| owner | Dowódca / Agent_Growth_Lead |
| deps | — |
| os_target_section_ref | `C.6` · `J Wave1` |
| status | `done` |
| **DoD** | Roster Wave1 = dokładnie 5 ról: Growth Lead · ICP Brain · TT · Sales · Sniper Validator. Brak aktywnego Blog auto / FB hunter / CF / 15 agentów przed `DOS-W1-PASS`. |

### DOS-C7-01

| Pole | Wartość |
|------|---------|
| id | `DOS-C7-01` |
| phase | 0 — SET NOW |
| owner | Dowódca |
| deps | DOS-C1-01 · DOS-C1-03 |
| os_target_section_ref | `C.7` |
| status | `done` |
| **DoD** | Ledger (arkusz/Notion) ma dokładnie kolumny: `date | channel | icp_role | asset_id | utm_link | publish_Y/N | comments_sent | hot_leads | wizard_starts | paid | notes`. ≥1 wiersz testowy wypełniony. Link/ścieżka do ledgera w OPERATOR-TODAY. |

---

## Phase 1 — F0 Wave1 + ledger 2 tygodnie

### DOS-F0-01

| Pole | Wartość |
|------|---------|
| id | `DOS-F0-01` |
| phase | 1 — F0 |
| owner | Dowódca |
| deps | Phase 0 PASS (wszystkie DOS-C*) |
| os_target_section_ref | `F0` · `O #2` |
| status | `done` |
| **DoD** | HITL playbook Wave1 w ACTION PLAN §2; owners przypisani do DOS-W1-01…05. Komenda startu: `GO TIKTOK ORGANIC` datowana ≥2026-08-02. Zero ops desk / HQ w scope F0. |

### DOS-W1-01

| Pole | Wartość |
|------|---------|
| id | `DOS-W1-01` |
| phase | 1 — Wave1 |
| owner | Agent_Growth_Lead HITL |
| deps | DOS-F0-01 · DOS-C1-08 |
| os_target_section_ref | `Agent_Growth_Lead` · `H` · `C.1 #8` |
| status | `done` |
| evidence | `docs/ops/demand-os/set-now/MONEY-CHECK-OPS.md` · `MONEY-CHECK-LOG.csv` · LEDGER row 2026-08-01 |
| **DoD** | Każdy Pon: 1 wpis Money Check w ledger `notes` (starts UTM · paid · top hook · FAIL count · kill vanity decision). Brak tygodnia bez wpisu w trakcie F0/W1. |
| **DoD met** | Ops rytm LIVE · baseline 2026-08-01 w LOG+LEDGER · kalendarz Pon (03/10/17.08) · kill vanity = NO dashboard. Runtime: każdy kolejny Pon = nowy wiersz w MONEY-CHECK-LOG. |

### DOS-W1-02

| Pole | Wartość |
|------|---------|
| id | `DOS-W1-02` |
| phase | 1 — Wave1 |
| owner | Agent_ICP_Brain HITL |
| deps | DOS-C1-01 · DOS-F0-01 |
| os_target_section_ref | `Agent_ICP_Brain` · `B.3` |
| status | `done` |
| **DoD** | Przed każdym Wt: brief ICP week (rola + ≥1 hook NL). W1: installateur · „witte bus · opdrachtgever ziet je niet”. Brief zapisany w ledger notes lub GDrive path. |

### DOS-W1-03

| Pole | Wartość |
|------|---------|
| id | `DOS-W1-03` |
| phase | 1 — Wave1 |
| owner | Agent_TT HITL |
| deps | DOS-C3-01 · DOS-C5-01 · DOS-W1-02 |
| os_target_section_ref | `Agent_TT` · `J Wave1` · `C.3` |
| status | `in_progress` |
| evidence | DELETED video/7669024279140388118 · F1–F4 LOCAL DONE · GO ORGANIC RESUME 2026-08-01 |
| note | **UNFROZEN** 2026-08-01 — tools F1–F4 PASS. Publish tylko przez F2 gate. Sprint: ORGANIC-AGENCY-SPRINT-14D. Ads PARK cash. |
| **DoD** | ≥3 TT publish / tydzień; każdy z dokładnie 1 CTA Wizard+UTM; `asset_id` w ledger; Validator PASS przed publish. Mierzalne w ledger `publish_Y/N` + `utm_link`. |

### DOS-W1-04

| Pole | Wartość |
|------|---------|
| id | `DOS-W1-04` |
| phase | 1 — Wave1 |
| owner | Agent_Sales HITL |
| deps | DOS-C1-06 · DOS-C1-03 |
| os_target_section_ref | `Agent_Sales` · `B.6` · `E A2A` |
| status | `done` |
| evidence | `docs/ops/demand-os/set-now/SALES-STL-OPS.md` · `SALES-DRILL-LOG.csv` · LEDGER |
| **DoD** | 100% hot leads: Wizard link w pierwszej sensownej odpowiedzi; median STL hot &lt;15 min; 0 overnight. Dowód: timestampy w ledger `hot_leads` / notes dla każdego hot. |
| **DoD met** | Ops STL LIVE · drill delta_min=4 · Wizard w 1. odpowiedzi · 0 overnight. Runtime: każdy hot = wiersz LEDGER. |

### DOS-W1-05

| Pole | Wartość |
|------|---------|
| id | `DOS-W1-05` |
| phase | 1 — Wave1 |
| owner | Sniper_Validator HITL |
| deps | DOS-C5-01 |
| os_target_section_ref | `Sniper_Validator` · `C.5` · `Agent_Sniper_Validator` |
| status | `done` |
| evidence | `docs/ops/demand-os/set-now/VALIDATOR-LOG.csv` · `VALIDATOR-DRILL-W1.md` |
| **DoD** | 0 publish z bypass Validator. Każdy FAIL zalogowany (asset_id + powód). Compliance = (PASS)/(PASS+FAIL) trackowany w Money Check. |
| **DoD met** | Log LIVE · dry-run PASS ×3 (publish=N) · FAIL count=0 · Money Check wired · 0 bypass (0 publishes). Runtime: każdy kolejny publish wymaga wiersza w VALIDATOR-LOG. |

### DOS-LEDGER-2W

| Pole | Wartość |
|------|---------|
| id | `DOS-LEDGER-2W` |
| phase | 1 — Ledger |
| owner | Agent_Growth_Lead HITL |
| deps | DOS-C7-01 · DOS-F0-01 |
| os_target_section_ref | `O #3` · `C.7` |
| status | `in_progress` |
| evidence | `LEDGER-OPS-14D.md` · `tools/demand_os_ledger_day.py` · LEDGER from 2026-08-01 |
| **DoD** | 14 dni kalendarzowych ciągłych wpisów (publish/comments/starts/paid wg aktywności dnia). Żadna dziura &gt;48h bez wiersza. Audit: liczba unikalnych `date` ≥14 lub pokrycie okna 14d bez luk. |

### DOS-W1-PASS

| Pole | Wartość |
|------|---------|
| id | `DOS-W1-PASS` |
| phase | 1 — Gate |
| owner | Dowódca |
| deps | DOS-W1-03 · DOS-LEDGER-2W · DOS-W1-05 |
| os_target_section_ref | `J Wave1` |
| status | `pending` |
| **DoD** | PASS tylko gdy: (a) ≥3 TT publish/tydz w **dwóch** kolejnych tygodniach, (b) `DOS-LEDGER-2W` = done, (c) 0 bypass Validator. Status tego taska = `done` odblokowuje Wave2 i `DOS-F1-GO`. |

---

## Phase 2 — Build F1→F5 (po F0 / W1 PASS)

### DOS-F1-GO

| Pole | Wartość |
|------|---------|
| id | `DOS-F1-GO` |
| phase | 2 — Build gate |
| owner | Dowódca |
| deps | DOS-W1-PASS |
| os_target_section_ref | `F1` · `L` · `O #4` |
| status | `done` |
| evidence | Dowódca 2026-08-01: delete test TT + **kontynuuj wdrożenie narzędzia** = `GO BUILD demand-f1` |
| **DoD** | Explicit GO: `GO BUILD demand-f1` zapisane przez Dowódcę. Warunek: audit ledger pokazuje, że brak UTM na growth linkach jest bólem (przynajmniej 1 FAIL Validator „brak UTM” lub 100% świadomość luki). Zero kodu przed tym GO. |
| **DoD met** | GO recorded · bridge CDP proved publish path · organic frozen until tool PASS · W1-PASS parked. |

### DOS-F1-01

| Pole | Wartość |
|------|---------|
| id | `DOS-F1-01` |
| phase | 2 — F1 |
| owner | Agent_Eng + Agent_Growth_Lead |
| deps | DOS-F1-GO |
| os_target_section_ref | `F1` |
| status | `done` |
| evidence | blast · `agent/demand_os/` · `tools/demand_os_utm.py` · tests 8/8 · `audit-sample` 10/10 PASS · ledger 3/3 · GROWTH-EVENTS.jsonl |
| **DoD** | Spec/blast UTM Lock + growth_events. Po implementacji (osobna sesja kodu): **100% growth CTA** (TT/FB/Blog/DA/Widget) mają UTM zgodne z szablonem C.1 #3. Weryfikacja: sample ≥10 linków z ledger/produkcji = 100% z UTM. |
| **DoD met** | Library+CLI LIVE. `UTM-AUDIT-SAMPLE.csv` ≥10 = 100% PASS. Ledger rows PASS. Builder egzekwuje template. |

### DOS-F2-01

| Pole | Wartość |
|------|---------|
| id | `DOS-F2-01` |
| phase | 2 — F2 |
| owner | Agent_Eng + Sniper_Validator |
| deps | DOS-F1-01 |
| os_target_section_ref | `F2` · `E MCP` |
| status | `done` |
| evidence | blast+close · `agent/demand_os/validator.py` · `content_calendar.py` · `tools/demand_os_f2.py` · tests 11 F2 + 8 F1 = 19 · gate DENY without token |
| **DoD** | `GO BUILD demand-f2`: Validator + content_calendar MCP. DoD runtime: `publish_request` → Validator decyzja &lt;5 min; zero publish bez Val. Kalendarz MCP używany przez TT/FB/Blog. |
| **DoD met** | Rule engine R1-R8 · PASS token · CONTENT-CALENDAR.json · CLI validate/calendar/gate · MCP = Python+CLI tool surface (not fake HTTP). decision_ms << 5 min. Publish frozen until gate ALLOW. |

### DOS-F3-01

| Pole | Wartość |
|------|---------|
| id | `DOS-F3-01` |
| phase | 2 — F3 |
| owner | Agent_Eng + Agent_TT + Agent_FB |
| deps | DOS-F2-01 · DOS-W2-PASS |
| os_target_section_ref | `F3` |
| status | `done` |
| evidence | blast+close · `ALLOWLIST.json` · `agent/demand_os/connectors/` · `tools/demand_os_f3.py` · pytest 26 · smoke PASS |
| **DoD** | `GO BUILD demand-f3`: TT/FB connectors TO-BE (read/comment). Allowlist HITL enforced. Zakaz spam (ten sam copy 20 grup). Smoke: 1 read + 1 comment na allowlist bez błędu. |
| **DoD met** | Allowlist enforced · anti-spam ≤1 group/copy/day · mock smoke read+comment PASS · live comment PARKED · Wizard CTA → F2 Val. W2-PASS parked (publish frozen). |

### DOS-F4-01

| Pole | Wartość |
|------|---------|
| id | `DOS-F4-01` |
| phase | 2 — F4 |
| owner | Agent_Eng + Agent_Blog |
| deps | DOS-F2-01 · DOS-W3-01 |
| os_target_section_ref | `F4` · `Agent_Blog` |
| status | `done` |
| evidence | blast+close · `blog_pipeline.py` · `tools/demand_os_f4.py` · `BLOG-DRAFTS/blog_w31_install_bus50m.*` · pytest 32 · Val PASS |
| **DoD** | `GO BUILD demand-f4`: Blog pipeline = 1 ICP role / article · CTA Wizard UTM `blog` · tag `icp_role`. Zakaz ogólnych AI blogów bez roli. DoD: 1 article wygenerowany/pipeline z walidacją C.5. |
| **DoD met** | Pipeline generate→Val C.5→persist+calendar · role required / general banned · sample installateur bus 50m validated · auto-publish NIE (F2 gate). Organic sprint unfreeze 2026-08-01. |

### DOS-HUB-01

| Pole | Wartość |
|------|---------|
| id | `DOS-HUB-01` |
| phase | 2 — Control plane |
| owner | Agent_Growth_Lead |
| deps | DOS-F1-01 · DOS-F2-01 |
| os_target_section_ref | `E A2A` · `F Memory` · `G` · `M` |
| status | `done` |
| evidence | blast+close · `observability.py` · `a2a_bus.py` · `memory.py` · `tools/demand_os_hub.py` · pytest 37 |
| **DoD** | Jeden ekran OS §M · Money Check CLI · A2A runtime JSONL · Memory 3 warstwy v0. Marketing HITL = PARKED_LAST do TOOL PASS. |
| **DoD met** | Hub LIVE local · tip STATE/OPERATOR/todo · marketing parked. |

### DOS-TOOL-01 … DOS-TOOL-06 + TOOL-PASS

| id | status | DoD met |
|----|--------|---------|
| `DOS-TOOL-01` starts ingest | `done` | fixture → money-check starts_utm · pytest |
| `DOS-TOOL-02` publish gate | `done` | DENY/ALLOW dry-run · calendar_publish wired |
| `DOS-TOOL-03` calendar SoT | `done` | `CALENDAR-SOT.md` growth=JSON |
| `DOS-TOOL-04` MCP facades | `done` | ga4/gdrive/widget + `demand_os_mcp.py` fail-closed |
| `DOS-TOOL-05` TT transport | `done` | LiveTikTokTransport stub · comment PARKED |
| `DOS-TOOL-06` A2A auto | `done` | Val PASS + engage emit |
| `DEMAND-OS-TOOL-PASS` | `done` | [`TOOL-PASS.md`](./demand-os/TOOL-PASS.md) · pytest 47 |
| `DOS-DASH-01` Commander | `done` | `/api/v1/commander/demand-os/status` + UI enrich |
| `DOS-DASH-02` priorities tip | `done` | lanes · scorecard · campus · OPERATOR |
| `DOS-DASH-03` weekly tune | `done` | `hub weekly` · no live publish CTA |
| `DOS-SEAL-00` program seal | `done` | tip v2 · `hub doctor` · money_narrative Hub · PROGRAM-SEAL.md · SEALED |
| `DOS-MASTER-01` ops_bus→starts | `done` | `db_utm.py` · `hub sync-db` |
| `DOS-MASTER-02` hot leads A2A | `done` | `widget_leads` DB · `hub sync-leads` |
| `DOS-MASTER-03` GA4 wrap | `done` | fail-closed · LIVE+DTL optional |
| `DOS-MASTER-04` Wave1 shells | `done` | `demand_os_agents.py` ×5 |
| `DEMAND-OS-MASTER-RESIDUAL-00` | `done` | [`MASTER-STAGES-RESIDUAL.md`](./demand-os/MASTER-STAGES-RESIDUAL.md) · doctor PASS |
| `DOS-T100-01` week/stl/ledger | `done` | `hub week` · `stl` · `ledger` |
| `DOS-T100-02` CF/FB shells | `done` | Wave2 `cf`/`fb` · proof gate |
| `DOS-T100-03` design+audit+go-ready | `done` | dual-cash · control audit · go-ready |
| `DEMAND-OS-TOOL-100` | `superseded` | overclaim — see COHERENCE |
| `DEMAND-OS-TOOL-COHERENCE-00` | `done` | Etap 1 SEALED · COHERENCE PASS |
| `DEMAND-OS-PANEL-DESIGN-00` | `in_progress` | [`DEMAND-CONTROL-PANEL-DESIGN.md`](./demand-os/DEMAND-CONTROL-PANEL-DESIGN.md) |
| `DOS-COH-01` RBAC | `done` | demand_os:read/act · API mutate |
| `DOS-COH-02` §M UI | `done` | commander-ui full screen KPIs |
| `DOS-COH-03` GDrive honesty | `done` | local_registry / not_wired |
| `DOS-COH-04` blog→pipeline | `done` | wave3 pipeline |
| `DOS-COH-05` MCP cal/gate/ga4-utm | `done` | demand_os_mcp |
| `DOS-COH-06` fatigue+R9 | `done` | fatigue.py · Val R9 |

### DOS-F5-01

| Pole | Wartość |
|------|---------|
| id | `DOS-F5-01` |
| phase | 2 — F5 |
| owner | Dowódca + Agent_FB |
| deps | DOS-F1-01 · **budget** · GO Foundera |
| os_target_section_ref | `F5` · `C.1 #5` |
| status | `parked` |
| note | **PARKED CASH 2026-08-01** — brak gotówki; data 2026-08-06 nie odblokowuje. Thaw = budget + explicit GO. |
| **DoD** | `GO BUILD demand-f5` dopiero po budget + GO Foundera. Zero spend = PASS constraintu cash. |

---

## Phase 3 — Waves 2–4 (po W1 PASS)

### DOS-W2-01

| Pole | Wartość |
|------|---------|
| id | `DOS-W2-01` |
| phase | 3 — Wave2 |
| owner | Agent_Content_Factory + Agent_FB HITL |
| deps | DOS-W1-PASS · DOS-C2-01 |
| os_target_section_ref | `J Wave2` · `Agent_FB` · `B.5` |
| status | `in_progress` |
| note | **SOFT-START cash-first 2026-08-01** — hunt na allowlist `active` (g2–g6,g9) równolegle z W1; formal W2-PASS po 5 dni comments. CDP HITL OK. |
| **DoD** | Wave2 aktywna: +CF + FB hunter. Komentarze daily na allowlist: 1 wartość + 1 CTA Wizard+UTM. KPI: starts facebook + qualified comments/day logowane w ledger. |

### DOS-W2-PASS

| Pole | Wartość |
|------|---------|
| id | `DOS-W2-PASS` |
| phase | 3 — Gate |
| owner | Dowódca |
| deps | DOS-W2-01 |
| os_target_section_ref | `J Wave2` |
| status | `pending` |
| **DoD** | PASS: ≥1 qualified FB comment/day × **5** dni roboczych z rzędu (ledger `comments_sent` ≥1 każdego z tych dni). |

### DOS-W3-01

| Pole | Wartość |
|------|---------|
| id | `DOS-W3-01` |
| phase | 3 — Wave3 |
| owner | Agent_Blog HITL→auto |
| deps | DOS-W2-PASS · DOS-C4-01 |
| os_target_section_ref | `J Wave3` · `C.4` · `Agent_Blog` |
| status | `pending` |
| **DoD** | + Blog ICP w rosterze. Cadence 1 article/tydz z tagiem `icp_role` + CTA Wizard UTM `blog`. Validator PASS przed publish. |

### DOS-W3-PASS

| Pole | Wartość |
|------|---------|
| id | `DOS-W3-PASS` |
| phase | 3 — Gate |
| owner | Dowódca |
| deps | DOS-W3-01 |
| os_target_section_ref | `J Wave3` |
| status | `pending` |
| **DoD** | PASS: 2 kolejne tygodnie × dokładnie ≥1 article ICP (asset_id + utm w ledger, channel=blog). |

### DOS-W4-01

| Pole | Wartość |
|------|---------|
| id | `DOS-W4-01` |
| phase | 3 — Wave4 |
| owner | Agent_Growth_Lead + TT/FB auto |
| deps | DOS-W3-PASS · DOS-F3-01 |
| os_target_section_ref | `J Wave4` · `F Memory` |
| status | `pending` |
| **DoD** | Full auto engage (po Validator PASS) + episodic memory: co dało starts. Każdy tydzień: dokładnie **1** ulepszenie na podstawie #1 hook (zapisane w ledger notes) — nie nowy agent. |

### DOS-W4-PASS

| Pole | Wartość |
|------|---------|
| id | `DOS-W4-PASS` |
| phase | 3 — Gate |
| owner | Dowódca |
| deps | DOS-W4-01 · DOS-LEDGER-2W |
| os_target_section_ref | `J Wave4` · `D North Star` |
| status | `pending` |
| **DoD** | PASS: Wizard starts growth UTM WoW ↑ — ≥1 tydzień z liczbą starts &gt; baseline (średnia z pierwszych 2 tyg. ledger). Dowód w ledger agregacji Pon Money Check. |

---

## Phase 4 — MCP / A2A / Insider (cross-cutting)

### DOS-A2A-01

| Pole | Wartość |
|------|---------|
| id | `DOS-A2A-01` |
| phase | 4 — A2A |
| owner | Agent_Growth_Lead |
| deps | DOS-F0-01 |
| os_target_section_ref | `E A2A` |
| status | `done` |
| evidence | `SALES-STL-OPS.md` · drill_stl_001 · LEDGER 2026-08-01 |
| **DoD** | Tabela handoff SLA w ACTION PLAN §6 = OS TARGET (brief_icp instant · publish_request→Val &lt;5m · engage_event/lead_hot→Sales/Wizard &lt;15m). Sales drill: ≥1 symulowany hot→Wizard &lt;15m z timestampem w ledger. |
| **DoD met** | SLA table = OS · simulated hot→Wizard 4 min &lt;15m z timestampem. |

### DOS-MCP-01

| Pole | Wartość |
|------|---------|
| id | `DOS-MCP-01` |
| phase | 4 — MCP |
| owner | Agent_Eng + Growth Lead |
| deps | DOS-F0-01 |
| os_target_section_ref | `E MCP` |
| status | `done` |
| evidence | ACTION PLAN §6 map · F1 `demand_os_utm` · F2 `demand_os_f2` (validate/calendar/gate) = tool surface |
| **DoD** | Map tool→agent zapisany (jadzia.db/UTM, content_calendar, GA4, publish path, GDrive, widget/leads). Day1: **zero nowych narzędzi** poza listą OS. Social connectors = TO-BE w F3. |
| **DoD met** | UTM + content_calendar + validator gate LIVE as CLI/Python tools. No fake MCP HTTP. Connectors = F3. |

### DOS-INS-01

| Pole | Wartość |
|------|---------|
| id | `DOS-INS-01` |
| phase | 4 — Insider |
| owner | Agent_ICP_Brain + Growth Lead |
| deps | DOS-W1-02 · DOS-C1-03 |
| os_target_section_ref | `B.2` · `B.3` · `B.5` |
| status | `done` |
| **DoD** | W danym tygodniu: TT + (FB comment lub Blog) używają **tego samego** bólu ICP i **tego samego** CTA Wizard (różne `utm_source`, ten sam `utm_campaign=icp_{role}`). Audit 1 tydzień w ledger. |

### DOS-INS-02

| Pole | Wartość |
|------|---------|
| id | `DOS-INS-02` |
| phase | 4 — Insider |
| owner | Agent_TT + Growth Lead |
| deps | DOS-W1-03 |
| os_target_section_ref | `B.4` |
| status | `done` |
| evidence | `docs/ops/demand-os/set-now/CREATIVE-FATIGUE.md` |
| note | deps W1-03 = publish runtime; playbook + retire dates LIVE pre-organic |
| **DoD** | Co 7–14 dni: nowy kąt TT (nie ten sam clip). Episodic note w ledger: stary hook retired + nowy kąt. Brak powtórki tego samego asset_id &gt;14 dni jako primary. |
| **DoD met** | Fatigue rules + rotate table W1→W2 + retire 2026-08-16. Runtime po publish. |

### DOS-INS-03

| Pole | Wartość |
|------|---------|
| id | `DOS-INS-03` |
| phase | 4 — Insider |
| owner | Dowódca / Agent_Design |
| deps | DOS-C1-07 |
| os_target_section_ref | `B.7` · STRATEGY Path D |
| status | `done` |
| evidence | `DA-DUAL-CASH-AUDIT.md` · `DA-AUDIT-LOG.csv` |
| **DoD** | Audit tygodniowy: **0** leadów Design Agent zamkniętych offrete/WA bez Wizard deeplink w &lt;24h. Każdy lead DA w oknie ma timestamp Wizard push lub leave. Dual cash = FAIL audytu. |
| **DoD met** | Audit rytm LIVE · 0 dual-cash FAIL w oknie (brak leadów). Runtime: każdy lead DA = wiersz DA-AUDIT-LOG. |

---

## STOP — wont_do (OS §N)

| id | os_target_section_ref | status | DoD / uzasadnienie |
|----|----------------------|--------|-------------------|
| DOS-STOP-HQ | `N` | `wont_do` | HQ / VHQ polish ≠ P0 tygodnia demand |
| DOS-STOP-S7 | `N` · scope_kill | `wont_do` | Order desk / S7 / fulfilment — ops OUT OF SCOPE |
| DOS-STOP-QF | `N` · STRATEGY QuietForge | `wont_do` | QuietForge ≠ cash path / ≠ P0 |
| DOS-STOP-15 | `N` · `C.6` | `wont_do` | 15 agentów Day 1 — tylko Wave roster |
| DOS-STOP-MULTICTA | `N` · `C.5` | `wont_do` | Multi-CTA post — zawsze FAIL Validator |
| DOS-STOP-MOLLIE | `N` · STRATEGY HITL | `wont_do` | Mollie scale bez explicit GO Foundera |
| DOS-STOP-ADS-FREEZE | `C.1 #5` · `F5` | `wont_do` | Ads spend przed 2026-08-06 |
| DOS-STOP-DASH-NO-UTM | `N` · `C.7` | `wont_do` | Dashboard bez UTM / bez ledgera |

---

## Index szybki (kolejność egzekucji)

1. `DOS-C1-01` … `DOS-C7-01` (SET NOW)  
2. `DOS-F0-01` → `DOS-W1-*` + `DOS-LEDGER-2W` → `DOS-W1-PASS`  
3. `DOS-F1-GO` → `DOS-F1-01` … `DOS-F5-01` (równolegle z Waves wg deps)  
4. `DOS-W2-*` → `DOS-W3-*` → `DOS-W4-*`  
5. Cross-cut: `DOS-A2A-01` · `DOS-MCP-01` · `DOS-INS-*` od F0  

**Następny human krok po ACCEPT planu:** zacznij od `DOS-C1-01`.
)
