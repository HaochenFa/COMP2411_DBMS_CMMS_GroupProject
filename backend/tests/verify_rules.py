import requests
import sys

BASE_URL = "http://localhost:5050/api"


def test_limits():
    print("Testing Limits...")
    # 1. Create 10 Managers
    for i in range(10):
        pid = f"MGR_{i}"
        resp = requests.post(f"{BASE_URL}/profiles", json={
            "personal_id": pid,
            "job_role": "Mid-level Manager"
        })
        # We need to create Person first, but let's assume we can just hit profile if person exists?
        # Wait, FK constraint. We need to create Persons first.

        # Create Person
        requests.post(f"{BASE_URL}/persons", json={
            "personal_id": pid,
            "name": f"Manager {i}"
        })

        # Create Profile
        resp = requests.post(f"{BASE_URL}/profiles", json={
            "personal_id": pid,
            "job_role": "Mid-level Manager"
        })
        if resp.status_code != 201:
            print(f"Failed to create manager {i}: {resp.text}")
            return False

    # 2. Try to create 11th Manager
    pid = "MGR_11"
    requests.post(f"{BASE_URL}/persons",
                  json={"personal_id": pid, "name": "Manager 11"})
    resp = requests.post(f"{BASE_URL}/profiles", json={
        "personal_id": pid,
        "job_role": "Mid-level Manager"
    })
    if resp.status_code == 400 and "Limit reached" in resp.text:
        print("SUCCESS: Manager limit enforced.")
    else:
        print(
            f"FAILURE: Manager limit NOT enforced. Status: {resp.status_code}, Resp: {resp.text}")
        return False

    return True


def test_relationships():
    print("\nTesting Relationships...")

    # 1. Create Building
    resp = requests.post(f"{BASE_URL}/buildings", json={
        "building_name": "Engineering Block",
        "campus": "Main"
    })
    if resp.status_code != 201:
        print(f"Failed to create building: {resp.text}")
        return False

    # 2. Assign Supervisor (MGR_0 from previous test)
    resp = requests.post(f"{BASE_URL}/building-supervision", json={
        "supervisor_id": "MGR_0",
        "building_name": "Engineering Block"
    })
    if resp.status_code == 201:
        print("SUCCESS: Supervisor assigned.")
    else:
        print(f"FAILURE: Supervisor assignment failed: {resp.text}")
        return False

    # 3. Create Chemical (Removed)

    # 4. Create Activity
    # Need organiser first (MGR_0)
    resp = requests.post(f"{BASE_URL}/activities", json={
        "activity_id": "ACT_1",
        "type": "Cleaning",
        "organiser_id": "MGR_0"
    })

    # 5. Link Chemical (Removed)

    return True


def test_location_maintenance():
    print("\nTesting Location and Maintenance...")

    # 1. Create External Company
    resp = requests.post(f"{BASE_URL}/external-companies", json={
        "name": "FixItAll Inc.",
        "contact_info": "555-0199"
    })
    if resp.status_code != 201:
        print(f"Failed to create external company: {resp.text}")
        return False
    company_id = 1  # Assume 1

    # 2. Create Location (needs Building created in test_relationships)
    # We assume test_relationships ran first and created "Engineering Block"
    resp = requests.post(f"{BASE_URL}/locations", json={
        "room": "101",
        "floor": "1",
        "building_name": "Engineering Block",
        "type": "Room",
        "campus": "Main",
        "school_name": None  # Optional
    })
    if resp.status_code != 201:
        print(f"Failed to create location: {resp.text}")
        return False
    loc_id = 1  # Assume 1

    # 3. Create Maintenance with Contractor and Chemical Attributes
    resp = requests.post(f"{BASE_URL}/maintenance", json={
        "type": "Repair",
        "frequency": "Once",
        "location_id": loc_id,
        "contracted_company_id": company_id,
        "chemical_used": True
    })
    if resp.status_code == 201:
        print("SUCCESS: Maintenance task created with contractor ID and boolean chemical.")
    else:
        print(f"FAILURE: Maintenance task creation failed: {resp.text}")
        return False

    return True


if __name__ == "__main__":
    # Ensure DB is fresh or handle errors gracefully
    # For this test, we assume a running backend.

    if test_limits() and test_relationships() and test_location_maintenance():
        print("\nALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\nTESTS FAILED")
        sys.exit(1)
