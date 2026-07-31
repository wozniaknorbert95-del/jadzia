---
status: "[ACTIVE — agent prep · ready_for_human]"
gate: "COM-AI-50-READY"
updated: "2026-07-31"
applies_from: "2026-08-02"
legal: "Kontrolki operacyjne — nie porada prawna. Founder + doradca NL/EU."
blast: "docs/handoffs/2026-07-31-COM-AI-50-READY-BLAST.md"
---

# COM-AI-50-READY — pack (SoT poza MKT/)

**Cel:** dependency przed organic publish ≥2026-08-02 + public Concierge/widget AI.  
**Nie blokuje:** shoot-plan docs · VHQ idle · Ads freeze (osobno do 2026-08-06).

## 1. Inventory — public AI surfaces (agent 2026-07-31)

| Surface | System / path | Customer-facing? | Disclosure today |
|---------|---------------|------------------|------------------|
| Widget chat | `POST /api/v1/widget/chat` → `agent/customer_agent.py` (Claude) | YES (public) | **MISSING** in API/UI response — prompt admits AI only server-side |
| Design Agent offerte | `api/routes/design_agent_offerte.py` | YES (if exposed) | **UNVERIFIED** — treat as AI until checked at publish |
| Commander / VHQ | `commander-ui` | NO (operator HITL) | N/A for Art.50 public path |
| Telegram WP agent | `api/telegram.py` → COI | Internal ops | N/A public |
| MKT 2026-W31 video | Human shoot plans | Organic later | Captions/edit may be AI-assisted → disclose if used |
| MKT images | No AI bus image as master | — | STOP synthetic masters |

## 2. Proposed interactive disclosure (NL)

> Je chat met een AI-assistent van FlexGrafik. Wil je een mens? Laat het weten — we nemen over.

**Handoff path:** user asks for human → Dowódca via Telegram / WhatsApp (SPEED-TO-LEAD manual).  
**Founder decision:** ACCEPT / EDIT copy before widget UI/API ships disclosure.

## 3. Claims / deepfake STOP

- No synthetic „client” faces as testimonials  
- No fake before/after — real footage only  
- Reviewer = Dowódca before any publish GO  

## 4. Marking / metadata (process stub)

| Step | Owner | Status |
|------|-------|--------|
| Decide when media is AI-generated vs AI-assisted vs none | Founder + counsel | **PARKED** |
| Record `ai_disclosure` on Asset Card | Marketing ops | Template exists in Campus PROGRAM asset contract |
| Machine-readable marking (KE Art.50) | Counsel | **UNVERIFIED** — escalate |

## 5. Evidence pack (fill at publish ≥2026-08-02)

- [ ] Screenshot of live disclosure (widget first message / chrome)
- [ ] Copy version + timestamp
- [ ] Model/provider if AI-assisted captions/edit (no secrets)
- [ ] Human approval name + timestamp
- [ ] Counsel note if obtained (optional path)

## 6. Agent vs human

| Item | Agent | Human |
|------|-------|-------|
| Inventory + this pack | DONE (this doc) | Review |
| Accept NL disclosure | — | **REQUIRED** |
| Counsel schedule before week-of publish | — | **REQUIRED if publishing** |
| Widget UI/API disclosure ship | Only after Founder accept + separate GO | Approve |
| Organic publish | — | Separate GO ≥2026-08-02 |

## 7. Decision log

| When | Who | Decision |
|------|-----|----------|
| 2026-07-31 | Founder | GO prep COM-AI-50 after FIRM-IA (this BLAST) |
| _pending_ | Founder | Accept / edit disclosure copy |
| _pending_ | Founder | Counsel Y/N before first organic ≥2026-08-02 |
