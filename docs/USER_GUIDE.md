# USER GUIDE — JADZIA (ZZPackage WooCommerce)

## 1. Wprowadzenie

### 1.1 Co to jest Jadzia i do czego służy

Jadzia to asystent (AI agent) działający przez Telegram, który pomaga Ci wprowadząć zmiany w sklepie **ZZPackage** (WooCommerce) pod adresem `https://zzpackage.flexgrafik.nl`.  
Najważniejsze: Jadzia **modyfikuje pliki sklepu przez SSH** (np. CSS, PHP w motywie), a potem pokazuje Ci, co zmienia — zanim to wdroży.

Przykłady tego, w czym Jadzia jest dobra:
- ✅ zmiana kolorów i stylów (CSS)
- ✅ poprawki tekstów, etykiet, opisów
- ✅ drobne poprawki logiki w PHP (np. ukrycie elementu, zmiana komunikatu)
- ✅ uporządkowane wdrażanie: pokazanie różnic, backup, możliwość cofnięcia

### 1.2 Dla kogo jest ten przewodnik

Ten przewodnik jest dla Ciebie — **FlexGrafik** — czyli osoby nietechnicznej, która szybko się uczy i chce:
- wprowadzać zmiany bez “grzebania w kodzie” ręcznie
- mieć kontrolę: co się zmienia, gdzie i jak to cofnąć
- robić to bezpiecznie i krok po kroku

### 1.3 Co Jadzia robi, a czego nie robi (granice systemu)

**Jadzia może:**
- ✅ edytować pliki w motywie (głównie w motywie child)
- ✅ tworzyć backupy przed zapisem
- ✅ pokazać różnice (co się zmieniło)
- ✅ pomóc w diagnozie, gdy coś nie działa

**Jadzia nie powinna (i Ty też tego nie zlecaj), chyba że wiesz co robisz:**
- ❌ “zrób wszystko naraz” (duże zmiany są ryzykowne)
- ❌ edycja krytycznych plików bez jasnej instrukcji i testu
- ❌ zmiany w wielu miejscach bez planu i bez weryfikacji

💡 Zasada: **małe kroki** → **test** → dopiero następny krok.

### 1.4 Słowniczek (krótkie, nietechniczne definicje)

- **Motyw (theme)**: wygląd i część zachowania sklepu (szablony).
- **Motyw child**: “nakładka” na motyw, w której robimy zmiany, żeby nie zniknęły po aktualizacji.
- **CSS**: styl (kolory, czcionki, odstępy, przyciski).
- **PHP**: logika (co się wyświetla, kiedy, jakie komunikaty).
- **Backup**: kopia pliku sprzed zmiany. Dzięki temu można szybko cofnąć.
- **Diff / różnice**: pokazanie “co było” vs “co będzie”.
- **Wdrożenie**: zapis zmian na serwerze (sklep zaczyna działać z nową wersją plików).

### 1.5 Najważniejsze zasady bezpieczeństwa (TL;DR) ⚠️

- ⚠️ **Zawsze czytaj podsumowanie zmian** zanim klikniesz “TAK”.
- ✅ **Testuj po wdrożeniu**: strona główna, produkt, koszyk, checkout.
- 🔄 Jeśli coś jest nie tak: **/cofnij natychmiast**.
- 📝 Zlecaj zmiany **konkretnie**: co, gdzie i jak ma wyglądać.
- 💡 Rób **jedną zmianę na raz** (albo serię małych kroków).

---

## 2. Jak zacząć (pierwsze uruchomienie i podstawy)

### 2.1 Jak pisać polecenia, żeby działały za pierwszym razem

Najlepsze polecenia to takie, które odpowiadają na 3 pytania:
- 📝 **CO** chcesz zmienić? (np. kolor przycisku “Dodaj do koszyka”)
- 📝 **GDZIE**? (np. strona produktu, koszyk, checkout, stopka)
- 📝 **JAK** ma wyglądać? (kolor, rozmiar, zachowanie, przykład)

Przykład dobrego polecenia:

