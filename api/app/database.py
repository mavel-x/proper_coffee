from sqlalchemy.engine import Engine
from sqlmodel import create_engine, SQLModel

from app.settings import DatabaseType, Settings


def create_db_engine(settings: Settings) -> Engine:
    if settings.db_type == DatabaseType.SQLITE:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(settings.database_url)
    SQLModel.metadata.create_all(engine)
    return engine


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
