import logging
import re
from typing import List, Optional, Dict, Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import as_declarative, declared_attr

from app.config import settings


logger = logging.getLogger(__name__)
engine = create_async_engine(settings.DB_DSN)


class DatabaseValidationError(Exception):
    def __init__(
        self, message: str, field: Optional[str] = None, object_id: int = None
    ) -> None:
        self.message = message
        self.field = field
        self.object = object_id


class ObjectDoesNotExist(Exception):
    pass


@as_declarative()
class Base:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return cls.__name__.lower()  # pylint: disable=no-member

    @classmethod
    def _raise_validation_exception(
        cls, e: IntegrityError, object_id: int = None
    ):
        info = e.orig.args
        m = re.findall(r"Key \((.*)\)=\(.*\) already exists|$", info[0])
        raise DatabaseValidationError(
            f"Unique constraint violated for {cls.__name__}",
            m[0] if m else None,
            object_id,
        )

    @classmethod
    async def _bulk_insert(cls, db: AsyncSession, list_data: List[Dict[str, Any]]):
        await db.execute(insert(cls).values(list_data).on_conflict_do_nothing())