```text
/zadanie
Na stronie produktu zmień kolor przycisku "Dodaj do koszyka" na #0B63F6,
a po najechaniu (hover) na #084BB5. Zostaw biały tekst i zaokrąglenie jak jest.
```

Przykład zbyt ogólnego polecenia:

```text
Zrób ładniej przyciski.
```

💡 Jeśli nie wiesz jak to opisać — dodaj:
- link do strony
- nazwę elementu (np. “button Add to cart”)
- krótki opis “jak jest teraz” i “jak ma być”

### 2.2 Najważniejsze komendy (ściąga)

Poniżej masz komendy, które realnie przydają się na co dzień:

| Komenda | Do czego służy | Kiedy używać |
|---|---|---|
| `/pomoc` | Lista komend i krótkie wyjaśnienie | Gdy nie pamiętasz komend |
| `/status` | Status agenta / czy są aktywne operacje | Gdy nie wiesz “co teraz” |
| `/zadanie` | Start nowej zmiany (Twoje polecenie) | Zawsze, gdy zaczynasz zmianę |
| `/skanuj` | Skan struktury projektu (WPExplorer) | 💡 Nowość: po większych zmianach w motywie |
| `/cofnij` | Cofnięcie ostatnich zmian | 🔄 Gdy coś się zepsuło |
| `/clear` | Awaryjne wyczyszczenie stanu | Gdy agent “utknął” |
| `/test` | Test połączenia SSH | Gdy pojawiają się problemy z połączeniem |

⚠️ W praktyce: najczęściej użyjesz `/zadanie`, potem potwierdzisz zmiany, a jeśli coś nie gra — `/cofnij`.

### 2.3 Jak wygląda typowy “cykl zmiany” (od prośby do wdrożenia)

Najczęstszy flow wygląda tak:

1) 📝 Ty wysyłasz polecenie (np. przez `/zadanie` + opis)  
2) Jadzia przygotowuje plan lub propozycję zmian  
3) Jadzia pokazuje **podsumowanie i diff** (co konkretnie zmieni)  
4) ✅ Ty odpowiadasz “TAK” (albo “NIE”)  
5) Jadzia zapisuje pliki na serwerze, robi backupy i kończy operację  
6) Ty testujesz sklep (Ctrl+F5, koszyk, checkout)  
7) Jeśli OK → kolejna zmiana. Jeśli nie → 🔄 `/cofnij`.

### 2.4 Jak rozpoznawać momenty, gdy Jadzia “czeka na Twoje TAK/NIE” ✅ ❌

Zazwyczaj Jadzia zadaje pytanie typu:
- “Potwierdzasz zmiany?”
- “Czy mam to wdrożyć?”
- “Czy wykonać deploy?”

Wtedy:
- ✅ odpowiadasz **TAK / OK** jeśli wszystko wygląda dobrze
- ❌ odpowiadasz **NIE** jeśli coś Ci się nie podoba lub chcesz doprecyzować

💡 Jeśli nie jesteś pewien — poproś o doprecyzowanie:

```text
Pokaż proszę dokładnie, które pliki zmieniasz i dlaczego.
```

### 2.5 Najczęstsze błędy użytkowników i jak ich uniknąć

| Błąd | Co się dzieje | Jak tego uniknąć 💡 |
|---|---|---|
| “Zmień wszystko” | Za dużo ryzyka naraz | Dziel zmianę na kroki |
| Brak miejsca “gdzie” | Agent zgaduje | Podaj: strona produktu/koszyk/checkout |
| Brak konkretu “jak” | Efekt nie taki jak chcesz | Podaj kolory, rozmiary, przykład |
| Brak testu po wdrożeniu | Problem wychodzi za późno | Zawsze testuj koszyk/checkout |
| Zbyt późne cofnięcie | Więcej szkód | 🔄 Cofnij od razu, potem diagnoza |

---

## 3. Przykłady użycia (gotowe prompty + oczekiwany efekt)

### 3.1 Jak opisywać: CO, GDZIE, JAK MA WYGLĄDAĆ 📝

