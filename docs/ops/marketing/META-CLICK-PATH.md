---
status: "[ACTIVE]"
title: "Meta Ads — klik po kliku (bez IT)"
updated: "2026-07-19"
gate: "META-PACK-01"
---

# META-CLICK-PATH — A1 → A2 → A3

Nie musisz rozumieć kodu. Otwórz **Meta Ads Manager** na komputerze i idź wiersz po wierszu.  
Teksty do wklejenia: [META-PACK-LEAN.md](./META-PACK-LEAN.md) (sekcje Instant Form + Creative).

---

## A1 — Wyklucz starych klientów (~10 min)

Cel: nie płacisz za reklamy do ludzi, którzy już kupili.

1. Ads Manager → menu (≡) → **Audiences** (Odbiorcy).
2. **Create audience** → **Custom Audience**.
3. Źródło: **Website** albo **Customer list** (jeśli masz CSV maili klientów Wizard).
   - Website: osoby które były na `zzpackage.flexgrafik.nl` w ostatnich 180 dniach (albo „Purchase” jeśli Meta pokazuje).
4. Nazwa: `zzp_clients_exclude_v1`.
5. Utwórz. Gotowe — użyjesz tego w A2 jako **wykluczenie**.

Jeśli nie masz listy / piksela słabo widzi klientów: i tak idź do A2 — ustaw wykluczenie „website visitors 180d” albo pomiń A1 i wróć później. **Nie blokuj publish.**

---

## A2 — Kampania + formularz + €10 (~20 min)

1. Ads Manager → **Create** → cel **Leads** (Lead generation) — **nie** Sales.
2. Nazwa kampanii: `zzp_branding_check_v1`.
3. Budżet: **€10 / dzień** (CBO / Advantage+ OK).
4. Ad set:
   - Lokalizacja konwersji: **Instant Form** / Instant Forms
   - Geo: **Netherlands** (nacisk Zuid-Holland + Noord-Brabant jeśli możesz)
   - Wiek: **25–55**
   - Advantage+ Audience: **ON**
   - **Exclude** audience z A1 (`zzp_clients_exclude_v1`)
5. Instant Form — **Create form** → wklej z META-PACK-LEAN:
   - Headline, Intro, pola (Naam, WhatsApp, E-mail, Vak), Thank-you + link Wizard UTM
6. Zapisz form. Jeszcze nie Publish całej kampanii — najpierw A3 (kreacja).

---

## A3 — 1 kreacja + Publish (~15 min)

**Opcja najlepsza:** film 9:16 (Reel) prawdziwy bus przed/po.  
**Fallback (żeby nie czekać):** 1 zdjęcie przed/po bus.

1. W adzie: wgraj Reel **albo** static.
2. Primary text (NL) z META-PACK-LEAN sekcja Creative.
3. Headline: `Gratis ZZP Branding Check`
4. CTA: **Meer informatie** / Complete form
5. Sprawdź podgląd formularza.
6. **Publish**.

Potem:

- **7 dni nie edytuj ad setu**
- Jak przyjdzie lead → WhatsApp &lt;15 min (skrypt w [SPEED-TO-LEAD.md](./SPEED-TO-LEAD.md))

---

## Checklist (odhacz u siebie)

| # | Zrobione? |
|---|-----------|
| A1 Audience wykluczenie (lub świadomie pominięte) | [ ] |
| A2 Kampania + Instant Form + €10 | [ ] |
| A3 Kreacja + Publish | [ ] |
| Pierwszy lead → WA &lt;15 min | [ ] |

Gotowe = tor A DONE. Resztę (shadow / propose) robi agent.
