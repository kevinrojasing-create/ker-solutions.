"""
Test login endpoint directly
"""
import asyncio
import sys
from database import get_db, engine
from routers.auth import login
from schemas import LoginRequest

async def test_login():
    print("Testing login endpoint...")
    
    # Create fake request
    credentials = LoginRequest(
        email="kevin.rojas.ing@gmail.com",
        password="Chile.2025"
    )
    
    try:
        async for db in get_db():
            result = await login(credentials, db)
            print(f"Login successful: {result}")
            break
    except Exception as e:
        print(f"Login failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_login())