Masz prosty szablon do kopiowania:

```text
/zadanie
CO: [co zmienić]
GDZIE: [na jakiej stronie / sekcji]
JAK: [kolor / zachowanie / przykład]
UWAGI: [czego nie ruszać]
```

Przykład dla e-commerce:

```text
/zadanie
CO: Zmień tekst przycisku w koszyku z "Proceed to checkout" na "Przejdź do kasy"
GDZIE: koszyk
JAK: Tylko tekst, bez zmian stylu
UWAGI: Nie ruszaj innych tłumaczeń
```

### 3.2 Kategorie przykładów (zanim skopiujesz prompt — co sprawdzić)

Zanim zlecisz zmianę:
- ✅ czy wiesz, gdzie jest problem (strona produktu/koszyk/checkout)?
- ✅ czy wiesz, jak to ma wyglądać docelowo?
- ⚠️ czy to nie dotyka płatności lub checkout? (wyższe ryzyko)

#### 3.2.1 Proste (kolor, tekst, rozmiar)

**Przykład 1 — kolor przycisku “Dodaj do koszyka”**

```text
/zadanie
Na stronie produktu ustaw przycisk "Dodaj do koszyka" na kolor #0B63F6.
Hover: #084BB5. Tekst biały. Bez zmiany rozmiaru.
```

**Przykład 2 — większy odstęp w sekcji opinii**

```text
/zadanie
Na stronie produktu dodaj większy odstęp (margin-top 24px) nad sekcją opinii.
Tylko CSS, bez PHP.
```

**Przykład 3 — poprawa tekstu w stopce**

```text
/zadanie
W stopce zmień tekst "All rights reserved" na "Wszelkie prawa zastrzeżone".
Zostaw resztę bez zmian.
```

#### 3.2.2 Średnie (ukrycie elementu, dodanie pola)

**Przykład 1 — ukrycie elementu “SKU” na stronie produktu**

```text
/zadanie
Na stronie produktu ukryj wyświetlanie SKU (numeru produktu).
Najlepiej przez CSS, jeśli to możliwe.
```

**Przykład 2 — dodanie pola informacyjnego pod ceną**

```text
/zadanie
Na stronie produktu dodaj pod ceną krótką informację:
"Wysyłka w 24-48h. Masz pytanie? Napisz do nas."
Styl: mniejsza czcionka, szary kolor (#666).
```

**Przykład 3 — banner informacyjny w koszyku**

```text
/zadanie
W koszyku dodaj banner nad listą produktów:
"Darmowa dostawa od 199 zł".
Ma wyglądać jak prosty pasek: tło #F3F6FF, tekst #0B63F6, padding 12px.
```

#### 3.2.3 Zaawansowane (zmiana logiki checkout, email)

⚠️ Te zmiany mają większe ryzyko. Rób je w małych krokach i testuj.

**Przykład 1 — walidacja pola w checkout**

```text
/zadanie
W checkout: jeśli numer telefonu jest pusty, pokaż komunikat:
"Proszę podać numer telefonu do kuriera."
Nie zmieniaj metod płatności ani dostawy.
```

**Przykład 2 — zmiana komunikatu po złożeniu zamówienia**

```text
/zadanie
Na stronie "Dziękujemy za zamówienie" dodaj podziękowanie:
"Dziękujemy! Jeśli potrzebujesz faktury, odpisz na maila potwierdzającego."
Tylko dodanie tekstu, bez przebudowy strony.
```

**Przykład 3 — email (ostrożnie)**

```text
/zadanie
W mailu potwierdzającym zamówienie dodaj na końcu zdanie:
"W razie pytań odpisz na tę wiadomość."
Jeśli to zbyt ryzykowne, zaproponuj alternatywę bez modyfikacji emaili.
```

### 3.3 Tabela: “Jak napisać polecenie” vs “Czego unikać” (porównanie)

