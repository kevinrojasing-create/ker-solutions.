import requests
import json

# Test registration
url = "http://localhost:8000/auth/register"
payload = {
    "email": "admin@ker.cl",
    "password": "admin123",
    "full_name": "Admin KER",
    "role": "owner"
}

print("🧪 Testing User Registration...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*60)

try:
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"\n✅ Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 201:
        print("\n🎉 SUCCESS! User created successfully!")
        user_data = response.json()
        print(f"\n📊 User Details:")
        print(f"  ID: {user_data.get('id')}")
        print(f"  Email: {user_data.get('email')}")
        print(f"  Name: {user_data.get('full_name')}")
        print(f"  Role: {user_data.get('role')}")
        print(f"  Active: {user_data.get('is_active')}")
        print(f"  Verified: {user_data.get('is_verified')}")
    else:
        print(f"\n❌ FAILED with status {response.status_code}")
        
except requests.exceptions.Timeout:
    print("\n⏱️ Request timed out after 10 seconds")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
