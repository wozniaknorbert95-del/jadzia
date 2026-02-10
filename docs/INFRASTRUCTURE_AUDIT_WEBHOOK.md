# INFRASTRUCTURE AUDIT – Telegram webhook (404)

**Kontekst:** VPS Ubuntu, `/root/jadzia`, bot działa (PID 202387). Webhook Telegram zwraca 404.

Raport przygotowany na podstawie plików projektu. **Punkty 1–4 wymagają uruchomienia podanych komend na VPS** – z repozytorium wynika tylko docelowa konfiguracja i porty.

---

## 1. HTTPS SETUP

**Do wykonania na VPS:**

```bash
# Czy nginx jest skonfigurowany?
ls /etc/nginx/sites-enabled/

# Domena
grep -r "server_name" /etc/nginx/sites-enabled/ 2>/dev/null

# Certyfikat SSL
ls /etc/letsencrypt/live/ 2>/dev/null

# Zawartość konfiguracji nginx dla projektu (jeśli jest)
cat /etc/nginx/sites-enabled/jadzia 2>/dev/null || cat /etc/nginx/sites-enabled/default
```

**Z projektu (docelowa konfiguracja):**

- W repozytorium jest **`jadzia-nginx.conf`** (do użycia na serwerze):
  - `server_name api.zzpackage.flexgrafik.nl;`
  - `listen 80;`
  - `proxy_pass http://127.0.0.1:8000;`
- **Brak Caddy** w projekcie – używany jest nginx.
- **Docelowa domena:** `api.zzpackage.flexgrafik.nl`.
- Obecny szablon **nie zawiera SSL** (tylko port 80). Dla webhooka Telegram **wymagany jest HTTPS** – na VPS trzeba:
  - dodać blok `listen 443 ssl` i `ssl_certificate` / `ssl_certificate_key` (np. z Certbot),
  - albo użyć osobnej konfiguracji z Certbot (`certbot --nginx`).

**Wniosek:** Nginx powinien być skonfigurowany według `jadzia-nginx.conf` dla `api.zzpackage.flexgrafik.nl`, a następnie rozszerzony o SSL (np. Let’s Encrypt). Bez tego webhook będzie 404 lub niedostępny po HTTPS.

---

## 2. FASTAPI PORT

**Z projektu:**

- **main.py:** port z zmiennej `API_PORT`, domyślnie **8000**.
  ```python
  port = int(os.getenv("API_PORT", 8000))
  uvicorn.run("main:app", host=host, port=port, ...)
  ```
- **.env:** wartość ustawiana przez `API_PORT` (w repozytorium nie ma jej w .env – na VPS sprawdź `.env`).
- **jadzia.service:** nie ustawia portu; używa `main.py`, więc obowiązuje `API_PORT` z `.env` lub 8000.

**Do wykonania na VPS:**

```bash
grep API_PORT /root/jadzia/.env
netstat -tlnp | grep python
# lub (bez net-tools):
ss -tlnp | grep python
```

**Oczekiwany wynik:** proces Pythona nasłuchuje na **8000** (albo na porcie z `API_PORT` w `.env`). Nginx w `jadzia-nginx.conf` proxy’uje na `127.0.0.1:8000`.

---

## 3. TELEGRAM WEBHOOK URL

**Format URL dla setWebhook:**

```
https://[DOMENA]/telegram/webhook
```

**Gdzie [DOMENA]:**

- **Z nginx + SSL:** `api.zzpackage.flexgrafik.nl`  
  → **`https://api.zzpackage.flexgrafik.nl/telegram/webhook`**
- **Bez reverse proxy (niezalecane, Telegram i tak wymaga HTTPS):** adres IP nie wystarczy; trzeba domeny z certyfikatem.

**Z kodu:** router Telegram ma prefix `/telegram`, endpoint to `/webhook` → pełna ścieżka to **`/telegram/webhook`** (plik `interfaces/telegram_api.py`: `APIRouter(prefix="/telegram")`, `@router.post("/webhook")`).

