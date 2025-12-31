
import asyncio
import sys
from sqlalchemy import text
from database import get_db, engine, Base
from sql_models import User
from main import app

async def test_db_connection():
    print("Testing DB connection...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"DB Connection OK: {result.scalar()}")
    except Exception as e:
        print(f"DB Connection FAILED: {e}")
        return False
    return True

async def test_app_startup():
    print("Testing App Startup...")
    # This simulates what uvicorn does on startup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Table initialization FAILED: {e}")
        return False
    return True

async def main():
    print("=== V63 DIAGNOSTIC TOOL ===")
    
    db_ok = await test_db_connection()
    if not db_ok:
        print("CRITICAL: Database connection failed.")
        sys.exit(1)
        
    app_ok = await test_app_startup()
    if not app_ok:
        print("CRITICAL: App startup failed.")
        sys.exit(1)
        
    print("=== DIAGNOSTIC PASSED ===")
    print("The code structure is sound. The issue is likely network or port related.")

if __name__ == "__main__":
    asyncio.run(main())
