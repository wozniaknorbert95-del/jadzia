---
todo: DOS-W1-05
os_target_section_ref: "Sniper_Validator · C.5"
status: done
set_at: "2026-07-31"
---

# Validator Drill — W1 (prep, pre-organic)

**Bypass = 0.** Żaden asset nie idzie na świat bez wiersza w [`VALIDATOR-LOG.csv`](./VALIDATOR-LOG.csv).

## Dry-run: `tt_w31_install_01` (draft)

| # | Reguła FAIL | PASS? |
|---|-------------|-------|
| 1 | &gt;1 primary CTA | **PASS** — tylko Wizard |
| 2 | Brak UTM | **PASS** — pełny UTM w shoot plan |
| 3 | Brak `icp_role` | **PASS** — installateur |
| 4 | Multi-CTA słowa | **PASS** — brak like/save/newsletter |
| 5 | Ads w freeze | **PASS** — organic only |
| 6 | HQ hero | **PASS** — bus/branding only |
| 7 | Offerte-koniec | **PASS** — CTA = Wizard |
| 8 | Gra dual CTA | **N/A** — nie post gry |

**Decyzja:** PASS (draft) · `publish_intended=N` do ≥2026-08-02.

## Compliance formula (Money Check Pon)

```
compliance_pct = PASS / (PASS + FAIL) * 100
```

Pole `validator_fail_count` w [`MONEY-CHECK.md`](./MONEY-CHECK.md) = liczba wierszy `decision=FAIL` w logu od ostatniego Pon.

## Reguła runtime Wave1

1. Draft → dry-run w logu  
2. PASS → publish  
3. Po publish → `LEDGER.csv` `publish_Y/N=Y`  
4. FAIL → nie publish; powód w `fail_rules`
