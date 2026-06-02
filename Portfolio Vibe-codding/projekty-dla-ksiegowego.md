# FlexGrafik — projekty w toku (dokument dla księgowego)

**Data dokumentu:** 6 maja 2026  
**Firma:** FlexGrafik (Rotterdam)  
**Cel:** krótki opis projektów w toku z przewidywaną datą zakończenia i szacunkową wartością — zgodnie z prośbą przed spotkaniem.

---

## Do uzupełnienia przed spotkaniem (Norbert)

| Pole | Wartość (wpisz) |
|------|-----------------|
| Szacunek godzin pracy na FlexGrafik w **2025** (zlecenia, klienci, administracja — **bez** czasu na naukę nowych umiejętności) | ___ godz. |
| Stawka godzinowa (do oszacowania „kosztu wytworzenia” vs. rynek) | € ___ /h |
| Partnerstwo **erkapremium** (montaż/druk): czy jest już przychód z tej współpracy, czy wyłącznie ustalenia na przyszłość? | ___ |

*Uwaga:* poniższe widełki „koszt u agencji” i „potencjał przychodu” są orientacyjne; po wpisaniu stawki i godzin można dodać własny wiersz „szacowany koszt nakładu własnego (godziny × stawka)”.

---

## Kontekst biznesowy (krótko)

FlexGrafik buduje **ekosystem** dla holenderskich ZZP (branding): strona **flexgrafik.nl** kieruje do **konfiguratora pakietów** (ZZPackage) i **gry** zbierającej kontakty. **jadzia-core** to wewnętrzny silnik automatyzacji (zlecenia, integracje, wsparcie operacyjne). **Bestelbus L** to metodyka i narzędzia do grafik e‑commerce z odniesieniem do rzeczywistych wymiarów (naklejki na furgonetki).  
**erkapremium:** współpraca handlowa (montaż/druk u partnera) — bez osobnego produktu w repozytorium GitHub.

**Stan przychodów z projektów wymienionych poniżej:** według stanu na przygotowanie tego dokumentu — **brak potwierdzonego przychodu z tych linii**; projekty są dokończane przed pełną monetyzacją (księgowy może to skorelować z Exact).

---

## Tabela zbiorcza

| # | Projekt | Data zakończenia (plan) | Gotowość (szac.) |
|---|---------|-------------------------|------------------|
| 1 | ZZPackage Wizard | czerwiec 2026 | ~85–95% (drobne UX/CRO) |
| 2 | Gra Bouwplaats Chaos (app.flexgrafik.nl) | czerwiec 2026 | produkcyjna, dopracowania |
| 3 | Strona flexgrafik.nl | czerwiec 2026 | ~90% (kilka stron/treści) |
| 4 | jadzia-core | czerwiec 2026 (rdzeń), potem rozbudowa | rdzeń działający |
| 5 | Bestelbus L (wizualizacje e‑commerce) | czerwiec 2026 | spec + tooling; finalne assety |
| 6 | Portfolio (usługi vibe coding / automatyzacja) | lipiec 2026 | w przygotowaniu |
| 7 | Oferta KFA-Finanse (landing) | **ukończone** (eksport strony) | technicznie gotowe |

---

## 1. ZZPackage Wizard — `zzpackage.flexgrafik.nl`

**Opis:** Siedmiokrokowy konfigurator pakietów brandingowych dla ZZP w NL; sprzedaż przez WooCommerce, spójny katalog produktów (JSON), własny motyw WordPress.

**Technologie:** WordPress, WooCommerce, PHP, JavaScript modułowy, testy E2E (Playwright), skrypty wdrożeniowe.

**Status:** Środowisko produkcyjne; wdrożenia na bieżąco; lista audytów/ulepszeń (UX, dostępność, konwersja) w dokumentacji repozytorium.

**Data zakończenia (plan):** **czerwiec 2026** (domknięcie priorytetowych poprawek funnelu).

**Szacunkowa wartość**

| Perspektywa | Szacunek |
|-------------|----------|
| Koszt wytworzenia u agencji (porównawczo) | **€8 000 – €15 000** |
| Potencjalny przychód | Pakiety od ok. **€199** (brutto, z oferty) × liczba zamówień — **do modelowania po starcie sprzedaży** |
| Jako produkt dla innych firm | Możliwy szablon procesu — **nie** sprzedawany obecnie jako osobny SaaS |

