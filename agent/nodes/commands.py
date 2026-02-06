"""
Węzły obsługi komend (status, rollback, help).
Returns: (response_text, awaiting_input, input_type)
"""

from typing import Tuple, Optional

from ..state import load_state, clear_state
from ..tools import rollback, test_ssh_connection
from ..alerts import send_alert


async def handle_status(
    chat_id: str,
    source: str,
) -> Tuple[str, bool, Optional[str]]:
    """Obsługa komendy /status"""
    state = load_state(chat_id, source)

    if not state:
        return ("✅ Agent jest gotowy. Brak aktywnych operacji.", False, None)

    return (
        f"**STATUS AGENTA**\n\n"
        f"ID: {state.get('id', 'brak')}\n"
        f"Status: {state.get('status', 'nieznany')}\n"
        f"Polecenie: {state.get('user_input', 'brak')[:100]}\n"
        f"Pliki do zmiany: {len(state.get('files_to_modify', []))}\n"
        f"Pliki zapisane: {len(state.get('files_written', []))}\n"
        f"Oczekuje odpowiedzi: {state.get('awaiting_response', False)}\n"
        f"Typ odpowiedzi: {state.get('awaiting_type', 'brak')}",
        False, None
    )


async def handle_rollback(
    chat_id: str,
    source: str,
) -> Tuple[str, bool, Optional[str]]:
    """Obsługa /rollback"""
    result = rollback(operation_id=None, chat_id=chat_id, source=source)
    clear_state(chat_id, source)

    if result["status"] == "ok":
        send_alert("rollback_executed", None, result.get("msg", "OK"))
        return (f"✅ Rollback zakonczony.\nPrzywrocono: {', '.join(result.get('restored', []))}", False, None)
    else:
        send_alert("rollback_failed", None, result.get("msg", "Rollback failed"))
        return (f"⚠️ Rollback: {result['msg']}", False, None)


def handle_help(
    chat_id: str,
    source: str,
) -> Tuple[str, bool, Optional[str]]:
    """Obsługa /help"""
    return (
        "**JADZIA - Pomoc**\n\n"
        "Jestem asystentem do zarzadzania sklepem internetowym.\n\n"
        "**Komendy:**\n"
        "/status - sprawdz status agenta\n"
        "/rollback - cofnij ostatnie zmiany\n"
        "/clear - wyczysc stan (awaryjne)\n"
        "/test - test polaczenia SSH\n"
        "/help - ta pomoc\n\n"
        "**Przyklady polecen:**\n"
        "- 'Zmien kolor przyciskow na niebieski'\n"
        "- 'Wylistuj pliki w motywie child'\n"
        "- 'Dodaj baner promocyjny na stronie glownej'\n"
        "- 'Popraw tekst w stopce'\n\n"
        "**Odpowiedzi:**\n"
        "- T / tak - zatwierdz zmiany\n"
        "- N / nie - odrzuc zmiany\n\n"
        "Zawsze pokazuje zmiany przed zapisaniem i czekam na Twoja zgode.",
        False, None
    )


async def handle_clear(
    chat_id: str,
    source: str,
) -> Tuple[str, bool, Optional[str]]:
    """Obsługa /clear"""
    clear_state(chat_id, source)
    return ("✅ Stan wyczyszczony. Agent gotowy do nowych polecen.", False, None)


async def handle_test() -> Tuple[str, bool, Optional[str]]:
    """Obsługa /test"""
    success, msg = test_ssh_connection()
    if success:
        return (f"✅ Test SSH: OK\n{msg}", False, None)
    else:
        return (f"❌ Test SSH: BLAD\n{msg}", False, None)
