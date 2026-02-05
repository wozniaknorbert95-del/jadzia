import os
from pathlib import Path

def check_file(path):
    p = Path(path)
    if not p.exists():
        return "BRAK", 0
    size = p.stat().st_size
    if size == 0:
        return "PUSTY", 0
    elif size < 50:
        return "PRAWIE PUSTY", size
    else:
        return "OK", size

# Wszystkie wymagane pliki
files = [
    # Główne
    ("main.py", True),
    (".env", True),
    ("pyproject.toml", True),
    ("run.bat", False),
    
    # Agent
    ("agent/__init__.py", True),
    ("agent/context.py", True),
    ("agent/guardrails.py", True),
    ("agent/state.py", True),
    ("agent/log.py", True),
    ("agent/diff.py", True),
    ("agent/tools.py", True),
    ("agent/prompt.py", True),
    ("agent/agent.py", True),
    
    # Interfaces
    ("interfaces/__init__.py", True),
    ("interfaces/api.py", True),
]

print("=" * 70)
print("JADZIA - DIAGNOSTYKA PLIKOW")
print("=" * 70)

missing_required = []
all_ok = True

for filepath, required in files:
    status, size = check_file(filepath)
    
    if status == "BRAK":
        marker = "[!!!]" if required else "[---]"
        if required:
            missing_required.append(filepath)
            all_ok = False
    elif status == "PUSTY":
        marker = "[!!!]"
        missing_required.append(filepath)
        all_ok = False
    elif status == "PRAWIE PUSTY":
        marker = "[OK ]"  # __init__.py może być mały
    else:
        marker = "[OK ]"
    
    print(f"{marker} {filepath:35} {status:15} ({size} B)")

print("=" * 70)

# Sprawdź .env
print("\nSprawdzam .env...")
if Path(".env").exists():
    content = Path(".env").read_text()
    
    checks = [
        ("ANTHROPIC_API_KEY", "sk-ant-"),
        ("CYBERFOLKS_HOST", ""),
        ("CYBERFOLKS_USER", ""),
    ]
    
    for key, prefix in checks:
        if f"{key}=" in content:
            line = [l for l in content.split('\n') if l.startswith(f"{key}=")]
            if line:
                value = line[0].split('=', 1)[1].strip()
                if prefix and value.startswith(prefix):
                    print(f"  [OK ] {key} = {value[:20]}...")
                elif value and value != f"{key}":
                    print(f"  [OK ] {key} = (ustawiony)")
                else:
                    print(f"  [!!!] {key} = PUSTY lub niepoprawny")
        else:
            print(f"  [!!!] {key} = BRAK")
else:
    print("  [!!!] Plik .env nie istnieje!")

# Sprawdź SSH key
print("\nSprawdzam SSH key...")
ssh_key_path = os.getenv("CYBERFOLKS_KEY_PATH", "")
if ssh_key_path:
    if Path(ssh_key_path).exists():
        print(f"  [OK ] Klucz SSH istnieje: {ssh_key_path}")
    else:
        print(f"  [!!!] Klucz SSH NIE istnieje: {ssh_key_path}")
else:
    # Sprawdź w .env
    if Path(".env").exists():
        content = Path(".env").read_text()
        if "CYBERFOLKS_KEY_PATH=" in content:
            line = [l for l in content.split('\n') if l.startswith("CYBERFOLKS_KEY_PATH=")]
            if line:
                path = line[0].split('=', 1)[1].strip()
                if path and Path(path).exists():
                    print(f"  [OK ] Klucz SSH: {path}")
                elif path:
                    print(f"  [!!!] Klucz SSH nie istnieje: {path}")
                else:
                    print(f"  [---] CYBERFOLKS_KEY_PATH pusty (użyje hasła)")
        elif "CYBERFOLKS_PASSWORD=" in content:
            print(f"  [OK ] Użyje hasła SSH (CYBERFOLKS_PASSWORD ustawione)")
        else:
            print(f"  [!!!] Brak CYBERFOLKS_KEY_PATH ani CYBERFOLKS_PASSWORD")

print("=" * 70)

if all_ok:
    print("\n[OK] Wszystkie wymagane pliki sa na miejscu!")
    print("\nUruchom JADZIA:")
    print("  python main.py")
    print("  lub")
    print("  run.bat")
else:
    print(f"\n[!!!] BRAKUJE {len(missing_required)} WYMAGANYCH PLIKOW:")
    for f in missing_required:
        print(f"  - {f}")