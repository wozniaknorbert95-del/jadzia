---
status: "[ACTIVE]"
title: "FlexGrafik Virtual Campus — Program SoT (VF-CAMPUS-PLAN-00)"
gate: "VF-CAMPUS-PLAN-00"
updated: "2026-07-27"
owner: "Norbert Wozniak (Dowódca) — Accountable"
audit_source: "AUDYT_VF-CAMPUS-PLAN-00_2026-07-27.md"
map_sot: "docs/ops/FLEXGRAFIK-CAMPUS-MAP.md"
runtime_changes_allowed: false
budget_freeze_until: "2026-08-06"
com_ai_50_from: "2026-08-02"
founder_override: "2026-07-27 — Campus W1 priority; MKT-ASSET-00 parked_by_founder"
active_gate_pointer: "VF-CAMPUS-W3"
w2_status: "completed"
w3_status: "completed"
w3_close: "docs/handoffs/2026-07-27-VF-CAMPUS-W3-CLOSE.md"
proposed_next_gate: "VF-CAMPUS-W4"
proposed_next_gate_active: false
---

# FlexGrafik Virtual Campus — Program (v2)

## 0. Boundary (P6)

> **Campus v1 jest nakładką orientacji i obserwowalności nad istniejącymi systemami; nie jest workflow engine, IAM, ERP ani QuietForge OS.**

**Founder override (2026-07-27):** Mission Control / Campus **first**. `MKT-ASSET-00` = `parked_by_founder` (not completed). No marketing work in Campus sessions.

**Wizja:** jedna task-first mapa firmy — każdy pokój pokazuje tylko stan do udowodnienia, prowadzi do decyzji i zostawia audyt.

**Atlas (mapa pokoi):** [FLEXGRAFIK-CAMPUS-MAP.md](./FLEXGRAFIK-CAMPUS-MAP.md)  
**Ten dokument = program wykonawczy** (fakty → fale → DoD → kod później).

---

## 1. Cel + North Star

**Cel (1 zdanie):** Dowódca widzi cały biznes FlexGrafik z Mission Control bez zgadywania — każdy hop/pokój ma dowód lub jawny `UNVERIFIED`/`PARKED`.

**North Star operatora:** task zakończony (zatwierdź / sprawdź order / utwórz asset / zobacz ryzyko) w ≤5 min daily loop; 0 silent dead hops; 0 fake LIVE.

---

## 2. Non-goals / STOP

| STOP | Do kiedy / na zawsze |
|------|----------------------|
| 3D campus / QuietForge décor | always |
| QuietForge `services/` w jadzia-core | always |
| 6th primary Commander tab | always (D0.15) |
| SSO / iframe merge OS↔jadzia | always (D0.19) |
| Ads / paid Meta spend | **2026-08-06** |
| Mollie LIVE / Purchase / Gate D | osobne Founder GO |
| Fake PASS / fake LIVE bez Evidence Ledger | always |
| IG | out of scope |
| Deploy VPS bez Zasada 11 GO | always |
| W1–W4 w tej samej sesji co W0 | PLAN-00 scope |
| Równoległy W1+MKT w jednym agencie/sesji | default zakaz |

---

## 3. Gate machine (B2)

```text
active_gate = dokładnie jedna praca, którą agent może wykonać teraz
unblocked   = dozwolona po osobnym Founder GO, nieaktywna
parked      = widoczna w roadmapie, zabroniona do startu
```

```text
VF-CAMPUS-01 (map) DONE
  → VF-CAMPUS-PLAN-00 (W0 docs) CLOSE
  → C0 Founder GO
  → active = MKT-ASSET-00
       W1 = unblocked (NIE active)
  → MKT-ASSET-00 CLOSE
  → C1 Founder: cash continuation OR active=VF-CAMPUS-W1
  → W1 → W2 → W3 → C2 Founder GO → W4
OUT/PARK: Procurement · Dispatch · Print Pack SaaS · Finance agent
```

Równoległość W1+MKT tylko: **inny owner / osobna sesja / osobny worktree**.

