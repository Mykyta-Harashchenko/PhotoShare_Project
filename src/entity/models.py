import enum
from sqlalchemy import Integer, String, Date, Boolean, Text, ForeignKey, DateTime, func, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    birthday: Mapped[Date] = mapped_column(Date, nullable=True)
    phone: Mapped[str] = mapped_column(String(14), nullable=True)

    role: Mapped[Role] = mapped_column(
        "role", Enum(Role, name="role"), default=Role.user, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    about: Mapped[str] = mapped_column(Text, nullable=True)


class Tag(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    foto: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="posts")

    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="post_tags")

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="comments")

    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="comments")


class PostTag(Base):
    __tablename__ = 'post_tags'
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), primary_key=True)
