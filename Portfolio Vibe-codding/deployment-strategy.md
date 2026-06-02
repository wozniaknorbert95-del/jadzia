# Strategia Wdrożenia — Cohesion TODO Ekosystem FlexGrafik

**Data:** 21.03.2026 | **Autor:** AG (Antigravity)  
**Scope:** 3 moduły — APP, FLEX, ZZP | ~62 zadania łącznie

---

## 1. Myśl przewodnia — 1 projekt naraz (NIE równolegle)

> [!IMPORTANT]
> **Rekomendacja: jeden moduł na raz, nie 3 jednocześnie.**
>
> Uruchamianie agenta na 3 projektach równocześnie przy zasadzie 1-1-1 to przepis na chaos. Każda sesja powinna mieć **jeden kontekst, jeden branch, jeden deploy**.

**Dlaczego NIE równolegle:**
- Wiele zadań cross-domain dotyczy TYCH SAMYCH plików (`footer.php`, `header.php`, `fg-design-system.css`)
- Merge konflikty między branchami
- Dowódca musi osobno deployować każdy moduł — 3 równoległe = chaos ręcznego FTP
- Agent traci kontekst skacząc między 3 różnymi tech stackami (React/Vite, WP/Astra, WP/custom theme)

---

## 2. Kolejność modułów — REKOMENDOWANA

```
Faza 1 → ZZP (zzpackage.flexgrafik.nl)   ← ZACZNIJ TUTAJ
Faza 2 → FLEX (flexgrafik.nl)
Faza 3 → APP (app.flexgrafik.nl)
```

**Dlaczego ZZP pierwsza?**
- ZZP to **główny lejek sprzedażowy** — każdy dzień bez spójności = potencjalna utrata konwersji
- ZZP ma `ZZP-002` (cart persistence bug) — **krytyczny bug biznesowy**, blokuje sprzedaż
- ZZP ma `ZZP-003` (iDEAL SVG 404) — **blokuje checkout**
- Style z ZZP stają się wzorcem dla FLEX i APP (te przejmują `fg-design-system.css`)

**Dlaczego FLEX druga?**
- flexgrafik.nl to strona-matka ekosystemu, ale nie ma krytycznych bugów płatności
- Tłumaczenie EN→NL (`FLEX-002`) jest długie (~3-5 dni z Gemini CLI) — można ją zlecić równolegle gdy pracujesz nad APP
- FLEX jest na WordPress — podobny stack do ZZP, więc wiedza przenosi się płynnie

**Dlaczego APP ostatnia?**
- APP jest na Vite/React — odrębny tech stack, wymaga innego kontekstu
- Główne zadanie (`APP-001` — PL→NL) to ~3-5 dni z Gemini CLI, można zaplanować wcześniej
- APP nie blokuje sprzedaży — jest grą, nie sklepem

---

## 3. Scope P1 per moduł — co zrobić TERAZ

### 🟥 ZZP — P1 (najpierw!) | ~18h łącznie

| ID | Zadanie | Czas |
|----|---------|------|
| `ZZP-002` | **Cart persistence bug** | 2h |
| `ZZP-003` | **iDEAL SVG 404 fix** | 1h |
| `ZZP-001` | Weryfikacja KvK footer | 30min |
| `ZZP-W1-001` | Lockup logo w headerze | 2h |
| `ZZP-W1-002` | Meta-title standard | 30min |
| `ZZP-W1-003` | Favicon F-magenta | 30min |
| `ZZP-W2-001` | Legacy neon CSS cleanup | 2h |
| `ZZP-W2-002` | CSS Custom Properties | 1h |
| `ZZP-W5-001` | Wizard layout padding | 2h |
| `ZZP-W6-001` | Migracja `.fg-button` | 3h |
| `ZZP-W6-002` | Inputs `.fg-input` | 2h |
| `ZZP-W7-001` | Header cross-domain | 2h |
| `ZZP-W7-002` | Sekcja cross-promo gry | 2h |
| `ZZP-W9-001` | Wizard mobile touch 44px | 3h |
| `ZZP-W9-002` | iOS input fix | 2h |
| `ZZP-W10-003` | Zero JS errors checkout | 2h |

### 🟧 FLEX — P1 | ~17h łącznie

