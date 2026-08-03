---
status: SUPERSEDED
branch: tool-integrity-seal
date: 2026-08-03
gate: DEMAND-OS-MARKETING-4-00
next_item: 4-TOOL-01
superseded_by: docs/handoffs/2026-08-03-DEMAND-OS-TOOL-FIRST-DIRECTION-CORRECTION.md
---

# Handoff — 4-P0-01 HITL Ready (**SUPERSEDED — do not follow**)

> **STALE:** Dowódca 2026-08-03 — tool 100% first; live publish PARKED.  
> See `TOOL-FIRST-DIRECTION-CORRECTION` + `.cursor/rules/demand-os-tool-first.mdc`.

## What Was Done

- Executed owner verify pack from `OWNER-VERIFY-COMMANDS.md` before any action
- Reconfirmed TT packet gates for `tt_w32_install_01`
- Caption reviewed: single Wizard CTA only (`cap_tt_w32_01.txt`)
- Parked `4-P0-01` as `ready_for_human` in `MASTER-TODO-4.md` / `STATE.md` / `.cursor/current-task.md`
- Did **not** publish, deploy, run Ads, or write a fake LEDGER row

## Verification (this session)

| Check | Result |
|-------|--------|
| `python tools/demand_os_hub.py doctor` | `ok: true` · `marketing: HITL_LIVE` |
| `go_day_ready` | `score: 100.0` · `ok: true` |
| local `marketing_hitl_gate` | `BLOCKED` (no local `DEMAND_OS_MARKETING_HITL=GO`; prod READY per GO EXEC-CLOSE) |
| `pytest tests -k demand_os -q` | `102 passed, 832 deselected` |
| `demand_os_f2.py gate --asset-id tt_w32_install_01` | `GATE ALLOW` |
| Calendar slot | `validated` · pass_token `val_0c4b38ca481f09dd1bb4` |
| LEDGER row `tt_w32_install_01` | **absent** (correct until REAL publish) |

## HITL checklist (Dowódca — only remaining work)

1. Creative: W32 witte bus — **nie** republish deleted `tt_w31_install_01`
2. Caption (copy exact):

```text
Opdrachtgevers zien je bus vóór ze bellen.

Witte bus = anoniem.
Branding = herkenbaar voor de installateur.

Start in de Wizard (2 min):
https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic&utm_campaign=icp_installateur&utm_content=tt_w32_install_01

#installateur #zzp #bedrijfsbus #voertuigbelettering
```

3. Publish organic on TikTok (HITL) · no boost
4. Send agent: TikTok `video/<id>` or public URL + publish timestamp

## Ledger template (agent appends AFTER real publish only)

```csv
2026-08-03,tiktok,installateur,tt_w32_install_01,https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic&utm_campaign=icp_installateur&utm_content=tt_w32_install_01,Y,0,0,0,0,4-P0-01 HITL LIVE · video/<ID>
```

Also bump calendar status `validated` → `published` when closing.

## What Is Left

1. Founder HITL publish `tt_w32_install_01`
2. Agent: append LEDGER + update calendar + mark `4-P0-01` `done` + CLOSE handoff
3. Separately (not bundled): `4-P0-02` FB hunt · `4-P0-03` blog

## Critical Warnings

- No autonomous publish from this branch
- No Ads / boost / paid spend
- No VPS deploy
- No fake ledger evidence
- Local disk has only `assets/tt-upload/tt_w31_install_01.mp4` — do **not** treat as W32 publish proof

## Next Step

Dowódca publishes TT; reply with video id. Agent closes ledger + handoff.

```text
DONE: [4-P0-01 owner verify PASS; gate ALLOW; caption CTA-ok; SoT ready_for_human; no fake ledger]
LEFT: [Founder HITL TT publish tt_w32_install_01; then agent ledger+CLOSE; then 4-P0-02 separately]
RISKS: [Local gate BLOCKED without env GO — expected; creative path for W32 not in repo assets/]
V-FILES: [docs/ops/demand-os/4-P0-01-TT-HITL-EXECUTION-PACKET.md | docs/ops/demand-os/MASTER-TODO-4.md | docs/ops/demand-os/set-now/cap_tt_w32_01.txt | docs/ops/demand-os/set-now/LEDGER.csv]
NEXT_COMMAND_FOR_NEW_AGENT: [@blast 4-TOOL-01 · TOOL FIRST · this handoff SUPERSEDED]

---
CURRENT_STAGE: SUPERSEDED
RECOMMENDED_NEXT: @blast 4-TOOL-01
WHY_NEXT: SUPERSEDED — do not Founder-publish; tool 100% first.
---
```
