# import asyncio
# import pytest
# from unittest.mock import patch, MagicMock
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
# from pydantic_settings import BaseSettings
#
# from Project.src.database.db import DatabaseSessionManager, get_db, Base
# from Project.main import app
# from Project.src.entity.models import Role, User
# from Project.src.schemas import user
# from Project.src.schemas.roles import RoleEnum
# from Project.src.conf.config import config
#
#
#
# engine = create_async_engine(config.DB_TEST_URL, echo=True, future=True)
#
# SessionLocal = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     autocommit=False,
#     expire_on_commit=False,
#     autoflush=False,
# )
#
# test_user_data = {"username": "testuser", "email": "testuser@example.com", "password": "123456"}
#
#
# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest.fixture(scope="function", autouse=True)
# async def setup_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
#
# @pytest.fixture(scope="function")
# async def db_session():
#     async with SessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()
#
#
# @pytest.fixture(scope="function")
# def override_get_db():
#     async def _get_db():
#         async with SessionLocal() as session:
#             yield session
#
#     app.dependency_overrides[get_db] = _get_db
#
#     yield
#     app.dependency_overrides.clear()
#
#
# @pytest.mark.asyncio
# async def test_db_session(db_session):
#     assert isinstance(db_session, AsyncSession)
#     assert db_session.is_active
