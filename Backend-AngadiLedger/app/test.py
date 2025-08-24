import asyncio
from app.database import SessionLocal

async def test_async_session():
    try:
        async with SessionLocal() as db:
            await db.execute("SELECT 1")
        print("Async DB connection working!")
    except Exception as e:
        print(f"Async DB connection failed: {e}")

asyncio.run(test_async_session())
