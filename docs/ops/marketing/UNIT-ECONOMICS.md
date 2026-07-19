---
status: "[ACTIVE]"
title: "Marketing OS — Unit Economics"
updated: "2026-07-19"
---

# Unit Economics — FlexGrafik demand

## Definicje

| Symbol | Definicja |
|--------|-----------|
| `spend` | Wydatki paid Meta (EUR) w oknie |
| `leads` | Instant Form leads (unikalne) |
| `wizard_starts` | Sesje Wizard z UTM kampanii (InitiateCheckout lub start) |
| `purchases` | Purchase (Pixel/CAPI) z atrybucją kampanii |
| **CPL** | `spend / leads` |
| **Lead→Wizard** | `wizard_starts / leads` |
| **Lead→Purchase** | `purchases / leads` |
| **CPA_wizard** | `spend / purchases` (gdy purchases=0 → ∞; nie scale) |

## Próg sterujący (start)

`CPA_wizard < 0.40 × marża_brutto_ZZPackage` (próg startowy).

Przykład roboczy (zastąp realną marżą po 10 zakupach):

- Checkout typowy ≥ €199, marża ≥ 60% → marża brutto ≈ €119+
- 40% marży ≈ **CPA max ~ €47** (orientacyjnie)
- Jeśli CPA &gt; próg przez 14d learning → kill scale, popraw offer/form/creative

## Reguły decyzji

| Warunek | Akcja |
|---------|-------|
| purchases = 0 po 14d przy spend ≥ €100 | Nie scale; sprawdź Pixel/CAPI + offer |
| Lead→Wizard &lt; 10% | Form/offer broken — nie scale budżetu |
| CPL &lt; €10 i Lead→Wizard ≥ 30% | Scale +€5 / 3 dni |
| CPL €10–20, Lead→Wizard ≥ 20% | Hold; wymień 1 creative |
| CPL &gt; €25 lub 0 leadów / 5d | Kill creative |

## Co nie steruje budżetem

Followers, likes, reach, video views **bez** wizard_starts / purchases.
