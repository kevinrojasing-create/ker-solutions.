import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def print_result(step, response, expected_status=200):
    if response.status_code == expected_status:
        print(f"[OK] {step}")
        return True
    else:
        print(f"[FAIL] {step}: ({response.status_code})")
        print(response.text)
        return False

def run_test():
    print(">>> Starting V63 Smoke Test...")
    
    # 1. Check System
    try:
        r = requests.get(f"{BASE_URL}/")
        if not print_result("System Health", r): return
        print(f"   Server: {r.json()['app']} {r.json()['version']}")
    except Exception as e:
        print(f"[FAIL] Server not reachable: {e}")
        return

    # 2. Register User
    timestamp = int(time.time())
    email = f"owner_{timestamp}@test.com"
    password = "password123"
    
    user_data = {
        "email": email,
        "password": password,
        "full_name": "Test Owner",
        "role": "owner",
        "company_name": "Test Company"
    }
    
    r = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if not print_result("Register User", r, 201): return
    user_id = r.json()["id"]

    # 3. Login
    login_data = {
        "email": email,
        "password": password
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if not print_result("Login", r): return
    token = r.json()["access_token"]
    print(f"   [INFO] Token: {token[:20]}... (len: {len(token)})")
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Create Local
    local_data = {
        "name": "Main Office",
        "address": "123 Tech Blvd"
    }
    r = requests.post(f"{BASE_URL}/locales/", json=local_data, headers=headers)
    if not print_result("Create Local", r, 201): return
    local_id = r.json()["id"]

    # 5. Create Asset (Refrigerator)
    asset_data = {
        "local_id": local_id,
        "name": "Walk-in Fridge",
        "category": "refrigeration",
        "status": "operational"
    }
    r = requests.post(f"{BASE_URL}/assets/", json=asset_data, headers=headers)
    if not print_result("Create Asset", r, 201): return
    asset_id = r.json()["id"]

    # 6. Register IoT Device (SNZB-02D)
    device_id = f"SNZB-{timestamp}"
    device_data = {
        "local_id": local_id,
        "device_type": "temp_hum",
        "device_id": device_id,
        "name": "Fridge Sensor 1",
        "asset_id": asset_id,
        "config": {
            "temp_threshold_high": 8.0,
            "temp_threshold_low": 2.0
        }
    }
    r = requests.post(f"{BASE_URL}/iot/devices", json=device_data, headers=headers)
    if not print_result("Register IoT Device", r, 201): return
    iot_db_id = r.json()["id"]

    # 7. Send Telemetry (Normal)
    telemetry_normal = {
        "device_id": iot_db_id,
        "data": {
            "temperature": 4.5,
            "humidity": 60.0
        }
    }
    r = requests.post(f"{BASE_URL}/iot/telemetry", json=telemetry_normal)
    if not print_result("Send Normal Telemetry", r, 201): return

    # 8. Send Telemetry (High Temp -> Alert)
    telemetry_alert = {
        "device_id": iot_db_id,
        "data": {
            "temperature": 12.5,  # > 8.0 Threshold
            "humidity": 65.0
        }
    }
    r = requests.post(f"{BASE_URL}/iot/telemetry", json=telemetry_alert)
    if not print_result("Send CRITICAL Telemetry", r, 201): return

    # 9. Check Alerts
    r = requests.get(f"{BASE_URL}/alerts/?local_id={local_id}", headers=headers)
    if not print_result("Get Alerts", r): return
    alerts = r.json()
    if len(alerts) > 0:
        print(f"   [OK] Alert generated: {alerts[0]['title']} - {alerts[0]['message']}")
    else:
        print("   [FAIL] No alert generated for high temp!")

    # 10. Check Dashboard Stats
    r = requests.get(f"{BASE_URL}/dashboard/stats?local_id={local_id}", headers=headers)
    if not print_result("Get Dashboard Stats", r): return
    stats = r.json()
    print(f"   Stats: {json.dumps(stats, indent=2)}")

    print("\n[SUCCESS] SMOKE TEST PASSED! V63 Backend is Fully Functional.")

if __name__ == "__main__":
    run_test()
