---
status: "[ACTIVE]"
title: "Marketing OS — FlexGrafik (rząd 20)"
gate: "MKT-OS-01"
updated: "2026-07-19"
---

# Marketing OS — FlexGrafik

Plan 1. rzędu = postuj / odpal ads / blog.  
**Ten OS = jeden bottleneck, jedna metryka sterująca, jedna pętla uczenia, 1 asset → N kanałów.**

## North Star

`CPA_wizard` (koszt paid → Purchase w Wizardzie) **&lt; 40% marży brutto** na typowym ZZPackage (korekta po 10 zakupach).

| Metryka | Rola |
|---------|------|
| CPA_wizard | Sterująca — scale / kill |
| Lead→Purchase % | Jakość lejka |
| CPL | Diagnostyka kreacji |
| Zasięg | Vanity bez Wizard — nie steruje |

**Bez Pixel/CAPI Purchase:** tylko learning ≤ €10/dzień na Leads — **zakaz scale**.

**Bottleneck (hipoteza):** zimny ruch → Purchase bez kwalifikacji → start = Leads + Speed-to-Lead, nie Traffic/Sales.

## Granice repo

| Powierzchnia | Repo | Rola |
|--------------|------|------|
| Control plane | **jadzia-core** (ten katalog + Commander) | HITL publish, scorecard, lead SLA, playbooki |
| Cash | **zzpackage** Wizard | Purchase = wygrany event |
| Intent SEO | **zzpackage** `docs/content/blog/` | Cluster → Wizard |
| QuietForge B2B | **services** only | Case po liczbach FG — zero QF w jadzia |
| Paid auction | Meta Ads Manager | Learning machine (Ads API = PARK) |
| Short-form | FB Reels + TikTok | Ten sam master asset |

## Mapa plików

| Plik | Treść |
|------|-------|
| [UNIT-ECONOMICS.md](./UNIT-ECONOMICS.md) | CPA, wzory, progi |
| [CHANNEL-MATRIX.md](./CHANNEL-MATRIX.md) | 1 asset → kanały + UTM |
| [FB-FIRST-CAMPAIGN.md](./FB-FIRST-CAMPAIGN.md) | Learning loop 14d Instant Form |
| [FB-AUTOMATION-PLAYBOOK.md](./FB-AUTOMATION-PLAYBOOK.md) | Tor A Business Suite; Tor B PARK |
| [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md) | Szablon PON |
| [TIKTOK-ORGANIC.md](./TIKTOK-ORGANIC.md) | Dystrybucja assetu (C1-01 PARK) |
| [ASSET-FACTORY.md](./ASSET-FACTORY.md) | 1 shoot → N cutów |
| [L0-INSTRUMENTATION.md](./L0-INSTRUMENTATION.md) | Pixel/CAPI + UTM verify |
| [SPEED-TO-LEAD.md](./SPEED-TO-LEAD.md) | SLA &lt;15 min; MKT-STL-01 trigger |

## Procesy (PROCESS-CATALOG)

- **P-MKT-01** — Publish HITL (LIVE)
- **P-MKT-02** — Auction learning loop
- **P-MKT-03** — Intent blog ZZP
- **P-MKT-04** — Asset Factory
- **P-MKT-05** — Speed-to-Lead

## PARK

Gate D, Mollie LIVE experiments, TikTok API (`C1-01`), Ads API / F4, QuietForge w jadzia, auto-publish, MBA regen.
