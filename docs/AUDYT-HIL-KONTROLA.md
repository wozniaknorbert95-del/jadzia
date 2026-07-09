# AUDYT: COI Commander — Warstwa człowieka, HITL i kontrola dowodzenia

**Data:** 2026-07-09 · **Status:** Pre-Faza 0 (blokujący) · **Zlecenie:** Dowódca (Norbert)
**Wykonawca:** Panel Audytowy AI Systems — powołany do oceny *obsługi człowieka* i *sposobu sterowania/zarządzania* systemem.

> Fokus audytu: **jak człowiek (Dowódca, ADHD) steruje, zatwierdza, nadzoruje i przejmuje kontrolę nad agentami** — oraz gdzie plan mu to utrudnia, zagraża lub daje fałszywe poczucie kontroli. Nie oceniamy tu stacku ani backendu jako takiego.

---

## 1. PROFESJONALNY PLAN AUDYTU

### 1.1 Cel
Ocenić plan COI Commander **wyłącznie przez pryzmat obsługi człowieka** i kontroli dowodzenia.
Pytanie przewodnie: *czy Dowódca po otwarciu dashboardu panuje, czy jest panikowany?*

### 1.2 Zakres
- **IN:** HITL/HOTL, queue design, approval flows, ludzka autoryzacja (authz), Telegram boundary, obciążenie poznawcze (ADHD), failure→human escalation, rozliczalność (audit).
- **OUT:** implementacja backendu, dobór bibliotek, SEO, koszty infra (chyba że wpływają na kontrolę człowieka).

### 1.3 Skład panelu (specjaliści "od systemów AI")
| Rola | Co wnosi |
|---|---|
| **HIL / Interaction Lead** | obsługa człowieka, UX neurodywersyjny (ADHD) |
| **AI Control & Governance** | autorytet, macierz uprawnień, escalation, audit trail |
| **Agent Reliability / AI Safety** | failure modes, silent failure, dead-man's switch |
| **Cognitive Load Analyst** | pojemność uwagi, single-pane, queue design |

### 1.4 Metodologia (4 testy)
1. **Mapowanie do frameworków** — każdy moduł przez: HITL authority-levels [1], 3-bucket action classification [3], EU AI Act / GDPR Art.22 [1][4], FAILURE.md silent-failure [3], cognitive-load 5–7 chunks + ADHD [2][4].
2. **Test odwracalności** (Elementum: *"can this decision be undone?"*) dla każdej akcji człowieka [1].
3. **Test "czy ktoś słucha"** (FAILURE.md: escalation trafia do człowieka, który słucha) — co gdy Dowódca **NIE** działa [3].
4. **Test obciążenia poznawczego** — czy 1 ekran = spokój czy panika (Miller 5–7, 3 priorytety, progressive disclosure) [2][4].

### 1.5 Ramy oceny (scorecard)
| Wymiar | Pytanie kontrolne |
|---|---|
| Autorytet | Kto, co i z jakim ryzykiem zatwierdza? |
| Odwracalność | Co po błędnym kliknięciu? |
| Wykrywalność | Czy system krzyczy, gdy agent/podziela cicho failuje? |
| Obciążenie | 1 ekran = spokój czy panika? |
| Ciągłość | Co gdy Dowódca znika na 3 dni? |
| Rozliczalność | Kto, kiedy, skąd (dashboard / TG / auto)? |

### 1.6 Harmonogram
- **Dzień 1:** plan + warsztat 2h (walkthrough "poniedziałek rano").
- **Dzień 2:** synteza CE + macierz autorytetu.
- **Wyjście:** ten dokument + uzupełnione D0.5 / D0.6 / D0.7 o warstwę człowieka.

---

## 2. AKCJA — WYKONANIE AUDYTU

### 2.1 Co jest DOBRE (zostawić, nie ruszać)
- **Słuszna diagnoza źródła:** *"backend pracuje, nie ma warstwy człowieka"* — to właściwy problem, nie "brak funkcji".
- **Telegram boundary (D0.7):** jasna granica alerty-only vs primary surface — dobra higiena HITL.
- **Registry pattern jako DoD:** *"moduł = WORKING dopiero gdy widać last action + pending queue + pause/resume"* — obserwowalność człowieka wbudowana w definicję ukończenia. Excelent.
- **Approval gate na FB publish:** nieodwracalna akcja (publiczny post) ma bramkę HITL (Approve + Publish). Zgodne z EU AI Act (override/reversal) [1][4].
- **Faza 0 przed kodem:** unika budowania UI bez IA — dojrzałe podejście.
- **Świadomość anti-patterns:** TG ≠ główny UI, COI ≠ agent-os-ui, nie mieszanie Basic/JWT.
- **JWT proxy (secret po stronie serwera):** właściwy wzorzec dla UI trzymającego uprawnienia.

