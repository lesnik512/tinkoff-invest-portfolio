from fastapi import FastAPI
from tinvest import UnexpectedError

from app import exceptions
from app.api.views import router
from app.config import settings


def get_app() -> FastAPI:
    application = FastAPI(title=settings.SERVICE_NAME, debug=settings.DEBUG)
    application.include_router(router, prefix="/api")
    application.add_exception_handler(
        UnexpectedError, exceptions.unexpected_error_exception_handler
    )
    return application


app = get_app()
