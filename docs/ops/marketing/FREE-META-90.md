---
status: "[ACTIVE]"
title: "FREE-META-90 — darmowy potencjał Meta ≥90%"
updated: "2026-07-25 (gate ≥9/10 PASS · tip 92da711 · S5 Away+IR ON)"
gate: "META-FREE-90"
---

# FREE-META-90 — scorecard (SoT)

**Cel:** darmowy potencjał Meta ≥ **9/10 PASS**. Kampanie Ads dopiero po gate + GO.  
**Prod tip:** VPS **`92da711`** (feature `d004900`).

**Źródła:** [FB-AUTOMATION-PLAYBOOK.md](./FB-AUTOMATION-PLAYBOOK.md) · [CHANNEL-MATRIX.md](./CHANNEL-MATRIX.md) · [SPEED-TO-LEAD.md](./SPEED-TO-LEAD.md) · [FB-TOKEN-ROTATION.md](../FB-TOKEN-ROTATION.md)

## Scorecard (1 pkt = PASS)

| # | Kryterium | Owner | Status | Evidence |
|---|-----------|-------|--------|----------|
| S1 | Page token + publish + `read_insights` | agent | **PASS** | OPS-FB-TOKEN-01 |
| S2 | Scope `pages_read_user_content` + fb-health | agent | **PASS** | App Add Ready · OAuth · `has_pages_read_user_content=true` · `Token OK (Page)` |
| S3 | DTL organic ok · Organic ER ≠ `—` | agent | **PASS** | `organic_er_baseline_30d=0.0` fact · ingest facts≥9 |
| S4 | Redact `access_token` w logach FB | agent | **PASS** | `_redact_secrets` LIVE na VPS |
| S5 | Messenger Away + menu NL (3 pozycje) | Dowódca+agent | **PASS** | BS: **Wiadomość o nieobecności Wł.** (id `1271421616051451`) + **Automatyczna odpowiedź Wł.** (id `1271432256050387`) · NL CTAs Wizard / Offerte / WA +31 6 87286151 · Zapisz HITL 2026-07-25 |
| S6 | Page action button → Wizard lub Messenger | agent+verify | **PASS** | Page UI: **Wyślij wiadomość** LIVE |
| S7 | ≥2 realne posty NL w 14d | agent | **PASS** | posts `…959232…` + `…959244…` + UTM organic |
| S8 | ≥1 video/Reel + CTA UTM organic | agent | **PASS** | calendar entry 26 · Drive video · `utm_content=reel_a` |
| S9 | IG Pro ↔ Page + dual-publish | Dowódca HITL | **FAIL** | BS: **Powiąż z kontem na Instagramie** (poza gate ≥9) |
| S10 | SPEED-TO-LEAD organic (log lub ćwiczenie) | agent | **PASS** | ćwiczenie 2026-07-25T06:15Z — patrz CLOSE |

**Score LIVE 2026-07-25:** **9/10 (90%)** — gate ≥9 **PASS**.  
**Leftover Low:** S9 IG dual · Graph `persistent_menu` (brak scope `pages_messaging`; BS bez szablonu menu 2026-07).

**Baseline F0:** 1/10.

## PARK (nie w mianowniku)

Ads / Instant Form · Ads API create · L0 Purchase · ManyChat/Tor B · TikTok · Grupa FB · Graph persistent_menu (scope) · S9 IG

## HITL leftover (po gate)

### S9 — IG (~5–15 min) — opcjonalnie
1. BS → **Powiąż z kontem na Instagramie**.  
2. Dual-publish 1 asset (BS) albo FB+IG + nota w kalendarzu.

## Hard STOP

Bez Ads create · bez Mollie LIVE · bez fake PASS · deploy tylko ze GO.  
**Kampanie (`META-CLICK-PATH`):** tylko gdy Dowódca powie **„final”**.
