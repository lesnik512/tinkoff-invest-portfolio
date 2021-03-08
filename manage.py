import datetime

import tinvest
import typer
from tinvest import OperationStatus

from app.config import settings
from app.constants import allowed_operation_types
from app.deps import get_db_typer
from app.models import Operation
from app.utils.cli import force_sync
from app.utils.generators import grouper


app = typer.Typer()


@app.command()
@force_sync
async def import_ops():
    async with get_db_typer() as db:
        async with tinvest.AsyncClient(settings.TOKEN) as client:
            response = await client.get_accounts()
            accounts = response.payload.accounts
            for account in accounts:
                response = await client.get_operations(
                    from_=datetime.datetime.min,
                    to=datetime.datetime.max,
                    broker_account_id=account.broker_account_id,
                )
                ops = [x for x in response.payload.operations if x.operation_type in allowed_operation_types and x.status == OperationStatus.done]
                for chunk in grouper(ops, 100):
                    await Operation.bulk_create_for_account(db, chunk, account.broker_account_id)

        typer.echo("done")


if __name__ == "__main__":
    app()
