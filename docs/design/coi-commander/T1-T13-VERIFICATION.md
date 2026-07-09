# T1–T13 — weryfikacja domknięcia w planie v3

**Data:** 2026-07-09  
**Plan:** [`COI-COMMANDER-PLAN-v3.md`](COI-COMMANDER-PLAN-v3.md)  
**Audyt źródłowy:** [`AUDYT-V2-GAP.md`](AUDYT-V2-GAP.md)

Metoda: każdy wiersz T z audytu GAP musi mieć **konkretną sekcję** w planie v3 (nie tylko changelog w czacie).

| T | Wymaganie audytu | Sekcja planu v3 | Deliverable / faza | Status |
|---|------------------|-----------------|-------------------|--------|
| **T1** | Emergency bez laptopa: `/ticket` + signed deep-link; eskalacja Delegat; zero SSH | § BLOKERY N1; § D0.14; § Telegram v3; Workshop test #5 | D0.14, F2 DoD | ✅ w planie |
| **T2** | Audit log: retencja GDPR, storage, reader-roles, tamper-evidence, pola | § BLOKERY N2; § D0.10; F1 `GET /audit-log` | D0.10, F1 | ✅ w planie |
| **T3** | Graduation: `override_rate < X%` przez N prób → HOTL per action-type | § BLOKERY N3; § D0.11; F3 + `POST /feedback` | D0.11, F3 | ✅ w planie |
| **T4** | Public (unpublish+notify) vs internal (60s undo) | § BLOKERY N5; CE-05 fix w GATE STATUS; F1 publish/unpublish | D0.8 Risk Matrix, F2 Marketing | ✅ w planie |
| **T5** | Escalation recipient gdy Dowódca = blocker | § BLOKERY N6; § D0.9; architektura Email→Delegat | D0.9, F2 Settings | ✅ w planie |
| **T6** | JWT role claims + server-side enforcement + scoping Delegata | § BLOKERY N7; § D0.13; F1 `@require_scope` | D0.13, F1 | ✅ w planie |
| **T7** | Severity policy + SLA registry per queue-type | § POZOSTAŁE N4/N8; § D0.8 | D0.8 | ✅ w planie |
| **T8** | Pause/resume: held queue + manual fallback | § N9; D0.3 wireframes; F2 Agents | D0.3, F2 | ✅ w planie |
| **T9** | UI language PL vs content NL | § N15; § D0.12 | D0.12 | ✅ w planie |
| **T10** | WCAG + dashboard-down TG health push | § N10/N16; F2 Global | F2 | ✅ w planie |
| **T11** | Deep-linki signed + expireable, bez sesji w URL | § N12; § D0.7, D0.14; F1 `POST /auth/deeplink` | D0.7, D0.14, F1 | ✅ w planie |
| **T12** | Publish lock / last-writer (agent vs człowiek) | § N13; F1 version lock 409 | F1, F2 | ✅ w planie |
| **T13** | Cost guardrail bulk approve (KILLSWITCH) | § N14; F2 Global; DoD f2-hitl-proof | F2 | ✅ w planie |

---

## Blokery N1–N7 (must-have przed approve)

| N | Opis | Domknięte przez |
|---|------|-----------------|
| N1 | no-laptop recovery | T1 → D0.14 |
| N2 | audit log pełna spec | T2 → D0.10 |
| N3 | graduation thresholds | T3 → D0.11 |
| N5 | public undo semantics | T4 → N5 section + D0.8 |
| N6 | escalation recipient | T5 → D0.9 |
| N7 | multi-role authz | T6 → D0.13 |

**Wniosek weryfikacji:** Wszystkie T1–T13 mają explicite sekcje w planie v3. Plan nadal **DRAFT** — wymaga **approve Dowódcy** przed jakimkolwiek startem (F0 workshop, UX brief, kod).

---

## CE resztkowe (post-v2)

| CE | Gap v2 | Fix v3 |
|----|--------|--------|
| CE-01 | severity policy | D0.8 (T7) |
| CE-02 | no-laptop | D0.14 (T1, T11) |
| CE-03 | push do siebie | D0.9 (T5) |
| CE-04 | 11→nav | D0.1 N4b |
| CE-05 | public undo | N5 (T4) |
| CE-08 | graduation | D0.11 (T3) |
| CE-09 | authz odroczone | **nie odroczone** — D0.13 (T6) |
| CE-10 | per-source SLA | D0.8 N8 (T7) |
