# Pierwsza kampania Facebook Ads — FlexGrafik
### Playbook startowy | €8–15/dzień · 14-dniowy test
*lipiec 2026 · dopisek do Planu Automatyzacji FB*

> Kontekst z Twojej odpowiedzi: Meta podpięte ✅, Meta App utworzone ✅, Jadzia COI publikuje posty ✅.
> To znaczy, że masz już content engine + infrastrukturę API. Kampania ma tylko skierować ruch w tę gotową lejkę (→ Wizard + WhatsApp).

---

## 0. Zanim klikniesz „Publikuj" — verify checklist (15 min)

Musisz potwierdzić te 4 rzeczy, inaczej przepalisz budżet:

1. **Ad Account + metoda płatności** aktywna w Meta Business Suite (iDEAL/karta).
2. **Meta Pixel + Conversions API** działają na `zzpackage.flexgrafik.nl` — sprawdź w **Events Manager → Test Events** czy `InitiateCheckout` / `Purchase` (zapłata w Wizardzie) się odpalają. **Bez tego nie odpalaj celu „Sales"** — odpalaj „Leads".
3. **Custom Audience z obecnych klientów** (lista e-mail/telefon z zamówień Wizarda) → użyjesz do **wykluczenia** (nie płać za tych, co już kupili) i do **Lookalike** później.
4. **Dostęp reklamowy do Page** z rolą „Ads admin" + zweryfikowana domena `flexgrafik.nl` w Business Settings (Meta wymaga weryfikacji domeny dla konwersji).

---

## 1. Wybór celu — dlaczego LEADS (Instant Form) na start

| Cel | Dla kogo | Werdykt dla Ciebie |
|---|---|---|
| **Leads (Instant Form)** | B2B/usługi, niska tarcie, brak landing page'a | ✅ **Twój start** — najtańszy lead, praca na mobile, prosto do follow-up |
| Engagement → **Messaging (WhatsApp)** | Tani konwersje-od-ręcznej-bot, masz 24/7 | ✅ **Test równoległy** (patrz sekcja 6) |
| Sales (konwersje Wizarda) | Gdy masz ≥50 zakupów/tydz. do nauki piksela | ⏳ Miesiąc 2 — po zebraniu danych |
| Traffic / Awareness | Prawie nigdy ROI na pierwszej kampanii | ❌ Pomiń |

**Logika:** zimny ruch ZZP-era do checkout Wizarda konwertuje słabo. Najpierw **zbierz lead tanio** przez Instant Form (z lead-magnetem = kod z Twojej Branding Game), potem kieruj do Wizarda z kodem rabatowym. To pasuje do Twojej filozofii QuietForge: „no phone tag", ale z kwalifikacją.

---

## 2. Struktura kampanii #1 — „ZZP Branding Check"

```
Kampania: Lead Generation
├─ Kupowanie: Aukcja
├─ Budżet kampanii (CBO/Advantage+): €8/dzień   ← jeden ad set na start
├─ Lokalizacja konwersji: Instant Form
└─ Ad Set: „NL ZZP Bouw/Techniek — check"
   ├─ Budżet: Advantage+ campaign budget
   ├─ Optymalizacja: Leads (Instant Form)
   └─ Reklamy (3 warianty do testu A/B/C):
        ├─ A: Reel „przed/po busa" (najmocniejszy)
        ├─ B: Karuzela „3 kroki do profesjonalnego merk" (proces)
        └─ C: Single image — testimonial klienta
```

**Reguła:** przy €8/dzień mieści się **jeden ad set + 3 kreacje**. Daj algorytmowi (Advantage+) znaleźć zwycięzcę. Rozdzielanie na kilka ad setów przy tym budżecie = żaden nie wyjdzie z fazy uczenia.

---

## 3. Targetowanie — holenderscy ZZP w bouw/techniek

**Lokalizacja:** Nederland — z naciskiem na **Zuid-Holland (Rotterdam/Den Haag)** + **Noord-Brabant** (blisko produkcji Heesch). Gęstość ZZP wysoka, dostawa szybsza = lepsze doświadczenie. Po 7 dniach rozszerz na całe NL.

**Wiek/Płeć:** 25–55 lat, wszystkie płcie.

