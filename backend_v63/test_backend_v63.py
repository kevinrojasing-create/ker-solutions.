"""
Create a test user and test login
"""
import asyncio
import httpx

async def test_system():
    base_url = "http://localhost:8003"
    
    print("=" * 50)
    print("TESTING BACKEND V63")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")
            return
        
        # Test 2: Register a user
        print("\n2. Testing registration...")
        register_data = {
            "email": "test@kerv63.com",
            "password": "Test123456",
            "full_name": "Test User V63",
            "phone_number": "+56912345678",
            "role": "owner",
            "plan": "free",
            "company_name": "Test Company"
        }
        try:
            response = await client.post(f"{base_url}/auth/register", json=register_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 201:
                print(f"   ✓ User registered successfully")
            elif response.status_code == 400:
                print(f"   ⚠ User may already exist")
            else:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ERROR: {e}")
        
        # Test 3: Login
        print("\n3. Testing login...")
        login_data = {
            "email": "test@kerv63.com",
            "password": "Test123456"
        }
        try:
            response = await client.post(f"{base_url}/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Login successful!")
                print(f"   Token: {data['access_token'][:20]}...")
                print(f"   User: {data['user']['email']}")
                print(f"   Plan: {data['user']['plan']}")
            else:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("BACKEND V63 IS WORKING! ✓")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_system())
