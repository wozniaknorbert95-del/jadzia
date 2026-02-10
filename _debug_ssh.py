import sys
sys.path.insert(0, '.')
import os
from dotenv import load_dotenv
load_dotenv()

# 1. Pokaż config
print("=== SSH CONFIG ===")
print(f"SSH_HOST: {os.getenv('SSH_HOST')}")
print(f"SSH_PORT: {os.getenv('SSH_PORT', '22')}")
print(f"SSH_USER: {os.getenv('SSH_USER')}")
print(f"SSH_PASSWORD: {'***SET***' if os.getenv('SSH_PASSWORD') else 'EMPTY'}")
print(f"SSH_KEY_PATH: {os.getenv('SSH_KEY_PATH', 'None')}")
print(f"BASE_PATH: {os.getenv('BASE_PATH')}")

# Alternatywne nazwy (CYBERFOLKS_*)
print(f"\nCYBERFOLKS_HOST: {os.getenv('CYBERFOLKS_HOST')}")
print(f"CYBERFOLKS_USER: {os.getenv('CYBERFOLKS_USER')}")
print(f"CYBERFOLKS_PASSWORD: {'***SET***' if os.getenv('CYBERFOLKS_PASSWORD') else 'EMPTY'}")

# 2. Test połączenia Paramiko
print("\n=== SSH CONNECTION TEST ===")
try:
    import paramiko

    host = os.getenv('SSH_HOST') or os.getenv('CYBERFOLKS_HOST')
    port = int(os.getenv('SSH_PORT') or os.getenv('CYBERFOLKS_PORT') or 22)
    user = os.getenv('SSH_USER') or os.getenv('CYBERFOLKS_USER')
    password = os.getenv('SSH_PASSWORD') or os.getenv('CYBERFOLKS_PASSWORD')

    print(f"Connecting to {user}@{host}:{port}...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=user,
        password=password,
        timeout=10
    )
    print("✅ SSH Connected!")

    # Test command
    stdin, stdout, stderr = client.exec_command('pwd')
    pwd = stdout.read().decode().strip()
    print(f"✅ PWD: {pwd}")

    # Test file exists
    base_path = os.getenv('BASE_PATH')
    stdin, stdout, stderr = client.exec_command(f'ls -la {base_path}/wp-config.php 2>&1')
    result = stdout.read().decode().strip()
    print(f"✅ wp-config.php: {result}")

    # List directory
    stdin, stdout, stderr = client.exec_command(f'ls {base_path}/ | head -10')
    files = stdout.read().decode().strip()
    print(f"✅ Files in BASE_PATH:\n{files}")

    client.close()
    print("\n✅ SSH TEST PASSED")

except Exception as e:
    print(f"❌ SSH FAILED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
