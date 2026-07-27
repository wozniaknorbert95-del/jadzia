---
status: "[CLOSED]"
title: "FREE-META-90 — darmowy potencjał Meta ≥90%"
updated: "2026-07-26 (CLOSED 9/10 · IG removed · next = FREE-TIKTOK)"
gate: "META-FREE-90"
---

# FREE-META-90 — scorecard (SoT) — **CLOSED**

**Cel:** darmowy potencjał Meta ≥ **9/10 PASS**.  
**Wynik:** **9/10 PASS** — gate **CLOSED** 2026-07-26.  
**Prod tip (przy close):** VPS **`92da711`**.

**Następny kanał organiczny:** [FREE-TIKTOK.md](./FREE-TIKTOK.md) (nie Instagram).

**Źródła:** [FB-AUTOMATION-PLAYBOOK.md](./FB-AUTOMATION-PLAYBOOK.md) · [CHANNEL-MATRIX.md](./CHANNEL-MATRIX.md) · [SPEED-TO-LEAD.md](./SPEED-TO-LEAD.md) · [FB-TOKEN-ROTATION.md](../FB-TOKEN-ROTATION.md)

## Scorecard (1 pkt = PASS)

| # | Kryterium | Owner | Status | Evidence |
|---|-----------|-------|--------|----------|
| S1 | Page token + publish + `read_insights` | agent | **PASS** | OPS-FB-TOKEN-01 |
| S2 | Scope `pages_read_user_content` + fb-health | agent | **PASS** | `has_pages_read_user_content=true` · `Token OK (Page)` |
| S3 | DTL organic ok · Organic ER ≠ `—` | agent | **PASS** | `organic_er_baseline_30d` fact |
| S4 | Redact `access_token` w logach FB | agent | **PASS** | `_redact_secrets` LIVE |
| S5 | Messenger Away + menu NL (3 pozycje) | Dowódca+agent | **PASS** | Away `1271421616051451` + IR `1271432256050387` · NL CTAs |
| S6 | Page action button → Wizard lub Messenger | agent+verify | **PASS** | **Wyślij wiadomość** LIVE |
| S7 | ≥2 realne posty NL w 14d | agent | **PASS** | posts + UTM organic |
| S8 | ≥1 video/Reel + CTA UTM organic | agent | **PASS** | calendar · `utm_content=reel_a` |
| S9 | ~~IG Pro ↔ Page~~ | — | **N/A** | **Brak Instagram** — usunięte z planu 2026-07-26 (nie FAIL, poza mianownikiem) |
| S10 | SPEED-TO-LEAD organic | agent | **PASS** | ćwiczenie 2026-07-25 |

**Score LIVE (closed):** **9/10 (90%)** w mianowniku S1–S8+S10. S9 nie liczy się (N/A).  
**Baseline F0:** 1/10.

## PARK (nie w mianowniku)

Ads / Instant Form · Ads API create · L0 Purchase · ManyChat/Tor B · Grupa FB · Graph `persistent_menu` (brak `pages_messaging`) · **Instagram (out of scope)**

## Closeout note 2026-07-26

- Nie budujemy IG. Nie czekamy na Meta 10/10 przez Instagram.  
- TikTok = osobny gate [FREE-TIKTOK.md](./FREE-TIKTOK.md).  
- Kampanie Meta: tylko po Dowódca **„final”** → [META-CLICK-PATH.md](./META-CLICK-PATH.md).

## Hard STOP

Bez Ads create · bez Mollie LIVE · bez fake PASS · deploy tylko ze GO.
