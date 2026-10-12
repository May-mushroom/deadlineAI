from fastapi.testclient import TestClient

import asyncio
from sqlalchemy import text
from database.session import get_engine

from app.main import app


def test_health():
    r = TestClient(app).get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def main():
    engine = get_engine()
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Connected to Supabase!", result.scalar())
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await engine.dispose()

asyncio.run(main())