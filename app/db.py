import logging
from typing import List, Dict, Any

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import as_declarative, declared_attr, Session

from app.config import settings


logger = logging.getLogger(__name__)
engine = create_async_engine(settings.DB_DSN)
sync_engine = create_engine(settings.DB_DSN)


@as_declarative()
class Base:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return cls.__name__.lower()  # pylint: disable=no-member

    @classmethod
    async def filter(cls, db: AsyncSession, conditions: List[Any]):
        query = sa.select(cls)
        db_execute = await db.execute(query.where(sa.and_(*conditions)))
        return db_execute.scalars().all()

    @classmethod
    def sync_bulk_insert(cls, db: Session, list_data: List[Dict[str, Any]]):
        db.execute(insert(cls).values(list_data).on_conflict_do_nothing())
