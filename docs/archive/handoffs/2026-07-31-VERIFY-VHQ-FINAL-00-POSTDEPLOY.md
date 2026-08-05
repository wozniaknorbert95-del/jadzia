---
status: "[VERIFY PASS]"
gate: "VF-VHQ-FINAL-00"
verified_at: "2026-07-31T13:49+02:00"
prod_url: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w67a"
vps_tip: "76788d9"
runtime_feature: "c870cbd"
cache: "vhq-w67a"
seal: "FINISHED_PARTIAL_LOOP"
---

# VERIFY — VF-VHQ-FINAL-00 post-deploy

## Control plane

| Check | Result |
|-------|--------|
| VPS `git HEAD` | `76788d9` |
| `systemctl jadzia` | **active** |
| `/health` | **ok** |
| `todo.active_gate` | `null` |
| `dashboard_seal` | `FINISHED_PARTIAL_LOOP` |
| pytest final+firm_ia | **17/17** |
| Dirty stage risk | MKT/ + SDD local only — **not staged** |

## Prod UI contracts

| Check | Result |
|-------|--------|
| HTTP 200 `?v=vhq-w67a` | PASS |
| `#vhq-floors` | **0** (absent) |
| `P3 Sterowanie` button | **0** |
| Firm Chain 1–4 | PASS |
| Finish Card + deliver honesty | PASS |
| Tools / Sign in | PASS |
| Chrome live: Esc home / chain | PASS |

## Verdict

**VERIFY PASS.** Dashboard seal holds. No reopen of FINAL unless regression.

## Tip note

`prod_tip` points feature CLOSE `c870cbd`; VPS HEAD may be docs tip `76788d9` ahead — expected.
