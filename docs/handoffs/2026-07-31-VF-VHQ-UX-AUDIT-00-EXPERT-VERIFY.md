---
status: "[VERIFY+EXPERT]"
title: "VF-VHQ-UX-AUDIT-00 — post-deploy verify + expert ops-console analysis"
updated: "2026-07-31"
gate: "VF-VHQ-UX-AUDIT-00"
surface: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w61a"
prod_tip: "889f538"
feature_tip: "a49644c"
cache: "vhq-w61a"
verdict_ux_gates: "Pass"
verdict_mission_maturity: "Conditional — SNR + incomplete commercial loop"
evidence: "docs/handoffs/evidence-vhq-ux-audit-prod/"
---

# Post-deploy verify + expert analysis

## 1. Fresh verification (evidence-first)

| Check | Evidence | Result |
|-------|----------|--------|
| VPS tip | `889f538` · jadzia **active** | OK |
| Worker | healthy · loop alive · `ssh_connection=ok` | OK |
| Assets | `vhq-w61a` ×3 in HTML · `vhqNeedsHomeData` in app.js | OK |
| Cold-open MC rail | summary ops live · **prio 3 · queue 22** · not `Ładowanie ops…` | **F1 PASS** |
| Network | `/priorities/today` + `/queue` **200** · no 5xx | PASS |
| Vault CTA | **Open Vault** → `vhq=approval-vault` | **F2 PASS** |
| Console | only verbose password-form (allowlist) · no apple-meta warn | **F3 PASS** |
| Esc ladder | Vault → Esc → MC → Esc → `vhq=console` | PASS |
| Order Desk | **PARKED · EV-W2-010** · no fake LIVE | PASS |
| Marketing | **UNVERIFIED · EV-W3-001** · observe-only | PASS |
| Vault pending | 1× **L3/pending** + **L3 STOP** · **0 Approve** (honest) | PASS |
| Viewports | 1024: rail OK · no overflowX · mobile ~375–500: rail OK · LH a11y **100** | PASS |
| Q1–Q7 surface signals | risk/decision/vault/dept/gaps/next-action all present on MC | PASS |

Mobile evidence: `evidence-vhq-ux-audit-prod/ux-verify-12-mobile-mc.png`.

**UX hard-gate verdict after deploy: Pass.**  
(Audit REPORT Phase A Conditional Pass superseded by deploy + this verify.)

---

## 2. Expert lens — ops / control-plane / virtual HQ

Ocena jak dla systemów typu **mission control / SOC-lite / AI-ops console** (nie landing page, nie CRM).

### Co jest dojrzałe (industry-grade honesty)

1. **Trust calibration** — statusy LIVE / PARTIAL / UNVERIFIED / PARKED z evidence ID. To rzadkie i poprawne; większość „AI HQ” kłamie kolorem.
2. **Approval ladder** — L3 STOP bez przycisku Approve przy `approval_needed · L3/pending` = brak mode error „kliknij i leci deploy/Ads”. Zgodne z modelami L0–L4.
3. **Escape integrity** — teleport + Esc ladder + Sign in / Operations Console. Krytyczne przy time pressure; tu działa.
4. **Work View > décor** — MC to Decision Rail + pulse + flow break (Order PARKED). Nie symulacja 3D jako substytut kontroli.
5. **Fail-closed UI** — Order / Marketing / Finance nie udają desków. Program §1 „without guessing” w warstwie *honest gaps* jest spełniony.

### Co blokuje „fully fulfills its job” (nie hard UX gate, ale mission maturity)

| # | Problem | Klasa | Dlaczego boli Directora |
|---|---------|-------|-------------------------|
| E1 | **CEO stub** × wiele wpisów CRITICAL w priorities + queue | **Signal-to-noise** | OODA pęka: Q3 „what needs my decision” tonie w szumie. System wygląda na „always on fire”. |
| E2 | Freshness/GA4 **red** stale na każdym cold-open | **Alarm fatigue** | Prawdziwy sygnał ryzyka miesza się z chronicznym chipem. |
| E3 | Vault strip „pending 1” = wyłącznie L3 STOP | **Control affordance clarity** | Honest, ale Director może pomyśleć „nie mogę nic zatwierdzić” bez czytania L3 copy — OK jeśli copy zostaje widoczna (dziś jest). |
| E4 | Commercial loop **Sales→Wizard→Order break** | **Incomplete value chain** | Understand OK; *improve company cash loop* nie — świadomie PARKED (EV-W2-010). |
| E5 | Brak LCP/INP trace w oryginalnym audycie | **Perf gap (minor)** | Nie blokuje; na MC po deploy subiektywnie snappy. |

### Scorecard vs Program §1 + ARCH

| Facet | Post-deploy |
|-------|-------------|
| Understand ≤30s **with interaction** | **PASS** — rail ładuje się; Q-loop sygnały na MC |
| Control L1/L2 | **PASS z zastrzeżeniem** — L1 dispositions na queue; L2 path istnieje; aktualny pending = L3 STOP (poprawne) |
| Improve without guessing | **PASS honesty / FAIL completeness** — gaps labeled; Order nie LIVE |
| ARCH UX principles 1–7 | **PASS** (teleport, one-question rooms, honest status, phone MC, no 6th tab) |

**Ekspercki werdykt misji:**  
VHQ jest już **wiarygodnym command surface** (trust + escape + rail).  
Nie jest jeszcze **wysokiej jakości decision instrument** — SNR (E1/E2) obniża wartość pod time pressure bardziej niż brak 3D.

---

## 3. Recommended next (1 path)

**Nie** otwierać 3D / Order LIVE / MKT.  
**Tak** — osobny mały gate **P2-SNR-00** (tylko jeśli Founder GO):  
1) stłumić / schować CEO stub z CRITICAL surface albo oznaczyć `STUB` poza Decision Rail,  
2) degenerować chroniczne freshness red do secondary chrome,  
3) zostawić EV-W2-010 honesty.

Bez GO: **idle** — audyt UX zamknięty Pass.

---

## 4. Audit closure stamp

| Artefakt | Status |
|----------|--------|
| Phase A REPORT | supersede verdict → Pass (see §1) |
| Phase B fix + deploy | DONE `a49644c` / `vhq-w61a` |
| Prod re-walk + viewport gap fill | DONE this doc |
| P2/P3 backlog | parked (E1/E2 = next value) |
| 3D / MKT / Order LIVE | still parked |
