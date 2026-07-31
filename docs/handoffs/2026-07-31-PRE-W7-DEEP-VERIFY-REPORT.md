---
status: "[SUPERSEDED]"
title: "PRE-W7 — głęboka weryfikacja W1–W6 (REAL vs obietnice)"
updated: "2026-07-31"
gate: "PRE-W7-VERIFY"
prod_tip: "da1b2d6"
runtime_commit: "06212d7"
cache: "vhq-w60a"
pytest_ops_bus: "10/10 PASS"
verdict: "NO-GO W7 until FIX_NOW hygiene; runtime W5/W6 REAL"
superseded_by: "docs/handoffs/2026-07-31-PRE-W7-SOT-HYGIENE-CLOSE.md"
---

# PRE-W7 — Deep verify (evidence-first)

**Fresh checks this session (2026-07-31):**  
VPS tip `da1b2d6` · cache `vhq-w60a` · vault panel yes · worker healthy · `ssh_connection=ok` · `ops_bus_events` 16 cols · pytest `10 passed`.

---

## 1) REAL DONE (nie puste obietnice)

| Wave | Verdict | Dowód świeży |
|------|---------|--------------|
| **W1 Shell** | REAL | `#vhq-shell` + floors/teleport w `commander-ui` |
| **W2 MC** | REAL | Command View mounts + vault strip DOM |
| **W3/W3.2 Commercial** | REAL | Work Views + evidence dirs W31/W32 |
| **W4 Ops rooms** | REAL (honest PARKED) | Order Desk `PARKED · EV-W2-010` w registry + prod screenshot |
| **W5 Ops Bus** | REAL + LIVE | schema prod 7 rows; hooks disposition/brief/order; API; tests |
| **W6 Approval Vault** | REAL + LIVE | panel + `vhqFetchPendingApprovals` + L2 `{state}` + L3 no Approve; prod dogfood |

### Prod bus (SQLite) — stan faktyczny

| id | type | level | state | source |
|----|------|-------|-------|--------|
| 1 | wizard_started | L0 | none | commander_ui dogfood |
| 2–3 | lead_qualified | L1 | none | jadzia (disp/CTA) |
| 4 | wizard_started | L0 | none | jadzia CTA |
| 5 | lead_qualified | **L2** | **pending** | dogfood w6 |
| 6 | approval_needed | L2 | **approved** | companion (approve OK) |
| 7 | approval_needed | L3 | pending | STOP (approve 403) |

`order_created` rows on prod: **0** (36 orders w DB — emit tylko na *first insert* po W5; brak nowego WC webhook od deployu). Hook w kodzie **jest** (`order_node.py` L28–57) + pytest pokrywa.

---

## 2) PARTIAL / nie mylić z DONE

| Claim | Reality |
|-------|---------|
| „Approval Vault LIVE” (PROGRAM Deploy row) | UI room badge = **PARTIAL** — cienka ścieżka Ops Bus, nie pełny approval OS |
| „Full Ops Bus catalog” | Tylko 4 typy: `lead_qualified`, `wizard_started`, `order_created`, `approval_needed` |
| „7 pytań ≤30s” | To jest **W7 DoD**, nie W2/W6 — brak formalnego dogfoodu ≤30s po W6 |
| Bus trail bez JWT | Shell honesty bez kart — JWT wymagany (G4 CLOSED przez PRE-W6) |
| `order_created` na prod | Kod+test REAL; **brak live WC event** od W5 (residual G5 — accepted) |

---

## 3) MUST FIX BEFORE W7 (FIX_NOW)

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| **F1** | Tip drift: VPS/`git` = `da1b2d6`, `todo.campus_prod_tip` / handoffy często `03f3bac` | docs | tip-sync SoT → `da1b2d6` / runtime `06212d7` / `vhq-w60a` |
| **F2** | `todo.active_gate=VF-VHQ-W7-DOGFOOD` przy jednoczesnym `parked` + `active:null` | confusing | `active_gate=null` lub `parked` explicit; W7 tylko po GO |
| **F3** | Gate note W6: „Deploy under GO” mimo DEPLOY PASS | stale | update note → CLOSED+DEPLOYED |
| **F4** | PROGRAM frontmatter `prod_tip_at_plan: 3487ec0` | stale | refresh lub mark historical |
| **F5** | ARCH approval-vault primary action nadal „Open Audyt…” | stale vs W6 | wskazać Ops Bus pending / Vault room |
| **F6** | PROGRAM „W6 LIVE” vs room **PARTIAL** | oversell | wording: LIVE path / PARTIAL maturity |

### SHOULD FIX (jakość bus, nie blocker UI Vault)

| # | Issue | Why |
|---|-------|-----|
| **S1** | Po L2 Approve companion (id=6) parent `lead_qualified` (id=5) zostaje `approval_state=pending` | `set_approval_state` flipuje tylko companion — Audyt/list bez filtra myli. Albo sync parent, albo dokumentuj „companion-only” w SoT |
| **S2** | Brak prod `order_created` | Nie forsuj fake WC; przy następnym real insert zweryfikuj 1 wiersz albo osobny controlled smoke |
| **S3** | Brud lokalny MKT + stare untracked handoffs | Nie commitować; hygiene osobno |

---

## 4) NIE ruszać (poprawnie PARKED / STOP)

- Order Desk LIVE  
- Silent L3/L4 approve  
- Full §8 catalog  
- Ads / Mollie / Gate D  
- MKT commit  
- 3D  

---

## 5) W7 readiness

**NO-GO na start W7 teraz.**

Powód: runtime W5/W6 jest realny, ale SoT/tip/gate hygiene (F1–F6) musi być czysta zanim Founder zrobi ≤30s dogfood — inaczej W7 mierzy brudne SoT, nie produkt.

Po FIX_NOW → **GO conditional** (osobne GO `VF-VHQ-W7-DOGFOOD`):

1. Prod `?v=vhq-w60a` + JWT  
2. 7 pytań Director ≤30s + honest gaps  
3. Evidence `evidence-vhq-w7-dogfood/`  
4. PASS gaps = PARTIAL/PARKED (Marketing UNVERIFIED, Order PARKED, Finance park) — nie fail

---

## 6) Recommended path (1-1-1)

**Teraz:** PRE-W7 hygiene tip-sync (F1–F6) + decyzja S1 (sync parent **albo** SoT „companion-only”).  
**Potem:** GO W7 dogfood.  
**Nie:** nowy runtime feature przed W7.

REPORT_VERDICT: **W5/W6 runtime REAL · SoT hygiene NOT clean · W7 NO-GO until FIX_NOW**
