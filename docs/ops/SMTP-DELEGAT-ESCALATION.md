# SMTP — eskalacja email do Delegata (COI-CMD-SMTP-01)

**Kod:** `agent/commander/escalation.py` → `_send_delegat_email`  
**VPS:** `/opt/jadzia`  
**Delegat (settings):** `wozniaknorbert95@gmail.com` (`delegat_configured: true`)

Cel: gdy Dowódca nieaktywny ≥24h i item SLA **red** → email do Delegata (oprócz TG).

---

## Jak to działa

```
worker_loop
  → check_sla_escalations()
  → TG do Dowódcy (zawsze przy red)
  → jeśli inactive ≥24h + delegat_email + SMTP_HOST
       → email do Delegata
```

Bez `SMTP_HOST` → log `email skipped` (bez crashu). TG działa niezależnie.

---

## Zmienne `.env` (VPS only)

| Key | Przykład | Uwagi |
|-----|----------|-------|
| `SMTP_HOST` | `smtp.gmail.com` | wymagane do wysyłki |
| `SMTP_PORT` | `587` | STARTTLS (default w kodzie) |
| `SMTP_USER` | Gmail konta z App Password | zwykle = adres Delegata |
| `SMTP_PASSWORD` | **App Password** (16 znaków) | nie zwykłe hasło Gmail |
| `SMTP_FROM` | ten sam co `SMTP_USER` | opcjonalne; default = USER |

**Nigdy nie commituj** `SMTP_PASSWORD` / pełnego `.env`.

---

## TY TYLKO TO — szczegółowa instrukcja Gmail App Password

**Konto docelowe:** `wozniaknorbert95@gmail.com` (Delegat — to samo co w Commander settings).  
**Czas:** ~5–10 min (pierwszy raz z 2FA dłużej).  
**Cel:** dostać 16-znakowe **App Password** — Jadzia użyje go zamiast zwykłego hasła Gmail.

> **Uwaga:** zwykłe hasło do Gmail **nie zadziała** z SMTP. Google wymaga App Password przy 2FA.

### Krok 0 — właściwe konto

1. Otwórz przeglądarkę (Chrome/Edge).
2. Upewnij się, że jesteś zalogowany jako **`wozniaknorbert95@gmail.com`**.
3. Sprawdź: prawy górny róg Gmail → awatar → adres pod nazwą.
4. Jeśli to inne konto → wyloguj / przełącz na właściwe.

### Krok 1 — Security

1. Otwórz: https://myaccount.google.com/security  
   (albo: Google Account → menu lewe **Security** / **Bezpieczeństwo**).
2. Przewiń do sekcji **How you sign in to Google** / **Jak logujesz się do Google**.

### Krok 2 — włącz 2-Step Verification (jeśli nieaktywne)

Jeśli **2-Step Verification** ma status **Off** / **Wyłączona**:

1. Kliknij **2-Step Verification** / **Weryfikacja dwuetapowa**.
2. **Get started** / **Rozpocznij**.
3. Zaloguj się ponownie (hasło konta).
4. Podaj telefon (SMS lub aplikacja Authenticator — dowolna bezpieczna opcja).
5. Potwierdź kod z SMS/aplikacji.
6. Włącz **Turn on** / **Włącz**.
7. Wróć do https://myaccount.google.com/security — status 2FA powinien być **On**.

Jeśli 2FA już **On** → pomiń ten krok.

### Krok 3 — App passwords

1. Na stronie Security, pod 2-Step Verification, kliknij **App passwords** / **Hasła do aplikacji**.  
   Bezpośredni link (działa tylko gdy 2FA włączone):  
   https://myaccount.google.com/apppasswords
2. Google może poprosić o ponowne hasło konta — wpisz je.
3. Jeśli widzisz komunikat że App passwords niedostępne:
   - konto Workspace zarządzane przez firmę → admin musi zezwolić, **albo**
   - używasz tylko kluczy dostępu / zaawansowanej ochrony → tymczasowo włącz klasyczne App passwords, albo użyj innego konta Gmail osobistego.
4. Pole **App name** / **Nazwa aplikacji**: wpisz `Jadzia COI`.
5. Kliknij **Create** / **Utwórz**.
6. Pojawi się żółte/okienko z hasłem w formacie:

   ```text
   abcd efgh ijkl mnop
   ```

   To jest **16 znaków** (Google pokazuje ze spacjami — spacje są tylko do czytelności).

