"""
Skrypt diagnostyczny połączenia SSH.
Ładuje konfigurację z .env (SSH_* i CYBERFOLKS_*) i próbuje połączyć się przez paramiko.
"""

import os
import sys
import traceback

from dotenv import load_dotenv

load_dotenv()

# Odczyt z .env (prefiksy SSH_ i CYBERFOLKS_)
host = os.getenv("SSH_HOST") or os.getenv("CYBERFOLKS_HOST", "")
port_raw = os.getenv("SSH_PORT") or os.getenv("CYBERFOLKS_PORT") or "22"
user = os.getenv("SSH_USER") or os.getenv("CYBERFOLKS_USER", "")
password = os.getenv("SSH_PASSWORD", "")
key_path_raw = os.getenv("SSH_KEY_PATH") or os.getenv("CYBERFOLKS_KEY_PATH", "") or None

# Port jako int
try:
    port = int(port_raw)
except (TypeError, ValueError):
    port = None

# Plik klucza tylko jeśli istnieje
key_path = None
if key_path_raw and key_path_raw.strip():
    key_path = key_path_raw.strip() if os.path.exists(key_path_raw.strip()) else None

# --- 1. Wypisanie wczytanych wartości (bez hasła/klucza) ---
print("=== Konfiguracja SSH (z .env) ===")
print(f"  Host:     {host or '(pusty)'}")
print(f"  User:     {user or '(pusty)'}")
print(f"  Port:     {port_raw} -> {port if port is not None else 'BLAD: nieprawidlowa wartosc'}")
print(f"  Key Path: {key_path_raw or '(nie ustawiony)'}")
print(f"  Haslo:    {'(ustawione)' if password else '(puste)'}")
print()

# --- 2. Sprawdzenie istnienia pliku klucza ---
if key_path_raw and key_path_raw.strip():
    exists = os.path.exists(key_path_raw.strip())
    print(f"  Plik klucza istnieje na dysku: {exists}")
    if not exists:
        print(f"  Sciezka sprawdzana: {os.path.abspath(key_path_raw.strip())}")
else:
    print("  Plik klucza: nie skonfigurowany (uzycie hasla)")
print()

# --- 3. Walidacja przed polaczeniem ---
if not host or not user:
    print("BLAD: Brak Host lub User w .env. Ustaw SSH_HOST/CYBERFOLKS_HOST oraz SSH_USER/CYBERFOLKS_USER.")
    sys.exit(1)
if port is None:
    print("BLAD: Port musi byc liczba. Sprawdz SSH_PORT / CYBERFOLKS_PORT.")
    sys.exit(1)
if not key_path and not password:
    print("BLAD: Potrzebny plik klucza (SSH_KEY_PATH) lub haslo (SSH_PASSWORD).")
    sys.exit(1)

# --- 4. Polaczenie paramiko z pelnym logowaniem bledow ---
print("=== Probuje polaczenia SSH (paramiko) ===")
try:
    import paramiko

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connect_kwargs = {
        "hostname": host,
        "port": port,
        "username": user,
        "timeout": 30,
    }
    if key_path:
        connect_kwargs["key_filename"] = key_path
    if password:
        connect_kwargs["password"] = password

    client.connect(**connect_kwargs)
    client.close()

    print("SUKCES")
except Exception as e:
    print("NIEPOWODZENIE")
    print()
    print("Typ wyjatku:", type(e).__name__)
    print("Wiadomosc:", e)
    print()
    print("Pelny traceback:")
    print(traceback.format_exc())
    sys.exit(1)
