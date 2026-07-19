---
status: "[ACTIVE]"
title: "Chat Trust Pack — deploy/verify CLOSE (jadzia host)"
gate: "INSPIRE-2026-07-19-chat-trust-pack"
updated: "2026-07-19"
result: "PASS"
---

# Chat Trust Pack — jadzia deploy CLOSE

Jadzia **nie** implementuje Trust Pack — hostuje `/opt/inspire` + bridge.

## DoD / evidence

| Check | Result |
|-------|--------|
| Local smoke `is_intent_request` + `label_for(bus_l)=Bestelbus L` | **PASS** |
| jadzia pytest orchestrator/inspire | **10 passed**, 8 skipped |
| Bridge `reply_nl` = `turn.reply_nl` (orchestrator) | **PASS** — no MA-/SKU builder in bridge |
| `deploy-jadzia.ps1` | **PASS** — inspire pytest 160 · VPS validate-brain ok · jadzia active · OpenRouter PASS |
| `DA_CHAT_ENGINE=orchestrator` + `INSPIRE_REPO_PATH=/opt/inspire` on VPS | **PASS** |
| VPS opening smoke | **PASS** — `OPENING_HAS_MA=False` |
| `dtp-design-agent.js` Cyber-Folks | **PASS** — 49012 bytes · LiteSpeed purge OK |

## Note

- Trust Pack source still **dirty/uncommitted** in `flexgrafik-inspire` at deploy time (upload from working tree).
- JS deploy script post-ssh had CRLF noise; file re-verified via clean scp+wc.

## Next

Meta pack (OPERATOR-TODAY #1–4) — osobny plan.
