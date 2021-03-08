from typing import Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from tinvest import Operation as OperationSchema, InstrumentType, OperationTypeWithCommission, OperationStatus, Currency

from app.db import Base


class Operation(Base):
    id = sa.Column(sa.String, primary_key=True, index=True, autoincrement=False)
    status = sa.Column(sa.Enum(OperationStatus), nullable=False)
    currency = sa.Column(sa.Enum(Currency), nullable=False)
    commission = sa.Column(sa.Numeric, nullable=False)
    payment = sa.Column(sa.Numeric, nullable=False)
    price = sa.Column(sa.Numeric, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    quantity_executed = sa.Column(sa.Integer, nullable=False)
    figi = sa.Column(sa.String, nullable=False)
    instrument_type = sa.Column(sa.Enum(InstrumentType), nullable=False)
    is_margin_call = sa.Column(sa.Boolean, default=False)
    date = sa.Column(sa.DateTime(timezone=True), nullable=False)
    operation_type = sa.Column(sa.Enum(OperationTypeWithCommission), nullable=False)
    broker_account_id = sa.Column(sa.String, nullable=False)

    @classmethod
    async def bulk_create_for_account(
        cls, db: AsyncSession, data: Sequence[OperationSchema], broker_account_id: str
    ) -> None:
        await cls._bulk_insert(
            db,
            [
                dict(
                    **x.dict(exclude={"trades", "commission"}),
                    broker_account_id=broker_account_id,
                    commission=getattr(x.commission, "value", 0),
                )
                for x in data
            ]
        )
