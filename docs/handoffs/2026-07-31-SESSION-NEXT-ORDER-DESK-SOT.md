---
status: "[SESSION BRIEF · NEXT]"
title: "Next session — agency pack after FINAL seal"
updated: "2026-07-31"
verify: "docs/handoffs/2026-07-31-VERIFY-VHQ-FINAL-00-POSTDEPLOY.md"
primary_gate: "VF-ORDER-DESK-SOT-00"
parallel_hitl: "COM-AI-50-READY (ACCEPT copy)"
---

# Next session — FlexGrafik agency brief

## 0. Baseline (verified)

- VHQ FINAL **DEPLOY + VERIFY PASS** · `vhq-w67a` · seal `FINISHED_PARTIAL_LOOP`
- Nav F7 OK · Esc HQ OK · Order Desk still PARKED (correct)
- Prod: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w67a

## 1. Mission (1-1-1)

**Primary:** `VF-ORDER-DESK-SOT-00` — discovery SoT for Order Desk (docs only).  
**Why:** Dashboard is done; company still breaks at Deliver. Without SoT, every UI is lipstick.

**Parallel HITL (Dowódca, 10 min):** ACCEPT/EDIT NL disclosure in `docs/ops/marketing/COM-AI-50-READY-PACK.md` + counsel Y/N — **no organic before 2026-08-02**.

## 2. Squad (RACI)

| Role | Who | R |
|------|-----|---|
| Product / SoT architect | Agent | Lifecycle + field dict |
| Data / INT-002 analyst | Agent | Inventory `orders` + bus |
| HQ UX thin contract | Agent | Read-only Work View sketch |
| Compliance / Growth | Dowódca | COM-AI ACCEPT |
| Approver | **Dowódca** | D1–D5 accept |
| Deploy | — | **none this session** |

## 3. Agenda (ADHD)

1. `/vibe-init` → tip `vhq-w67a` · Conflicts 0 if VCMS  
2. Read VERIFY + this brief + Order Desk discovery spec  
3. Execute plan Tasks 0–3 (docs)  
4. Founder 20 min review  
5. CLOSE discovery · propose `VF-ORDER-DESK-WV-00` only if ACCEPT  

## 4. STOP

Order LIVE · fake S7 · Mollie · Ads · reopen FINAL nav · stage `MKT/` · mega fulfilment build

## 5. Definition of done (next session)

- [x] SoT pack D1–D5 drafted (`docs/ops/ORDER-DESK-SOT-v0.md`)  
- [ ] Founder decision logged  
- [x] todo tip synced · active_gate cleared · `ready_for_human` awaiting ACCEPT  
- [ ] COM-AI decision logged if Dowódca had time  

## 6. Artifacts

| Doc | Path |
|-----|------|
| Spec | `docs/superpowers/specs/2026-07-31-order-desk-sot-discovery-design.md` |
| Plan | `docs/superpowers/plans/2026-07-31-order-desk-sot-discovery.md` |
| VERIFY | `docs/handoffs/2026-07-31-VERIFY-VHQ-FINAL-00-POSTDEPLOY.md` |
| COM-AI pack | `docs/ops/marketing/COM-AI-50-READY-PACK.md` |
