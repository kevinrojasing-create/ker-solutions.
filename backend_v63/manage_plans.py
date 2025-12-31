import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import async_session_factory
from sql_models import User, SubscriptionPlan
from sqlalchemy import select, update

async def unlock_all_features():
    async with async_session_factory() as db:
        print("🔓 Unlocking Monitor 360 Plan for ALL users...")
        await db.execute(
            update(User).values(plan=SubscriptionPlan.MONITOR_360)
        )
        await db.commit()
        print("✅ Success! All users now have access to IoT & AI features.")
        
        # Verify
        result = await db.execute(select(User))
        for u in result.scalars().all():
             print(f"   User: {u.email} -> Plan: {u.plan}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(unlock_all_features())
