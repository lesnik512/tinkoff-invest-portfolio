from contextlib import contextmanager

from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.db import engine, sync_engine


async def get_db():
    session = AsyncSession(engine)
    try:
        async with session.begin_nested():
            yield session
    except PendingRollbackError:
        pass
    finally:
        try:
            await session.commit()
        except PendingRollbackError:
            pass
        await session.close()


@contextmanager
def get_db_typer():
    session = Session(sync_engine)
    try:
        with session.begin_nested():
            yield session
    except PendingRollbackError:
        pass
    finally:
        try:
            session.commit()
        except PendingRollbackError:
            pass
        session.close()