| ID | Zadanie | Czas |
|----|---------|------|
| `FLEX-001` | **Logo 404 fix** | 1h |
| `FLEX-003` | Ciemne tło wszystkich podstron | 2h |
| `FLEX-W1-001` | Lockup logo w headerze | 2h |
| `FLEX-W1-002` | Meta-title standard | 30min |
| `FLEX-W1-003` | Favicon F-magenta | 30min |
| `FLEX-W2-001` | Legacy neon CSS cleanup | 2h |
| `FLEX-W2-002` | CSS Custom Properties | 1h |
| `FLEX-W3-001` | Google Fonts Montserrat+Inter | 30min |
| `FLEX-W3-002` | Font tokens CSS | 1h |
| `FLEX-W6-001` | Migracja `.fg-button` | 3h |
| `FLEX-W6-002` | Formularze CF7 `.fg-input` | 2h |
| `FLEX-W7-001` | Header cross-domain | 2h |
| `FLEX-W7-002` | Hero dwa NL CTA | 2h |
| `FLEX-W9-001` | iOS input fix | 1h |
| `FLEX-W10-001` | Obrazy WebP + lazy-load | 3h |
| `FLEX-W10-002` | Preconnect + font-display | 2h |

### 🟦 APP — P1 | ~16h łącznie

| ID | Zadanie | Czas |
|----|---------|------|
| `APP-001` | **PL→NL tłumaczenie UI** | 3-5 dni |
| `APP-002` | Cross-link do Wizarda na game-over | 2h |
| `APP-003` | Trust signals footer | 1h |
| `APP-W1-001` | Lockup FlexGrafik w headerze | 3h |
| `APP-W1-002` | Pisownia FlexGrafik fix | 30min |
| `APP-W1-003` | Meta-title standard | 30min |
| `APP-W1-004` | Favicon F-magenta | 30min |
| `APP-W2-001` | Legacy neon cleanup TypeScript | 2h |
| `APP-W2-002` | Tło menu #070707 | 30min |
| `APP-W3-001` | Google Fonts w index.html | 1h |
| `APP-W7-001` | Top-bar gry cross-domain | 3h |
| `APP-W7-002` | Victory/Game Over CTA | 2h |
| `APP-W9-001` | Touch targets 44px | 2h |
| `APP-W9-002` | iOS input fix | 1h |
| `APP-W10-001` | Code-split Vite | 3h |
| `APP-W10-002` | Preconnect + manifest PWA | 1h |

---

## 4. Elementy blokujące (czekające na materiały)

> [!WARNING]
> Te zadania NIE mogą się zacząć bez materialów od Norberta. Przygotuj je z wyprzedzeniem!

| Zadanie | Czego brakuje |
|---------|--------------|
| Favicon F-magenta (wszystkie 3 moduły) | Plik `favicon-magenta-F.ico` / `.png` (32×32, 180×180) |
| ZZP-005 / APP-W4-002 | Finalne grafiki kategorii produktów |
| FLEX-001 | Upload `Logooo FlexGrafik.webp` na Cyber-Folks FTP |
| ZZP-003 / APP-W1-004 | Upload nowego favicon na serwer |
| FLEX-008 | Zdjęcia portfolio (min. 5 realizacji before/after) |
| APP-W4-003 | Logotypy 3M, Oracal, Mimaki jako grayscale PNG |
| FLEX-002 / APP-001 | Tłumaczenia Gemini CLI (uruchomić **teraz** równolegle do pracy nad ZZP!) |

---

## 5. Taktyka — jak prowadzić sesje

### Schemat jednej sesji (zasada 1-1-1):

```
1. Uruchom AG na JEDNYM projekcie (np. zzpackage)
2. AG bierze JEDNO zadanie z listy P1
3. AG robi changes → diff → commit (feat: ZZP-002 fix cart persistence)
4. Norbert deploy ręcznie na Cyber-Folks
5. Weryfikacja → następne zadanie
```

### Sugerowany rytm tygodniowy:
- **Poniedziałek–środa:** ZZP P1 (krytyczne bugi + tokeny CSS + .fg-button)
- **Czwartek–piątek:** ZZP P2 + start FLEX P1
- **Równolegle (async):** Uruchom Gemini CLI dla tłumaczeń FLEX-002 i APP-001

