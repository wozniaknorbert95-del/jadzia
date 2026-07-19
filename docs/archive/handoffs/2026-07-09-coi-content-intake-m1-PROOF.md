# Handoff PROOF: COI Content Intake M1 (2026-07-09)

**Branch:** `master`  
**Commit:** `d40d0d8` — feat(content-intake): M1 Marketing composer, GDrive image publish  
**Gate:** `COI-CONTENT-INTAKE-M1` → **completed**  
**VPS:** `185.243.54.115` `/opt/jadzia` @ `d40d0d8`  
**Public URL:** https://api.zzpackage.flexgrafik.nl/commander/

---

## Co zrobione

| Obszar | Status |
|--------|--------|
| Schema `content_type`, `media_source`, `scheduled_publish_at` | ✅ |
| GDrive URL normalizacja (`agent/media/gdrive.py`) | ✅ |
| FB publish: tekst + zdjęcie (`publish_calendar_content`) | ✅ |
| Video w kolejce — publish zwraca błąd M2 (świadomie) | ✅ |
| Commander UI — zakładka **Marketing** (composer + filtry) | ✅ |
| Folder GDrive w settings prod | ✅ `1SYueUiXAtu9hn1tAtTUJsR-NLZZFnsGW` |

---

## Git + deploy

| Krok | Status |
|------|--------|
| Commit + push `master` | ✅ `d40d0d8` |
| VPS `git pull` | ✅ fast-forward |
| `venv/bin/pip install -r requirements.txt` | ✅ |
| `systemctl restart jadzia` | ✅ active |
| `set-marketing-gdrive-folder.py` (venv python) | ✅ |

**Uwaga deploy:** Na VPS były lokalne untracked kopie skryptów — usunięte przed pull (zastąpione wersją z repo).

---

## Testy lokalne

```
pytest tests/unit/test_gdrive.py \
       tests/unit/test_content_calendar_media.py \
       tests/unit/test_facebook_publisher.py \
       tests/unit/test_content_calendar_api.py -q
→ 22 passed
```

---

## Prod smoke (agent)

| Test | Wynik |
|------|-------|
| `GET /commander/` localhost | 200 |
| VPS HEAD = `d40d0d8` | ✅ |
| Settings GDrive folder zapisany | ✅ |

**Nie testowane live:** publish FB z prawdziwym GDrive file URL (wymaga Dowódcy + `FB_PAGE_ID`/`FB_ACCESS_TOKEN`).

---

## Walidacja Dowódcy (2 min)

1. Otwórz https://api.zzpackage.flexgrafik.nl/commander/ → JWT → **Marketing**
2. Sprawdź hint z linkiem do folderu Drive
3. Wgraj grafikę do folderu COI-Marketing → **Udostępnij link do pliku** (nie folderu)
4. Nowy wpis: typ **Grafika**, wklej link pliku, NL caption, data → **Zapisz szkic** lub **Zaplanuj**
5. Opcjonalnie: **Opublikuj teraz** na wpisie `approved` (jeśli FB skonfigurowane)

---

## Backlog (nie M1)

| ID | Opis |
|----|------|
| COI-CONTENT-INTAKE-M2 | Video/Reels publish |
| COI-CMD-QUEUE-CLEAN | Usuń E2E `deploy02-*` z Home |
| COI-CMD-SMTP-01 | Email eskalacji (brak SMTP w `.env`) |

---

## Następny krok

- **Ty:** walidacja Marketing + jeden test publish (grafika z Drive)
- **Agent:** M2 video lub cleanup queue — po Twoim OK