| ✅ Dobrze | ❌ Źle |
|---|---|
| “Na stronie produktu zmień kolor przycisku na #0B63F6 i hover #084BB5” | “Zmień kolor przycisków” |
| “W koszyku ukryj SKU, najlepiej CSS” | “Usuń zbędne rzeczy” |
| “W checkout dodaj walidację telefonu, nie ruszaj płatności” | “Popraw checkout” |
| “Dodaj banner o darmowej dostawie, tło #F3F6FF” | “Dodaj banner” |

---

## 4. /skanuj (WPExplorer) — kiedy i jak używać

### 4.1 Co robi skan i co powstaje po skanie (projektowa “mapa”)

Komenda `/skanuj` to **nowość** 🔄 — właśnie wdrożona.  
Jej zadanie to przeskanowanie struktury Twojego motywu (i powiązań w plikach), żeby Jadzia:
- lepiej rozumiała, gdzie są ważne pliki
- szybciej trafiała w właściwe miejsca
- zmniejszyła ryzyko “zgadywania”

Po skanie powstaje plik (mapa projektu):

```text
agent/context/project_structure.json
```

W skrócie: to “mapa” Twojego motywu **hello-theme-child-master**: pliki, zależności, hooki.

### 4.2 Kiedy uruchamiać /skanuj (rekomendacje + limity)

Rekomendacje:
- ✅ raz dziennie wystarczy
- ✅ po większych zmianach w motywie (np. dodanie wielu plików)
- ✅ gdy Jadzia “nie trafia” w dobre pliki lub gubi kontekst

⚠️ Nie nadużywaj:
- jeśli nic się nie zmieniało — skan nie jest potrzebny
- jeśli masz małe zmiany CSS/tekstu — zwykle nie ma sensu robić skanu

### 4.3 Czego oczekiwać po /skanuj (czas, komunikaty, możliwe ostrzeżenia)

Po wpisaniu:

```text
/skanuj
```

Zobaczysz komunikat o wyniku. Czas zależy od:
- liczby plików w motywie
- szybkości połączenia SSH
- rozmiaru katalogu (pobierany jest pakiet tar.gz)

Typowe czasy:
- ✅ mały motyw: 20–60 sekund
- ⚠️ większy motyw: 1–3 minuty

### 4.4 Co zrobić, jeśli /skanuj się nie uda (krótka ścieżka diagnostyki) ⚠️

Jeśli `/skanuj` zwraca błąd:

1) ✅ Uruchom `/test` (czy SSH działa)  
2) 📝 Zrób screenshot lub skopiuj komunikat błędu  
3) 💡 Sprawdź logi (jeśli masz dostęp), albo wklej błąd do supportu/diagnostyki  
4) 🔄 Jeśli to było po wdrożeniu zmian w sklepie i coś nie działa — `/cofnij`

### 4.5 Tabela: “Objaw” → “Co to znaczy” → “Co zrobić”

| Objaw | Co to znaczy | Co zrobić ✅ |
|---|---|---|
| “SSH timeout” | Połączenie z serwerem zbyt wolne / przerwane | Spróbuj ponownie, potem `/test` |
| “Download failed” | Problem z pobraniem paczki (tar.gz) | Spróbuj ponownie, sprawdź logi |
| “Permission denied” | Brak dostępu do ścieżki | Sprawdź konfigurację ścieżek |
| “No files found” | Motyw pusty lub zła ścieżka | Zweryfikuj motyw/ścieżkę |

---

## 5. Best Practices

### 5.1 Przed zleceniem zmiany (checklista)

- [ ] Sprawdź czy to naprawdę potrzebne
- [ ] Opisz dokładnie **CO i GDZIE** 📝
- [ ] Przygotuj screenshot (opcjonalnie) 📝
- [ ] Sprawdź czy backup działa (`/status` po ostatniej zmianie) ✅

💡 Przykład “dobrego startu”:

```text
/zadanie
Na stronie koszyka: chcę ukryć pole kuponu, ale zostawić informację o darmowej dostawie.
Nie ruszaj checkout.
```

### 5.2 Po wdrożeniu (checklista)

