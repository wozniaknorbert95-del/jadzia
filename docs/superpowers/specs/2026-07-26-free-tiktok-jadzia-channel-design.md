---
status: "[ACTIVE]"
title: "FREE-TIKTOK — Jadzia channel (thin gate → FB-parity publisher)"
updated: "2026-07-26"
gate: "FREE-TIKTOK"
---

# Design: TikTok as Jadzia distribution channel

## Intent

TikTok (`@flexgrafik.nl`) is the **next organic distribution surface**, managed by Jadzia the same way Facebook organic is managed: Asset Factory → propose/HITL → publish → measure → SPEED-TO-LEAD.  
**Instagram is out of scope forever** for this OS (no account → no S9 IG → do not build dual-publish Meta).

Principles: max effect / min complexity (Google/IBM). One gate. One publisher path. No shadow stacks (n8n/CrewAI/RPA farms) unless a later gate explicitly opens them.

## Non-goals (HARD PARK)

| Inspiration node | Verdict | Why |
|------------------|---------|-----|
| Trend scraper + Whisper + vector DB | **PARK** | No lead ROI; anti-ToS scrape risk; LLM hook patterns already in Asset Factory notes |
| Autonomous Content Factory (HeyGen/ElevenLabs auto-post) | **PARK** | Brand/quality risk; Jadzia already has master Reel pipeline |
| RPA / Appium / ADB DM farms | **PARK** | Shadowban + account loss; no public DM API; L1 stays WA/Messenger |
| Native Lead Ads TikTok | **PARK** until paid TikTok GO | Paid surface — separate from free organic gate |
| Fake Meta 10/10 via IG | **FORBIDDEN** | No IG |

## LIVE evidence (browser 2026-07-26) — no guesswork

Verified on logged-in session `@flexgrafik.nl`:

- **TikTok Studio** exists and is the real web control plane: Upload, Posts, Analytics, Comments, Inspiration, Monetization.  
- Profile **Edit profile (web)** fields only: Username, Name, Bio (80 chars) — **no Website field**.  
- Bio EN, 72/80 — no room for full Wizard URL without rewrite.  
- Catalog already has **≥12 videos**; last **7d analytics**: 20 views (−92.6%), FYP 86.7%.  
- Existing CTA pattern: creator **first comment** with `https://zzpackage.flexgrafik.nl/` (missing UTM).  
- Therefore T1 ≠ „set bio website” alone; T1 = **measurable Wizard+UTM** (primary: first comment / caption on new post).  
- T2 ≠ first-ever video; T2 = **one new** NL clip with UTM CTA.

## Must-have (NOW) — system first

Mirror the **FB organic spine** in code. **Do not** treat Studio browser upload as the product.

1. **TT-PUB-01** — `agent/publishers/tiktok.py` + calendar `platform=tiktok` + Commander publish (same spine as FB).  
2. **Env** — `TIKTOK_ACCESS_TOKEN` on VPS + verified media URL domain (Developer console).  
3. **E2E** — one approved calendar video entry → `tiktok_post_id`.  
4. **CHANNEL-MATRIX** — master → `tt_hook` · `utm_source=tiktok` (ops caption/comment after system path works).  
5. **SoT** — FREE-META closed 9/10; **no IG**; FREE-TIKTOK tracks system scorecard.

## Should-have (NEXT — after TT-PUB live)

| Phase | Deliverable | Jadzia shape (like FB) |
|-------|-------------|------------------------|
| **TT-INS-01** | Video list/detail metrics → DTL fact | Like FB insights ingest |
| **TT-CMT-01** | Comment webhook → LLM draft reply → Wizard UTM CTA | Like Messenger propose — **not** auto-DM |
| Ops UTM | First-comment / caption UTM on published clips | Studio leftover OK only as backup |

## Must-not confuse with L1

- TikTok **DM automation = never** in free/MVP stack (no public API; RPA banned).  
- Conversion path: **bio → Wizard** (+ WA SPEED-TO-LEAD). Same as Meta organic CTA discipline.

## Architecture (target, still lean)

```
Asset Factory (MKT/YYYY-WW/)
    → tt_hook_15s.mp4 + NOTES.md (UTM)
    → Marketing Brain propose (existing)
    → HITL Approve
    → Publisher TikTok (HITL now → API later)
    → DTL / weekly scorecard (views + wizard_starts utm=tiktok)
    → Lead → WA <15m (SPEED-TO-LEAD)
```

No second orchestration bus. No Pinecone. No phone farm.

## FREE-TIKTOK scorecard (denominator = 3)

| # | Criterion | Owner | PASS evidence |
|---|-----------|-------|---------------|
| T1 | Bio link → Wizard + UTM | agent+HITL | URL visible on profile |
| T2 | ≥1 NL clip on `@flexgrafik.nl` | agent+HITL | permalink |
| T3 | Calendar note (tiktok organic + WW) | agent | Commander/calendar entry |

**Gate PASS = 3/3.** Cadence 2–3/week is ops after PASS, not part of denominator.

## FREE-META closure rule

- Score stays **9/10 PASS**.  
- Former S9 IG → **N/A (no IG)** — removed from leftover and closeout plans.  
- Do not invent a 10th Meta point for TikTok (separate gate).

## Hard STOP

TikTok Developer auto-approve without Dowódca GO · RPA DM · Ads without **„final”** (Meta) · Mollie LIVE · secrets in repo · fake PASS · VPS deploy without GO.

## Success

OPERATOR reads: Meta organic DONE @ 9/10 · TikTok FREE gate active/PASS · next = TT-PUB-01 or Meta **„final”**. Zero IG mentions in active plans.