**Detailed targeting (łączenie zbiorów):**
- **Zawody/branże:** ZZP, zelfstandig ondernemer, small business owner
- **Sektor:** bouwbedrijf, aannemer, installatietechniek, elektrotechniek, dakdekker, schilder, hovenier, loodgieter
- **Interesy/profesja:** voertuigbelettering, wagenparkbeheer, bedrijfskleding, reclame/branding
- **Zachowania:** Facebook Page admins, Small business owners

**Advantage+ Audience:** ✅ WŁĄCZ („Use Advantage+ Audience"). Przy małym budżecie Meta częściej wygrywa własnym rozszerzeniem niż ręcznym targetowaniem.

**Wykluczenia:** Custom Audience „obecni klienci" (z Wizarda) — nie płać za tych, co już kupili.

---

## 4. Instant Form — gotowa treść (NL, do wklejenia)

**Headline (tytuł formularza):**
> Gratis ZZP Branding Check — hoe herkenbaar is jouw bus?

**Introductietekst:**
> Ben jij een ZZP'er in de bouw of techniek? In 2 minuten ontdek je hoeveel klanten jouw bus, kleding en bordje op de klus missen. Je krijgt direct een **persoonlijke check + een kortingscode** voor je ZZPackage.

**Formuliervragen (krótko = więcej leadów — nie dodawaj zbędnych pól):**
1. Naam (tekst)
2. Telefoonnummer of WhatsApp (telefoon)
3. E-mailadres (e-mail)
4. **Wat is je vak?** (wybór: Installateur · Dakdekker · Schilder · Loodgieter · Elektricien · Hovenier · Anders)
5. *(opcjonalnie)* Plaats/gemeente (tekst)

**Bedankpagina (Thank-you screen) — TU jest conversion:**
> ✅ Bedankt! We sturen je check binnen 1 werkdag via WhatsApp.
> 🔥 **Start meteen:** configureer je ZZPackage in 5 minuten → [zzpackage.flexgrafik.nl/wizard/](https://zzpackage.flexgrafik.nl/wizard/)
> 🎁 Jouw korting: speel de Branding Game voor je code → [flexgrafik.nl/hoe-scoor-jij-je-branding/](https://flexgrafik.nl/hoe-scoor-jij-je-branding/)
> 📱 Liever eerst overleggen? WhatsApp Norbert → +31 6 87286151

⚠️ **Wymagane:** link do **privacybeleid** (masz `flexgrafik.nl/privacybeleid/`) + zgoda AVG w formularzu.

---

## 5. Kreacje reklamowe (3 warianty NL)

### Ad A — Reel „przed/po" (główny, najwyższy CTR)
- **Format:** Film pionowy 9:16 (Reel/IG) + kwadrat 1:1 do Feed
- **Hook (0–3s):** nagranie z banalnie obklejonym bus-em → cięcie → gotowy premium wrap
- **Prim tekst:**
  > Jouw bus rijdt 365 dagen langs je klanten. Staat jouw merk er echt op? 🚐
  > Van subtiel logo tot full-wrap — in 10 werkdagen klaar. Bekijk hoe het eruit ziet vóór je bestelt 👇
- **Headline:** Gratis ZZP Branding Check
- **CTA:** Meer informatie

### Ad B — Karuzela „3 kroki"
- **Karty:** 1) Wizard 2) Betaal veilig (iDEAL) 3) Ontvang in 10 werkdagen
- **Prim tekst:** „Geen afspraak nodig. Geen verborgen kosten. Jij kiest, wij regelen druk, maat en techniek."
- **CTA:** Meer informatie

### Ad C — Social proof (testimonial)
- **Zdjęcie:** klient przy obklejonym bus-ie
- **Prim tekst:** „'Sinds de belettering krijg ik meer reacties op de klus.' — [Imię], installateur. Doe de gratis check 👇"
- **CTA:** Meer informatie

