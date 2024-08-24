import contextlib
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.conf.config import config

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker = sessionmaker(bind=self._engine, expire_on_commit=False, class_=AsyncSession)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        async with self._session_maker() as session:
            try:
                yield session
            except Exception as err:
                print(err)
                await session.rollback()
                raise
            finally:
                await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session
