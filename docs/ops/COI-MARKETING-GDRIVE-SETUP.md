# COI Marketing — Google Drive setup (Norbert)

**Konto:** `wozniaknorbert95@gmail.com` (Google One 5 TB)  
**Cel:** Folder na grafiki i wideo; Jadzia **nie przechowuje plików** — tylko linki URL.

---

## Ważne: co agent zrobił vs co Ty (2 min)

| Kto | Co |
|-----|-----|
| **Agent / Jadzia** | Moduł `agent/media/gdrive.py` — normalizacja linków + probe; ustawienia `marketing_gdrive_folder_*` w Commander |
| **Ty** | Utworzenie folderu na **swoim** Drive (wymaga logowania Google — agent nie ma dostępu do Twojego Gmail) |

Po utworzeniu folderu wklej link poniżej — agent zapisze go w ustawieniach prod.

---

## Krok 1 — Utwórz folder (Ty, ~2 min)

1. Otwórz https://drive.google.com/ (konto `wozniaknorbert95@gmail.com`)
2. **Nowy → Folder**
3. Nazwa: **`COI-Marketing`**
4. Prawy przycisk na folderze → **Udostępnij**
5. **Ogólny dostęp** → **Każdy, kto ma link** → rola **Wyświetlający**
6. **Skopiuj link** (format: `https://drive.google.com/drive/folders/XXXXXXXX`)

---

## Krok 2 — Podłącz folder do Jadzia (agent lub Ty na VPS)

Wyślij agentowi link folderu w czacie **albo** na VPS:

```bash
cd /opt/jadzia
PYTHONPATH=/opt/jadzia python3 deployment/set-marketing-gdrive-folder.py \
  "https://drive.google.com/drive/folders/TWOJ_FOLDER_ID"
```

W Commander → **Ustawienia** pojawi się zapisany URL (po implementacji UI M1).

---

## Krok 3 — Dodawanie postów (codziennie)

1. Wrzuć **gotowy** JPG/PNG/MP4 do `COI-Marketing`
2. Na pliku: **Udostępnij → każdy z linkiem → wyświetlający**
3. Skopiuj link **pliku** (nie folderu)
4. Commander → Marketing → wklej link + tekst NL + data

---

## Jak Jadzia „łączy” Drive (bez OAuth)

Nie ma pełnej integracji API z Twoim kontem (M1). Połączenie = **kontrakt linków**:

- Wklejasz link `.../file/d/ID/view`
- Backend zamienia na `https://drive.google.com/uc?export=download&id=ID`
- Przy zapisie: probe (czy plik publiczny)
- Przy publikacji: Meta pobiera z tego URL

**Zero uploadu na VPS.**

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| „Link niedostępny” w Commander | Plik nie jest „każdy z linkiem” — popraw udostępnianie |
| FB nie publikuje wideo | Duży MP4 + virus scan Google → M2 lub host na R2 |
| Zły link | Użyj linku z **pliku**, nie folderu |

---

## Opcjonalnie później (M3)

Google Drive API + OAuth — tylko jeśli probe na wideo systematycznie pada. Nie jest wymagane na M1.
