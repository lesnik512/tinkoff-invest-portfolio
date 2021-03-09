import sqlalchemy as sa
from tinvest import InstrumentType, OperationTypeWithCommission, OperationStatus, Currency

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


class MarketInstrument(Base):
    figi = sa.Column(sa.String, primary_key=True, index=True, autoincrement=False)
    currency = sa.Column(sa.Enum(Currency), nullable=False)
    name = sa.Column(sa.String, nullable=False)
    ticker = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.Enum(InstrumentType), nullable=False)
