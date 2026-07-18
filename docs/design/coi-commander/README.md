# COI Commander — design gate

**Status:** F0 spec + F1 API + F2 MVP UI zaimplementowane w repo.

## Dokumenty

| # | Plik |
|---|------|
| 1 | [`../../AUDYT-HIL-KONTROLA.md`](../../AUDYT-HIL-KONTROLA.md) |
| 2 | [`AUDYT-V2-GAP.md`](AUDYT-V2-GAP.md) |
| 3 | [`COI-COMMANDER-PLAN-v3.md`](COI-COMMANDER-PLAN-v3.md) |
| 4 | [`UX-BRIEF-COMMANDER.md`](UX-BRIEF-COMMANDER.md) |
| 5 | [`UX-DOGFOOD-PHONE.md`](UX-DOGFOOD-PHONE.md) |
| 6 | [`adr/D0.15-hub-ia-nav.md`](adr/D0.15-hub-ia-nav.md) + specs D0.16–D0.19 |

## Implementacja

- **API:** `api/routes/commander.py` + `agent/commander/`
- **UI:** `commander-ui/` → `http://localhost:8000/commander/`
- **Testy:** `tests/unit/test_commander_api.py`

## Uruchomienie UI

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
# Otwórz /commander/ i wklej JWT (scripts/jwt_token.py)
```