---

## 6. Archimedyczny punkt startowy — PIERWSZE zadanie

Zacznij od: **`ZZP-002` — Cart persistence bug**

- Bezpośredni wpływ na sprzedaż
- Ograniczony scope: `zzp-wizard-core.js` + `zzp-checkout.js`
- Wyraźne kryterium sukcesu: produkty z Wizarda = produkty na checkout

---

## 7. Ulepszony prompt dla Antigravity

Poniżej gotowy prompt do wklejenia w nowej sesji AG:

---

```
Cześć AG. Nowa sesja — projekt: zzpackage.flexgrafik.nl

## Kontekst
Zakończyliśmy audyt spójności ekosystemu (3 domeny). Mamy gotowe pliki:
- docs/audyt-spojnosci/cohesion-todo-ZZP.md (backlog zadań)
- docs/audyt-spojnosci/style-rules-ZZP.md (reguły stylu)
- docs/audyt-spojnosci/global-style-rules.md (tokeny systemowe)

## Cel tej sesji
Zadanie: ZZP-002 — Cart persistence bug
Plik: zzp-wizard-core.js + zzp-checkout.js
Problem: Produkty wybrane w Wizardzie znikają przed checkout (sessionStorage / WC cart API)
Branch: feature/zzp-002-cart-persistence

## Zasady (nie pytaj o nie — są niezmienne)
- Zasada 1-1-1: jedno zadanie, jeden commit, jeden ręczny deploy przez Norberta
- Stack: WordPress + WooCommerce na Cyber-Folks (PHP, nie Node)
- Deploy: TYLKO ręcznie przez Norberta — nie proponuj auto-deploy
- Język kodu: EN | Komentarze: EN | Komunikacja ze mną: PL

## Czego oczekuję
1. Przeczytaj cohesion-todo-ZZP.md §ZZP-002
2. Przeczytaj brain-zzp.md §13 (bekende issues)
3. Zaproponuj diagnozę i plan naprawy (nie kod — najpierw plan)
4. Czekaj na moje potwierdzenie przed implementacją

Confirm scope przed startem.
```

---

### Wariant dla FLEX (po zakończeniu ZZP):

```
Cześć AG. Nowa sesja — projekt: flexgrafik.nl (WordPress)

## Kontekst
Zakończyliśmy ZZP P1. Teraz: flexgrafik.nl
Pliki: cohesion-todo-FLEX.md + style-rules-FLEX.md + global-style-rules.md

## Cel tej sesji  
Zadanie: FLEX-001 — Logo 404 fix
Plik: header.php, assets/images/
Problem: Logooo-FlexGrafik.png daje 404 — strona-matka bez logo
Branch: feature/flex-001-logo-fix

## Zasady
[identyczne jak wyżej]

## Czego oczekuję
1. Przeczytaj cohesion-todo-FLEX.md §FLEX-001
2. Przeczytaj brain-flex.md §KRITIEKE ISSUES
3. Zaproponuj plan naprawy z listą plików do zmiany
4. Czekaj na potwierdzenie

Confirm scope.
```

### Wariant dla APP (Vite/React):

```
Cześć AG. Nowa sesja — projekt: app.flexgrafik.nl (Vite + React)

## Kontekst
Pliki: cohesion-todo-APP.md + style-rules-APP.md + global-style-rules.md

## Cel tej sesji
Zadanie: APP-W1-002 — Pisownia FlexGrafik fix (search & replace)
Pliki: index.html, src/constants.ts, src/gameMessages.ts
Problem: "Flexgrafik" zamiast "FlexGrafik" — błędna pisownia w całym projekcie
Branch: feature/app-w1-002-branding-typo

## Zasady
- Stack: Vite + React + TypeScript
- Deploy: npm run build → Norbert wysyła dist/ na serwer
- Zasada 1-1-1 obowiązuje

## Czego oczekuję
1. Grep dla "Flexgrafik" (małe g) w całym projekcie
2. Pokaż mi listę plików z wynikami
3. Czekaj na potwierdzenie przed replace

Confirm scope.
```

---

*Deployment Strategy V1.0 | 21.03.2026 | AG Brand Agency*
