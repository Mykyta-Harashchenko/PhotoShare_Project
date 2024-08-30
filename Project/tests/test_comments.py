# test_comments.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from Project.src.entity.models import User, Post, Comment
from Project.src.repository.comments import CommentRepository

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from Project.src.database.db import Base
from Project.src.conf.config import config

engine = create_async_engine(config.DB_TEST_URL, echo=True, future=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    expire_on_commit=False,
    autoflush=False,
)

# Фікстура для налаштування бази даних
@pytest.fixture(scope="session")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Фікстура для сесії бази даних
@pytest.fixture(scope="function")
async def db_session():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
def setup_test_data(db_session: AsyncSession):
    user = User(id=1, username='test_user', email='test@example.com')
    post = Post(id=1, description="Test Post", owner=user)
    db_session.add(user)
    db_session.add(post)
    db_session.commit()
    return user, post


@pytest.mark.asyncio
async def test_create_comment(db_session: AsyncSession, setup_test_data):
    user, post = setup_test_data
    repo = CommentRepository(db_session)
    text = "Test Comment"
    comment = await repo.create_comment(post_id=post.id, user_id=user.id, text=text)
    assert comment.text == text
    assert comment.user_id == user.id
    assert comment.post_id == post.id


@pytest.mark.asyncio
async def test_get_comment_by_id(db_session: AsyncSession, setup_test_data):
    user, post = setup_test_data
    repo = CommentRepository(db_session)
    comment = await repo.create_comment(post_id=post.id, user_id=user.id, text="Test Comment")
    found_comment = await repo.get_comment_by_id(comment.id)
    assert found_comment is not None
    assert found_comment.id == comment.id


@pytest.mark.asyncio
async def test_update_comment(db_session: AsyncSession, setup_test_data):
    user, post = setup_test_data
    repo = CommentRepository(db_session)
    comment = await repo.create_comment(post_id=post.id, user_id=user.id, text="Initial Text")

    updated_comment = await repo.update_comment(comment.id, "Updated Text")
    assert updated_comment.text == "Updated Text"

    fetched_comment = await repo.get_comment_by_id(comment.id)
    assert fetched_comment is not None
    assert fetched_comment.text == "Updated Text"


@pytest.mark.asyncio
async def test_delete_comment(db_session: AsyncSession, setup_test_data):
    user, post = setup_test_data
    repo = CommentRepository(db_session)
    comment = await repo.create_comment(post_id=post.id, user_id=user.id, text="To be deleted")
    await repo.delete_comment(comment.id)
    found_comment = await repo.get_comment_by_id(comment.id)
    assert found_comment is None


@pytest.mark.asyncio
async def test_get_comments_by_post_id(db_session: AsyncSession, setup_test_data):
    user, post = setup_test_data
    repo = CommentRepository(db_session)
    await repo.create_comment(post_id=post.id, user_id=user.id, text="Comment 1")
    await repo.create_comment(post_id=post.id, user_id=user.id, text="Comment 2")
    comments = await repo.get_comments_by_post_id(post.id, limit=10, offset=0)
    assert len(comments) == 2


@pytest.mark.asyncio
async def test_get_comments_by_user_id(db_session: AsyncSession, setup_test_data):
    user, post = setup_test_data
    repo = CommentRepository(db_session)
    await repo.create_comment(post_id=post.id, user_id=user.id, text="Comment 1")
    await repo.create_comment(post_id=post.id, user_id=user.id, text="Comment 2")
    comments = await repo.get_comments_by_user_id(user.id, limit=10, offset=0)
    assert len(comments) == 2
