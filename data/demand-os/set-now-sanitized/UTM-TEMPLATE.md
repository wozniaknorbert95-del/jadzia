---
todo: DOS-C1-03 · DOS-C1-04
os_target_section_ref: "C.1 #3 · C.1 #4"
status: done
set_at: "2026-07-31"
---

# UTM Template + Gra bridge

## Template (OS C.1 #3 — 1:1)

```
https://zzpackage.flexgrafik.nl/wizard/?utm_source={channel}&utm_medium=organic&utm_campaign=icp_{role}&utm_content={asset_id}
```

## Wypełnione przykłady (W1 installateur)

| asset_id | channel | URL |
|----------|---------|-----|
| `tt_w31_install_01` | tiktok | `https://zzpackage.flexgrafik.nl/wizard/?utm_source=tiktok&utm_medium=organic&utm_campaign=icp_installateur&utm_content=tt_w31_install_01` |
| `fb_w31_install_01` | facebook | `https://zzpackage.flexgrafik.nl/wizard/?utm_source=facebook&utm_medium=organic&utm_campaign=icp_installateur&utm_content=fb_w31_install_01` |
| `blog_w31_install_01` | blog | `https://zzpackage.flexgrafik.nl/wizard/?utm_source=blog&utm_medium=organic&utm_campaign=icp_installateur&utm_content=blog_w31_install_01` |
| `da_w31_install_01` | design_agent | `https://zzpackage.flexgrafik.nl/wizard/?utm_source=design_agent&utm_medium=organic&utm_campaign=icp_installateur&utm_content=da_w31_install_01` |
| `wa_w31_install_01` | whatsapp | `https://zzpackage.flexgrafik.nl/wizard/?utm_source=whatsapp&utm_medium=organic&utm_campaign=icp_installateur&utm_content=wa_w31_install_01` |

## Gra bridge (C.1 #4)

| Reguła | Wartość |
|--------|---------|
| Osobny post | tylko `https://app.flexgrafik.nl` (+ GAME10 → Wizard coupon) |
| Zakaz | Wizard CTA równolegle w tym samym poście |
| Validator | „gra = 1 CTA game” = FAIL jeśli drugi link |
