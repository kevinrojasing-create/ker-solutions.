"""
Register user for V63 cleanly (using V63 Schemas and defaults)
"""
import asyncio
from database import get_db, init_db
from routers.auth import register
from schemas import RegisterRequest, UserRole, SubscriptionPlan

async def register_initial_user():
    print("Registering initial user...")
    
    # Create request using V63 valid data
    user_data = RegisterRequest(
        email="kevin.rojas.ing@gmail.com",
        password="Chile.2025",
        full_name="Kevin Rojas",
        phone_number="+56912345678",
        role=UserRole.OWNER,
        plan=SubscriptionPlan.DIGITAL,  # Valid V63 Plan
        company_name="KER Solutions Clean"
    )
    
    async for db in get_db():
        try:
            new_user = await register(user_data, db)
            print(f"User created: {new_user.email} with plan {new_user.plan}")
        except Exception as e:
            print(f"Registration failed: {e}")
        break

if __name__ == "__main__":
    asyncio.run(register_initial_user())