---

## 2. Gra „Bouwplaats Chaos” — `app.flexgrafik.nl`

**Opis:** Gra przeglądarkowa (platformówka 2D) dla ZZP; zbiera dane kontaktowe i kieruje do ZZPackage z parametrami kampanii (np. kody). Leaderboard, integracja z API WordPress (zapis leadów, start gry).

**Technologie:** React, TypeScript, Vite, Canvas (własny renderer), Cloudflare Turnstile, Sentry, analityka.

**Status:** Build produkcyjny, testy (Vitest/Playwright); rozwój produktowy możliwy po starcie kampanii.

**Data zakończenia (plan):** **czerwiec 2026**.

**Szacunkowa wartość**

| Perspektywa | Szacunek |
|-------------|----------|
| Koszt wytworzenia u agencji | **€10 000 – €20 000** |
| Potencjalny przychód | Pośredni: **leady i konwersje do ZZPackage** — wartość w EUR zależy od współczynnika konwersji |
| Jako osobny produkt | Gra **nie** jest przedmiotem sprzedaży; narzędzie marketingowe FlexGrafik |

---

## 3. Strona wizytówka — `flexgrafik.nl` (repozytorium `flexgrafik-nl`)

**Opis:** Główna strona marki NL (WordPress, motyw potomny Astra): portfolio, usługi, kontakt, linki do ZZPackage i gry, podstawy prawne i analityka.

**Technologie:** WordPress, PHP, CSS, JS (m.in. widget czatu na wybranych stronach).

**Status:** W dużej mierze wdrożone; otwarte drobne punkty (m.in. spójność stron „Over ons” / landing gry / regulaminy — według `todo.json` w repozytorium).

**Data zakończenia (plan):** **czerwiec 2026**.

**Szacunkowa wartość**

| Perspektywa | Szacunek |
|-------------|----------|
| Koszt wytworzenia u agencji | **€2 500 – €5 000** |
| Potencjalny przychód | Wspiera **zaufanie i wejście do lejka** — nie rozlicza się osobno |
| Jako produkt | Strona firmowa — brak odsprzedaży |

---

## 4. jadzia-core — silnik automatyzacji

**Opis:** Backend (API) do orkiestracji operacji FlexGrafik: kolejki zadań, powiadomienia (webhook), opcjonalnie Telegram, integracja z agentem AI, narzędzia operacyjne (m.in. SSH/deploy, eksploracja WordPress), endpointy wykorzystywane przez zewnętrzne automaty (np. n8n).

**Technologie:** Python, FastAPI, SQLite, JWT, Anthropic API, httpx, testy jednostkowe.

**Status:** Kod o charakterze produkcyjnym; dokumentacja produktowa częściowo w wersji roboczej; rozbudowa po uruchomieniu pełnego obciążenia.

**Data zakończenia (plan):** **czerwiec 2026** dla stabilnego rdzenia; **utrzymanie i moduły** — ciągle.

**Szacunkowa wartość**

| Perspektywa | Szacunek |
|-------------|----------|
| Koszt wytworzenia u agencji | **€15 000 – €30 000** (złożoność integracji i automatyzacji) |
| Potencjalny przychód (wewnętrznie) | Oszczędność czasu operacyjnego / skrót realizacji zleceń — **do opisania kwotowo po wdrożeniu procesów** |
| Jako produkt/SaaS dla innych firm | **Potencjał** (automatyzacja sklepu/procesów): orientacyjnie **€99 – €299 / mies.** — *hipoteza rynkowa, brak aktywnej sprzedaży SaaS* |

---

## 5. Bestelbus L — generator / pakiet wizualizacji e‑commerce

**Opis:** Zestaw specyfikacji i promptów pod spójne zdjęcia „naklejka na średniej furgonetce” dla sklepu (18 SKU DIY), z odniesieniem do **cm** i stref bezpiecznych; skrypt QA treści promptów (Node.js); skrypt PowerShell do normalizacji grafik do formatu sklepowego (np. 1200×895 px). Podstawa pod **narzędzie/generator** dla e‑commerce.

