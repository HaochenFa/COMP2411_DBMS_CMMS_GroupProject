import requests

BASE_URL = "http://127.0.0.1:5050/api"

endpoints = [
    "/reports/maintenance-summary",
    "/reports/people-summary",
    "/reports/activities-summary",
    "/reports/school-stats",
    "/reports/maintenance-frequency"
]

print("Checking Dashboard Endpoints...")
for ep in endpoints:
    try:
        res = requests.get(f"{BASE_URL}{ep}")
        if res.status_code != 200:
            print(f"❌ {ep}: Failed ({res.status_code}) - {res.text}")
        else:
            print(f"✅ {ep}: Success")
    except Exception as e:
        print(f"❌ {ep}: Connection Error - {e}")
