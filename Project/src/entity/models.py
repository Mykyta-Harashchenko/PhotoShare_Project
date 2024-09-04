import enum
from sqlalchemy import Integer, String, Date, Boolean, Text, ForeignKey, DateTime, func, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


class Role(enum.Enum):
    """
    Defines user roles in the system.

    This enumeration class represents the different roles a user can have in the system.

    Attributes:
    - admin (str): The administrator role, granting full access to the system.
    - moderator (str): The moderator role, allowing limited management permissions.
    - user (str): The basic user role, providing standard access.
    """

    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    """
    Represents a user in the system.

    This class defines the structure of the user entity in the database.

    Attributes:
    - id (int): The unique identifier for the user.
    - username (str): The username chosen by the user.
    - email (str): The email address of the user (must be unique).
    - hashed_password (str): The hashed password for authentication.
    - avatar (str): The URL of the user's avatar image (optional).
    - refresh_token (str): The refresh token for user sessions (optional).
    - created_at (DateTime): The date and time when the user was created.
    - updated_at (DateTime): The date and time of the user's last update.
    - first_name (str): The first name of the user.
    - last_name (str): The last name of the user.
    - birthday (Date): The birth date of the user (optional).
    - phone (str): The phone number of the user (optional).
    - role (Role): The role assigned to the user (admin, moderator, or user).
    - is_active (bool): Whether the user account is active.
    - is_blocked (bool): Whether the user account is blocked.
    - about (str): Additional information about the user (optional).
    - posts (list[Post]): A list of posts created by the user.
    - comments (list[Comment]): A list of comments made by the user.
    """
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
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"), default=Role.user, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    about: Mapped[str] = mapped_column(Text, nullable=True)
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="owner")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")


class Tag(Base):
    """
    Represents a tag associated with posts.

    This class defines the structure of the tag entity in the database.

    Attributes:
    - id (int): The unique identifier for the tag.
    - tag (str): The name of the tag (must be unique).
    """
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class Post(Base):
    """
    Represents a post created by a user.

    This class defines the structure of the post entity in the database.

    Attributes:
    - id (int): The unique identifier for the post.
    - url (str): The URL of the image or media associated with the post.
    - qr_code (str): The URL of the QR code associated with the post (optional).
    - description (str): The description or caption of the post.
    - created_at (DateTime): The date and time when the post was created.
    - owner_id (int): The ID of the user who created the post.
    - owner (User): The user who created the post.
    - tags (list[Tag]): A list of tags associated with the post.
    - comments (list[Comment]): A list of comments made on the post.
    """
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=True)
    qr_code: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="post_tags")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    """
    Represents a comment made on a post.

    This class defines the structure of the comment entity in the database.

    Attributes:
    - id (int): The unique identifier for the comment.
    - text (str): The content of the comment.
    - created_at (DateTime): The date and time when the comment was created.
    - updated_at (DateTime): The date and time of the last update to the comment.
    - user_id (int): The ID of the user who made the comment.
    - user (User): The user who made the comment.
    - post_id (int): The ID of the post the comment is associated with.
    - post (Post): The post the comment is associated with.
    """
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
    """
    Represents the relationship between posts and tags.

    This class defines the many-to-many relationship between posts and tags in the database.

    Attributes:
    - post_id (int): The ID of the post.
    - tag_id (int): The ID of the tag.
    """
    __tablename__ = 'post_tags'
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), primary_key=True)
