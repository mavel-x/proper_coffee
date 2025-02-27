from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.routers import coffee_router
from app.core.database import DatabaseSessionManager
from app.env_settings import Settings


@asynccontextmanager
async def lifespan(app_: FastAPI):
    yield
    if app_.state.session_manager.engine is not None:
        await app_.state.session_manager.close()
    if app_.state.http_client is not None:
        await app_.state.http_client.aclose()


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Coffee API",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.session_manager = DatabaseSessionManager(settings.db_url)
    app.state.http_client = httpx.AsyncClient()
    app.include_router(coffee_router)
    register_exception_handlers(app)
    return app
