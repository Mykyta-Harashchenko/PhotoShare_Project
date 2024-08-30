# import asyncio
#
# import pytest
# import pytest_asyncio
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
#
# from Project.src.conf.config import config
# from Project.main import app
# from Project.src.database.db import get_db, Base
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
#     """Create an instance of the event loop to be used in tests."""
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
# import pytest
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from Project.src.database.db import Base
# from Project.src.conf.config import config
#
# # Налаштування асинхронного двигуна SQLAlchemy
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
# # Фікстура для налаштування бази даних
# @pytest.fixture(scope="session")
# async def setup_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
# # Фікстура для сесії бази даних
# @pytest.fixture(scope="function")
# async def db_session():
#     async with SessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.close()