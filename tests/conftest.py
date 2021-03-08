import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine
from app.deps import get_db
from app.main import app


@pytest.fixture
async def db():
    session = AsyncSession(engine)
    try:
        async with session.begin_nested():
            yield session
    except PendingRollbackError:
        pass
    finally:
        try:
            await session.rollback()
        except PendingRollbackError:
            pass
        await session.close()


@pytest.fixture
def client(db):
    def _get_db():
        return db

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        yield client
