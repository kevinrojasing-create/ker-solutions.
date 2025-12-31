import asyncio
import httpx

async def test_register():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/auth/register",
            json={
                "email": "admin@ker.cl",
                "password": "admin123",
                "full_name": "Admin KER",
                "role": "owner"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 201:
            print("✅ SUCCESS! User created")
            data = response.json()
            print(f"User ID: {data['id']}")
            print(f"Email: {data['email']}")
            print(f"Role: {data['role']}")
        else:
            print("❌ FAILED")

if __name__ == "__main__":
    asyncio.run(test_register())
