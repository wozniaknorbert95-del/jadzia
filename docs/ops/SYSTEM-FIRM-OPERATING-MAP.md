---
status: "[SOT · AS-IS DZIAŁY]"
title: "SYSTEM FIRM OPERATING MAP — działy jak w normalnej firmie"
updated: "2026-07-31"
owner: "Dowódca"
authority: "AS-IS mapa działów — jak jest dziś"
problem: "Backend Trap — bez popytu Wizard nie zarabia"
strategy_sot: "docs/ops/strategy/STRATEGY-PACK.md"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md"
---

# SYSTEM FIRM OPERATING MAP

> Mapa **działów AS-IS** — kto za co odpowiada, kto co robi, po co (euro).  
> Silnik kasy = Wizard. Reszta albo karmi silnik, albo jest sterem/kosztem.  
> **Strategia SoT:** [`strategy/STRATEGY-PACK.md`](./strategy/STRATEGY-PACK.md) (snajper).  
> **OS TO-BE:** [`SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`](./SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md).

```mermaid
flowchart TB
  CEO[DOWODCA_Owner_CEO]

  CEO --> MKT[MARKETING]
  CEO --> SALES[SPRZEDAZ]
  CEO --> COM[COMMERCE_WIZARD]
  CEO --> DES[DESIGN]
  CEO --> OPS[ORDER_PRODUKCJA]
  CEO --> FIN[FINANSE]
  CEO --> CS[CS]
  CEO --> GOV[ZARZADZANIE_HQ]
  CEO --> ENG[ENGINEERING]
  CEO --> QF[QUIETFORGE_produkt]

  style CEO fill:#111,color:#fff
  style MKT fill:#E11D48,color:#fff
  style SALES fill:#EA580C,color:#fff
  style COM fill:#CA8A04,color:#fff
  style DES fill:#7C3AED,color:#fff
  style OPS fill:#2563EB,color:#fff
  style FIN fill:#059669,color:#fff
  style CS fill:#0891B2,color:#fff
  style GOV fill:#64748B,color:#fff
  style ENG fill:#44403C,color:#fff
  style QF fill:#9F1239,color:#fff
```

---

## MARKETING — czerwony

**Po co w firmie:** bez uwagi nie ma klientów → bez klientów Wizard = €0.

```mermaid
flowchart TB
  subgraph MKT [DZIAL_MARKETING]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_HITL_Dowodca]
    WHO2[Pomaga_Marketing_OS_jadzia]
    WHO3[TOBE_Growth_Architect_Asset_24_7]

    JOB1[Robi_co]
    J1[krece_material_bus_before_after]
    J2[publikuje_TikTok_primary]
    J3[dokleja_UTM_do_kazdego_linku]
    J4[cross_FB_po_TT]
    J5[Money_Check_starts_co_tydzien]

    WHY[Dlaczego]
    W1[wpuszcza_ruch_do_lejka]
    W2[bez_tego_Backend_Trap]
  end

  OWN --> WHO1
  OWN --> WHO2
  WHO1 --> JOB1
  JOB1 --> J1 --> J2 --> J3 --> J4 --> J5
  J5 --> WHY --> W1 --> W2

  style MKT fill:#E11D48,color:#fff
```

**Narzędzia:** TikTok, FB, GDrive, jadzia Marketing OS, GA4  
**Start:** `GO TIKTOK ORGANIC` · Ads FREEZE do 2026-08-06

---

## SPRZEDAŻ / CONCIERGE — pomarańcz

**Po co w firmie:** lead stygnie w godzinę — ktoś musi domknąć rozmowę do Wizard.

```mermaid
flowchart TB
  subgraph SALES [DZIAL_SPRZEDAZ]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_Widget_AI_Sprzedawca]
    WHO2[Robi_HITL_Dowodca_WA_TG]
    WHO3[TOBE_Lead_Scoring_AI]

    JOB1[co_robi]
    J1[odpowiada_na_chat_widget]
    J2[Speed_to_Lead_ponizej_15_min]
    J3[pcha_CTA_do_Wizard]
    J4[zero_leadow_overnight]

    WHY[Dlaczego]
    W1[zamienia_uwage_w_sesje_Wizard]
    W2[bez_tego_ruch_umiera]
  end

  OWN --> WHO1
  OWN --> WHO2
  WHO1 --> JOB1
  WHO2 --> JOB1
  JOB1 --> J1 --> J2 --> J3 --> J4
  J4 --> WHY --> W1 --> W2

  style SALES fill:#EA580C,color:#fff
```

**Narzędzia:** widget INT-001, Commander, Telegram, WhatsApp

---

## COMMERCE / WIZARD — złoty = SILNIK €

**Po co w firmie:** jedyna droga zakupu. Tu powstają pieniądze. Reszta firmy istnieje, żeby tu ktoś wszedł i zapłacił.

