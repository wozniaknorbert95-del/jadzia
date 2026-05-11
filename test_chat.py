import requests
import json

url = "http://127.0.0.1:8000/api/v1/widget/chat"
payload = {
    "session_id": "test_cli_manual",
    "message": "Hallo, hoe gaat het?"
}

try:
    response = requests.post(url, json=payload, timeout=20)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
