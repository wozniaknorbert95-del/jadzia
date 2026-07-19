# FlexGrafik × QuietForge — Plan automatyzacji Facebook 24/7
### Twój sztab Meta: Strategia · Automation · Content · Compliance
*Wersja 1 · lipiec 2026 · przygotowane dla Norberta / FlexGrafik.nl + QuietForge*

> Złota zasada tego dokumentu: **24/7 obecność i przechwytywanie leadów = realne za darmo. Skala klientów z dnia na dzień = NIE bez płatnych reklam.** Pokażę Ci darmowy fundament, który pracuje całą dobę, oraz moment, w którym płatne ads stają się mnożnikiem, a nie wydatkiem.

---

## 0. Diagnoza — kim jesteś, do kogo mówisz, co masz w ręku

| Co wiem | Konsekwencja dla strategii |
|---|---|
| **FlexGrafik.nl** — productized branding dla holenderskich ZZP (bus-wrap, kleding, bouwborden, logo) | Produkt jest wizualny → FB/IG Reels = Twój najmocniejszy format. Pokazujesz „przed/po" busa. |
| **zzpackage.flexgrafik.nl** — Wizard (checkout w 5 min, płatność iDEAL) | Już masz „Wizard Cash Engine" → Twoim celem na FB jest kierowanie ruchu DO tegoWizarda, nie do ręcznej wyceny. |
| **QuietForge.flexgrafik.nl** — jesteś „Conversion Systems Architect" (Agent OS LangGraph, governance, EU VPS) | **To Twoja największa przewaga:** nie musisz kupować ManyChat/Buffer — możesz zautomatyzować FB samemu przez Graph API / Business SDK. A potem sprzedać ten system innym ZZP jako case study. |
| Profil FB `id=61568401273877` jest ustawiony na **locale pl_PL** | Rynek to holenderscy ZZP-erzy → Twoja obecność na FB **musi mówić po niderlandzku**. Profil PL nie pozyska holenderskiego dekkera. (Patrz Must-Have #2.) |
| Rotterdam + produkcja Heesch | Silnik lokalny: Marketplace, regionalne Grupy ZZP, „buurt" marketing. |
| Cel: ZZP w bouw/techniek — installateurs, hoveniers, schilders, dakdekkers, loodgieters, elektriciens | Homogenna nisza = łatwiej o treść i Grupę społeczną. |

**Twoja asymetryczna przewaga:** większość ZZP-branding firm kupuje SaaS do automatyzacji. Ty **jesteś** producentem automation. Twój FB to jednocześnie kanał sprzedaży FlexGrafik **i** portfolio produktu QuietForge. Każda automatyzacja, którą tu postawisz, to gotowy case study.

---

## 1. Czerwone / zielone światło — co wolno automatyzować na FB

To chroni Twoje konto (`61568401273877`) przed banem. Meta 2026 karze agresywnie.

🟢 **ZIELONE (legalne, oficjalne API — rób to):**
- Planowanie postów/Reels/Stories przez **Meta Business Suite** lub **Graph API / Pages API** — brak kary algorytmu za scheduled posts [posteverywhere.ai](https://posteverywhere.ai/blog/how-the-facebook-algorithm-works).
- Auto-odpowiedzi w **Messenger** (Away message, menu, lead capture).
- **Comment-to-DM** na Reels (ktoś komentuje „BUS" → bot wysyła pakiet).
- **Meta Pixel + Conversions API** na stronie.
- Chatbot w Messenger (ManyChat lub Twój własny przez Messenger API).
- Publikacja do **Grupy, którą posiadasz** i do której ludzie dołączyli dobrowolnie.

🔴 **CZERWONE (ban / shadowban w 2026):**
- Masowe zapraszanie nieznajomyych do znajomych z profilu osobistego.
- Wysyłanie DM do nieznajomych bez ich inicjatywy (SPAM).
- Scraping danych, kupowanie followersów/lajków, „engagement pods".
- Auto-komentowanie pod cudzymi postami.
- Multi-accounting (fałszywe konta wspierające główne).

**Linia, której trzymaj się zawsze:** automatyzacja obsługuje ludzi, którzy **sami do Ciebie przyszli**. Nigdy nie pchaj się nieproszony do cudzych skrzynek.

---

## 2. Dwa tory automatyzacji (bo jesteś techniczny)

| | **Tor A — No-code (dziś)** | **Tor B — Self-hosted (Twoja przewaga)** |
|---|---|---|
| Narzędzie | Meta Business Suite + ManyChat free | **Facebook Business SDK / Graph API** + Twój Agent OS |
| Koszt | 0 € (z limitami) | 0 € (Twój czas + EU VPS, który już masz) |
| Limity | ManyChat free = **25 aktywnych kontaktów/mies.** (test-only) [messengerbot.app](https://messengerbot.app/manychat-messenger-bot-how-it-works-with-facebook-messenger-is-it-legal-free-options-and-whether-meta-allows-it/) | Brak — własny scheduler bez limitu kontaktów |
| Czas startu | 1 dzień | 1–2 tyg. (w tym App Review) |
| Kiedy | Startujesz Tor A **natychmiast**, równolegle budujesz Tor B. | Gdy ManyChat free się skończy / gdy chcesz pełnej kontroli i integracji z Wizardem + Jadzia COI. |

**Rekomendacja:** Tor A uruchom w dniu 1–3. Tor B (Business SDK) wbuduj w miesiącu 2 — i to **stanowczo** w Twoim przypadku, bo masz kompetencje i to Twój produkt (QuietForge).

---

## 3. PLAN DZIAŁANIA — 4 fazy

### FAZA 1 — Fundament 24/7 (tydzień 1)
Cel: konto pracuje, nawet gdy śpisz.

1. **Meta Business Suite** → połącz **Facebook Page** (Biznes, NIE profil osobisty) z **Instagram Professional**. Jedna publikacja → dwa kanały.
2. **Planner** → zaplanuj **30 dni** treści z góry: 3–5 postów feed/tydz., **2–4 Reels/tydz., Stories codziennie** [posteverywhere.ai](https://posteverywhere.ai/blog/how-the-facebook-algorithm-works).
3. **Auto-odpowiedzi Messenger**: Away message (NL) + menu → link do **Wizarda** + przycisk **WhatsApp** (Twój +31 6 87286151).
4. **Meta Pixel + Conversions API** na `zzpackage.flexgrafik.nl` **i** `flexgrafik.nl` (śledź checkout Wizarda — to Twoje dane, zanim ruszysz z płatnymi ads).
5. Załóż **własną Grupę FB** powiązaną z Page („ZZP Branding & Zichtbaarheid Rotterdam & omgeving").
6. **10 bazowych treści** gotowych do rotacji (patrz sekcja Must-Have #9).

### FAZA 2 — Capture 24/7 (tydzień 2–4)
Cel: nikt nie odchodzi bez śladu.

1. **Comment-to-DM** na Reels: „Koment *BUS* en ik stuur je het ZZPackage-pakket" → automat z ManyChat (test) **lub** Twój bot Messenger API.
2. **Facebook Lead / Instant Forms** — skonfiguruj teraz (dystrybucja wchodzi dopiero przy płatnych, ale setup jest darmowy).
3. **Facebook Marketplace** — 3 darmowe ogłoszenia regionalne (branding busa / kleding / logo). Gratis lejek lokalny.
4. **Reels pipeline 3×/tydz.** — to Twój główny silnik zasięgu (Reels = jedyny format stale docierający do **nieobserwujących**, +135% zasięgu vs zdjęcia) [posteverywhere.ai](https://posteverywhere.ai/blog/how-to-get-more-facebook-followers).
5. **Stories codziennie** — proces produkcji, „dzisiaj w drukarni Heesch", pakowanie PostNL.

### FAZA 3 — Skalowanie (miesiąc 2–3)
Cel: z „obecny" → „pozyskuję".

1. **Dołącz do 10–15 Grup ZZP/bouw** (np. „Klussenbedrijven Nederland", regionalne „ZZP Bouw Zuid-Holland"). Wartościowe odpowiedzi, nie spam linkiem.
2. **Cross-post** z Twojej Grupy + UGC od klientów (zdjęcie busa klienta na klus → jego rekomendacja).
3. **Partnerzy (ErKa)** — taguj montaże, oni tagują Ciebie = darmowy zasięg z drugiej marki.
4. **Pierwszy budżet paid:** Boost 2–3 najlepszych Reels (€5–10/dzień) + 1 Lead Ad z Instant Form → to moment przejścia „darmowo" → „ROI". Darmowy fundament sprawia, że ten € trafia w przygotowaną lejkę, nie w próżnię.
5. **QuietForge case study:** „Jak zautomatyzowałem własny FB 24/7 i co to dało" → zasilasz leady B2B do QuietForge. Twój FB = lab Twojego produktu.

### FAZA 4 — Pełna automatyzacja przez Business SDK (miesiąc 2+, gdy chcesz kontroli)
1. **App Review** na uprawnienia: `pages_manage_posts`, `pages_messaging`, `leads_retrieval`, `ads_management`, `pages_read_engagement`.
2. **Własny scheduler** podpięty do **Agent OS** → publikacja portfolio przed/po automatycznie, gdy dodasz realizację do Jadzia COI.
3. **Webhook na leady** → Instant Form → **Wizard** → Jadzia COI → human approval gate (masz to już w architekturze).
4. **Self-hosted bot Messenger** bez limitu 25 kontaktów ManyChat — z Twoją polityką HITL.

---

## 4. 10 MUST-HAVE dla Twojego konta FB

### 1. 🔧 Meta Business Suite + połączony Page ↔ IG Professional
- **Co:** darmowe centrum dowodzenia (scheduling nieograniczony, Inbox, Insights) [thestacc.com](https://thestacc.com/best/free-social-media-scheduling-tools/).
- **Dlaczego:** 0 €, brak limitu postów, jedna publikacja na FB+IG, brak kary za scheduling.
- **Limit:** planowanie FB do ~29–30 dni w przód, IG do 75 dni, max 25 postów/dzień.
- **Akcja:** `business.facebook.com` → przypisz Page + IG Professional jako Business Portfolio.

### 2. 🏷️ Strona Page w pełni zoptymalizowana i **holenderskojęzyczna**
- **Kategorie:** Print/Design, Vehicle Branding, Workwear, Sign Company.
- **O nas:** propozycja wartości NL („Van anonieme vakman naar professioneel merk — in 10 werkdagen").
- **Przycisk akcji:** „Stuur ons een bericht" → Messenger **lub** bezpośrednio → `zzpackage.flexgrafik.nl/wizard/`.
- **Lokalizacja:** Rotterdam (siedziba) + Heesch (produkcja) — local SEO w FB.
- **Język treści:** **Nederlands.** Twój profil PL zostaje osobisty; **Page jest narzędziem biznesowym dla NL rynku.**
- **Tryb Profesjonalny / Professional Mode** na profilu osobistym = opcja, ale Page daje reklamę i Insights.

### 3. 💬 Auto-odpowiedzi w Messenger 24/7
- **Co:** Away message + welcoming menu nawet o 02:00.
- **Setup:** Meta Business Suite → Inbox → Automations, **lub** ManyChat, **lub** Twój bot.
- **Treść:** powitanie NL → 3 opcje: ① „Configureer je pakket" (→ Wizard), ② „Vraag offerte" (→ formularz), ③ „WhatsApp" (+31 6 87286151).
- **Efekt:** lead o 3 w nocy rano nie ucieka do konkurencji.

### 4. 📊 Meta Pixel + Conversions API na Wizardzie
- **Co:** kod śledzący konwersje (rozpoczęcie checkout, zakup w Wizardzie).
- **Dlaczego dziś, przed płatnymi:** gromadzisz dane i uczysz piksela, żeby gdy odpalisz ads, od pierwszego dnia były celowane. CAPI (server-side) = bypass ad-blockerów + zgodność z RODO.
- **Akcja:** Meta Events Manager → Pixel na `zzpackage.flexgrafik.nl` + `flexgrafik.nl`.

### 5. 👥 Własna Grupa FB powiązana z Page
- **Dlaczego #1 na tej liście z punktu widzenia zasięgu:** Grupy mają **10–15× większy zasięg organiczny niż Page** (20–40% vs 1–6%) [fbgroupbulkposter.com](https://fbgroupbulkposter.com/blog/facebook-organic-reach-2026).
- **Nazwa:** „ZZP Branding & Meer Zichtbaarheid — Rotterdam & NL".
- **Model:** wartość (tipy: „Hoe herkenbaar is jouw bus op 50m?"), Case study klientów, pytań-community.
- **Automation:** cross-post treści Page → Grupa.

### 6. 🤖 Comment-to-DM automation na Reels
- **Jak działa:** komentarz słowem-kluczem („BUS", „PAKKET", „KORTING") → automat wysyła DM z linkiem do Wizarda i kodem z Twojej gry (Branding Game).
- **Narzędzie:** ManyChat (test) **lub** własny flow przez Messenger API (Tor B).
- **Efekt:** zamieniasz zasięg Reels (oglądanie) w leads (DM z danymi).
- ⚠️ **Limit 2026:** ManyChat free = **25 aktywnych kontaktów/mies.** — na test, nie na produkcję [setsmart.io](https://setsmart.io/blog/manychat-pricing). Dla skali → własny bot lub ManyChat Essential ($14/mies.).

### 7. 🎬 Silnik treści Reels 3×/tydzień
- **Dlaczego:** Reels = jedyny format stale docierający do nieobserwujących; +135% zasięgu vs zdjęcia; algorytm faworyzuje short-form video [posteverywhere.ai](https://posteverywhere.ai/blog/how-to-get-more-facebook-followers).
- **Pillery treści (rotacja):**
  1. **Przed/po busa** (najmocniejszy — wizualny proof).
  2. **Proces 5 kroków** (Wizard → zapłata → produkcja Heesch → PostNL).
  3. **Edukacja NL:** „3 manieren waarop jouw bus klanten wint" / „Hoe herkenbaar ben jij op de klus?".
  4. **UGC:** klient + jego obklejony bus.
- **Narzędzie:** CapCut (gratis), Canva Free, oryginalny dźwięk (komercyjny = brak auto-publish przez API).

### 8. 🛒 Marketplace + Events (darmowy lokalny lejek)
- **Marketplace:** 3 stale aktualizowane ogłoszenia (Wagenbelettering / Werkkleding / Logo-ontwerp) zasięg = lokalny, darmowy, konwertujący dla trades.
- **Events:** darmowe wydarzenie „ZZP Branding Check Rotterdam" — nawet wirtualne, generuje zasięg i listę zainteresowanych.

### 9. 🗂️ Zapas 30 dni treści w Plannerze + content pillars
- **Co:** nigdy nie publikuj „z głowy pod ścianę". Zaplanuj blok 30 dni w Meta Business Suite Planner.
- **Bank treści (10 sztuk startowych):**
  1. Przed/po busa — instalateur
  2. Przed/po busa — dakdekker
  3. „10 werkdagen levering" — proces
  4. FAQ: „Wat zit er in een ZZPackage?"
  5. Materiały premium (3M/Avery) — dlaczego trwałość
  6. Werkkleding borduuren vs druk — różnica
  7. Bouwbord A3 na klus → leads z sąsiedztwa
  8. Testimonial klienta
  9. „Wizard in 2 minuten" — screen recording
  10. Gra → kod rabatowy (łączy FB z Branding Game)

### 10. ⚙️ App Review Business SDK + własny scheduler (Twój as w rękawie)
- **Co:** formalna aplikacja Meta App Review na uprawnienia biznesowe.
- **Dlaczego:** odblokowuje `pages_manage_posts`, `pages_messaging`, `leads_retrieval`, `ads_management` — wtedy Twój **Agent OS** publikuje, odpowiada i zbiera leady 24/7 bez jakichkolwiek limitów ManyChat.
- **Integracja:** lead z Instant Form → webhook → Wizard → Jadzia COI → human approval (HITL, jak już masz w architekturze QuietForge).
- **Efekt:** kompletny, darmowy, własny system automatyzacji FB = **zarówno przewaga operacyjna FlexGrafik, jak i sprzedawalny produkt QuietForge.**

---

## 5. Darmowy „stack" — co dokładnie kosztuje 0 €

| Narzędzie | Rola | Koszt | Limit 2026 |
|---|---|---|---|
| **Meta Business Suite** | Scheduling + Inbox + Insights FB+IG | 0 € | Nieograniczony (FB ~30 dni w przód) |
| **Meta Pixel + Conversions API** | Śledzenie konwersji Wizarda | 0 € | Brak |
| **ManyChat** (Free) | Messenger/IG chatbot (test) | 0 € | **25 aktywnych kontaktów/mies.** |
| **Facebook Business SDK** (Python/Node/PHP) | Własny scheduler + bot + leady | 0 € | Wymaga App Review |
| **Metricool** (Free) | Analytics cross-platform | 0 € | 50 postów/mies., 1 marka |
| **CapCut** | Montaż Reels | 0 € | Brak |
| **Canva Free** | Grafiki, szablony | 0 € | Brak |
| **WhatsApp Business** | Kanał konwersji obok Messenger | 0 € | Brak (już masz +31 6 87286151) |
| **Meta Business Agent** (AI) | Autonomiczny AI do wsparcia sprzedaży | 0 € start, **token-billing** na WhatsApp [techcrunch.com](https://techcrunch.com/2026/06/03/metas-ai-agent-for-whatsapp-business-is-now-available-globally/) | Globalnie od 3.06.2026 |

---

## 6. Surowa prawda o „darmowo 24/7 pozyskiwanie klientów"

- ✅ **24/7 obecność i capture** — w pełni realne za darmo (auto-odpowiedzi, scheduling, Pixel, comment-to-DM). Nikt nie ucieka.
- ✅ **Zasięg organiczny** — możliwy, ale realistycznie **~1,65% followersów Page** na post [posteverywhere.ai](https://posteverywhere.ai/blog/how-the-facebook-algorithm-works). **Grupy i Reels** to Twoje dźwignie.
- ⚠️ **Skala leadów** — bez płatnych reklam nie następuje. Darmowy fundament przygotowuje lejek; pierwszy budżet paid (€5–10/dzień) w miesiącu 2–3 to mnożnik, nie koszt.
- 💡 **Twoja przewaga konkurowania:** większość konkurencji płaci za SaaS. Ty **budujesz własny** automation (QuietForge) — więc Twój koszt krańcowy automatyzacji FB dąży do zera, a sam system staje się **produktem do sprzedaży** B2B.

---

## 7. Pierwszy krok — DZIŚ (checklista ~2h)

- [ ] Załóż/przypisz **Facebook Page** dla FlexGrafik (NL) w Meta Business Suite
- [ ] Połącz **Instagram Professional** (NL)
- [ ] Ustaw **Away/Welcome auto-odpowiedź** Messenger z 3 opcjami (Wizard / offerte / WhatsApp)
- [ ] Wstaw **Meta Pixel** na `zzpackage.flexgrafik.nl`
- [ ] Wrzuć **3 pierwsze treści** (przed/po busa + proces + FAQ) i zaplanuj na najbliższy tydzień
- [ ] Załóż **Grupę FB** „ZZP Branding — Rotterdam & NL" i powiąż z Page

> Gdy to masz, daj znać — wchodzimy w **Tor B (Business SDK)**: przygotuję Ci scope App Review i szkic scheduler-a podpiętego pod Twój Agent OS, tak żeby Wizard, Jadzia COI i Messenger działały jako jeden pipeline z human-approval.

---

*Uwaga: poprawny adres Wizarda to `zzpackage.flexgrafik.nl` (we wpisie pojawiła się literówka „flexgrafk").*
*Źródła danych 2026: posteverywhere.ai, socialinsider.io, fbgroupbulkposter.com, thestacc.com, messengerbot.app, setsmart.io, techcrunch.com, theverge.com.*
