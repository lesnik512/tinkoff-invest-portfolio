from fastapi.exception_handlers import (
    http_exception_handler,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from starlette import status
from tinvest import UnexpectedError


async def unexpected_error_exception_handler(
    request, exc: UnexpectedError
) -> JSONResponse:
    return await http_exception_handler(
        request, HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    )
