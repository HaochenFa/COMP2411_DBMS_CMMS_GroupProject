import requests
import json

BASE_URL = "http://127.0.0.1:5050/api/reports"

endpoints = [
    "/maintenance-summary",
    "/people-summary",
    "/activities-summary",
    "/school-stats",
    "/maintenance-frequency"
]

print(f"Testing endpoints at {BASE_URL}...\n")

for ep in endpoints:
    url = BASE_URL + ep
    try:
        response = requests.get(url)
        status = response.status_code
        print(f"[{status}] {ep}")
        if status != 200:
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"[FAIL] {ep}")
        print(f"    Exception: {e}")

print("\nDone.")
