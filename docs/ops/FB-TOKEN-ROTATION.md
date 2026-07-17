# Facebook Page Token — long-lived (raz a dobrze)

**Strona:** FlexGrafik (`FB_PAGE_ID=491325420727745`)  
**App:** FlexGrafik Jadzia COI  
**VPS:** `/opt/jadzia`

Cel: **Page Access Token** z `expires_at=0` (bez daty wygaśnięcia), żeby nie rotować co kilka tygodni.

---

## Pipeline (automatyczny)

```
Graph Explorer (short USER)
  → fb_exchange_token + FB_APP_ID/FB_APP_SECRET  → long-lived USER (~60 dni)
  → exchange-fb-page-token                        → PAGE (idealnie nigdy nie wygasa)
  → .env FB_ACCESS_TOKEN + restart jadzia
```

Skrypt: `deployment/set-fb-access-token.py` (robi kroki 2–3 automatycznie).

---

## Jednorazowo na VPS — App ID + Secret

Jeśli na VPS **brak** `FB_APP_ID` / `FB_APP_SECRET`:

1. [Meta Developers](https://developers.facebook.com/apps/) → **FlexGrafik Jadzia COI** → Settings → Basic  
2. Skopiuj **App ID** i **App Secret**  
3. Agent zapisze na VPS (nigdy do gita) albo:

```bash
# na VPS — wartości tylko lokalnie
cd /opt/jadzia
# dopisz do .env:
# FB_APP_ID=...
# FB_APP_SECRET=...
chown jadzia:jadzia .env && chmod 640 .env
```

---

## Rotacja / nowy token (gdy trzeba)

### Krok 1 — Ty (~3 min) — Graph Explorer

1. [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Meta App: **FlexGrafik Jadzia COI**
3. Permissions: `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`
4. **Generate Access Token** → zaloguj / zatwierdź
5. Wystarczy **User** token (nie musisz wybierać Page — skrypt zrobi long-lived + Page)
6. **Copy** → przekaż agentowi jako `FB_TOKEN=...` (po zapisie na VPS traktuj jako spalony)

### Krok 2 — Agent / VPS

```bash
cd /opt/jadzia
venv/bin/python deployment/set-fb-access-token.py "WKLEJ_TOKEN"
chown jadzia:jadzia .env && chmod 640 .env
systemctl restart jadzia
venv/bin/python deployment/inspect-fb-token.py
# oczekiwane: type PAGE, is_valid true, expires_at 0 (idealnie)
```

**UI:** Commander → Marketing → „Facebook: Token OK (Page)”.

---

## Diagnostyka

| Objaw | Przyczyna | Fix |
|-------|-----------|-----|
| OAuth 190 / expired | Token wygasł | Nowy USER z Explorera + `set-fb-access-token.py` |
| `long_lived_exchange: skipped` | Brak App ID/Secret | Uzupełnij `FB_APP_*` na VPS |
| `short_lived_warning` | PAGE z krótkim TTL | Brak long-lived — sprawdź App Secret |
| 403 / USER zamiast PAGE | Exchange page nie zadziałał | `exchange-fb-page-token.py` + permissions |

**Skrypty:**

| Skrypt | Opis |
|--------|------|
| `deployment/set-fb-access-token.py` | Zapis + long-lived + USER→PAGE |
| `deployment/exchange_fb_long_lived.py` | short USER → long USER |
| `deployment/exchange-fb-page-token.py` | USER → PAGE |
| `deployment/inspect-fb-token.py` | Typ, expiry |
| `deployment/retry-calendar-publish.py` | Retry wpisu po naprawie |

---

## TY TYLKO TO

### B0 — Jednorazowo (tylko gdy agent zgłosi brak App credentials)

1. Meta Developers → FlexGrafik Jadzia COI → Settings → Basic  
2. Skopiuj **App ID** + **App Secret**  
3. Wklej agentowi jednym komunikatem (nie commituj)

### B1 — Nowy token (~3 min)

1. Graph API Explorer → app FlexGrafik Jadzia COI  
2. Permissions: `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`  
3. Generate Access Token → Copy  
4. Wklej agentowi: `FB_TOKEN=...`

**Nie robisz:** SSH, edycji `.env`, restartu, long-lived curl, E2E — to agent.

---

## Bezpieczeństwo

- Nigdy nie commituj tokenów / App Secret do gita  
- Po wklejeniu tokenu w czacie — uważaj za spalony; produkcja ma kopię w `.env`  
- `.env` tylko na VPS: `chmod 640`, owner `jadzia:jadzia`
