import requests
import json
import time

BASE_URL = "http://localhost:8001"

def print_result(name, success, details=""):
    icon = "✅" if success else "❌"
    print(f"{icon} {name}: {details}")

def test_maintenance_flow():
    print("🚀 Test Flow: Preventive Maintenance")
    
    # 1. Login/Get Token (assuming no auth for dev or simplified)
    # Actually V63 likely uses auth. Let's try to get a token or bypass if dev mode allows.
    # Looking at main.py: docs_url="/docs" if settings.ENVIRONMENT == "development" else None
    # Let's inspect if we can use a test user. The seeding script might have created one.
    # Assume we need to register or login.
    
    # Simplified: Register a temp owner
    email = f"test_maint_{int(time.time())}@kers.cl"
    password = "password123"
    
    # Register
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Maintenance",
        "role": "owner",
        "plan": "control_total"
    })
    if resp.status_code == 201:
        print_result("Register", True)
    elif resp.status_code == 400 and "exists" in resp.text:
        print_result("Register", True, "User exists")
    else:
        print_result("Register", False, resp.text)
        return

    # Login
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print_result("Login", False, resp.text)
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result("Login", True)

    # 2. Create Local
    resp = requests.post(f"{BASE_URL}/locales/", headers=headers, json={
        "name": "Test Factory",
        "address": "123 Ind zone"
    })
    if resp.status_code != 201:
        print_result("Create Local", False, resp.text)
        return
    local_id = resp.json()["id"]
    print_result("Create Local", True, f"ID: {local_id}")

    # 3. Create Asset
    resp = requests.post(f"{BASE_URL}/assets/", headers=headers, json={
        "local_id": local_id,
        "name": "Industrial Generator",
        "status": "operational"
    })
    if resp.status_code != 201:
        print_result("Create Asset", False, resp.text)
        return
    asset_id = resp.json()["id"]
    print_result("Create Asset", True, f"ID: {asset_id}")

    # 4. Create Maintenance Schedule (Due NOW)
    resp = requests.post(f"{BASE_URL}/maintenance/schedules", headers=headers, json={
        "asset_id": asset_id,
        "maintenance_type": "inspeccion",
        "description": "Weekly Inspection",
        "frequency_days": 7,
        "next_due_date": "2023-01-01T12:00:00" # Past date to trigger immediately
    })
    if resp.status_code != 201:
        print_result("Create Schedule", False, resp.text)
        return
    schedule_id = resp.json()["id"]
    print_result("Create Schedule", True, f"ID: {schedule_id}")

    # 5. Trigger Ticket Generation
    resp = requests.post(f"{BASE_URL}/maintenance/generate-tickets", headers=headers)
    if resp.status_code != 200:
        print_result("Generate Tickets", False, resp.text)
        return
    tickets = resp.json()
    print_result("Generate Tickets", True, f"Generated: {len(tickets)}")
    
    if len(tickets) > 0:
        ticket = tickets[0]
        print(f"   🎫 Ticket ID: {ticket['id']}")
        print(f"   📝 Description: {ticket['description']}")
        
        # Verify schedule updated
        resp = requests.get(f"{BASE_URL}/maintenance/schedules", headers=headers, params={"asset_id": asset_id})
        schedules = resp.json()
        for s in schedules:
            if s["id"] == schedule_id:
                print(f"   📅 New Due Date: {s['next_due_date']}")
    else:
        print_result("Ticket Generation Check", False, "No tickets generated")

if __name__ == "__main__":
    try:
        test_maintenance_flow()
    except Exception as e:
        print(f"❌ Error: {e}")
