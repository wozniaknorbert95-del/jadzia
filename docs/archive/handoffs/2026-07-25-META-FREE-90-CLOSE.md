# Handoff — META-FREE-90 (GATE ≥9/10 CLOSE)

**Date:** 2026-07-25  
**Status:** **SUCCESS** — **9/10 LIVE** @ tip **`92da711`** (feature `d004900`)  
**standing_go_closeout:** `false`  
**Kampanie Ads:** HOLD until Dowódca **„final”** (`META-CLICK-PATH`)  
**Session:** S5 Away + Instant Reply ON (HITL Zapisz)

## VERIFY

| Check | Result |
|-------|--------|
| Local / VPS tip | `92da711` |
| `jadzia` | active (prior VERIFY) |
| fb-health | PAGE · `has_read_insights=true` · `has_pages_read_user_content=true` · `Token OK (Page)` · scopes: posts/engagement/user_content/show_list/profile/read_insights (**no** `pages_messaging`) |
| parks | `l0_purchase`, `ads_api_create` only |
| Hard STOP | Ads create / Mollie / secrets — held |

## Scorecard

| PASS | FAIL / park |
|------|-------------|
| S1–S8, S10 | **S9** IG dual (Low leftover) |

**Gate ≥9/10:** **PASS (9/10)**.

## S5 evidence (BS Page FlexGrafik · asset `491325420727745`)

| Automation | Status | id |
|------------|--------|-----|
| Wiadomość o nieobecności (Away) | **Wł.** | `1271421616051451` |
| Automatyczna odpowiedź (Instant Reply) | **Wł.** | `1271432256050387` |

- Dowódca: HITL **Zapisz zmiany** confirmed 2026-07-25.  
- NL CTAs (menu Tor A): Wizard · Offerte · WhatsApp `+31 6 87286151`.  
- Graph `persistent_menu`: **park** — token scopes lack `pages_messaging`; BS Automations has **no** menu template (search „menu” → empty). Instant Reply + Away = free-Meta Messenger stack.

## LEFT (Low · poza gate)

1. **S9** — BS Powiąż Instagram + 1 dual-publish  
2. Graph `persistent_menu` — tylko po OAuth `pages_messaging` + GO  
3. Kampanie — dopiero **„final”**  
4. Mollie L0 Purchase — park  
5. Optional: Instant Reply copy polish if UI still shows PL default after Lexical race (Away ON is gate signal)

## RISKS / DON'T

- Nie Ads create/edit bez GO  
- Nie Mollie LIVE / fake Purchase  
- Nie loguj raw `access_token`  
- Nie traktuj S9 FAIL jako blocker gate (już ≥9)  
- Deploy VPS tylko ze świeżym GO

## NEXT

```text
STOP META-FREE-90 gate.
Kampanie: czekaj na Dowódca „final” → META-CLICK-PATH.
Opcjonalnie Low: S9 IG dual.
```

## V-FILES

- `docs/ops/marketing/FREE-META-90.md`
- `docs/handoffs/2026-07-25-META-FREE-90-CLOSE.md`
- `docs/ops/marketing/OPERATOR-TODAY.md`
- `todo.json`