**Wskazówka 2026:** AI-generated obrazy = traktowane identycznie przez algorytm (brak kary) [posteverywhere.ai](https://posteverywhere.ai/blog/how-the-facebook-algorithm-works). Ale dla zaufania ZZP-erów **prawdziwe zdjęcia busów > stock/AI**.

---

## 6. Test równoległy (opcja, jeśli masz €15/dzień) — WhatsApp Messaging

Jeśli możesz rozdzielić €15/dzień, odpal **drugą mini-kampanię**:
- **Cel:** Engagement → **Messaging → WhatsApp**
- **Kreacja:** ten sam Reel „przed/po"
- **Akcja:** kliknięcie → otwiera chat WhatsApp do +31 6 87286151 z gotową wiadomością „Hi Norbert, ik wil graag..."
- **Dlaczego:** wiadomości WA są **najtańsze** na Meta, a Ty masz już 24/7 obsłużone (bot/auto-odpowiedź z Must-Have #3).
- **Werdykt po 7 dniach:** porównaj **cost per lead** z kampanii #1 (formularz) vs **cost per WA-wiadomość**. Tańsze = skaluj.

---

## 7. Budżet, faza uczenia i realistyczne liczby

- **Budżet startowy:** €8–15/dzień (zalecane €10). Mniej niż €8 = faza uczenia się nie kończy.
- **Czas testu:** **minimum 14 dni** bez edycji ad setu (edycja resetuje fazę uczenia).
- **Faza uczenia:** Meta potrzebuje ~**50 zdarzeń (leadów) / tydzień / ad set** do pełnej optymalizacji. Przy €10/dzień osiągniesz to, jeśli CPL < €14.
- **Realistyczny benchmark CPL (NL, B2B/ZZP):** **€5–25 / lead**. Pierwsze dni drożej, potem spada.
- **Cel:** pod €15/lead = dobry. Poniżej €10 = skaluj.

---

## 8. Decyzje: kill / scale (reguły bez emocji)

Po 7 dniach spójrz na wyniki ad setu/kreacji:

| Sytuacja | Akcja |
|---|---|
| CPL < €10 i leady jakościowe | **SKALUJ** +€5/dzień, co 3 dni |
| CPL €10–20 | Daj kolejne 7 dni; wyłącz 1 najsłabszą kreację |
| CPL > €25 lub 0 leadów w 5 dni | **WYŁĄCZ** kreację; zostaw zwycięzcę; rozszerz Advantage+ Audience |
| Lead, ale nie odpowiada / spam | Uważaj botów; dodaj pytanie „Wat is je vak?" jako filtr |
| CPA (koszt zakupu) w Wizardzie policzalne | Przełącz 1 ad set na cel **Sales** optymalizowany na `Purchase` |

**KPI, które musisz śledzić tygodniowo:**
1. **CPL** (cost per lead) — Instant Form
2. **Lead → Wizard start rate** (% leadów, co weszło do checkout)
3. **Lead → Purchase rate** (% leadów, co zapłaciło)
4. **CPA** (cost per purchase w Wizardzie) = prawdziwy ROI

Ten 4. metrics mówi Ci, czy kampania zarabia. Jeśli CPA < marża na ZZPackage → lejesz budżet.

---

## 9. Po 14 dniach — co dalej

1. **Lookalike Audience** z listy leadów → nowy ad set (zazwyczaj niższy CPL).
2. **Retargeting:** osoby, co otworzyły Wizarda ale nie zapłaciły → Reel retargeting + kod z gry (3–5 dni).
3. **Druga kampania: Sales objective** optymalizowana na `Purchase` (gdy masz dane z Pixel/CAPI).
4. **Jadzia COI:** jeśli Twoja app ma `leads_retrieval`, podłącz **webhook** z Instant Form → Jadzia → human approval → Wizard. Wtedy leady lądują automatycznie w Twoim pipeline, nie w Excelu.

---

## 10. Jedna strona — start w 60 minut

1. Verify checklist (sekcja 0)
2. Nowa kampania → **Leads** → Instant Form
3. Budżet €10/dzień, Advantage+ campaign budget
4. Audience: NL (Zuid-Holland + Brabant), ZZP/bouw, Advantage+ ON, wyklucz klientów
5. Wklej Instant Form z sekcji 4 (NL) + privacy link
6. 3 kreacje (A Reel / B Karuzela / C Testimonial) z sekcji 5
7. Publikuj. **Nie dotykaj przez 7 dni.**
8. Po 7 dniach — decyzja wg sekcji 8.

> Daj znać po 7 dniach z CPL i liczbą leadów — policzymy ROI razem i zdecydujemy, czy skalujemy, czy testujemy WhatsApp-track.
