# UX Dogfood — Phone Commander (CEO Dashboard)

**Prod:** `https://api.zzpackage.flexgrafik.nl/commander/`  
**Pass bar:** wszystkie CRITICAL = PASS przed następnym UX gate.

| # | Krok | UX-01 | UX-02 | UX-03 | PASS/FAIL |
|---|------|-------|-------|-------|-----------|
| 1 | TG `/commander` → login code → Home bez pola JWT w twarz | C | | | |
| 2 | Chrome nav PL (Start/Marketing/Analityka/Agenci/Ustawienia) | C | C | | |
| 3 | Ack/Odłóż/Zamknij na sales_cta (PL) | C | | | |
| 4 | Primary 5 desktop≡mobile; Audyt secondary | | C | | |
| 5 | Empty Marketing/Analityka/Agenci/Audyt ≠ error copy | | C | | |
| 6 | Home kolejka widoczna mimo wolnego secondary API | | | C | |
| 7 | Mapa → os.flexgrafik.nl + cmd (Basic Auth OK) | | | C | |
| 8 | Back do Commandera — sesja JWT OK | | | C | |
| 9 | Touch ≥44px primary; brak EN chrome na primary path | C | C | C | |

**CEO Dashboard PASS** = kolumna UX-03 + pełna lista PASS.