### Krok 4 — skopiuj i wklej agentowi

1. **Skopiuj całe hasło od razu** (okienko znika — nie zobaczysz go drugi raz; wtedy trzeba wygenerować nowe).
2. Wklej **w tym czacie Cursor** jednym blokiem (nie wrzucaj do gita, nie commituj, nie wklejaj do Slack/public):

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=wozniaknorbert95@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM=wozniaknorbert95@gmail.com
```

Podmień `abcd efgh ijkl mnop` na swoje wygenerowane hasło (ze spacjami OK — skrypt je usunie).

3. Po wklejeniu agent zapisze to **tylko na VPS** (`.env`), zrestartuje `jadzia` i wyśle maila testowego.
4. Sprawdź skrzynkę `wozniaknorbert95@gmail.com` (także **Spam**) — subject: `[SMOKE] COI Commander SMTP`.

### Krok 5 — po udanym smoke (higiena)

1. W czacie potraktuj App Password jako „zużyte w logu” — nie udostępniaj dalej.
2. Jeśli hasło wyciekło do publicznego miejsca → wróć do App passwords → **Revoke** / **Usuń** to hasło → wygeneruj nowe → wklej agentowi ponownie.
3. Zwykłego hasła Gmail **nie zmieniaj** z tego powodu.

### FAQ / problemy

| Widzisz… | Co zrobić |
|----------|-----------|
| Brak pozycji **App passwords** | Najpierw włącz 2-Step Verification (Krok 2), odśwież stronę |
| „App passwords aren’t available” (Workspace) | Użyj osobistego Gmail albo poproś admina Workspace o włączenie |
| Tylko klucze Passkey, zero App passwords | Tymczasowo dodaj metodę 2FA (telefon) — wtedy App passwords się pojawią |
| Nie pamiętam hasła Gmail | [Odzyskaj konto](https://accounts.google.com/signin/recovery) zanim ruszysz dalej |
| Chcę inne konto niż `wozniaknorbert95@…` | Wygeneruj App Password na tamtym koncie; podaj nowy `SMTP_USER`/`SMTP_FROM`; agent zaktualizuje też `delegat_email` w settings jeśli trzeba |

### Checklist przed wysłaniem do agenta

- [ ] Zalogowany jako `wozniaknorbert95@gmail.com`
- [ ] 2-Step Verification = On
- [ ] App Password utworzone (`Jadzia COI`)
- [ ] Skopiowane 16 znaków
- [ ] Blok `SMTP_HOST`…`SMTP_FROM` gotowy do wklejenia w czat

---

## Agent / VPS — po paste

```bash
cd /opt/jadzia

# Dopisz/zaktualizuj SMTP_* w .env (ręcznie lub set-smtp-env.py)
# chown jadzia:jadzia .env && chmod 640 .env

systemctl restart jadzia
systemctl is-active jadzia   # active

# Smoke (nie drukuje sekretów)
venv/bin/python deployment/smoke-smtp-escalation.py
# oczekiwane: SMTP_SMOKE=PASS
```

Sprawdź skrzynkę Delegata (i spam): subject `[SMOKE] COI Commander SMTP`.

---

## Diagnostyka

| Objaw | Przyczyna | Fix |
|-------|-----------|-----|
| log `email skipped host=None` | brak `SMTP_HOST` | uzupełnij `.env` + restart |
| `SMTPAuthenticationError` / 535 | złe hasło / nie App Password | nowe App Password |
| timeout / connection refused | firewall / zły host:port | `smtp.gmail.com:587` |
| smoke PASS, brak maila w INBOX | spam / zły `To` | sprawdź spam + `delegat_email` w settings |
| eskalacja produkcyjna bez emaila | Dowódca aktywny &lt;24h | zamierzone; smoke omija ten gate |

**Skrypty:**

| Skrypt | Opis |
|--------|------|
| `deployment/smoke-smtp-escalation.py` | Test send via `_send_delegat_email` |
| `deployment/set-smtp-env.py` | Zapis `SMTP_*` do `.env` (bez printu hasła) |

---

## Poza scope

TikTok, INSPIRE, BFG secret scrub, rotacja FB App Secret.
