---
status: "[SPEC]"
title: "VF-VHQ-FINAL-00 — Final Director Dashboard"
updated: "2026-07-31"
gate: "VF-VHQ-FINAL-00"
program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
supersedes_ui: "docs/superpowers/specs/2026-07-31-vhq-firm-ia-design.md §4.1–4.2 dual-axis floor tabrow"
cache_target: "vhq-w67a"
runtime_changes_allowed: true
approved_by: "Dowódca (plan approve 2026-07-31)"
---

# Design: VF-VHQ-FINAL-00

## 1. Problem

Director Decision Instrument (S1–S6+S8) and FIRM-IA are LIVE, but Founder still sees **chaotic duplicate navigation** (Firm Chain 1–4 + P0–P3/MAG) and thin rooms. “Finished dashboard” must mean **one home + one nav axis + honest rooms**, not fake Order Desk LIVE.

## 2. Goal

Cold-open VHQ ≤30s: money/risk/NBA/gaps; **only Firm Chain 1–4** as map filter; every room = Work View or Finish Card; Deliver honesty EV-W2-010; Console = Tools only.

## 3. Non-goals / STOP

- Order Desk LIVE / S7 fake PASS  
- 3D · Ads · Mollie · Gate D · 6th tab  
- COM-AI organic as this gate  
- Mega-diff all rooms + Growth in one session  
- Deploy without GO DEPLOY  

## 4. Supersedes (explicit)

| Prior | After FINAL |
|-------|-------------|
| FIRM-IA: keep Firm Chain **and** floor tabrow P0–P3/MAG | Floor IDs stay in `VHQ_ROOMS` data only; **UI filter = firmStage only** |
| DI S2: Esc room → MC → Console | Esc room → MC (stay HQ); Console = Tools |
| COM-AI as active_gate during FINAL | COM-AI parked (Growth lane) |

FIRM-IA CLOSE/DEPLOY remain historical DONE — do not rewrite.

## 5. Binary DoD (seal)

| ID | Pass when |
|----|-----------|
| F1 | Cold-open MC ≤30s: money/risk/NBA + gaps |
| F2 | Esc/Close never parents to Console |
| F7 | Visible nav = `#vhq-firm-chain` only; no `#vhq-floors` tablist; no dual Sterowanie |
| F3 | Every room: Work View or Finish Card fields |
| F4 | Deliver stage honest PARKED / EV-W2-010 |
| F5 | DI S1–S6+S8 regression; no fake S7 |
| F6 | Founder dogfood evidence + CLOSE |

## 6. Nav contract (F7)

```text
[ Virtual HQ · FlexGrafik ]     [ Tools / Sign in ]
1 Popyt | 2 Sprzedaż | 3 Realizacja | 4 Sterowanie
────────────────────────────────────────────────
Room tiles (firmStage)          | Work View / Finish Card
```

- MAG rooms under stage `deliver`  
- Breadcrumb: `HQ › {stage label} › {room}` — no P3/MAG jargon in chrome  

## 7. Finish Card fields

`status · evidenceId · owner · sot · limitation · firmRole · unlockHint`  
`lastVerified` may show `registry / not live-verified` when not runtime-fresh.

## 8. Waves

W0 SoT → W1 Nav One Axis → W2 Finish Cards → W3 MVP Work Views → W4 Founder seal (+ GO DEPLOY)

## 9. SoT hierarchy

Knowledge Index → `todo.json` → VHQ-PROGRAM → DI scorecard → this spec → plan → lanes appendix → handoffs
