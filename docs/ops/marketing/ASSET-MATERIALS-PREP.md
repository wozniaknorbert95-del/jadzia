---
status: "[ACTIVE]"
title: "Asset Materials Prep — next session SoT"
gate: "MKT-ASSET-00"
updated: "2026-07-27"
parent: "ASSET-FACTORY.md"
budget_context: "freeze organic only do 2026-08-06"
---

# Asset Materials Prep — zbiór / repo / adaptacja

**Cel następnej sesji:** zebrać lub znaleźć materiały (własne + gotowe repo/szablony) do **pierwszego kompletnego WW** pod organic free (FB + TT).  
**Nie cel sesji:** paid Meta · deploy · nowy kod publishera (już LIVE `@4cf66fe`).

**Parent:** [ASSET-FACTORY.md](./ASSET-FACTORY.md) · [GTM-1PAGER.md](./GTM-1PAGER.md) · [CHANNEL-MATRIX.md](./CHANNEL-MATRIX.md).

---

## Campus — pokój Marketing (gdzie jesteśmy)

**Full map:** [FLEXGRAFIK-CAMPUS-MAP.md](../FLEXGRAFIK-CAMPUS-MAP.md) · **Program:** [FLEXGRAFIK-CAMPUS-PROGRAM.md](../FLEXGRAFIK-CAMPUS-PROGRAM.md) §13 · WW target: **`MKT/2026-W31/`**.

**DoD (PLAN-00):** Asset Card + Experiment Card + rights + UTM + Founder HITL — nie sam folder.

```
FlexGrafik (Firma)
└── Marketing Studio (P1)
    ├── SoT strategii      → GTM-1PAGER · OPERATOR-TODAY
    ├── Dashboard          → Commander ?v=mkt-dash08
    ├── Automaty (boty)    → MB propose · calendar publish · DTL ingest
    ├── HITL Dowódca       → FB organic · TT token · (paid PARK do 08-06)
    └── Produkcja treści   → Asset Factory → MKT/2026-W31/  ← NASTĘPNA SESJA
```

| Pokój (departament) | Repo / surface | Agenci / automaty |
|---------------------|----------------|-------------------|
| **Marketing** | jadzia-core `docs/ops/marketing/` | MB · Commander publish · weekly scorecard |
| **Sprzedaż** | jadzia REV-DEMAND · zzpackage Wizard | lead_node · widget CTA · WA SLA |
| **Produkcja** | zzpackage · INSPIRE / design-agent | mockup · wrap preview |
| **Obsługa** | Commander queue · SPEED-TO-LEAD | cs_followup · HITL tickets |
| **Finanse** | DTL · UNIT-ECONOMICS | margin facts · CPA_wizard (paid później) |

---

## Definition of Done — sesja materiałów

Na koniec następnej sesji Dowódca/agent ma **jeden z trzech** outcomes (nie wszystkie naraz):

| Outcome | Done when |
|---------|-----------|
| **A — Inventory** | Lista: co mamy (GDrive, VPS, repo) vs braki vs [output WW](#output-docelowy-mktyyyy-ww) |
| **B — Repo scout** | 1–3 kandydatów repo/szablonów + verdict adapt / fork / skip |
| **C — WW v0** | Folder `MKT/YYYY-WW/` z min. `master_reel_9x16` **lub** plan shoot + placeholders + `NOTES.md` |

Minimum na start organic: **`master_reel_9x16.mp4`** + **`tt_hook_15s.mp4`** + **`NOTES.md`** (UTM + hipoteza).

---

## Output docelowy (`MKT/YYYY-WW/`)

Z [ASSET-FACTORY](./ASSET-FACTORY.md) — priorytet w freeze:

| Priorytet | Plik | Freeze? |
|-----------|------|---------|
| **P0** | `master_reel_9x16.mp4` | tak — FB organic + future paid |
| **P0** | `tt_hook_15s.mp4` | tak — TT KPI wizard_starts |
| **P0** | `NOTES.md` | tak — UTM · CTA · hipoteza |
| P1 | `feed_1x1.mp4` | po freeze / paid |
| P1 | `carousel_1..3.png` | po freeze |
| P2 | `testimonial.jpg` | compound |

**GDrive SoT folder:** ten sam co Commander / CHANNEL-MATRIX (`MKT/YYYY-WW/`).

---

## Checklist — co zbierać (inventory)

### Własne (FlexGrafik)

- [ ] Real bus przed/po (zdjęcia lub istniejące wideo) — **nie AI stock**
- [ ] Poprzednie posty FB / TT (reuse cut?)
- [ ] INSPIRE / design-agent outputy (mockupy wrap)
- [ ] Case studies / testimonial klient ZZP bouw
- [ ] NL copy: hook z [GTM messaging pillars](./GTM-1PAGER.md#positioning)

### Ekosystem repo (skan lokalny)

| Repo | Szukaj |
|------|--------|
| `jadzia-core` | marketing docs · GDrive refs · calendar entries |
| `zzpackage.flexgrafik.nl` | wizard assets · blog stills |
| `flexgrafik-nl` | brand · portal media |
| `Flex-vcms/flex-vcms` | content / marketing pointers |
| `flexgrafik-meta` | brand guidelines |

### Zewnętrzne (repo scout — opcjonalnie)

Kryteria **adapt** (nie greenfield):

- Licencja OK komercyjnie
- Export mp4/png bez lock-in
- 9:16 Reel template lub bus-before/after niche
- **Nie** osobna strategia TikTok — tylko cut z mastera

Verdict w handoff: `ADAPT` | `FORK` | `SKIP` + 1 linia why.

---

## NOTES.md — szablon (wklej do WW)

```markdown
# MKT/2026-WXX
hypothesis: ZZP bouw herkenbaarheid bus — gratis check → Wizard
utm_campaign: zzp_branding_check_v1
channels: meta organic, tiktok organic
cta: wizard utm_source=tiktok|meta medium=organic
asset_source: [own shoot | repo NAME | reuse FILE]
dowodca_approval: [ ] publish FB  [ ] publish TT
```

---

## STOP (sesja materiałów)

- Publish paid Meta (freeze)
- TikTok Studio spam bez `NOTES.md` + UTM
- Osobna kreacja per kanał bez mastera
- Commit sekretów / .env
- Fake „WW DONE” bez plików w GDrive lub lokalnym staging

---

## Po sesji materiałów → kolejność

1. Commander HITL FB organic (`utm_medium=organic`)
2. TT token VPS → calendar E2E ([FREE-TIKTOK](./FREE-TIKTOK.md))
3. Po **2026-08-06**: Meta paid ([META-FINAL-CHECKLIST](./META-FINAL-CHECKLIST.md))