- [ ] Sprawdź zmianę na stronie (Ctrl+F5) ✅
- [ ] Przetestuj funkcjonalność (np. koszyk nadal działa) ✅
- [ ] Jeśli OK — możesz zlecić kolejną zmianę ✅
- [ ] Jeśli NIE — `/cofnij` natychmiast ❌

💡 Minimalny test po wdrożeniu:
- strona główna
- strona produktu
- koszyk
- checkout (bez płatności, jeśli nie trzeba — wystarczy dojść do ostatniego kroku)

### 5.3 Bezpieczeństwo

#### 5.3.1 Co Jadzia może zepsuć ⚠️

- ⚠️ pliki krytyczne (np. `functions.php`)
- ⚠️ logikę checkout (płatności, wysyłki, walidacje)
- ⚠️ integracje (np. zewnętrzne API, płatności)

#### 5.3.2 Jak się chronić ✅

- ✅ małe zmiany na raz
- ✅ zawsze testuj po wdrożeniu
- ✅ jeśli ryzyko jest wysokie — zlecaj zmianę w 2 krokach:
  - krok 1: przygotowanie (np. tylko dodanie funkcji, bez aktywacji)
  - krok 2: włączenie i test
- ✅ miej kopię zapasową całego sklepu (nie tylko backupy Jadzi)

---

## 6. FAQ (minimum 15 pytań)

**Q1: Jak często mogę używać /skanuj?**  
A: ✅ Raz dziennie wystarczy, albo po większych zmianach w motywie. Jeśli robisz małe zmiany CSS/tekstu, zwykle nie ma potrzeby skanować.

**Q2: Czy Jadzia pamięta poprzednie rozmowy?**  
A: Nie w sensie “długiej pamięci”. Każde nowe `/zadanie` traktuj jak nową sesję — warto dodać kontekst w wiadomości.

**Q3: Ile czasu zajmuje typowa zmiana?**  
A: CSS/tekst zwykle 30–60 sekund, a PHP 1–3 minuty. Zależy od złożoności i liczby plików.

**Q4: Co jeśli Jadzia zwróci błąd?**  
A: 📝 Skopiuj błąd i spróbuj raz jeszcze. Jeśli to po wdrożeniu i coś nie działa — ❌ `/cofnij` od razu.

**Q5: Co zrobić, gdy strona “wygląda tak samo” po zmianie?**  
A: Najpierw zrób Ctrl+F5 (twarde odświeżenie). Jeśli nadal nie widać zmian, powiedz Jadzi gdzie dokładnie nie działa.

**Q6: Co zrobić, gdy po zmianie coś się “rozjechało” na mobile?**  
A: 🔄 Cofnij zmianę, jeśli problem jest duży. Potem zleć poprawkę z dopiskiem “mobile-first” i podaj screeny.

**Q7: Czy mogę cofnąć tylko jedną część zmian?**  
A: Zwykle cofnięcie dotyczy ostatniej paczki zmian. Jeśli chcesz “częściowo”, zleć nową zmianę naprawczą.

**Q8: Kiedy używać /clear?**  
A: Gdy agent utknął i nie reaguje sensownie (np. miesza dwa zadania). To awaryjna opcja.

**Q9: Skąd mam wiedzieć, że Jadzia czeka na potwierdzenie?**  
A: Jadzia napisze wprost “Potwierdzasz?” albo poprosi o “TAK/NIE”. Wtedy nie opisuj nowego zadania, tylko potwierdź lub odrzuć.

**Q10: Czy mogę zlecić kilka zmian naraz, czy lepiej po kolei?**  
A: Lepiej po kolei ✅. Jeśli musisz łączyć, to w jednym obszarze (np. tylko strona produktu) i z jasnymi punktami.

**Q11: Czy Jadzia może edytować wtyczki?**  
A: Zwykle nie powinno się edytować wtyczek bezpośrednio. Najbezpieczniej robić zmiany w motywie child.

**Q12: Czy Jadzia może zmieniać treści w Elementorze?**  
A: Jeśli treści są w panelu, to pliki nie zawsze wystarczą. Najlepiej opisz problem — Jadzia zaproponuje najbezpieczniejszą drogę.

