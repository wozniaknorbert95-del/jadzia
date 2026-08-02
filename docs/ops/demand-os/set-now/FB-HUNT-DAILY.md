---
status: "[ACTIVE · SOFT-START]"
updated: "2026-08-01"
todo: DOS-W2-01
actor: "Trebron Norbert (personal FB) via Chrome CDP HITL"
---

# FB Hunt — daily playbook (45–60 min)

**Allowlist `active` only:** fb_g2, fb_g3, fb_g4, fb_g5, fb_g6, fb_g9  
(`join_requested` g1/g7/g8/g10 = czekaj admin — **nie blocker**)

## Reguły (agency)

1. **1 grupa / dzień** — ten sam copy ≠ 2 grupy (anti-spam F3)
2. Comment = **1 wartość NL** + **1 CTA** Wizard UTM `utm_source=facebook`
3. Przed comment z linkiem: Val C.5 (`demand_os_f2 validate` lub sanity UTM Lock)
4. **Nie** twierdź że jesteś hovenier / VCA / fake trade
5. Live Graph comment env = PARK; **CDP HITL = OK**
6. Ads / boost = STOP

## UTM template

```text
https://zzpackage.flexgrafik.nl/wizard/?utm_source=facebook&utm_medium=organic&utm_campaign=icp_installateur&utm_content={asset_id}
```

`asset_id` przykład: `fb_hunt_w32_d1`

## Rotacja grup (sugerowana)

| Dzień sprintu | target_id |
|---------------|-----------|
| D1 | fb_g2 |
| D2 | fb_g3 |
| D3 | fb_g4 |
| D4 | fb_g5 |
| D5 | fb_g6 |
| D6 | fb_g9 |
| D7+ | rotate again |

## Po każdym comment

1. Append [`ENGAGE-LOG.jsonl`](./ENGAGE-LOG.jsonl) (target_id, asset_id, utm, ok)
2. LEDGER: `channel=facebook` · `comments_sent=1` · `publish_Y/N=N` (engage ≠ publish)
3. Notes: short quote kontekstu wątku (bez PII)

## DoD → DOS-W2-PASS

≥1 qualified comment / dzień roboczy × **5** dni z rzędu.

## Blocker log 2026-08-01

| target | evidence | next |
|--------|----------|------|
| fb_g2 | Personal: banner verify · `Opublikuj` disabled | czekaj admin verify |
| fb_g3 | Personal joined · `Opublikuj` stayed disabled after fill (CDP React) | Dowódca paste HITL z banku **lub** comment as Page |
| Comment bank | [`FB-HUNT-COMMENTS-W32.md`](./FB-HUNT-COMMENTS-W32.md) | Val PASS d1 · prep d2 |
| Policy tip | Page FlexGrafik can comment where Page is member | optional until personal verify clears |
