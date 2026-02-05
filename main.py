"""
main.py — Punkt wejścia aplikacji JADZIA

Uruchomienie:
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    
Lub:
    python main.py
"""

import os
import sys
from pathlib import Path

# Upewnij się że katalog projektu jest w PATH
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

# Utwórz folder data jeśli nie istnieje
(PROJECT_DIR / "data").mkdir(exist_ok=True)

# Import aplikacji FastAPI
from interfaces.api import app

# Eksportuj app dla uvicorn
__all__ = ["app"]


def main():
    """Uruchom serwer bezpośrednio"""
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    print("=" * 60)
    print("  JADZIA - AI Agent do zarządzania sklepem")
    print("=" * 60)
    print(f"  Uruchamiam na: http://{host}:{port}")
    print(f"  Dokumentacja:  http://{host}:{port}/docs")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[str(PROJECT_DIR / "agent"), str(PROJECT_DIR / "interfaces")]
    )


if __name__ == "__main__":
    main()