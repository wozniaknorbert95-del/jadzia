# UX Brief — COI Commander (F0)

**Status:** Spec dla workshopu i implementacji  
**Gate:** AUDYT-HIL-KONTROLA.md + AUDYT-V2-GAP.md + PLAN v3  
**Język UI:** PL | **Content biznesowy:** NL

## Pytanie przewodnie

Czy Dowódca po otwarciu dashboardu **panuje**, czy jest **panikowany**?

## CE-01..CE-10 (skrót wymagań)

| ID | Wymaganie UX |
|----|--------------|
| CE-01 | Queue tiered CRITICAL/ACTION/INFO + max 3 priorytety dziś |
| CE-02 | Zero SSH z TG; `/ticket` + signed deep-link |
| CE-03 | SLA amber/red + eskalacja do Delegata |
| CE-04 | Home ≤7 chunków; moduły drill-down |
| CE-05 | Public unpublish vs internal 60s undo |
| CE-06 | Action Risk Matrix 3-bucket |
| CE-07 | ApprovalCard z escalation context |
| CE-08 | Feedback → graduacja HITL→HOTL |
| CE-09 | Role Dowódca/Delegat/Viewer server-side |
| CE-10 | Freshness badge per source |

## Blokery N (must-have)

- **N1** Emergency no-laptop: mobile signed link
- **N2** Audit log pełna spec (D0.10)
- **N3** Graduation thresholds (D0.11)
- **N5** Public vs internal undo
- **N6** Escalation recipient ≠ self
- **N7** JWT scopes enforced backend

## Scorecard (6 wymiarów)

| Wymiar | Pass |
|--------|------|
| Autorytet | Risk Matrix + scopes |
| Odwracalność | unpublish + 60s undo |
| Wykrywalność | SLA + 2nd recipient |
| Obciążenie | Home ≤7, PL UI |
| Ciągłość | Delegat + 24h escalate |
| Rozliczalność | Audit hash-chain 24mo |

## IA (D0.1 → D0.15)

Top nav (max 5, desktop≡mobile): **Start | Marketing | Analityka | Agenci | Ustawienia**  
Audyt = secondary (D0.15). Session chrome = D0.16. Empty/error/stale = D0.17. Home load = D0.18. Hops = D0.19.  
Dogfood: [UX-DOGFOOD-PHONE.md](UX-DOGFOOD-PHONE.md).

## Daily Loop (D0.2)

1. Otwórz Home → 3 priorytety
2. Jedna akcja approve/publish
3. Done (<5 min)

## Komponenty (D0.4)

ApprovalCard, QueueItem, AgentStatusChip, MetricTile, StaleDataBadge, HeldQueueBanner

## Powiązane specy

- [D0.8 Risk Matrix](specs/D0.8-risk-matrix-sla.md)
- [D0.9 Approval + Escalation](specs/D0.9-approval-escalation.md)
- [D0.10 Audit Log](specs/D0.10-audit-log.md)
- [D0.11 Graduation](specs/D0.11-graduation.md)
- [D0.12 UI Language](specs/D0.12-ui-language.md)
- [D0.13 Authz](specs/D0.13-authz.md)
- [D0.14 Emergency](specs/D0.14-emergency.md)
- [D0.5 ADR Hosting](adr/D0.5-hosting-adr.md)
- [Workshop checklist](WORKSHOP-F0-CHECKLIST.md)