**Q13: Czy mogę poprosić o zmianę w konkretnym pliku?**  
A: Tak ✅. Jeśli znasz plik, napisz “zmień w pliku X” — przyspiesza to działanie.

**Q14: Jak sprawdzić, jakie pliki były zmienione ostatnio?**  
A: Użyj `/status` i przeczytaj podsumowanie. Jeśli masz logi, możesz też przejrzeć ostatnie wpisy.

**Q15: Co oznacza “backup” i gdzie jest trzymany?**  
A: Backup to kopia sprzed zmiany. Jadzia tworzy go automatycznie przed zapisem, żeby dało się szybko cofnąć.

**Q16: Co zrobić, gdy /test SSH nie działa?**  
A: Najpierw sprawdź, czy serwer działa i czy klucz jest poprawny. Jeśli nie wiesz — wklej wynik `/test` do diagnostyki.

**Q17: Czy mogę używać Jadzi równolegle na kilku czatach/sesjach?**  
A: Technicznie bywa to możliwe, ale dla bezpieczeństwa lepiej robić jedną zmianę na raz, żeby nic się nie pomieszało.

---

## 7. Advanced Tips (dla power users)

### 7.1 Jak łączyć zmiany (kolejność i minimalizacja ryzyka)

Jeśli musisz zrobić serię zmian, użyj takiej kolejności:
1) ✅ najpierw zmiany “wizualne” (CSS)
2) ✅ potem zmiany tekstów
3) ⚠️ dopiero na końcu zmiany logiki (PHP) — i testy po każdym kroku

Dobry plan (przykład):
- krok 1: zmiana kolorów przycisków
- krok 2: poprawa tekstów w koszyku
- krok 3: dopiero potem checkout (walidacja) + test

### 7.2 Jak pracować: Jadzia + Cursor lokalnie (workflow)

To jest opcja “pro”, gdy chcesz większą kontrolę:
- 💡 robisz małe testy lokalnie (np. import modułów, sprawdzenie konfiguracji)
- 🔄 deploy robisz ostrożnie na VPS (pull + restart)
- 📝 trzymasz wszystkie zmiany w Git (łatwy rollback)

Prosty workflow:
1) lokalnie: przygotowanie i test (np. `python test_wp_explorer_import.py`)
2) commit + push
3) VPS: `git pull`
4) restart serwisu
5) test przez Telegram

### 7.3 Jak czytać logi (podstawy)

Gdzie szukać:
- `logs/jadzia.log` — standardowe wyjście serwisu
- `logs/jadzia-error.log` — błędy (stderr)
- `logs/agent.log` — audit trail (JSON Lines)

Przykładowe komendy (VPS):

```bash
tail -200 /root/jadzia/logs/jadzia.log
tail -200 /root/jadzia/logs/jadzia-error.log
tail -200 /root/jadzia/logs/agent.log
```

Gdy diagnozujesz `/skanuj`:

```bash
tail -200 /root/jadzia/logs/jadzia.log | grep -i wp_explorer
tail -200 /root/jadzia/logs/wp_explorer.log
```

💡 Co wklejać do diagnostyki:
- pełny komunikat błędu z Telegram
- 50–200 linii logów z tego samego czasu
- informację: “co zrobiłeś przed błędem”

### 7.4 Tabela: “Szybka diagnoza problemów” (objawy → kroki)

| Objaw | Najczęstsza przyczyna | Co zrobić 💡 |
|---|---|---|
| Zmiana nie widoczna | cache przeglądarki | Ctrl+F5, sprawdź w incognito |
| Strona biała / error 500 | błąd w PHP | ❌ `/cofnij`, potem logi error |
| /test nie działa | SSH / klucz / host | sprawdź `.env`, połączenie, uprawnienia |
| /skanuj fail | transfer tar / timeout | sprawdź `wp_explorer.log`, powtórz raz |
| Checkout nie działa | walidacja/płatność | natychmiast `/cofnij` + test koszyka |