```mermaid
flowchart TB
  subgraph COM [DZIAL_COMMERCE_WIZARD]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_Wizard_UI_zzpackage]
    WHO2[Robi_WooCommerce]
    WHO3[Robi_Mollie_platnosc]
    WHO4[TOBE_Mockup_AI_Dynamic_Price]

    JOB1[co_robi]
    J1[konfiguracja_pakietu_ZZP]
    J2[checkout_min_199_EUR]
    J3[capture_platnosci]
    J4[dogfood_co_tydzien]

    WHY[Dlaczego]
    W1[JEDYNY_GENERATOR_EURO]
    W2[bez_ruchu_z_Marketing_i_Sales_tu_jest_zero]
  end

  OWN --> WHO1 --> WHO2 --> WHO3
  WHO1 --> JOB1 --> J1 --> J2 --> J3 --> J4
  J4 --> WHY --> W1 --> W2

  style COM fill:#CA8A04,color:#fff
```

**Guard:** marża ≥60% · Gate D / skala Mollie tylko z GO

---

## DESIGN / INSPIRE — fiolet

**Po co w firmie:** ZZP kupuje oczami — musi zobaczyć bus / branding zanim zapłaci.

```mermaid
flowchart TB
  subgraph DES [DZIAL_DESIGN]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_Inspire_agent]
    WHO2[Robi_HITL_Illustrator]
    WHO3[TOBE_Mockup_AI_w_Wizard_3s]

    JOB1[co_robi]
    J1[brief_i_mockup_inspiracyjny]
    J2[dostarcza_proof_visual_do_Marketing]
    J3[wspiera_oferte_przed_checkout]

    WHY[Dlaczego]
    W1[buduje_zaufanie_i_wow]
    W2[NIE_zastepuje_platnosci]
  end

  OWN --> WHO1 --> WHO2
  WHO1 --> JOB1 --> J1 --> J2 --> J3
  J3 --> WHY --> W1 --> W2

  style DES fill:#7C3AED,color:#fff
```

---

## ORDER / PRODUKCJA / ERKA — niebieski

**Po co w firmie:** po płatności ktoś musi zrobić i dostarczyć — inaczej nie ma powtórki ani case’a do Marketingu.

```mermaid
flowchart TB
  subgraph OPS [DZIAL_ORDER_PRODUKCJA]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_INT002_mirror_jadzia]
    WHO2[Robi_Erka_partner_HITL]
    WHO3[Widzi_Order_Desk_RO_PARK]
    WHO4[TOBE_Order_Intelligence_ops_state]

    JOB1[co_robi]
    J1[przyjmuje_paid_order]
    J2[triage_brief_pliki]
    J3[produkcja_u_partnera]
    J4[wysylka_i_status_dla_klienta]

    WHY[Dlaczego]
    W1[domyka_obietnice_po_pieniadzach]
    W2[dziś_desk_nie_LIVE_HITL_checklist]
  end

  OWN --> WHO1 --> WHO2
  WHO3 -.-> WHO1
  WHO1 --> JOB1 --> J1 --> J2 --> J3 --> J4
  J4 --> WHY --> W1 --> W2

  style OPS fill:#2563EB,color:#fff
```

**Zakaz:** fake S7 / Order LIVE bez GO UNPARK

---

## FINANSE — zielony

**Po co w firmie:** pilnuje, żeby zamówienie nie było „sprzedażą na stratę”.

```mermaid
flowchart TB
  subgraph FIN [DZIAL_FINANSE]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_HITL_margin_check]
    WHO2[Dane_WC_Mollie_koszt_Erka]
    WHO3[TOBE_Finance_Autopilot]

    JOB1[co_robi]
    J1[po_kazdym_paid_cena_minus_koszt]
    J2[pilnuje_marzy_ge_60pct]
    J3[eskaluje_gdy_marza_spada]

    WHY[Dlaczego]
    W1[skala_bez_marzy_zabija_firme]
  end

  OWN --> WHO1 --> WHO2
  WHO1 --> JOB1 --> J1 --> J2 --> J3 --> WHY --> W1

  style FIN fill:#059669,color:#fff
```

---

## CS — cyan

**Po co w firmie:** zadowolony klient = kolejny lead / case do TikToka.

```mermaid
flowchart TB
  subgraph CS [DZIAL_CS]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_CS_tickets_COI]
    WHO2[Robi_HITL_WA_TG]
    WHO3[TOBE_CS_Auto_Loop]

    JOB1[co_robi]
    J1[kontakt_Dplus3_po_dostawie]
    J2[zbiera_feedback_i_zgode_na_case]
    J3[upsell_gdy_pasuje]

    WHY[Dlaczego]
    W1[zamyka_petle_z_powrotem_do_Marketing]
  end

  OWN --> WHO1 --> WHO2
  WHO1 --> JOB1 --> J1 --> J2 --> J3 --> WHY --> W1

  style CS fill:#0891B2,color:#fff
```

---

## ZARZĄDZANIE / HQ / VCMS — szary = STER

**Po co w firmie:** porządek i bezpieczeństwo decyzji — **nie sprzedaż**.

