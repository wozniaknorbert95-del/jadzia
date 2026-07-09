# Handoff — zamknięcie sesji 2026-07-09

**Repo:** jadzia-core `master` @ `27a5961`  
**VPS:** `/opt/jadzia` @ `1036d6e` (Phase B), `jadzia` active

---

## Dziś zamknięte

| Program | Status |
|---------|--------|
| COI Commander v3 | prod, workshop done |
| Content Intake M1 | composer, GDrive, FB photo, deploy |
| Marketing Phase B | failed UX, TG alert, fb-health, retry, probe, deploy |
| FB token + post #16 | Page token OK, QR opublikowany |

---

## Teraz (Ty, ~2 min) — jedyny sensowny krok przed końcem dnia

Otwórz https://api.zzpackage.flexgrafik.nl/commander/ → **Marketing**:

1. Pasek **Facebook: Token OK (Page)**
2. Wpis **QR** w **Opublikowane** + link do FB
3. Filtr **Nieudane** istnieje (może być pusty — OK)

To zamyka pętlę walidacji bez nowego kodu.

---

## Następna sesja — rekomendacja

**#1 `COI-CMD-QUEUE-CLEAN`** (~15 min, niskie ryzyko)  
Usuń testowe `deploy02-*` hot_leady z Home — od razu czyściej w Commander.

**#2 dopiero potem** `COI-CONTENT-INTAKE-M2` (video/Reels) — większy scope, gdy marketing flow jest potwierdzony operacyjnie.

**Higiena (kiedy masz chwilę):** nowy Page Token w Meta + unieważnij stary (był w czacie) — `docs/ops/FB-TOKEN-ROTATION.md`.

---

## Nie ruszać teraz

- M2 video — osobna sesja
- SMTP Delegata — wymaga Gmail app password od Ciebie
- INSPIRE engine stash — osobny track
