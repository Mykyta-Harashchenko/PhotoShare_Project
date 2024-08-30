import asyncio

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from Project.src.database.db import get_db
from Project.main import app
from Project.src.conf.config import config
from Project.src.entity.models import User, Post, Comment
from Project.src.repository.comments import CommentRepository

Base = declarative_base()

engine = create_async_engine(config.DB_TEST_URL, echo=True, future=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    expire_on_commit=False,
    autoflush=False,
)

test_user_data = {"username": "testuser", "email": "testuser@example.com", "password": "123456"}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the event loop to be used in tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest.fixture(scope="function")
def override_get_db():
    async def _get_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db

    yield
    app.dependency_overrides.clear()



@pytest.mark.asyncio
async def test_create_comment(db_session: AsyncSession):
    # Arrange: Create a test user and post
    new_user = User(username="testuser", email="testuser@example.com", password="hashedpassword")
    new_post = Post(title="Test Post", content="This is a test post", user=new_user)
    db_session.add_all([new_user, new_post])
    await db_session.commit()
    await db_session.refresh(new_user)
    await db_session.refresh(new_post)

    repo = CommentRepository(db_session)
    comment_text = "This is a test comment"

    new_comment = await repo.create_comment(post_id=new_post.id, user_id=new_user.id, text=comment_text)

    assert new_comment is not None
    assert new_comment.text == comment_text
    assert new_comment.post_id == new_post.id
    assert new_comment.user_id == new_user.id


@pytest.mark.asyncio
async def test_get_comment_by_id(db_session: AsyncSession):

    new_user = User(username="testuser", email="testuser@example.com", password="hashedpassword")
    new_post = Post(title="Test Post", content="This is a test post", user=new_user)
    new_comment = Comment(text="Test Comment", user=new_user, post=new_post)

    db_session.add_all([new_user, new_post, new_comment])

    await db_session.commit()
    await db_session.refresh(new_comment)

    repo = CommentRepository(db_session)

    search_comment = await repo.get_comment_by_id(new_comment.id)

    assert search_comment is not None
    assert search_comment.id == new_comment.id
    assert search_comment.text == new_comment.text


@pytest.mark.asyncio
async def test_update_comment(db_session: AsyncSession):
    new_user = User(username="testuser", email="testuser@example.com", password="hashedpassword")
    new_post = Post(title="Test Post", content="This is a test post", user=new_user)

    new_comment = Comment(text="first Comment", user=new_user, post=new_post)
    db_session.add_all([new_user, new_post, new_comment])
    await db_session.commit()
    await db_session.refresh(new_comment)

    repo = CommentRepository(db_session)
    updated_text = "Updated Comment"

    updated_comment = await repo.update_comment(comment_id=new_comment.id, new_text=updated_text)

    assert updated_comment is not None
    assert updated_comment.text == updated_text


@pytest.mark.asyncio
async def test_delete_comment(db_session: AsyncSession):

    new_user = User(username="testuser", email="testuser@example.com", password="hashedpassword")
    new_post = Post(title="Test Post", content="This is a test post", user=new_user)
    new_comment = Comment(text="Comment", user=new_user, post=new_post)
    db_session.add_all([new_user, new_post, new_comment])
    await db_session.commit()
    await db_session.refresh(new_comment)

    repo = CommentRepository(db_session)

    await repo.delete_comment(comment_id=new_comment.id)

    deleted_comment = await repo.get_comment_by_id(new_comment.id)

    assert deleted_comment is None

@pytest.mark.asyncio
async def test_get_comments_by_post_id(db_session: AsyncSession):
    new_user = User(username="testuser", email="testuser@example.com", password="hashedpassword")
    new_post = Post(title="Test Post", content="This is a test post", user=new_user)
    comment1 = Comment(text="First Comment", user=new_user, post=new_post)
    comment2 = Comment(text="Second Comment", user=new_user, post=new_post)
    db_session.add_all([new_user, new_post, comment1, comment2])
    await db_session.commit()

    repo = CommentRepository(db_session)

    comments = await repo.get_comments_by_post_id(post_id=new_post.id, limit=10, offset=0)

    assert len(comments) == 2
    assert comments[0].text == "First Comment"
    assert comments[1].text == "Second Comment"


@pytest.mark.asyncio
async def test_get_comments_by_user_id(db_session: AsyncSession):

    new_user = User(username="testuser", email="testuser@example.com", password="hashedpassword")
    new_post = Post(title="Test Post", content="This is a test post", user=new_user)
    comment1 = Comment(text="First Comment", user=new_user, post=new_post)
    comment2 = Comment(text="Second Comment", user=new_user, post=new_post)
    db_session.add_all([new_user, new_post, comment1, comment2])
    await db_session.commit()

    repo = CommentRepository(db_session)

    comments = await repo.get_comments_by_user_id(user_id=new_user.id, limit=10, offset=0)

    assert len(comments) == 2
    assert comments[0].text == "First Comment"
    assert comments[1].text == "Second Comment"