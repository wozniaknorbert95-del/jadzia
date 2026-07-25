---
status: "[ACTIVE]"
title: "FREE-META-90 — darmowy potencjał Meta ≥90%"
updated: "2026-07-25 (F1–F3 LIVE · score 8/10 · S5/S9 HITL)"
gate: "META-FREE-90"
---

# FREE-META-90 — scorecard (SoT)

**Cel:** darmowy potencjał Meta ≥ **9/10 PASS**. Kampanie Ads dopiero po gate + GO.

**Źródła:** [FB-AUTOMATION-PLAYBOOK.md](./FB-AUTOMATION-PLAYBOOK.md) · [CHANNEL-MATRIX.md](./CHANNEL-MATRIX.md) · [SPEED-TO-LEAD.md](./SPEED-TO-LEAD.md) · [FB-TOKEN-ROTATION.md](../FB-TOKEN-ROTATION.md)

## Scorecard (1 pkt = PASS)

| # | Kryterium | Owner | Status | Evidence |
|---|-----------|-------|--------|----------|
| S1 | Page token + publish + `read_insights` | agent | **PASS** | OPS-FB-TOKEN-01 |
| S2 | Scope `pages_read_user_content` + fb-health | agent | **PASS** | App Add Ready · OAuth · `has_pages_read_user_content=true` · `Token OK (Page)` |
| S3 | DTL organic ok · Organic ER ≠ `—` | agent | **PASS** | `organic_er_baseline_30d=0.0` fact · ingest facts≥9 |
| S4 | Redact `access_token` w logach FB | agent | **PASS** | `_redact_secrets` LIVE na VPS |
| S5 | Messenger Away + menu NL (3 pozycje) | Dowódca HITL | **FAIL** | BS UI redirect; **checklist poniżej** |
| S6 | Page action button → Wizard lub Messenger | agent+verify | **PASS** | Page UI: **Wyślij wiadomość** LIVE |
| S7 | ≥2 realne posty NL w 14d | agent | **PASS** | posts `…959232…` + `…959244…` + UTM organic |
| S8 | ≥1 video/Reel + CTA UTM organic | agent | **PASS** | calendar entry 26 · Drive video · `utm_content=reel_a` |
| S9 | IG Pro ↔ Page + dual-publish | Dowódca HITL | **FAIL** | BS: **Powiąż z kontem na Instagramie** |
| S10 | SPEED-TO-LEAD organic (log lub ćwiczenie) | agent | **PASS** | ćwiczenie 2026-07-25T06:15Z — patrz CLOSE |

**Score LIVE 2026-07-25:** **8/10 (80%)** — gate ≥9 **nie** met.  
**Do 9/10:** PASS **S5** (Away+menu) **lub** **S9** (IG dual) — ~15 min HITL.

**Baseline F0:** 1/10.

## PARK (nie w mianowniku)

Ads / Instant Form · Ads API create · L0 Purchase · ManyChat/Tor B · TikTok · Grupa FB

## HITL leftover (do gate)

### S5 — Messenger Away + menu (~10 min)
1. Meta Business Suite → Skrzynka → Ustawienia → Automatyczne odpowiedzi.  
2. Away ON (NL): np. *Bedankt voor je bericht. We reageren <15 min in werktijd. Wizard: …utm_medium=organic…*  
3. Menu: Wizard · Offerte · WhatsApp `+31 6 87286151`.

### S9 — IG (~5–15 min)
1. BS → **Powiąż z kontem na Instagramie**.  
2. Dual-publish 1 asset (BS) albo FB+IG + nota w kalendarzu.

## Hard STOP

Bez Ads create · bez Mollie LIVE · bez fake PASS · deploy tylko ze GO.
