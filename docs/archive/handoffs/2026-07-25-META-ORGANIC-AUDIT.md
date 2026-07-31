# META / FB — weryfikacja planu + audyt potencjału darmowego

**Date:** 2026-07-25  
**Status:** **VERIFY PASS** (OPS-FB-TOKEN-01) · **ORGANIC GAP** (metrics)  
**standing_go_closeout:** `false`

## 1) Plan OPS-FB-TOKEN-01 — czy wszystko zrobione?

| DoD | LIVE 2026-07-25 re-check |
|-----|--------------------------|
| Page token + `expires_at=0` | **PASS** |
| `has_read_insights=true` · scopes incl. `read_insights` | **PASS** |
| `message_pl=Token OK (Page)` | **PASS** |
| Park `fb_read_insights` gone | **PASS** (parks: `l0_purchase`, `ads_api_create`) |
| Hard STOP: no Ads create / no hot_lead Confirm | **HELD** |
| Dogfood Start | `Ops: OK` · Marketing organic HITL UI LIVE · scorecard W30 |
| Docs closeout | `2026-07-25-OPS-FB-TOKEN-01-CLOSE.md` |

**Werdykt planu:** wykonany w 100% względem scope token/insights. To **nie** zamyka całego Meta organic.

## 2) Audyt ekspercki — ile darmowego Meta wykorzystujemy?

Skala dla funnelu FlexGrafik (Page NL + Wizard + Instant Form paid HOLD): **~40%** potencjału organic/free, który jest dla nas sensowny.

### Już wykorzystane (działa / LIVE)

- Facebook **Page** FlexGrafik + Graph publish (text/photo/video) HITL w Commanderze
- Token **PAGE** long-lived + scopes publish/engagement list + **`read_insights`**
- Pixel L0 **InitiateCheckout** PASS
- Kalendarz organiczny (draft/schedule/publish) · 5 published (głównie smoke)
- Marketing Brain propose + weekly draft (organic ER baseline = `—`)

### Zablokowane / niedomknięte (ekspert FB)

1. **Organic metrics / ER → DTL** — **FAIL** mimo `read_insights`  
   - Graph `#10` na engagement pól: wymaga **`pages_read_user_content`** (lub Page Public Content Access)  
   - Insights: `#100` „must be a valid insights metric” (nazwy `post_impressions` / v25 — do poprawki)  
   - Scorecard: `Organic ER baseline: —` · DH `facebook_organic` degraded (`no_published_posts` / stare ingest)
2. **Cadence treści** — kolejka pełna smoke/testów; mało realnego contentu NL pod ZZP  
3. **Instagram organic** — brak w stacku (scopes/IG user)  
4. **Messenger / inbox response** — brak API; WA &lt;15 min = HITL ręczny  
5. **L0 Purchase** — park Mollie  
6. **Paid lean (#1)** — HOLD €5 (poza „darmowym”; optimize po 7d wg META-CLICK-PATH)  
7. **Ads API create** — świadomy park (ticket_only)

### Bezpieczeństwo (ops)

- `requests` exception loguje pełny URL z `access_token=` → ryzyko w `journalctl`.  
  **NEXT:** redact w loggerze + rozważyć rotację tokenu po sesjach debug (HITL).

## 3) Co robić dalej (jedna ścieżka)

**NEXT ticket (agent + 1× OAuth HITL):** `OPS-FB-ORGANIC-METRICS-01`

1. Meta App / Graph: dodać **`pages_read_user_content`** → re-auth → `set-fb-access-token.py`  
2. Kod: zaktualizować insight metrics pod Graph v25 + nie logować tokena w URL  
3. Re-ingest DTL `facebook_organic` → scorecard ER ≠ `—`  
4. Równolegle (Dowódca): 1–2 realne posty/Reels NL/tydzień (HITL) — nie smoke  

**Kampanie / Ads:** dopiero gdy powiesz „final” (META-CLICK-PATH optimize).

## Evidence (no secrets)

- `fb-health`: ok · PAGE · `has_read_insights=true` · scopes: `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`, `public_profile`, `read_insights`
- Live `/posts` 200; post node engagement → `#10 pages_read_user_content`
- Commander `?v=mkt-dash08` · Marketing loaded · Opublikowane: 5