### 2.2 Gdzie plan PĘKA (mapa luk w obsłudze człowieka)
| Moduł planu | Co działa | Co pęka (ludzka kontrola) |
|---|---|---|
| Commander Queue | agregacja | brak tierowania ryzyka (CE-01), brak SLA/escalation (CE-03) |
| Telegram `/zadanie` | alerty | SSH do prod POZA authenticated plane (CE-02) |
| Home / 11 modułów | Registry | sprzeczność z ADHD "single pane" (CE-04) |
| Approve + Publish | bramka | brak undo / confirm / audit (CE-05) |
| pause / resume agentów | sterowanie | brak macierzy autorytetu (CE-06) |
| ApprovalCard | komponent | brak kontekstu eskalacji (CE-07) |
| FB / lead korekty | HITL | brak pętli uczenia (CE-08) |
| single-operator | prostota | brak delegacji / fallback (CE-09) |
| Analytics tiles | dane | brak freshness / staleness (CE-10) |

### 2.3 Głosy specjalistów (skrót)
- **HIL Lead:** *"Chcą 'wszystko w jednym miejscu' dla ADHD — ale queue z 4 typami elementów + 11 modułów to przepis na przeładowanie. Dać 3 priorytety dnia, nie 14."*
- **AI Control:** *"Brak macierzy autorytetu. Kto pauzuje agenta FB? Kto zatwierdza post? Czy to samo kliknięcie? To ceremonia, nie kontrola (NIST)."*
- **Reliability:** *"Najgroźniejszy fail to cichy. Queue bez SLA 'pending > 24h' to zombie — Dowódca myśli, że panuje, a nic nie wychodzi."*
- **Cognitive:** *"5–7 chunków na ekran. 11 modułów + queue = 15+ elementów. Albo progressive disclosure, albo porażka."*

---

## 3. LISTA BŁĘDÓW KRYTYCZNYCH (z uzasadnieniem)

### CE-01 — Queue bez tierowania ryzyka (krytyczne: ADHD + HITL)
**Błąd:** Commander Queue agreguje posty (pending_approval), hot leads, błędy agentów i zadania — wszystkie traktowane równo.
**Dlaczego krytyczne:** Łamie dwie zasady naraz: (a) **ADHD** — wymusza ciągłą re-priorytetyzację [2][4]; (b) **HITL authority-levels** — różne elementy mają różny autorytet/ryzyko (post = ryzyko marki, lead = pieniądz, error = ops) [1]. Bez tierowania → over-escalation (wszystko woła uwagę) lub under-escalation (prawdziwy błąd zakopany pod postami).
**Uzasadnienie:** Elementum [1]: *"Authority levels should vary by risk"*; UXPin [4]: priorytetyzacja + 5–7 chunków; ADHD research [2]: *"Today's 3 priorities (not 15)"*.
**Wpływ na człowieka:** Dowódca otwiera dashboard i czuje panikę, nie spokój → porzuca narzędzie.
**Poprawka:** Queue = 3 poziomy severity (CRITICAL / ACTION / INFO) + filtr "tylko moje 3 priorytety dziś".

### CE-02 — Telegram `/zadanie` WP SSH poza authenticated control plane (krytyczne: bezpieczeństwo + kontrola)
**Błąd:** Plan daje Telegramowi "awaryjny WP SSH (`/zadanie`)" — modyfikacja systemu produkcyjnego z chatbota.
**Dlaczego krytyczne:** Narusza wytyczną NHIMG [3]: high-impact actions (prod modification) wymagają zatwierdzenia **WEWNĄTRZ** authenticated workflow, nie w wątku czatu. Brak: intent-based authz, kontekstu (co zmieniono / dokąd / po co), audit trail, dual-approval. Jest też **sprzeczne z własnym D0.7**, który mówi TG = alerty only / *"nigdy registry / planning"*.
**Uzasadnienie:** NHIMG [3]: *"approval must sit inside the authenticated control plane, not in a ticket, chat thread, or change log"*; KILLSWITCH.md [3]: forbidden actions + escalation.
**Wpływ na człowieka:** Dowódca może przez pomyłkę/czat zdestruować prod WP bez śladu i bez drugiego potwierdzenia.
**Poprawka:** `/zadanie` tylko otwiera ticket → wykonanie w dashboardzie (HITL + audit). SSH prod tylko z dashboardu z dual-approval + log.

