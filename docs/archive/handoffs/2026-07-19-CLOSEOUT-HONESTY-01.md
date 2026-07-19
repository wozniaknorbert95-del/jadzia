---
status: "[ACTIVE]"
title: "CLOSEOUT-HONESTY-01 — tip sync + residual close"
gate: "CLOSEOUT-HONESTY-01"
updated: "2026-07-19"
result: "PASS_WITH_HUMAN_PARK"
---

# CLOSEOUT-HONESTY-01

Cel: domknąć luki po MKT-SHIP / terminal UI **bez FAKE PASS**. Każdy punkt ma DoD i werdykt z evidence.

## DoD matrix

| ID | DoD (zaliczenie tylko gdy…) | Werdykt | Evidence |
|----|-----------------------------|---------|----------|
| **D1 Tip SoT** | SoT nie twierdzi starego `3e60437`; UI tip kanoniczny **`8d40efc`+**; VPS `git rev-parse` ≥ `8d40efc` | **PASS** (po pull VPS) | UI landed `8d40efc`; docs tip moves on master |
| **D2 CSS handoff** | Osobny CLOSE w hot handoffs ≤15; README start-here wskazuje ten plik | **PASS** | ten dokument |
| **D3 VCMS** | Scan **Conflicts: 0**; handbook tip evidence ≥ `8d40efc` LIVE (REVISION tip match po Deploy-VPS) | **PASS** | Conflicts:0 · LIVE tip `2d559ef` · handbook contains `8d40efc` ×3 |
| **D4 Blog** | HTTP **200** slug LIVE + WP post `publish` + MD5 asset = tip `65e522b` file | **PASS** (wąski) | post ID `3213` · MD5 `0eb86e632d1c74aca34bf169ac10f41b` |
| **D4b Hosting honesty** | Nie twierdzić „full git sync hosting”; zapisać: seed/scp asset only | **PASS** (honesty) | brak pełnego tipu git na Cyber-Folks |
| **D5 FB token** | `check_token_health` z dotenv: `ok=true`, `token_type=PAGE` (bez druku sekretów) | **PASS** | `message_pl=Token OK (Page)`, `expires_at=0` |
| **D5b Queue stale** | Kolejka może mieć stare CRITICAL „token wygasł” mimo health OK — **nie** udawać że zniknęły | **ready_for_human** | Dowódca: ack/close starych ticketów w Commanderze |
| **D6 VPS hygiene** | Brak `?? path` w `/opt/jadzia`; tip match origin HEAD | **PASS** | `PATH_GONE=yes` · VPS tip `c1d4e9a` |
| **D7 UI smoke** | LIVE `/commander/`: `coi-terminal` + `Organic HITL`/`mkt-os-strip` + CSS `#3d9eff` HTTP 200 | **PASS** | Home terminal + Marketing view strip/links LIVE |

## PARK (świadomie nie zamykane tu)

- OPERATOR-TODAY Meta #1–4 (Events / Audience / Asset shoot / Ads €10)
- Gate D · Mollie LIVE · Ads API · TikTok API
- Full Cyber-Folks = git tip zzpackage (poza zakresem; blog asset OK)
- VCMS `data/` + `repos/*.md` dirty po scan — **nie** commitowane (Conflicts=0; plan 1-1-1)
- services dirty media — nietknięte

## Next

1. Dowódca: Meta pack #1–4  
2. Dowódca: wyczyść/ack stale FB tickets w kolejce (token LIVE OK)  
3. Organic #5 dopiero z media w Drive  
