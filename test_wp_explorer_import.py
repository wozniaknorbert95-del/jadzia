"""
Test importu WPExplorer - dry run bez faktycznego skanu.
Uruchom: python test_wp_explorer_import.py
"""

import sys
import os

# Dodaj sciezke projektu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test czy wszystkie importy dzialaja."""
    print("=" * 50)
    print("TEST 1: Importy")
    print("=" * 50)

    try:
        from agent.tools.wp_explorer import WPExplorer, get_config
        print("[OK] Import WPExplorer: OK")
        print("[OK] Import get_config: OK")
    except ImportError as e:
        print(f"[FAIL] Import FAILED: {e}")
        return False

    try:
        from agent.tools.wp_explorer.models import ScanResult, ProjectStructure
        print("[OK] Import models: OK")
    except ImportError as e:
        print(f"[FAIL] Import models FAILED: {e}")
        return False

    return True


def test_config():
    """Test czy config laduje sie poprawnie."""
    print("\n" + "=" * 50)
    print("TEST 2: Konfiguracja")
    print("=" * 50)

    try:
        from agent.tools.wp_explorer import get_config
        config = get_config()

        print(f"SSH Host: {config.ssh_host}")
        print(f"SSH Port: {config.ssh_port}")
        print(f"SSH User: {config.ssh_user}")
        print(f"SSH Key Path: {config.ssh_key_path}")
        print(f"WordPress Base Path: {config.wordpress_base_path}")
        print(f"Theme Path: {config.theme_relative_path}")
        print(f"Output Path: {config.output_path}")

        # Sprawdz czy wartosci nie sa puste
        if not config.ssh_host:
            print("[WARN] WARNING: ssh_host jest pusty!")
            return False
        if not config.ssh_user:
            print("[WARN] WARNING: ssh_user jest pusty!")
            return False

        print("\n[OK] Config loaded: OK")
        return True

    except Exception as e:
        print(f"[FAIL] Config FAILED: {e}")
        return False


def test_explorer_init():
    """Test czy WPExplorer mozna zainicjalizowac."""
    print("\n" + "=" * 50)
    print("TEST 3: Inicjalizacja WPExplorer")
    print("=" * 50)

    try:
        from agent.tools.wp_explorer import WPExplorer
        explorer = WPExplorer()
        print("[OK] WPExplorer() created: OK")
        print(f"     Config SSH Host: {explorer.config.ssh_host}")
        return True

    except Exception as e:
        print(f"[FAIL] WPExplorer init FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 50)
    print("WP EXPLORER - DRY RUN TEST")
    print("=" * 50 + "\n")

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Config", test_config()))
    results.append(("Explorer Init", test_explorer_init()))

    print("\n" + "=" * 50)
    print("PODSUMOWANIE")
    print("=" * 50)

    all_passed = True
    for name, passed in results:
        status = "[OK] PASS" if passed else "[FAIL] FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] WSZYSTKIE TESTY PRZESZLY - MOZNA KONTYNUOWAC")
    else:
        print("[WARN] NIEKTORE TESTY FAILED - SPRAWDZ BLEDY")
    print("=" * 50 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
