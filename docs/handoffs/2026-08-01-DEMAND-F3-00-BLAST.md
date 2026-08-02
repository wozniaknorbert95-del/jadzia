---
status: "[BLAST · CLOSED LOCAL]"
title: "DEMAND-F3-00 — TT/FB connectors (allowlist + anti-spam)"
updated: "2026-08-01"
gate: "DEMAND-OS-F3-00"
todo: DOS-F3-01
founder_go: "GO BUILD demand-f3 (Dowódca: Go 2026-08-01)"
runtime_changes_allowed: false
deploy_vps: false
---

# BLAST — DEMAND-F3-00

## Potrzeba

F2 pilnuje **co** wolno opublikować. F3 pilnuje **gdzie** wolno czytać/komentować.

| Amatorskie | Profesjonalne |
|------------|---------------|
| Hardcoded grupa / spam 20× | Allowlist JSON · max 5 grup · HITL fill |
| Live Graph bez dry-run | Transport: mock smoke + live tylko gdy skonfig + explicit |
| Ten sam copy wszędzie | Anti-spam fingerprint · ≤1 grupa / copy / dzień |
| Comment bez Val | Wizard CTA w comment → F2 Validator |

## Binary DoD

| # | DoD | Pass when |
|---|-----|-----------|
| D1 | ALLOWLIST.json | own_page + tt_own active · ≤5 group slots |
| D2 | enforce allowlist | unknown / pending_fill = DENY |
| D3 | anti-spam | same copy → 2nd group = FAIL |
| D4 | read smoke | 1 read allowlisted target OK |
| D5 | comment smoke | 1 comment dry-run OK (+ Val jeśli UTM) |
| D6 | pytest | green; F1/F2 still green |

## STOP

Mass comment · Ads · VPS · publish bypass F2 gate · Wave2 15 agents
