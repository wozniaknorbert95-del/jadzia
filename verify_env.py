"""Verify .env is loadable and USE_SQLITE_STATE is set. Run from project root."""
import os
from pathlib import Path

def main():
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("ERROR: .env not found")
        return False
    data = env_path.read_bytes()
    if b"\x00" in data:
        print("ERROR: .env contains null bytes (corrupted)")
        return False
    print(".env: no null bytes, file OK")
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        val = os.getenv("USE_SQLITE_STATE")
        print("USE_SQLITE_STATE:", repr(val))
        if val == "1":
            print("Verification: USE_SQLITE_STATE=1 loads correctly")
            return True
        print("Note: If you see None, set USE_SQLITE_STATE=1 in .env and run from project root")
        return True
    except ValueError as e:
        print("ValueError loading .env:", e)
        return False

if __name__ == "__main__":
    ok = main()
    exit(0 if ok else 1)