**Technologie:** Markdown/specyfikacje, Node.js (audyt), PowerShell + przetwarzanie obrazów; zewnętrznie generacja obrazów (np. modele AI).

**Status:** Dokumentacja i QA promptów na wysokim poziomie; końcowa spójność eksportów grafik — do domknięcia wraz z assetami.

**Data zakończenia (plan):** **czerwiec 2026**.

**Szacunkowa wartość**

| Perspektywa | Szacunek |
|-------------|----------|
| Koszt wytworzenia u agencji | **€2 000 – €4 000** (spec + tooling, bez pełnej aplikacji SaaS) |
| Potencjalny przychód | Sprzedaż naklejek / zestawów wg cennika w dokumentacji — **zależnie od kanału sprzedaży** |
| Jako narzędzie SaaS dla sklepów | **Potencjał:** orientacyjnie **€29 – €79 / mies.** — *do walidacji po uporządkowaniu produktu* |

---

## 6. Portfolio — usługi „vibe coding” (automatyzacja, e‑commerce)

**Opis:** Planowane **profesjonalne portfolio** prezentujące dokonania: automatyzacja procesów w firmie, narzędzia e‑commerce, integracje AI — z case studies (m.in. jadzia-core, Bestelbus, ZZPackage, gra).

**Technologie:** Do ustalenia (prawdopodobnie strona statyczna lub mały stack front-end); treści i case studies z istniejących projektów.

**Status:** W przygotowaniu.

**Data zakończenia (plan):** **lipiec 2026** (~2 miesiące od domknięcia głównego ekosystemu FlexGrafik).

**Szacunkowa wartość**

| Perspektywa | Szacunek |
|-------------|----------|
| Koszt wytworzenia u agencji | **€1 500 – €4 000** (landing portfolio + treści) |
| Potencjalny przychód | **Zlecenia B2B** (projekty godzinowe / wdrożenia) — bez górnej granicy, zależnie od konwersji |
| Jako produkt | Nie jest produktem — **kanał sprzedaży usług** |

---

## 7. Oferta KFA-Finanse — `oferta-kafinanse`

**Opis:** Statyczna strona ofertowa (Next.js, eksport statyczny) dla polskiego biura finansowego w NL: propozycja modernizacji www, asystenta AI, pakietu treści.

**Technologie:** Next.js 15, React, TypeScript; hosting pod ścieżką `basePath` (np. `/ofertakf`).

**Status:** **Zbudowana i wyeksportowana**; w źródle mogą pozostać drobne TODO w copy — do weryfikacji przed wysyłką do klienta.

**Data zakończenia:** **ukończone** (warstwa techniczna); ewentualne poprawki merytoryczne — krótki termin.

**Szacunkowa wartość**

| Perspektywa | Szacunek |
|-------------|----------|
| Koszt wytworzenia u agencji | **€800 – €2 500** (landing B2B) |
| Potencjalny przychód | **Jednorazowe zlecenie** — kwota wg oferty podpisanej z klientem |
| Jako produkt | Nie dotyczy |

---

## Repozytorium pomocnicze (bez osobnej pozycji „projekt kończony”)

**flexgrafik-meta** — dokumentacja, procesy i roadmapa całego ekosystemu (nie generuje przychodu bezpośrednio; podnosi jakość wdrożeń).

---

## Podsumowanie dla księgowego

- **Projekty 1–5 i 6** są **dopinane do czerwca–lipca 2026** z naciskiem na **sprzedaż przez ZZPackage** oraz **lejek** (strona + gra).  
- **Wartość** podana jest w trzech wymiarach: **koszt porównawczy (agencja)**, **potencjał przychodu / oszczędności**, **hipoteza SaaS** tam, gdzie ma to sens — z zaznaczeniem, że **przychód z tych linii nie został jeszcze potwierdzony** w momencie sporządzenia dokumentu.  
- Po uzupełnieniu tabeli na górze dokumentu księgowy może spiąć to z **urencriterium** i prognozą z Exact.

---

*Dokument przygotowany na podstawie repozytoriów w folderze GitHub FlexGrafik oraz wcześniejszej analizy kodu i dokumentacji wewnętrznej.*
