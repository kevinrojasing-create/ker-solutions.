import requests
import json

url = "http://localhost:8000/auth/register"
data = {
    "email": "owner@ker.cl",
    "password": "owner123",
    "full_name": "Owner KER",
    "role": "owner",
    "company_name": "KER Solutions"
}

print("Testing registration...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("\n🎉🎉🎉 SUCCESS! USER CREATED! 🎉🎉🎉")
        user = response.json()
        print(f"ID: {user['id']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user['role']}")
    else:
        print(f"\n❌ Failed: {response.status_code}")
except Exception as e:
    print(f"\n❌ Error: {e}")