---

## 4. Evidence Ledger (B1) — snapshot 2026-07-27T15:50+02:00

| Claim ID | Twierdzenie | Klasa | Dowód | Zebrano | Wygasa | Owner A | Status |
|----------|-------------|-------|-------|---------|--------|---------|--------|
| EV-CAMPUS-001 | Prod tip jadzia `4cf66fe` | git/prod | [DEPLOY-FREEZE-CLOSE](../handoffs/2026-07-27-DEPLOY-FREEZE-CLOSE.md) · VPS `/opt/jadzia` | 2026-07-27 | przy nowym deploy | Ops/COI | **verified** (handoff; local HEAD `d427a94` ≠ prod — OK) |
| EV-CAMPUS-002 | Commander `?v=mkt-dash08` | prod | URL 200 + cache `mkt-dash08` in HTML | 2026-07-27T15:50+02 | 24h | Ops/COI | **verified** |
| EV-CAMPUS-003 | VCMS Conflicts=0 | governance | `node tools/vcms-scan.js` → Conflicts: 0 | 2026-07-27T15:50+02 | start kolejnej sesji | Govern | **verified** |
| EV-CAMPUS-004 | Order #3149 E2E INT-002 | business | archive handoff deploy-int-002 + SPINE proof | history | never | Ops/COI | **verified** (history) |
| EV-CAMPUS-005 | Worker health / SSH | prod | `/worker/health` → healthy · `ssh_connection=ok` · INC-SSH-RECOVERY-00 **CLOSED** 2026-07-31 | 2026-07-31 | przy regresji | Ops/COI | **verified** (recovered) |
| EV-CAMPUS-006 | Scorecard #1–9 | docs | [SCORECARD-AI-OS-ZALICZENIE](./SCORECARD-AI-OS-ZALICZENIE.md) PASS 2026-07-18 | 2026-07-18 | per-item re-verify W2+ | Ops/COI | **verified** (docs; freshness stale → re-verify before W3 badges) |
| EV-CAMPUS-007 | Design-agent health hop | prod | `GET /api/v1/design-agent/health` → **200** `status=ok` | 2026-07-27T15:50+02 | 24h | Ops/COI | **verified** |

### Reguły statusów

| Status | Znaczenie |
|--------|-----------|
| **LIVE** | aktywny dowód w ledgerze w oknie freshness |
| **UNVERIFIED** | brak aktywnego dowodu — **nie** używaj PARTIAL jako zastępstwa |
| **PARTIAL** | działa z **opisanym** ograniczeniem + evidence |
| **DEGRADED** | działa, narusza SLO → wymaga incident |
| **PARKED** | świadomy zakaz startu |
| **ROADMAP** | brak runtime — przyszły gate |

---

## 5. RACI decyzyjny (B3)

Accountable = **człowiek**, nie system.

| Decyzja | R | A | C | I | Dowód |
|---------|---|---|---|---|-------|
| CLOSE PLAN-00 | Architect/agent | **Dowódca** | Ops, Security | sztab | ten PROGRAM + handoff |
| zmiana `todo.active_gate` | agent | **Dowódca** | Ops | — | handoff + todo |
| oznaczenie room LIVE | owner pokoju | **Ops/COI (Norbert)** | Security | Founder | Evidence Ledger row |
| hop/link change W1–W2 | IA agent | **Ops/COI** | Security | Founder | Hop Contract PASS |
| deploy VPS | agent prep | **Dowódca** | Ops | — | Zasada 11 GO |
| paid spend po freeze | Marketing | **Dowódca** | Finance | Ops | cap + UTM + stop-loss |
| Mollie / Purchase | Finance | **Dowódca** | Security | Ops | osobne GO |
| organic publish ≥2026-08-02 | Marketing | **Dowódca** | Compliance | Ops | COM-AI-50 pack |
| incident SSH | Ops | **Ops/COI** | Security | Founder | INC + recovery test |

---

## 6. Campus Contract schema (W0: schema; runtime manifest = W1+)

