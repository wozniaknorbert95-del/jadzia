# BLAST — COI-OPS-AI-01 (≥60% ops AI) — preferred next

**Date:** 2026-07-18  
**Decision:** Po deploy+verify → **OPS-AI-01** (nie PM ritual jako pierwszy).  
**Why:** Scorecard #9 to jedyny **FAIL** z liczbą; PM (#5) jest PARTIAL-link i nie blokuje zaliczenia formuły 60%.

## B — Background

Baseline v1 (2026-07-18): **11 AI / 13 human = 45.8%** (`docs/ops/OPS-AI-SCORECARD.md`).  
Cel: `ops_ai_ratio ≥ 0.60` w oknie 14d, bez fałszowania i bez wyłączania CRITICAL HITL.

## L — Limits (1-1-1)

- Jedna sesja = **jeden** tor: albo instrumentacja widget (`created_at` / AI ops count), albo bezpieczny wzrost AI spawn w v1 contract — **nie oba mega**.
- Prefer: **instrumentacja** (uczciwy wzrost mianownika AI) przed spamowaniem ticketami.
- **Nie** Gate D / Mollie LIVE / auto-publish marketing / deploy bez GO.
- PM ritual = osobny gate później (`COI-PM-01` hop OS).

## A — Approach (rekomendowany tor)

1. **Re-measure** na VPS: `deployment/_ops_ai_count_14d.py` → zapis snapshot w OPS-AI-SCORECARD.  
2. **Gap analysis v1:** które klasy AI są under-counted (widget sessions bez `created_at`)?  
3. **Minimal instrumentation** (1 PR): durable field / event liczony jako `ai_executed_ops` zgodnie z kontraktem v1 — albo rozszerzenie kontraktu v1.1 z datą.  
4. Jeśli po instrumentacji nadal &lt;60%: dozwolone **safe AI ops** z listą (widget replies, brief INFO/ACTION spawn, freshness polls) — bez CRITICAL auto-approve.  
5. Re-measure → PASS tylko przy liczbie ≥60% + commit scorecard + CLOSE.

### Alternatywa (park)

**PM ritual (`COI-PM-01`):** checklist Dowódcy OS Mission Control (Basic Auth) → 1 HITL task → handoff. Nie podnosi #9; użyj gdy OPS zablokowane brakiem danych &gt;2 sesje.

## S — STOP

- Fałszywy PASS bez SQL/evidence  
- Liczenie human publish jako AI  
- Auto-approve CRITICAL  
- Merge Agent OS do jadzia  

## T — DoD OPS-AI-01

- [ ] Fresh 14d count script na VPS (output w scorecard)  
- [ ] Ratio ≥ **0.60** **lub** udokumentowany blocker instrumentacji z następnym 1-1-1  
- [ ] CRITICAL HITL retained (smoke: queue ma approve path)  
- [ ] Scorecard #9 → LIVE/PASS tylko przy ≥60%  
- [ ] `todo` `COI-OPS-AI-01` completed **tylko** przy PASS  
- [ ] Handoff CLOSE  

## Estimate

1 sesja instrumentacja + measure; opcjonalnie +1 sesja safe AI volume.
