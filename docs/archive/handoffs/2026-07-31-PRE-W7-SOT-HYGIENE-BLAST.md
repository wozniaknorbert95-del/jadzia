---
status: "[BLAST]"
title: "PRE-W7-SOT-HYGIENE — F1–F6 tip/gate/PROGRAM/ARCH"
updated: "2026-07-31"
gate: "PRE-W7-SOT-HYGIENE"
baseline_tip: "da1b2d6"
runtime_commit: "06212d7"
cache_asset: "vhq-w60a"
runtime_changes_allowed: false
source: "docs/handoffs/2026-07-31-PRE-W7-DEEP-VERIFY-REPORT.md"
---

# BLAST — PRE-W7-SOT-HYGIENE

## Intent

Close SoT drift from deep verify so W7 dogfood measures product, not docs noise.

## Scope (docs only)

| ID | Fix |
|----|-----|
| F1 | Tip sync steering → prod tip + runtime `06212d7` + `vhq-w60a` |
| F2 | `active_gate` honesty — not W7 while parked |
| F3 | W6 gate note CLOSED+DEPLOY (no “Deploy under GO”) |
| F4 | PROGRAM/ARCH frontmatter tip/runtime/cache |
| F5 | ARCH approval-vault primary = Ops Bus Vault Work View |
| F6 | PROGRAM: Vault path DEPLOYED · maturity PARTIAL |
| S1 | Companion-only L2 documented (no code) |

## STOP

- No `commander-ui` / agent / API / pytest runtime  
- No jadzia restart (docs pull only)  
- No W7 unpark  
- No MKT / Order LIVE / Ads / Mollie / 3D  
- No historical W5 handoff rewrites  

## Exit

CLOSE stamped · tip match VPS · W7 remains parked until `GO VF-VHQ-W7-DOGFOOD`.