### CE-03 — Brak wykrywania "człowiek poza pętlą" / dead-man's switch (krytyczne: cichy fail)
**Błąd:** Registry ma last_run / last_error, ale **NIE MA SLA**: co gdy pending approval > 24h, agent nie pobiegł od X, queue rośnie nieprzeczytana.
**Dlaczego krytyczne:** FAILURE.md [3]: silent failure to najgroźniejszy tryb — *"zombie tasks"*, nic nie krzyczy. Dla solo ADHD-foundera dashboard musi **AKTYWNIE** eskalować gdy ignorowany, a nie pasywnie wyświetlać. Dashboard z zastarzałymi danymi = gorszy niż brak dashboardu (fałszywe poczucie kontroli).
**Uzasadnienie:** dev.to [3]: *"zombie tasks alive by every metric except the one that matters"*; latitude.so [5]: silent quality degradation niewidoczna dla monitoringu.
**Wpływ na człowieka:** Myśli, że nadzoruje, a biznes stoi (posty nie wychodzą, leady bez odpowiedzi).
**Poprawka:** SLA per element: *"pending > 12h → amber, > 24h → red + push"*; *"agent silent > 2× interval → alert"*.

### CE-04 — "Jeden cockpit ADHD" sprzeczny z 11 modułami (krytyczne: przeładowanie poznawcze)
**Błąd:** Plan zakazuje "10 modułów naraz" (anti-pattern), ale Faza 3 lista **~11 modułów** pod Commanderem, a Home ma je (niejawnie) pokrywać. IA limit "max 8 nav" vs 11 modułów — nieuzgodnione.
**Dlaczego krytyczne:** ADHD research [2]: sukces to 3 priorytety, energy-not-category, progressive disclosure; UXPin [4]: 5–7 chunków. 11 modułów + queue = przeładowanie, przeciwne do celu.
**Uzasadnienie:** [2]: *"3 priorities not 15"*; [4]: *"humans process 5–7 chunks"*.
**Wpływ na człowieka:** Home staje się ścianą info → porzuca tool (klasyczny "Notion graveyard" [2]).
**Poprawka:** Home = 3 priorytety dnia + queue + health strip; moduły = drill-down; energia zamiast kategorii.

### CE-05 — Nieodwracalne akcje bez undo / confirm / audit-trail (krytyczne: Accountability)
**Błąd:** FB publish (publiczny, nieodwracalny) ma Approve + Publish, ale brak: confirm dialog, "undo 60s", kto-kiedy-skąd log.
**Dlaczego krytyczne:** UXPin [4]: *"undo for destructive actions, confirm for significant changes"*. EU AI Act [1][4]: high-risk wymaga override/reversal + log. Brak rozliczalności: czy post wyszedł z dashboardu, z auto-hook czy z TG?
**Uzasadnienie:** [4] accessibility; GDPR Art. 22 [1][4]; Exterro [4]: defensibility.
**Wpływ na człowieka:** Błędny post publiczny, niewiadomo kto/co, brak cofnięcia.
**Poprawka:** confirm + 60s undo + append-only audit log (actor, source, ts) na każdą mutację.

### CE-06 — Brak macierzy autorytetu / 3-bucket classification (krytyczne: ceremonial HITL)
**Błąd:** pause / resume i approve istnieją, ale **NIGDZIE** nie zdefiniowano: które akcje low-risk (auto), sensitive (1× HITL), high-impact (dual). Dowódca = jedyny approver wszystkiego, bez granic.
**Dlaczego krytyczne:** NHIMG [3]: obowiązkowa 3-kubełkowa klasyfikacja akcji. NIST AI RMF [1][3]: HITL bez kontekstu / autorytetu / czasu = ceremonia (rubber-stamp).
**Uzasadnienie:** [3] three buckets; [1] ceremonial HITL.
**Wpływ na człowieka:** Albo wszystko klika na autopilocie (ryzyko marki/prawne), albo wszystko blokuje go jako wąskie gardło.
**Poprawka:** Action Risk Matrix (tabela): akcja → tier → approval → blast radius.

