# Facebook Page Token — rotacja i konfiguracja (COI Marketing)

**Strona:** FlexGrafik (`FB_PAGE_ID=491325420727745`)  
**App:** FlexGrafik Jadzia COI  
**VPS:** `/opt/jadzia`

---

## Wymagane uprawnienia (Graph API Explorer)

Przed **Generate Access Token** dodaj:

| Permission | Cel |
|------------|-----|
| `pages_manage_posts` | Publikacja, usuwanie postów |
| `pages_read_engagement` | Odczyt / insights (B3.1) |
| `pages_show_list` | Lista stron → Page Token |

---

## Krok 1 — Token w Meta (Dowódca, ~5 min)

1. Otwórz [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. **Meta App:** FlexGrafik Jadzia COI
3. Dodaj permissions (tabela wyżej)
4. **Generate Access Token** → zaloguj, zatwierdź
5. **User or Page → Get Token → FlexGrafik** (Page Access Token)
6. **Copy Token**

> User Token z Explorera też zadziała — skrypt na VPS wymieni go na Page Token automatycznie.

---

## Krok 2 — VPS (agent lub Dowódca)

```bash
ssh root@185.243.54.115
cd /opt/jadzia

# Zalecane: skrypt z auto-wymianą USER → PAGE
venv/bin/python deployment/set-fb-access-token.py "WKLEJ_TOKEN_TUTAJ"

chown jadzia:jadzia .env
chmod 640 .env
systemctl restart jadzia
```

**Smoke:**

```bash
venv/bin/python deployment/inspect-fb-token.py
# token_type: PAGE, is_valid: true

venv/bin/python deployment/retry-calendar-publish.sh ENTRY_ID
# lub Commander → Marketing → Ponów publikację
```

**UI:** Commander → Marketing → pasek „Facebook: Token OK (Page)”.

---

## Krok 3 — Long-lived token (opcjonalnie, backlog)

Krótkotrwały token z Explorera wygasa (typ. 1–60 dni). Na produkcji docelowo:

1. Wymiana User → long-lived User token (App Secret tylko na VPS)
2. Wymiana na long-lived **Page** token
3. Zapis `fb_token_expires_at` w Commander settings (bez sekretu)

Do czasu implementacji C3: powtarzaj Krok 1–2 gdy `fb-health` pokazuje wygaśnięcie lub publish fail OAuth 190.

---

## Diagnostyka

| Objaw | Przyczyna | Fix |
|-------|-----------|-----|
| OAuth 190 / expired | Token wygasł | Nowy token + restart |
| 403 publish_actions | USER token zamiast PAGE | `exchange-fb-page-token.py` |
| Post `failed`, brak na FB | Zobacz filtr **Nieudane** w Marketing | Ponów po naprawie tokenu |
| Grafika fail | Drive niepubliczny | Udostępnij plik: każdy z linkiem |

**Skrypty:**

| Skrypt | Opis |
|--------|------|
| `deployment/set-fb-access-token.py` | Zapis + auto PAGE exchange |
| `deployment/exchange-fb-page-token.py` | USER → PAGE |
| `deployment/inspect-fb-token.py` | Typ tokenu, expiry |
| `deployment/retry-calendar-publish.py` | Retry wpisu po naprawie |

---

## Bezpieczeństwo

- Nigdy nie commituj tokenów do git
- Po wklejeniu tokenu w czacie — wygeneruj nowy i unieważnij stary w Meta
- `.env` tylko na VPS, `chmod 640`, owner `jadzia:jadzia`
