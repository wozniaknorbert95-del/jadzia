# Prod dogfood — VF-VHQ-FINAL-00

**URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w67a&vhq=mc  
**Tip:** `53a19e2` (+ follow-up banner copy if tip advances)  
**Method:** Chrome DevTools evaluate_script + viewport screenshot (MC)

## Results

| Check | Result |
|-------|--------|
| `#vhq-floors` absent | PASS |
| No button `P3 Sterowanie` / `MAG Network` | PASS |
| Firm Chain = 1–4 only | PASS |
| Tools / Sign in | PASS |
| Cache hint `vhq-w67a` | PASS |
| Money/risk + ops mount present | PASS |
| Deliver → honesty EV-W2-010 visible | PASS |
| Deliver rooms count 7 | PASS |
| Order Desk PARKED + unlockHint | PASS |
| Esc Order Desk → `?vhq=mc` stay HQ (not Console) | PASS |
| Breadcrumb stage labels | PASS |

## Residual noted

- Top Commander tabs `[ Start ] [ Marketing ]…` still visible above HQ (Tools world) — by design, not second Firm Chain.
- Unsigned session: Decision Rail shows loading / empty until JWT (honest).
