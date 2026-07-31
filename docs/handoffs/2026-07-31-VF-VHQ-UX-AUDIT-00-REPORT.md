---
status: "[REPORT]"
title: "VF-VHQ-UX-AUDIT-00 — Deep UX audit report"
updated: "2026-07-31"
gate: "VF-VHQ-UX-AUDIT-00"
persona: "Dowódca / Director — time pressure; phone+desktop; first-time lens"
surface: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a"
runtime_at_audit: "06212d7"
cache_at_audit: "vhq-w60a"
phase_b_cache: "vhq-w61a"
verdict: "Conditional Pass"
evidence_dir: "docs/handoffs/evidence-vhq-ux-audit/"
---

# VF-VHQ-UX-AUDIT-00 — REPORT

## Verdict

**Conditional Pass**

Phase A on prod `vhq-w60a` found **1 Critical + 2 High** that block Program §1 (“understand / control without guessing”) under real interaction. Phase B ships minimal UI fixes under `commander-ui/**` + cache **`vhq-w61a`**. Prod re-walk of fixed slices is **blocked until GO DEPLOY** (Zasada 11). Not a fake PASS on live tip.

## Preflight (T1)

| Gate | Result |
|------|--------|
| Persona locked | Dowódca / Director |
| Chrome DevTools | connected |
| Screenshot + console + network + selector | green |
| JWT session | `coi_commander_jwt` present; auth “Zalogowano” |
| Tip/cache note | runtime `06212d7` · cache `vhq-w60a` at audit |

## Interaction Manifest (T2)

Timestamps are local walk clock (gaps ≥0.5s between interactions).

| # | t | Action | Result |
|---|---|--------|--------|
| 1 | 0:00 | Cold-open `?v=vhq-w60a` | Lands `vhq=mc` Command View |
| 2 | 0:02 | Observe Decision Rail | **FAIL** — `Ładowanie ops…` stuck; `#priorities`/`#queue-list` empty; network has ops-bus only (no `/priorities/today` / `/queue`) |
| 3 | 0:08 | Click Focus priorities / Focus queue | Clickable; scroll targets exist (empty lists) |
| 4 | 0:12 | Click Agent Operations | Teleport Work View OK |
| 5 | 0:18 | Esc | Returns MC |
| 6 | 0:20 | Esc again | Operations Console (`vhq=console`); Sign in reachable |
| 7 | 0:28 | Open `vhq=approval-vault` | Pending cards + L2 path; PARTIAL honest |
| 8 | 0:40 | Open `vhq=order-desk` | **PARKED · EV-W2-010** honest; no fake LIVE |
| 9 | 0:50 | Open `vhq=wizard-quote` | Work View + primary action; no fake KPI |
| 10 | 1:00 | Open `vhq=sales-room` | Queue/disposition surface mounts |
| 11 | 1:10 | Open `vhq=ai-agent-health` | PARTIAL honest |
| 12 | 1:20 | Floor tab P1 Commercial | World view (`vhq=world`) |
| 13 | 1:30 | Viewport 375×812 cold-open | Same empty-rail Critical; shell usable |
| 14 | 1:40 | Console read | 1 warn: deprecated `apple-mobile-web-app-capable` |
| 15 | *lab* | `await loadHome()` in console | Rail populates — proves data path OK, boot race only |

Screenshots: `docs/handoffs/evidence-vhq-ux-audit/` (`ux-00` … `ux-09`).

## Hard gates (T3)

| Gate | Threshold | Result (prod w60a) |
|------|-----------|-------------------|
| Console errors | 0 | **PASS** |
| Console warnings | 0 reportable | **FAIL → High** (apple meta deprecated) |
| Network 5xx | 0 | **PASS** (sampled fetch 200) |
| Auth 403/404 unexpected | 0 | **PASS** |
| Layout collapse | 0 @ 375/1440 | **PASS** (no collapse; empty rail is content bug) |
| a11y (Lighthouse snapshot MC) | Critical/Serious 0 | **PASS** — Accessibility **100** |
| Perf budgets | pragmatic MC | Not blocking; LCP/CLS not traced this gate (LH snapshot excludes perf) |

Allowlist noise: Chrome verbose “Password field is not contained in a form” (not treated as High).

## Findings

| ID | Sev | Persona impact | Repro | Evidence | Suspected file | Phase B |
|----|-----|----------------|-------|----------|----------------|---------|
| F1 | **Critical** | Cold-open MC shows empty priorities/queue forever → Director cannot understand/control without guessing or console hack | Cold-open with JWT; wait ≥1.5s; rail stays `Ładowanie ops…`; no `/queue` network | `ux-00`, `ux-05`; evaluate `prio:0` | `commander-ui/app.js` (`refresh` skips home when `view-hq`; race with `vhqColdOpenMissionControl`) | **FIXED** — `vhqNeedsHomeData` + `loadHome` after MC/Sales mount + re-query after await |
| F2 | **High** | Vault strip copy says “Open Vault” but CTA is “Open Audyt” → wrong control path | MC vault strip CTA | snapshot uid `Open Audyt` next to vault copy | `index.html` `#vhq-open-audit` + bind in `app.js` | **FIXED** — `#vhq-open-vault` → `approval-vault` |
| F3 | **High** | Console warning hard-gate fail | Cold-open any route | console msgid warn apple meta | `index.html` | **FIXED** — add `mobile-web-app-capable` |
| F4 | Medium | CEO stub priorities dominate queue signal | After manual `loadHome` | walk after console fix | data / brain_bus (not UI lie) | **P2 backlog** — not Phase B |
| F5 | Medium | Freshness/GA4 red chips noisy under time pressure | MC after data load | rail chips | analytics freshness (honest) | **P2** — copy/priority UX later |
| F6 | Low | SEO LH 75 / agentic 0 | LH snapshot | temp report | meta/SEO | **P3** |
| F7 | Low | Password field outside form (verbose) | Console | console verbose | settings JWT input | **P3** |

## Ranked backlog

- **P0** F1 Decision Rail cold-open — **closed in tip `vhq-w61a`** (await GO DEPLOY for prod)
- **P1** F2 Vault CTA · F3 meta warn — **closed in tip**
- **P2** F4 stub-noise · F5 freshness chrome
- **P3** F6 SEO · F7 form verbose

## Program goal scorecard

| Facet | Audit |
|-------|--------|
| Understand ≤30s with interaction | **Blocked on cold-open** until F1 deploy (manual `loadHome` proves data) |
| Control L1/L2 | Vault/Sales paths present; strip CTA mismatch (F2) |
| Improve without guessing | Order PARKED / pins UNVERIFIED honest |
| ARCH principles | Teleport+Esc OK; phone MC first OK structurally; honest status OK |

## Phase B note

Cache bump **`vhq-w61a`**. Deploy **not** performed (needs exact `GO DEPLOY`).
