from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.database import create_db_engine
from app.dependencies import SessionDropIn
from app.routers import places
from app.settings import Settings


def get_application(settings: Settings) -> FastAPI:
    app = FastAPI()
    app.include_router(places.router)

    engine = create_db_engine(settings)

    def get_db_session() -> Session:
        with Session(engine) as session:
            yield session

    app.dependency_overrides.update({
        SessionDropIn: get_db_session,
    })

    return app
