import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.main import app
from database import Base
from database.session import get_session


@pytest.fixture
def maker(tmp_path):
    """Session factory on a throwaway SQLite file. Needs `pip install aiosqlite` (tests skip without it)."""
    pytest.importorskip("aiosqlite")
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/test.db", poolclass=NullPool)

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_tables())
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
def client(maker):
    async def override():
        async with maker() as session:
            yield session

    app.dependency_overrides[get_session] = override
    yield TestClient(app)
    app.dependency_overrides.clear()