**Do wykonania na VPS (czy webhook był kiedyś ustawiany / wywoływany):**

```bash
grep -i webhook /root/jadzia/logs/*.log 2>/dev/null | tail -20
```

---

## 4. TELEGRAM CONFIG

**Do wykonania na VPS (bez pokazywania wartości):**

```bash
# Czy token jest ustawiony?
[ -n "$(grep -E '^TELEGRAM_BOT_TOKEN=.' /root/jadzia/.env 2>/dev/null)" ] && echo "set" || echo "empty"

# Czy webhook secret jest ustawiony?
[ -n "$(grep -E '^TELEGRAM_WEBHOOK_SECRET=.' /root/jadzia/.env 2>/dev/null)" ] && echo "set" || echo "empty"

# Wszystkie TELEGRAM_* (nazwy + maskowane wartości):
grep "^TELEGRAM_" /root/jadzia/.env 2>/dev/null | sed 's/=.*/=***/'
```

**Wymagane w kodzie:**

- **TELEGRAM_BOT_TOKEN** – używany w `interfaces/telegram_api.py` (sendMessage, odpowiedzi do użytkownika). Gdy pusty – webhook może działać, ale bez wysyłania odpowiedzi do Telegrama.
- **TELEGRAM_WEBHOOK_SECRET** – opcjonalny w sensie „czy request dojdzie”, ale **telegram_validator** przy braku secretu loguje ostrzeżenie i może odrzucać requesty (w zależności od ścieżki: natywny Telegram Update vs n8n).
- **TELEGRAM_BOT_ENABLED=1** – w `interfaces/api.py` router Telegram jest dodawany tylko gdy `os.getenv("TELEGRAM_BOT_ENABLED", "") == "1"`. **Bez tego endpoint `/telegram/webhook` w ogóle nie istnieje → 404.**

**Rekomendacja:** Na VPS w `.env` ustaw: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, `TELEGRAM_BOT_ENABLED=1` oraz (opcjonalnie) `ALLOWED_TELEGRAM_USERS`.

---

## 5. BRAKUJĄCY MODUŁ (dotenv)

**Z repozytorium:**

- **requirements.txt** zawiera:  
  `python-dotenv>=1.0.0`
- **api.py** na początku ma:  
  `from dotenv import load_dotenv` i `load_dotenv()`.

**Dlaczego może „brakować” dotenv na VPS:**

1. **venv był tworzony przed dodaniem `python-dotenv` do requirements.txt** – wtedy `pip install -r requirements.txt` nie był ponownie uruchomiony.
2. **Inne środowisko** – np. uruchomienie `python main.py` bez aktywnego venv z projektu.

**Do wykonania na VPS:**

```bash
cd /root/jadzia
./venv/bin/pip show python-dotenv
# Jeśli brak: reinstalacja
./venv/bin/pip install -r requirements.txt
# Restart serwisu
sudo systemctl restart jadzia
```

---

## PODSUMOWANIE – co zrobić, żeby webhook przestał dawać 404

1. **TELEGRAM_BOT_ENABLED=1** w `/root/jadzia/.env` (bez tego nie ma route’a `/telegram/webhook`).
2. **Nginx:** konfiguracja dla `api.zzpackage.flexgrafik.nl` z proxy na `127.0.0.1:8000` (np. z `jadzia-nginx.conf`) + **SSL** (np. Certbot).
3. **setWebhook:**  
   `https://api.zzpackage.flexgrafik.nl/telegram/webhook`
4. **Sprawdzić** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, opcjonalnie `ALLOWED_TELEGRAM_USERS`.
5. **Na VPS:** `pip install -r requirements.txt` w venv projektu i restart `jadzia`.

Po wykonaniu na VPS komend z sekcji 1–4 możesz wkleić ich output – wtedy można doprecyzować raport pod faktyczny stan serwera.
