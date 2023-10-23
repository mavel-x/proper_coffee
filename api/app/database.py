from sqlalchemy.engine import Engine
from sqlalchemy import create_engine

from app.settings import DatabaseType, Settings
from app.models import Base


def create_db_engine(settings: Settings) -> Engine:
    if settings.db_type == DatabaseType.SQLITE:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    return engine
