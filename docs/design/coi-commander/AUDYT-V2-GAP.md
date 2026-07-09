# AUDYT v2 — GAP KRYTYCZNY (pre-approve planu COI Commander v2)

**Data:** 2026-07-09 · **Odniesienie:** `AUDYT-HIL-KONTROLA.md` (CE-01..CE-10) + changelog v2
**Status:** Przegląd blokujący przed `approve` planu v2

> **Aktualizacja 2026-07-09:** Plan przeszedł do **v3** — [`COI-COMMANDER-PLAN-v3.md`](COI-COMMANDER-PLAN-v3.md). Weryfikacja T1–T13: [`T1-T13-VERIFICATION.md`](T1-T13-VERIFICATION.md). **Nadal wymaga approve Dowódcy przed startem.**

> UWAGA METODYCZNA: oceniam na podstawie changelogu v2 (plik `.cursor/plans/coi_commander_ux_plan_07ae3101.plan.md` jest poza workspace'em — po zsyncowaniu do `docs/design/coi-commander/` trzeba fizycznie zweryfikować, czy każdy wpis poniżej jest w tekście planu, nie tylko w podsumowaniu).

---

## 0. GATE STATUS — CE-01..CE-10 (czy v2 faktycznie zamyka?)

| CE | Realizacja w v2 | Status | Pozostały resztkowy gap → |
|----|-----------------|--------|----------------------------|
| CE-01 | Queue tiered + `GET /priorities/today` (max 3) | ✅ ZAMKNIĘTE | brak **polityki przypisywania severity** (N4) |
| CE-02 | Revoke `/zadanie` SSH → `/ticket` + dashboard-only | 🟡 ZAMKNIĘTE z luką | **dziura recovery no-laptop** (N1) |
| CE-03 | SLA >12h amber / >24h red+push; silent >2× interval | 🟡 ZAMKNIĘTE z luką | **push do samego siebie = nie eskalacja** (N6) |
| CE-04 | Home = 3 priorytety + queue + health (max 7 chunków) | ✅ ZAMKNIĘTE | brak mapowania 11 modułów→nav (N4b) |
| CE-05 | Confirm + 60s undo + append-only audit log | 🟡 ZAMKNIĘTE z luką | **undo na publicznym poście** niewystarczające (N5) |
| CE-06 | D0.8 Action Risk Matrix (low/sensitive/high-impact) | ✅ ZAMKNIĘTE | nowy deliverable D0.8 OK |
| CE-07 | D0.9 ApprovalCard contract (escalation context) | ✅ ZAMKNIĘTE | nowy deliverable D0.9 OK |
| CE-08 | `POST /feedback` → HITL→HOTL (F3) | 🟡 CZĘŚCIOWO | **brak progów graduacji** (N3) |
| CE-09 | Role Dowódca/Delegat/Viewer + escalation 24h (F3.1) | 🟡 ODROCZONE/CZĘŚCIOWO | **brak modelu authz ról** (N7) |
| CE-10 | Freshness na każdym tile analytics | 🟡 ZAMKNIĘTE z luką | brak **per-source SLA** (N8) |

**Wniosek:** v2 zamyka intencje CE, ale 7 z 10 ma resztkowy gap, a 3 (N1, N3, N7) to nowe krytyczne otwarcia. **Nie puszczać bez N1, N3, N5, N6, N7.**

---

## 1. CO JESZCZE JEST KRYTYCZNE (nowe — poza oryginalnym audytem)

### N1 — 🔴 KRYTYCZNE: CE-02 fix tworzy dziurę recovery "no-laptop"
**Problem:** Oryginalne uzasadnienie `/zadanie` to *"awaryjny WP SSH gdy nie masz laptopa"*. v2 go revoke'uje, ale **nie podaje ścieżki zastępczej**. Dowódca bez laptopa = ślepy na WP i bez możliwości reakcji.
**Dlaczego krytyczne:** Naprawa CE-02 otworzyła lukę operacyjną równie groźną co oryginał.
**Fix:** TG `/ticket` + **signed deep-link** do dashboard-ticket (otwiera się na telefonie w przeglądarce), albo eskalacja do Delegata/Viewer z dostępem dashboard. Nigdy SSH z TG.

### N2 — 🔴 KRYTYCZNE: D0.10 audit log nieokreślony (retencja/dostęp/immutability)
**Problem:** CE-05 mówi "append-only audit log", D0.10 to tylko "schema". Brak: gdzie trzymane, **retencja (GDPR — musi być zdefiniowana)**, kto czyta, **tamper-evidence**, wymagane pola (actor, action, source, ts, before/after, reason).
**Dlaczego krytyczne:** Bez tego "rozliczalność" (CE-05/CE-06) to puste hasło; EU AI Act high-risk wymaga konkretnego logu override/reversal.
**Fix:** W D0.10 dodać: storage (DB tabela nieusuwalna), retention (np. 24 msc), reader-roles, required fields, signing/hash-chain.

### N3 — 🔴 KRYTYCZNE: Brak progów graduacji HITL→HOTL (CE-08 nie do końca zamknięte)
**Problem:** `POST /feedback` istnieje, F3 "iteracyjnie", ale **nie ma metryki przejścia**. Bez progu (np. override_rate < X% przez N prób) system zostaje HITL na zawsze → Dowódca wiecznym recenzentem (regresja CE-08).
**Fix:** W CE-08/F3 dodać explicit graduation rule per action-type.

### N5 — 🔴 KRYTYCZNE: 60s undo na PUBLICZNYM poście FB niewystarczające
**Problem:** CE-05 "60s undo" zakłada soft-undo. Post FB jest **publiczny i widoczny od razu** — 60s nie cofa "zobaczenia" przez audience.
**Fix:** Dla akcji publicznych: confirm + **unpublish/delete + notify** (zamiast/obok 60s undo) + wpis w audit log "published then unpublished, reason".

### N6 — 🔴 KRYTYCZNE: CE-03 push trafia do tego samego człowieka, który ignoruje
**Problem:** SLA ">24h red+push" — ale jeśli Dowódca jest jedynym odbiorcą i to on nie zadziałał, push do niego nic nie zmienia.
**Fix:** CE-03 musi nazwać **odbiorcę eskalacji** (Delegat/email/2nd) gdy Dowódca = blocker. Łączy się z N7/F3.1.

### N7 — 🔴 KRYTYCZNE: CE-09 otwiera multi-role bez modelu authz
**Problem:** Role Dowódca/Delegat/Viewer wprowadzają nową powierzchnię ataku. JWT proxy był budowany pod **jednego** usera. "Viewer read-only" ukryty tylko w UI ≠ wymuszony server-side.
**Fix:** W CE-09 dodać: role claims w JWT, **server-side enforcement** (backend sprawdza scope, nie tylko front), scoping Delegata (które moduły), uniemożliwienie escalate-through-UI.

### N15 — 🟠 WYSOKIE: Język UI niezdefiniowany (PL vs NL) — tarcie ADHD
**Problem:** Norbert = PL, biznes = NL. Copy postów = NL, ale **język samego COMMANDER UI** nigdzie nie ustalony. Jeśli UI po angielsku (default Next.js) → tarcie poznawcze u PL-foundera z ADHD.
**Fix:** Explicit: UI Commander = PL (lub wybór), content biznesowy = NL. To wpływa na "obsługę człowieka" bezpośrednio.

---

## 2. BRAKUJE (sekcje / deliverables nieobecne w v2)

1. **Recovery-path no-laptop** (z N1) — osobna sekcja "Emergency bez laptopa".
2. **Audit Log spec poza schemą** (N2) — retencja, dostęp, immutability, pola.
3. **Graduation thresholds** (N3) — metryka HITL→HOTL.
4. **Public-action undo semantics** (N5) — rozróżnienie publiczne vs wewnętrzne.
5. **Escalation recipient model** (N6) — kto dostaje push gdy Dowódca milczy.
6. **Multi-role authz** (N7) — role claims, server-side enforcement, scoping.
7. **Severity-assignment policy + SLA registry** (N4/N8) — kto/co ustala CRITICAL i jaki SLA per queue-type.
8. **Pause/resume blast-radius & fallback** (N9) — co się dzieje z zaplanowanymi postami gdy pauzujesz agenta FB.
9. **UI language decision** (N15).
10. **WCAG/ARIA + dashboard-down continuity** (N10/N16) — accessibility i status push gdy dashboard leży.
11. **TG deep-link security** (N12) — signed/expireable, nie raw URL z sesją.
12. **Human/auto publish race** (N13) — lock/last-writer gdy agent i człowiek publikują to samo.
13. **Cost guardrail na bulk human actions** (N14) — KILLSWITCH cost-limit przy masowym approve.

---

## 3. TODO AKTUALIZACJI PLANU (konkretne edity przed approve)

| # | Gdzie w planie | Co dodać / zmienić | Zamyka |
|---|----------------|--------------------|--------|
| T1 | CE-02 / Telegram | sekcja "Emergency bez laptopa": TG `/ticket` + signed deep-link do dashboard; eskalacja do Delegata. Usunąć SSH. | N1 |
| T2 | D0.10 | retencja (GDPR), storage, reader-roles, tamper-evidence, required fields (actor/action/source/ts/before/after/reason) | N2 |
| T3 | CE-08 / F3 | graduation rule: `override_rate < X% przez N prób → HOTL` per action-type | N3 |
| T4 | CE-05 | rozróżnienie: publiczne (unpublish+notify) vs wewnętrzne (60s undo) | N5 |
| T5 | CE-03 | nazwać odbiorcę eskalacji (Delegat/email) gdy Dowódca = blocker | N6 |
| T6 | CE-09 / F3.1 | role claims w JWT + server-side enforcement + scoping Delegata | N7 |
| T7 | D0.8 | polityka przypisywania severity + SLA registry per queue-type | N4/N8 |
| T8 | CE-09 / F2 Agents | pause/resume: co z zaplanowanymi postami (held queue? manual fallback?) | N9 |
| T9 | F0 / Settings | decyzja języka UI (PL) vs content (NL) | N15 |
| T10 | F2 / global | WCAG/ARIA (klawiatura, kontrast, ruch) + TG health-push gdy dashboard down | N10/N16 |
| T11 | Telegram boundary | deep-linki = signed + expireable, bez sesji w URL | N12 |
| T12 | CE-06 / F2 | lock/last-writer przy publish (agent vs człowiek) | N13 |
| T13 | CE-06 / KILLSWITCH | cost-guardrail na bulk human actions (limit masowego approve) | N14 |

---

## 4. REKOMENDACJA (co zrobić przed approve)

**NIE puszczać planu v2 takiego jak jest.** v2 to ogromny krok do przodu (CE-01..CE-10 zamknięte intencyjnie), ale:

- **Blokery (muszą być w planie przed approve):** T1 (N1), T2 (N2), T3 (N3), T4 (N5), T5 (N6), T6 (N7).
- **Pozostałe (T7–T13):** mogą iść do F0/F1/F2 jako deliverables, ale muszą być **wymienione w planie**, żeby nie wypadły jak CE-08-orig (brak graduacji).

**Minimum do dodania jako sekcje:** Emergency-no-laptop (T1), Audit-Log-spec (T2), Graduation-thresholds (T3), Multi-role-authz (T6), UI-language (T9).

Po dopisaniu T1–T7 plan v2 jest "push-ready" z perspektywy warstwy człowieka.
