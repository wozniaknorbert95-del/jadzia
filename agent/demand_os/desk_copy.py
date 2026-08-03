"""Demand Desk plain-language copy — backend notes that may surface in UI."""

from __future__ import annotations

# Forbidden on primary desk surface (tests enforce via commander-ui contracts).
PRIMARY_SURFACE_FORBIDDEN = (
    "HITL",
    "CONTENT-CALENDAR",
    "ALLOWLIST",
    "ENGAGE-LOG",
    "set-now",
    "DEMAND_OS_",
    "ops_bus",
    "fixture fake",
    "UTM",
    "data_mode",
)

EMPTY_HITL_QUEUE = "Brak treści do zatwierdzenia — dodaj pozycję w kalendarzu."
EMPTY_HITL_NO_DATA = "Brak kalendarza treści na serwerze — zsynchronizuj dane operacyjne."
EMPTY_HUNT_QUEUE = "Brak celów kontaktowych — uzupełnij listę dozwolonych grup."
EMPTY_TOP_ASSETS = "Brak startów Wizard — pojawią się po pierwszym realnym wejściu."
EMPTY_TOP_ASSETS_NOTE = "Brak startów Wizard — pusta lista (nie dane testowe)."
CASH_WARNING_PARKED = "Publikowanie wstrzymane — przychody ruszą po odblokowaniu"
CONN_BANNER = "Brak połączenia — sprawdź logowanie i sieć."
LEDGER_BTN = "Dziennik dziś"
LEDGER_TOAST_OK = "Dziennik — wpis na dziś"
HITL_ERR = "Nie udało się zapisać decyzji — sprawdź pozycję w kalendarzu."
HUNT_CONFIRM = "Wysłać komentarz testowy do {target}? (bez publikacji na FB)"
SCOPE_VIEWER = "Tryb tylko odczyt — akcje wyłączone."
SCOPE_FORBIDDEN = "Brak uprawnień do Biura Popytu — tylko ograniczony odczyt."
ICP_REQUIRED = "Rola tygodnia i hasło (min 3 znaki) są wymagane"
ICP_SAVED = "Rola tygodnia zapisana"
GA4_UNAVAILABLE_STUB = "GA4 wyłączone (brak trybu live)"
GA4_UNAVAILABLE_CREDS = "GA4 niedostępne — brak konfiguracji"
GA4_UNAVAILABLE_ERROR = "GA4 niedostępne — błąd odczytu"