### CE-07 — ApprovalCard bez kontekstu eskalacji (krytyczne: rubber-stamp)
**Błąd:** D0.4 specyfikuje ApprovalCard, ale **NIE określa kontraktu treści**: co Dowódca widzi PRZED zatwierdzeniem (powód eskalacji, source, confidence).
**Dlaczego krytyczne:** Elementum [1]: reviewer musi widzieć output + reason + confidence + source + dostępne akcje. Bez tego ADHD-Dowódca zatwierdza na autopilocie → ryzyko. Brak confidence-routing = over-escalation.
**Uzasadnienie:** [1] reviewer handoff; confidence-based routing 10–15%.
**Wpływ na człowieka:** Zatwierdza posty/leady nie wiedząc, dlaczego u niego wylądowały.
**Poprawka:** ApprovalCard contract: `{ payload, escalation_reason, source, confidence, available_actions }`.

### CE-08 — Brak pętli uczenia z korekt człowieka (krytyczne: wąskie gardło na stałe)
**Błąd:** Gdy Dowódca odrzuca / poprawia posta czy lead-score, korekta **NIE wraca** do agenta. Brak ścieżki HITL → HOTL → autonomia.
**Dlaczego krytyczne:** Elementum [1]: *"start at HITL to capture corrections as training data"*; graduacja po pewności. Bez tego każdy post wymaga zatwierdzenia na zawsze → przeczy skalowalności.
**Uzasadnienie:** [1] HITL as training data, confidence graduation.
**Wpływ na człowieka:** Staje się wiecznym recenzentem, nie dowódcą.
**Poprawka:** Feedback endpoint: rejection / correction → agent memory / threshold tuning.

### CE-09 — Model single-operator bez delegacji / fallback (krytyczne: single point of failure)
**Błąd:** Wszystko do jednego człowieka. Brak delegacji (VA / agencja), brak fallback gdy niedostępny.
**Dlaczego krytyczne:** Oracle Digital GMP [2]: single-point autonomy risk; FAILURE.md [3]: escalation musi trafić do człowieka, który słucha. Gdy Dowódca znika 3 dni → biznes stoi.
**Uzasadnienie:** [2] dual-control; [3] *"routes to a human who is listening"*.
**Wpływ na człowieka:** Urlop = paraliż. Brak ciągłości.
**Poprawka:** Role (Dowódca + Delegat), *"if no action 24h → escalate to email / 2nd"*, read-only viewer dla VA.

### CE-10 — Brak freshness / staleness na danych (krytyczne: fałszywa pewność)
**Błąd:** Analytics tiles (GA4, orders, leads) bez "last sync", bez wskaźnika świeżości, bez SLA.
**Dlaczego krytyczne:** FAILURE.md [3]: silent failure includes *"API returned stale data"*. Jeśli connector GA4 cicho padnie, Dowódca widzi wczorajsze liczby i podejmuje złe decyzje myśląc, że live. ADHD-user ufa "jednemu cockpitowi" → szczególnie podatny.
**Uzasadnienie:** [3] data freshness; [5] silent quality degradation.
**Wpływ na człowieka:** Decyzje biznesowe na martwych danych.
**Poprawka:** *"last sync: 4 min"* + amber/red gdy > SLA + tooltip source.

---

### Źródła (frameworki użyte w audycie)
- [1] Elementum — HITL vs HOTL, authority levels, reversibility, EU AI Act, GDPR, NIST ceremonial HITL, confidence routing: https://www.elementum.ai/blog/human-in-the-loop-vs-human-on-the-loop
- [2] Notion ADHD dashboard (3 priorities, energy, no-shame reset) + Oracle Digital GMP (3 kategorie agentów, single-point autonomy): https://www.reddit.com/r/Notion/comments/1s5d6t9/ ; https://medium.com/@oracle_43885/human-in-the-loop-best-practices-for-ai-enabled-digital-gmp
- [3] NHIMG intent-based authz + KILLSWITCH.md + FAILURE.md + dev.to zombie tasks: https://nhimg.org/faq/how-should-security-teams-implement-human-in-the-loop-controls-for-ai-agents/ ; https://killswitch.md/ ; https://failure.md/ ; https://dev.to/bobrenze/how-ai-agents-handle-stalled-tasks-and-timeouts
- [4] UXPin dashboard principles (5–7 chunks, undo, progressive disclosure) + Exterro defensibility: https://www.uxpin.com/studio/blog/dashboard-design-principles/ ; https://www.exterro.com/resources/human-in-the-loop-the-only-responsible-ai-for-legal-and-compliance
- [5] Latitude — taxonomy silent failure: https://latitude.so/blog/ai-agent-failure-detection-guide
