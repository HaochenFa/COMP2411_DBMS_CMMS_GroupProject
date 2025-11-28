import requests
import json

BASE_URL = "http://127.0.0.1:5050/api"


def verify_api_schema():
    print("Verifying API Schema...")

    # 1. Check Maintenance
    try:
        response = requests.get(f"{BASE_URL}/maintenance")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                item = data[0]
                if 'active_chemical' in item:
                    print("✅ Maintenance: 'active_chemical' field present.")
                    print(f"   Sample value: {item['active_chemical']}")
                else:
                    print("❌ Maintenance: 'active_chemical' field MISSING.")
                    print(f"   Keys found: {list(item.keys())}")
            else:
                print("⚠️ Maintenance: No data returned.")
        else:
            print(f"❌ Maintenance: API Error {response.status_code}")
    except Exception as e:
        print(f"❌ Maintenance: Request failed - {e}")

    # 2. Check Locations
    try:
        response = requests.get(f"{BASE_URL}/locations")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                item = data[0]
                if 'building' in item:
                    print("✅ Locations: 'building' field present.")
                    print(f"   Sample value: {item['building']}")
                else:
                    print("❌ Locations: 'building' field MISSING.")
                    print(f"   Keys found: {list(item.keys())}")
            else:
                print("⚠️ Locations: No data returned.")
        else:
            print(f"❌ Locations: API Error {response.status_code}")
    except Exception as e:
        print(f"❌ Locations: Request failed - {e}")


if __name__ == "__main__":
    verify_api_schema()
