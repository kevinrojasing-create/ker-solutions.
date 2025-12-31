import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import settings

async def check_db():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT email, plan FROM users"))
        rows = result.fetchall()
        print(f"Users found: {len(rows)}")
        for row in rows:
            print(row)
            
if __name__ == "__main__":
    asyncio.run(check_db())