```yaml
# docs/ops/campus/rooms/<room_id>.yaml  (future W1+)
room_id: mission-control
floor: P3
label: Mission Control
purpose: "CEO daily loop — queue, ops health, system hops."
program_action: MAINTAIN
owner_role: Ops/COI
status: LIVE
status_evidence: EV-CAMPUS-002
source_of_truth:
  label: Commander Start
  url: https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08
primary_action:
  label: Clear CRITICAL queue
  target: https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08#view-home
room_card:
  kpis: [KPI-CEO-COLD-OPEN, KPI-CEO-QUEUE-CLEAR]
  last_verified_at: "2026-07-27T15:50:00+02:00"
access: operator
```

**Jedna definicja →** mapa, hop labels, truth card, audit (zakaz kopiowania statusów w 5 miejscach bez evidence ID).

---

## 7. Room register (wszystkie pokoje · Program action)

Status poniżej = **program baseline** z mapy, skorygowany regułami B1 (UNVERIFIED gdzie brak świeżego dowodu UI).

### P3 Governance

| room_id | Label | Map status → Program | Action | Primary task |
|---------|-------|----------------------|--------|--------------|
| boardroom | Boardroom | LIVE (docs) | MAINTAIN | Otwórz master-plan |
| mission-control | Mission Control | LIVE (EV-002) | MAINTAIN | Wyczyść kolejkę CRITICAL |
| agent-os-control | Agent OS Control | LIVE (scorecard#5; hop W2) | VERIFY | Approve task w OS |
| vcms-command | VCMS Command | LIVE (EV-003) | MAINTAIN | Conflicts=0 scan |
| approval-vault | Approval Vault | LIVE (docs+audit) | MAINTAIN | Verify audit chain |

### P2 Back Office

| room_id | Label | Status | Action | Primary task |
|---------|-------|--------|--------|--------------|
| finance-room | Finance Room | PARTIAL (Purchase PARK) | IMPROVE→W4 | Zobacz UNIT-ECONOMICS |
| knowledge-library | Knowledge Library | LIVE (docs) | MAINTAIN | Otwórz KNOWLEDGE index |
| data-ai-lab | Data & AI Lab | LIVE (MB propose) | MAINTAIN | Scoruj kartę MB |
| compliance | Compliance | LIVE (docs) | MAINTAIN | Sprawdź parks STOP |
| process-catalog | Process Catalog | LIVE (10/10) | MAINTAIN | Otwórz L1 card |

### P1 Commercial

| room_id | Label | Status | Action | Primary task |
|---------|-------|--------|--------|--------------|
| reception | Reception / Concierge | LIVE | MAINTAIN | Widget / TG route |
| showroom-wizard | Showroom / Wizard | LIVE | MAINTAIN | Otwórz Wizard |
| lead-game | Lead Game | LIVE | MAINTAIN | app.flexgrafik.nl |
| sales-room | Sales Room | LIVE | MAINTAIN | Disposition hot_lead |
| design-studio | Design Studio | PARTIAL→VERIFY (EV-007 health OK; UI in Wizard) | VERIFY | Hop DA / Wizard DA |
| marketing-studio | Marketing Studio | LIVE organic / PARKED paid | IMPROVE (assets) | Publish organic / Asset WW |
| brand-portal | Brand Portal | PARTIAL | IMPROVE | Trust → Wizard |
| client-support | Client Support | PARTIAL | IMPROVE | CS follow-up / WA SLA |

### Parter (P0)

| room_id | Label | Status | Action | Primary task |
|---------|-------|--------|--------|--------------|
| order-desk | Order Desk | LIVE (EV-004) | MAINTAIN | Sprawdź wyjątek order |
| content-calendar | Content / Calendar | LIVE | MAINTAIN | Approve calendar entry |
| preflight-proof | Preflight / Proof | PARTIAL | VERIFY | Media probe / approve |
| production-network | Production Network | HITL / UNVERIFIED dashboard | MAINTAIN HITL | Status Erka (manual) |
| dispatch | Dispatch | PARKED | PARK | — |

### Magazyn

| room_id | Label | Status | Action | Primary task |
|---------|-------|--------|--------|--------------|
| asset-warehouse | Asset Warehouse | HITL | IMPROVE (MKT-ASSET) | Uzupełnij MKT/2026-W31 |
| media-cdn | Media CDN | PARTIAL | VERIFY | URL probe |
| supplier-dock | Supplier Dock | ROADMAP | ROADMAP | — |

---

## 8. Residual Truth Card drafts (poza pilot — skrót)

Format W3 Truth Card wymagany dla wszystkich; poniżej drafty residual (pilot szczegółowo w §12).

| Room | Status + EV | Primary action | SoT | Limitation |
|------|-------------|----------------|-----|------------|
| Boardroom | LIVE docs | master-plan | flexgrafik-meta | brak live dashboard |
| VCMS | LIVE EV-003 | cmd.flexgrafik.nl | conflicts.md | Basic Auth |
| Agent OS | LIVE #5 | os.flexgrafik.nl | SESSION-ANCHOR | Basic Auth; hop W2 |
| Approval Vault | LIVE | Audyt secondary | handoffs | secondary nav only |
| Knowledge | LIVE | KNOWLEDGE-SYSTEM-INDEX | docs | docs-only |
| Data & AI Lab | LIVE | MB Decision Rail | brain_events | propose-only; no Ads |
| Compliance | LIVE docs | OPERATOR parks | AGENTS.md | — |
| Process Catalog | LIVE | PROCESS-CATALOG | 10/10 cards | — |
| Reception | LIVE | Widget/TG | jadzia | — |
| Lead Game | LIVE | app.flexgrafik.nl | INT-004 | — |
| Sales | LIVE | Home disposition | REV-DEMAND | — |
| Design | PARTIAL+EV-007 | Wizard DA / health | zzpackage+jadzia | hop contract W2 |
| Brand Portal | PARTIAL | flexgrafik.nl | brain.md ~75% | polish residual |
| Client Support | PARTIAL | CS form Home | cs_followup | WA manual |
| Content/Calendar | LIVE | Marketing kolejka | content_calendar | — |
| Preflight | PARTIAL | approve media | gdrive probe | — |
| Production Network | UNVERIFIED UI | Erka HITL | external | no dashboard |
| Dispatch | PARKED | — | — | VF-PARK-DISPATCH |
| Asset Warehouse | HITL | GDrive WW | ASSET-MATERIALS-PREP | MKT-ASSET-00 |
| Media CDN | PARTIAL | verified URLs | gdrive | — |
| Supplier Dock | ROADMAP | — | pitch Phase C | VF-PARK-PROCUREMENT |

---

## 9. Data Contracts — Scorecard #1–9 (B4)

```yaml
id: SC-01
label: Dashboard CEO
formula: cold_open_ok AND daily_loop_lt_5min
source_of_truth: commander-ui / UX-DOGFOOD-PHONE.md
window: last dogfood
freshness_slo: 30d
data_class: LIVE
status_rule: live if dogfood PASS within SLO; else UNVERIFIED
display: PASS/FAIL — never invent latency
owner: Ops/COI
```

| ID | Label | SoT | data_class | freshness_slo | Display if stale |
|----|-------|-----|------------|---------------|------------------|
| SC-01 | Dashboard CEO | Commander + dogfood | LIVE | 30d | insufficient_data |
| SC-02 | System wiedzy | KNOWLEDGE-SYSTEM-INDEX | docs/LIVE | 90d | insufficient_data |
| SC-03 | AI Sprzedawca | REV-DEMAND handoffs | LIVE | 30d | insufficient_data |
| SC-04 | AI Marketing | PUBLISH-B + calendar | LIVE | 14d | insufficient_data |
| SC-05 | AI Project Manager | Agent OS HITL task | LIVE | 30d | insufficient_data |
| SC-06 | AI Customer Success | cs_followup | LIVE | 30d | insufficient_data |
| SC-07 | AI Asystent Zarządu | brief_node HITL | LIVE | 30d | insufficient_data |
| SC-08 | ≥80% procesów | PROCESS-CATALOG 10/10 | docs/LIVE | 90d | insufficient_data |
| SC-09 | ≥60% ops AI | OPS-AI-SCORECARD SQL | derived | 14d | insufficient_data |

### KPI contracts (pilot W3 / W4)

```yaml
id: KPI-CEO-COLD-OPEN
label: Cold open Commander
formula: time_to_interactive_s <= 10
source_of_truth: dogfood / Lighthouse optional
window: last test
freshness_slo: 30d
data_class: LIVE
status_rule: live if freshness OK; else insufficient_data
display: "— / insufficient data"
owner: Ops/COI

id: KPI-MKT-WIZARD-STARTS
label: Wizard starts (UTM)
formula: count(wizard_starts with campaign UTM)
source_of_truth: GA4 / analytics_snapshots INT-009
window: rolling_7d
freshness_slo: 24h
data_class: LIVE
status_rule: live if snapshot fresh; else insufficient_data
display: "— / insufficient data"
owner: Marketing / Ops

id: KPI-CPA-WIZARD
label: CPA_wizard
formula: spend / purchases  # ∞ if purchases=0
source_of_truth: UNIT-ECONOMICS.md + Ads (PARKED until 2026-08-06)
window: campaign
freshness_slo: 24h
data_class: derived
status_rule: PARKED while freeze; else live if spend row exists
display: "PARKED (freeze)" | "— / insufficient data"
owner: Finance / Dowódca

id: KPI-ORDER-INGEST
label: Order webhook OK
formula: orders ingested without exception
source_of_truth: jadzia.db orders / INT-002
window: rolling_7d
freshness_slo: 24h
data_class: LIVE
status_rule: insufficient_data if no query in window
display: "— / insufficient data"
owner: Ops/COI

id: KPI-MARGIN-FLOOR
label: Margin >= 60%
formula: gross_margin_pct >= 0.60
source_of_truth: product economics / checkout rules
window: catalog
freshness_slo: 90d
data_class: manual/derived
status_rule: docs policy; display policy not fake 0
owner: Finance / Product
```

---

## 10. Hop Contracts (B5) — szablon W2

| hop_id | Source | Label | Target | Expected marker | Auth expect | W0 note |
|--------|--------|-------|--------|-----------------|-------------|---------|
| HOP-CMD | Home map | Commander | `/commander/?v=mkt-dash08` | `mkt-dash08` in HTML | 200 JWT session | EV-002 verified |
| HOP-OS | Home map | Agent OS | `https://os.flexgrafik.nl` | Mission Control UI title | 401/302→Basic Auth OK | W2 full chain |
| HOP-VCMS | Home map | VCMS | `https://cmd.flexgrafik.nl` | Command Center | 401/302→Basic Auth OK | W2 |
| HOP-WIZ | Home map | Wizard | `https://zzpackage.flexgrafik.nl/wizard/` | Wizard SPA | 200 | W2 |
| HOP-DA | Home map | Design Agent health | `/api/v1/design-agent/health` | JSON `status=ok` | 200 public | EV-007 verified |

**DoD W2:** 0 silent dead / incorrect / auth-broken hops. Test as proper role. Record HTTP chain + final URL + timestamp + screenshot.

---

## 11. Process linkage (PROCESS-CATALOG → room)

| Process | Campus room | Status |
|---------|-------------|--------|
| P-SALES-01/02 | Sales Room · Reception | LIVE |
| P-MKT-01 | Marketing Studio · Content/Calendar | LIVE |
| P-MKT-02 | Marketing Studio (paid) | PARKED freeze |
| P-MKT-04 Asset Factory | Asset Warehouse | HITL → MKT-ASSET-00 |
| P-MKT-05 Speed-to-Lead | Client Support | PARTIAL manual |
| P-BOARD-01 | Mission Control · Approval Vault | LIVE |
| P-ENG-01 | Agent OS Control | LIVE |
| P-GOV-01 | VCMS Command · Boardroom | LIVE |
| P-REV-01 | Order Desk · Finance | PARTIAL (Gate D park) |
| P-CEO-01 | Mission Control | LIVE |
| P-CS-01 | Client Support | LIVE manual |
| P-EMERGENCY-01 | Mission Control | LIVE |

---

## 12. Waves DoD (P1–P2)

### W1 Navigate (`VF-CAMPUS-W1`) — unblocked po C1
- Labels `P# · Room` on system map; home-sub „Mission Control”
- **No** new tab / view (D0.15 / D0.19)
- **5 task tests** (desktop + mobile/keyboard), pass ≥4/5 or fix each fail:
  1. Gdzie Marketing Studio?
  2. Jak otworzyć Wizard (cash)?
  3. Jak CS follow-up?
  4. Jak wejść do VCMS / Conflicts?
  5. Jak Agent OS approve?
- Event `campus_hop_clicked` (no PII) if analytics path exists; else PARK note
- Cache bump + dogfood

### W2 Trust (`VF-CAMPUS-W2` + `VF-VERIFY-DA-HEALTH`)
- All Hop Contracts PASS
- Room badges only with Evidence Ledger IDs
- EV-007 already green — still re-verify in W2 window

### W3 Operate (`VF-CAMPUS-W3`) — Truth Cards pilot×5

**Pilot rooms:** Mission Control · Wizard · Marketing Studio · Order Desk · Finance

Każda karta:
```text
Name + purpose
Status + Evidence ID
One primary action (task-first deep-link)
SoT link
1–3 KPI with Data Contract / freshness
Owner + last_verified
Known limitation / next action
```
Read-only. No fake KPI — show `insufficient data`.

### W4 Extend (`VF-CAMPUS-W4`) — po C2 Founder GO
- Analityka hint UNIT-ECONOMICS (KPI-CPA-WIZARD PARKED in freeze)
- Order Desk deep-link (not a tab)
- Only if Data Contracts verified

### OUT / PARK
| Gate | Reason |
|------|--------|
| `VF-PARK-PROCUREMENT` | Phase C ROADMAP |
| `VF-PARK-DISPATCH` | no fulfilment SoT |
| `VF-PARK-PRINTPACK-SAAS` | pre-revenue |
| `VF-PARK-FINANCE-AGENT` | docs+costs only; Purchase PARK |

---

## 13. Marketing tor (B6) — `MKT-ASSET-00`

**Active after PLAN-00 CLOSE (C0).** Freeze €0 paid → 2026-08-06.

### DoD (nie wystarczy sam folder)

1. `MKT/2026-W31/` z `master_reel_9x16` + `tt_hook_15s` + `NOTES.md`  
   **ALBO** shoot plan: scenariusz · shot list · owner · deadline · placeholders oznaczone
2. **Asset Card** per asset (audience, problem, 1 CTA, format/kanał, source files, **prawa**, claims checked, AI disclosure if any, owner/reviewer/approval ts, UTM, landing, event)
3. **Experiment Card** (1 hipoteza, **1** success metric, organic publish date, paid stop-loss)
4. Founder HITL przed publicznym publish
5. Od **2026-08-02**: dependency **`COM-AI-50-READY`** przed organic publish

### Asset Card template

```markdown
# Asset Card — <filename>
audience: ZZP bouw/techniek NL
problem: herkenbaarheid bus
cta: Gratis branding check → Wizard
format: 9:16 · <sec> · NL captions
channel: meta_organic | tiktok_organic
source_files: …
rights: own_shoot | licensed | …
claims_checked: [ ] no fake KPI
ai_disclosure: none | AI-assisted | AI-generated
owner: …
reviewer: Dowódca
approved_at: …
utm: utm_campaign=zzp_branding_check_v1&utm_source=…&utm_medium=organic
landing: https://zzpackage.flexgrafik.nl/wizard/
event: wizard_starts
```

### Experiment Card template

```markdown
# Experiment — MKT/2026-W31
hypothesis: …
success_metric: wizard_starts (utm)   # ONE only
organic_publish_earliest: …
paid_stop_loss: no paid until 2026-08-06; then cap €10/d + kill rules UNIT-ECONOMICS
com_ai_50: required if publish >= 2026-08-02
```

---

## 14. COM-AI-50-READY (B7)

**Od 2026-08-02** dependency dla organic publish + public Concierge/widget AI.

Checklist (kontrolki — **nie** porada prawna; Founder + doradca NL/EU):

- [ ] Disclosure „Rozmawiasz z asystentem AI” + human handoff
- [ ] Inventory outputs (text/image/video) × system
- [ ] Marking/metadata process (Art. 50 / wytyczne KE)
- [ ] Review AI claims / deepfake risk
- [ ] Evidence pack: screenshot, copy/version, ts, model/provider, approval

---

## 15. INC-SSH-RECOVERY-00 (P3) — **CLOSED 2026-07-31**

| Field | Value |
|-------|-------|
| Status | **CLOSED** — handoff `docs/handoffs/2026-07-31-INC-SSH-RECOVERY-00-CLOSE.md` |
| Post-fix | `/worker/health` → `ssh_connection=ok` · `status=healthy` |
| Evidence | EV-CAMPUS-005 · EV-W2-011 (historical) |
| Owner A | Ops/COI (Norbert) |

---

## 16. Todo control plane (P4)

### Kontrakt pól (W0)

| Field | Rule |
|-------|------|
| `id` | unique string |
| `status` | pending \| in_progress \| completed \| parked \| unblocked |
| `depends_on` | existing ids; no cycles; **parked ≠ dependency of active** |
| `active_gate` (header) | exactly **one** id; that task `in_progress` |
| `completed` | must cite evidence path in `note` or `checklist` |
| `runtime_changes_allowed` | `false` for PLAN-00 / docs gates |
| `evidence_required` | string in note for campus gates |

Schema sketch: [todo.schema.json](../todo.schema.json) (CI validation = follow-up, not W0 blocker).

---

## 17. Ritualy

1. Start sesji campus/MKT: `vcms-scan` → Conflicts=0 (odśwież EV-003)
2. Tip check: prod SHA vs handoff (EV-001)
3. Nie oznaczaj LIVE bez ledger row w freshness
4. Jedna sesja = jeden `active_gate`
5. Handoff: `git diff --name-only` proof (P5)

---

## 18. Definition of Done — program Campus v1

Campus v1 **DONE** gdy:
- W3 PASS (5 truth cards + Data Contracts)
- Mapa + PROGRAM zsynchronizowane (statusy z Evidence IDs)
- 0 fake LIVE
- Hop Contracts W2 PASS
- OUT/PARK jawne (nie ukryte jako LIVE)

**Nie** wymaga: QuietForge complete, Procurement, Dispatch, Print Pack SaaS, 3D.

---

## 19. C0 Founder GO checklist (po PLAN-00)

- [ ] PROGRAM v2 przeczytany (boundary + gate machine)
- [ ] Evidence Ledger zaakceptowany (SSH INC-SSH-RECOVERY-00 **CLOSED** · EV-CAMPUS-005 recovered)
- [ ] `active_gate = MKT-ASSET-00` zatwierdzony
- [ ] W1 pozostaje `unblocked` (nie start bez C1)
- [ ] Freeze €0 paid do 2026-08-06 potwierdzony
- [ ] COM-AI-50-READY znany przed publish ≥2026-08-02

---

## 20. Gaps OUT (pitch) — nie w W1–W3

| Gap | Gate | Next |
|-----|------|------|
| Procurement Brain | VF-PARK-PROCUREMENT | Phase C osobny |
| Print Pack SaaS tenants | VF-PARK-PRINTPACK-SAAS | GTM pilots |
| Dispatch | VF-PARK-DISPATCH | po fulfilment SoT |
| Finance agent | VF-PARK-FINANCE-AGENT | po Mollie GO |
| DA hop (history 404) | EV-007 now OK; W2 re-verify | VF-VERIFY-DA-HEALTH |

---

*W0 output. Runtime implementacja dopiero po Founder GO odpowiednich fal.*
