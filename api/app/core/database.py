import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseSessionManagerException(Exception):
    pass


class DatabaseSessionManager:
    def __init__(self, db_url: str, **engine_kwargs):
        self.engine = create_async_engine(db_url, **engine_kwargs)
        self._session_maker = async_sessionmaker(autocommit=False, bind=self.engine, expire_on_commit=False)

    async def close(self):
        if self.engine is None:
            raise DatabaseSessionManagerException("DatabaseSessionManager is not initialized")
        await self.engine.dispose()

        self.engine = None
        self._session_maker = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_maker is None:
            raise DatabaseSessionManagerException("DatabaseSessionManager is not initialized")

        session = self._session_maker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
