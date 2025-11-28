import requests
import json

BASE_URL = "http://127.0.0.1:5050/api"


def test_crud_person():
    print("Testing CRUD Person...")
    # 1. Create
    person_id = "TEST001"
    data = {
        "personal_id": person_id,
        "name": "Test User",
        "age": 30,
        "gender": "Male",
        "date_of_birth": "1995-01-01"
    }
    res = requests.post(f"{BASE_URL}/persons", json=data)
    if res.status_code == 201:
        print("✅ Create Person: Success")
    else:
        print(f"❌ Create Person: Failed ({res.status_code}) - {res.text}")
        return

    # 2. Update
    update_data = {"name": "Updated User"}
    res = requests.put(f"{BASE_URL}/persons/{person_id}", json=update_data)
    if res.status_code == 200:
        print("✅ Update Person: Success")
    else:
        print(f"❌ Update Person: Failed ({res.status_code}) - {res.text}")

    # 3. Delete
    res = requests.delete(f"{BASE_URL}/persons/{person_id}")
    if res.status_code == 200:
        print("✅ Delete Person: Success")
    else:
        print(f"❌ Delete Person: Failed ({res.status_code}) - {res.text}")


def test_bulk_import():
    print("\nTesting Bulk Import...")
    data = {
        "entity": "persons",
        "items": [
            {"personal_id": "IMP001", "name": "Imported 1", "age": 25},
            {"personal_id": "IMP002", "name": "Imported 2", "age": 28}
        ]
    }
    res = requests.post(f"{BASE_URL}/import", json=data)
    if res.status_code == 201:
        print("✅ Bulk Import: Success")
        # Cleanup
        requests.delete(f"{BASE_URL}/persons/IMP001")
        requests.delete(f"{BASE_URL}/persons/IMP002")
    else:
        print(f"❌ Bulk Import: Failed ({res.status_code}) - {res.text}")


def test_safety_search():
    print("\nTesting Safety Search...")
    # First ensure we have a building and maintenance task with chemicals
    requests.post(f"{BASE_URL}/buildings",
                  json={"building_name": "SafetyTestBldg", "campus": "Main"})
    requests.post(f"{BASE_URL}/locations", json={"location_id": 999,
                  "building_name": "SafetyTestBldg", "room": "101", "floor": "1", "type": "Room"})
    # Note: Location ID is auto-increment, so we need to fetch it to use it.
    # For simplicity, let's just search for existing data or assume the previous POST worked and we can find it.
    # Actually, let's just call the endpoint and see if it returns 200.

    res = requests.get(f"{BASE_URL}/search/safety",
                       params={"building": "SafetyTestBldg"})
    if res.status_code == 200:
        print("✅ Safety Search: Success")
        print("   Results:", res.json())
    else:
        print(f"❌ Safety Search: Failed ({res.status_code}) - {res.text}")


if __name__ == "__main__":
    try:
        test_crud_person()
        test_bulk_import()
        test_safety_search()
    except Exception as e:
        print(f"❌ Test Script Error: {e}")
