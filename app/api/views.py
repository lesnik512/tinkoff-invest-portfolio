import tinvest
from fastapi import APIRouter
from tinvest import UserAccounts

from app.config import settings

router = APIRouter()


@router.get("/accounts/", response_model=UserAccounts)
async def accounts():
    async with tinvest.AsyncClient(settings.TOKEN) as client:
        response = await client.get_accounts()
        return response.payload
