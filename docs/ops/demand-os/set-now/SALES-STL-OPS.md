---
todo: DOS-W1-04 · DOS-A2A-01
os_target_section_ref: "Agent_Sales · B.6 · E A2A"
status: done
set_at: "2026-08-01"
---

# Sales STL Ops — Wave1

## SLA (twarde)

| Klasa | SLA | Akcja |
|-------|-----|-------|
| hot | &lt;15 min (cel &lt;5) | Wizard link w **pierwszej** sensownej odpowiedzi |
| overnight | **0** | nie zostawiaj „na jutro” |
| cold | &lt;4h | nadal CTA Wizard, nie offerte-koniec |

## A2A handoffs

| Handoff | SLA | Owner |
|---------|-----|-------|
| `engage_event` → Sales | hot &lt;15m | Agent_Sales |
| `lead_hot` → Wizard | &lt;15m | Agent_Sales |
| `publish_request` → Val | &lt;5m | Sniper_Validator |

## Kanały → UTM

| Kanał | utm_source | asset_id przykład |
|-------|------------|-------------------|
| WhatsApp | whatsapp | wa_w31_install_01 |
| Widget | widget | wid_w31_install_01 |
| TT comment | tiktok | tt_w31_install_01 |
| FB | facebook | fb_w31_install_01 |

## Szablon NL (hot)

```text
Top dat je reageert. Wil je meteen zien wat het voor jouw bus kost?
Start hier (2 min): https://zzpackage.flexgrafik.nl/wizard/?utm_source=whatsapp&utm_medium=organic&utm_campaign=icp_installateur&utm_content=wa_w31_install_01
```

## Logowanie

Każdy hot → wiersz LEDGER: `hot_leads` += 1 · `notes` = `STL t_recv=… t_reply=… delta_min=…`

Zakaz: offrete jako koniec · „stuur ik later” · dual cash DA.
