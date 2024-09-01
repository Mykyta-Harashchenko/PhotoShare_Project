# import asyncio
#
# import pytest
# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
# from Project.src.conf.config import config
# from Project.src.database.db import Base, get_db
# from Project.main import app
# from Project.src.entity.models import User, Post
# from Project.src.repository.comments import CommentRepository
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
#
#
# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()
#
# @pytest.fixture(scope="session", autouse=True)
# async def setup_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
# @pytest.fixture(scope="function")
# async def db_session():
#     async with SessionLocal() as session:
#         try:
#             yield session
#         finally:
#             await session.rollback()
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
# @pytest.fixture
# def setup_test_data():
#     user = User(id=1, username='test_user', email='test@example.com')
#     post = Post(id=1, description="Test Post", owner=user)
#     return user, post
#
# @pytest.mark.asyncio
# async def test_create_comment(db_session: AsyncSession, setup_test_data, override_get_db):
#     user, post = setup_test_data
#     repo = CommentRepository(db_session)
#     text = "Test Comment"
#     try:
#         comment = await repo.create_comment(post_id=post.id, user_id=user.id, text=text)
#         assert comment.text == text
#         assert comment.user_id == user.id
#         assert comment.post_id == post.id
#     except Exception as e:
#         print(f"Error in test_create_comment: {e}")
#         raise
#
# @pytest.mark.asyncio
# async def test_get_comment_by_id(db_session: AsyncSession, setup_test_data, override_get_db):
#     user, post = setup_test_data
#     repo = CommentRepository(db_session)
#     try:
#         comment = await repo.create_comment(post_id=post.id, user_id=user.id, text="Test Comment")
#         found_comment = await repo.get_comment_by_id(comment.id)
#         assert found_comment is not None
#         assert found_comment.id == comment.id
#     except Exception as e:
#         print(f"Error in test_get_comment_by_id: {e}")
#         raise
#
# @pytest.mark.asyncio
# async def test_update_comment(db_session: AsyncSession, setup_test_data, override_get_db):
#     user, post = setup_test_data
#     repo = CommentRepository(db_session)
#     try:
#         comment = await repo.create_comment(post_id=post.id, user_id=user.id, text="Initial Text")
#         updated_comment = await repo.update_comment(comment.id, "Updated Text")
#         assert updated_comment.text == "Updated Text"
#         new_comment = await repo.get_comment_by_id(comment.id)
#         assert new_comment is not None
#         assert new_comment.text == "Updated Text"
#     except Exception as e:
#         print(f"Error in test_update_comment: {e}")
#         raise
#
# @pytest.mark.asyncio
# async def test_delete_comment(db_session: AsyncSession, setup_test_data, override_get_db):
#     user, post = setup_test_data
#     repo = CommentRepository(db_session)
#     try:
#         comment = await repo.create_comment(post_id=post.id, user_id=user.id, text="To be deleted")
#         await repo.delete_comment(comment.id)
#         found_comment = await repo.get_comment_by_id(comment.id)
#         assert found_comment is None
#     except Exception as e:
#         print(f"Error in test_delete_comment: {e}")
#         raise
#
# @pytest.mark.asyncio
# async def test_get_comments_by_post_id(db_session: AsyncSession, setup_test_data, override_get_db):
#     user, post = setup_test_data
#     repo = CommentRepository(db_session)
#     try:
#         await repo.create_comment(post_id=post.id, user_id=user.id, text="Comment 1")
#         await repo.create_comment(post_id=post.id, user_id=user.id, text="Comment 2")
#         comments = await repo.get_comments_by_post_id(post.id, limit=10, offset=0)
#         assert len(comments) == 2
#     except Exception as e:
#         print(f"Error in test_get_comments_by_post_id: {e}")
#         raise
#
# @pytest.mark.asyncio
# async def test_get_comments_by_user_id(db_session: AsyncSession, setup_test_data, override_get_db):
#     user, post = setup_test_data
#     repo = CommentRepository(db_session)
#     try:
#         await repo.create_comment(post_id=post.id, user_id=user.id, text="Comment 1")
#         await repo.create_comment(post_id=post.id, user_id=user.id, text="Comment 2")
#         comments = await repo.get_comments_by_user_id(user.id, limit=10, offset=0)
#         assert len(comments) == 2
#     except Exception as e:
#         print(f"Error in test_get_comments_by_user_id: {e}")
#         raise
