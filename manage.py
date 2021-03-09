import datetime
from collections import defaultdict

import sqlalchemy as sa
import tinvest
import typer
from tabulate import tabulate
from tinvest import OperationStatus

from app.config import settings
from app.constants import allowed_operation_types
from app.deps import get_db_typer
from app.models import Operation, MarketInstrument
from app.utils.generators import grouper


app = typer.Typer()


@app.command()
def import_operations():
    with get_db_typer() as db:
        client = tinvest.SyncClient(settings.TOKEN)

        response = client.get_accounts()
        accounts = response.payload.accounts
        for account in accounts:
            response = client.get_operations(
                from_=datetime.datetime.min,
                to=datetime.datetime.max,
                broker_account_id=account.broker_account_id,
            )
            ops = [x for x in response.payload.operations if x.operation_type in allowed_operation_types and x.status == OperationStatus.done]
            for chunk in grouper(ops, 100):
                Operation.sync_bulk_insert(
                    db,
                    [
                        dict(
                            **x.dict(exclude={"trades", "commission"}),
                            broker_account_id=account.broker_account_id,
                            commission=getattr(x.commission, "value", 0),
                        )
                        for x in chunk
                    ]
                )
        typer.echo(f"{len(ops)} operations returned")


@app.command()
def import_instruments():
    exclude_keys = {"isin", "lot", "min_price_increment", "min_quantity"}
    with get_db_typer() as db:
        client = tinvest.SyncClient(settings.TOKEN)

        response = client.get_market_stocks()
        instruments = response.payload.instruments
        for chunk in grouper(instruments, 100):
            MarketInstrument.sync_bulk_insert(
                db, [x.dict(exclude=exclude_keys) for x in chunk]
            )
        typer.echo(f"{len(instruments)} instruments returned")


@app.command()
def get_info():
    client = tinvest.SyncClient(settings.TOKEN)
    response = client.get_accounts()
    accounts = response.payload.accounts
    positions = defaultdict(list)
    for account in accounts:
        for pos in client.get_portfolio(account.broker_account_id).payload.positions:
            positions[pos.figi].append(pos)

    query = sa.select([
        sa.func.sum(Operation.payment).label("payment"),
        sa.func.sum(Operation.commission).label("commission"),
        Operation.figi
    ]).select_from(Operation).group_by(Operation.figi)
    with get_db_typer() as db:
        db_execute = db.execute(sa.select(MarketInstrument))
        instruments = {x.figi: x for x in db_execute.scalars().all()}
        db_execute = db.execute(query)
        result = []
        for payment, commission, figi in db_execute.all():
            if figi not in instruments:
                continue
            pos = positions[figi]
            result.append([
                figi,
                instruments[figi].name,
                payment - commission,
                pos[0].lots if len(pos) else "",
                pos[0].average_position_price.value if len(pos) else "",
                (payment + commission) / pos[0].lots if len(pos) else "",
            ])

    typer.echo(tabulate(result, headers=['figi', 'name', "result", "lots", "avg", "avg true"]))


if __name__ == "__main__":
    app()
