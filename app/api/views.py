import tinvest
from fastapi import APIRouter
from tinvest import Portfolio, UserAccounts

from app.config import settings


router = APIRouter()


@router.get("/accounts/", response_model=UserAccounts)
async def accounts():
    async with tinvest.AsyncClient(settings.TOKEN) as client:
        response = await client.get_accounts()
        return response.payload


@router.get("/portfolio/{account_id}/", response_model=Portfolio)
async def portfolio(account_id: str):
    async with tinvest.AsyncClient(settings.TOKEN) as client:
        response = await client.get_portfolio(account_id)
        return response.payload