```mermaid
flowchart TB
  subgraph GOV [DZIAL_ZARZADZANIE]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_VHQ_Commander]
    WHO2[Robi_VCMS_scan]
    WHO3[Robi_meta_reguly_GO_deploy]

    JOB1[co_robi]
    J1[Conflicts_0]
    J2[GO_na_deploy_cene_partnera]
    J3[STOP_fake_S7_Mollie_bez_GO]

    WHY[Dlaczego]
    W1[chroni_prod]
    W2[NIE_generuje_euro]
    W3[za_duzo_czasu_tu_rowna_sie_Backend_Trap]
  end

  OWN --> WHO1 --> WHO2 --> WHO3
  WHO1 --> JOB1 --> J1 --> J2 --> J3
  J3 --> WHY --> W1 --> W2 --> W3

  style GOV fill:#64748B,color:#fff
```

---

## ENGINEERING / AGENT OS — grafit = KOSZT

**Po co w firmie:** buduje bramki, które skracają drogę do euro — albo stoi.

```mermaid
flowchart TB
  subgraph ENG [DZIAL_ENGINEERING]
    OWN[Odpowiada_Dowodca]
    WHO1[Robi_agent_os_HITL]
    WHO2[Robi_kod_jadzia_Wizard_tylko_GO]

    JOB1[co_robi]
    J1[1_gate_1_modul_1_sesja]
    J2[tylko_bramki_G1_do_G7]
    J3[PARK_gdy_nie_ma_sciezki_do_euro]

    WHY[Dlaczego]
    W1[przyspiesza_dostawe]
    W2[bez_GO_BUILD_nie_koduje_produktu]
  end

  OWN --> WHO1 --> WHO2
  WHO1 --> JOB1 --> J1 --> J2 --> J3 --> WHY --> W1 --> W2

  style ENG fill:#44403C,color:#fff
```

---

## QUIETFORGE — bordo = PRODUKT OS (osobno)

**Po co:** sprzedaż systemu innym — **po** tym jak FlexGrafik zarobi na sobie.

```mermaid
flowchart TB
  subgraph QF [QUIETFORGE]
    OWN[Odpowiada_Dowodca]
    WHO1[Pitch_deck]
    WHO2[Mapa_tego_OS_na_FG]
    WHO3[PrintPack_ROADMAP]

    WHY[Dlaczego]
    W1[to_produkt_nie_cash_loop_FG]
    W2[ZAKAZ_budowy_SaaS_zamiast_Marketing]
  end

  OWN --> WHO1 --> WHO2 --> WHO3 --> WHY --> W1 --> W2

  style QF fill:#9F1239,color:#fff
```

---

## JAK DZIAŁY PODAJĄ SOBIE PIŁKĘ (normalna firma)

```mermaid
flowchart LR
  MKT[MARKETING_uwaga] --> SALES[SPRZEDAZ_domknij]
  SALES --> COM[WIZARD_zaplac]
  DES[DESIGN_pokaz] --> SALES
  DES --> COM
  COM --> OPS[ORDER_zrob]
  OPS --> FIN[FINANSE_marza]
  OPS --> CS[CS_feedback]
  CS --> MKT
  GOV[ZARZADZANIE] -.->|pilnuje| COM
  ENG[ENGINEERING] -.->|buduje_tylko_GO| MKT
  ENG -.-> COM
  ENG -.-> OPS

  style MKT fill:#E11D48,color:#fff
  style SALES fill:#EA580C,color:#fff
  style COM fill:#CA8A04,color:#fff
  style DES fill:#7C3AED,color:#fff
  style OPS fill:#2563EB,color:#fff
  style FIN fill:#059669,color:#fff
  style CS fill:#0891B2,color:#fff
  style GOV fill:#64748B,color:#fff
  style ENG fill:#44403C,color:#fff
```

---

## GDZIE DZIŚ PADA PIŁKA

```mermaid
flowchart LR
  MKT[MARKETING] -->|URYWA_brak_rytmu_TT| SALES
  SALES -->|URYWA_STL_HITL| COM
  COM -->|SLABE_bez_ruchu| OPS
  GOV[HQ] -->|ZABIERA_CZAS| MKT
  ENG[AgentOS] -->|ZABIERA_CZAS| MKT

  style MKT fill:#E11D48,color:#fff
  style SALES fill:#EA580C,color:#fff
  style COM fill:#CA8A04,color:#fff
  style OPS fill:#2563EB,color:#fff
  style GOV fill:#64748B,color:#fff
  style ENG fill:#44403C,color:#fff
```

---

## JUTRO RANO — kto co robi

```mermaid
flowchart TD
  D[DOWODCA] --> M[MARKETING_1_clip_TT_plus_UTM]
  D --> S[SPRZEDAZ_telefon_WA_ponizej_15min]
  D --> X[STOP_HQ_STOP_kod_STOP_Ads]

  M --> W[mierzy_Wizard_start]
  S --> W
  W --> P[cel_Paid_real]

  style D fill:#111,color:#fff
  style M fill:#E11D48,color:#fff
  style S fill:#EA580C,color:#fff
  style X fill:#64748B,color:#fff
  style W fill:#CA8A04,color:#fff
  style P fill:#059669,color:#fff
```

**ACCEPT:** `ACCEPT SYSTEM-FIRM-OPERATING-MAP`  
**START:** `GO TIKTOK ORGANIC`
