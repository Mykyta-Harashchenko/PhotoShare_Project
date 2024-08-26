from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from Project.src.entity.models import Comment, Post


class CommentRepository:
    def __init__(self, db: AsyncSession):
        """
        Initializes the repository with a database session.

        :param db: The database session to use for database operations.
        :type db: AsyncSession
        """
        self.db = db

    async def handle_exception(self, e):
        """
        Handles exceptions by printing the error message, rolling back the transaction, and raising an HTTPException.

        :param e: The exception to handle.
        :type e: Exception
        :raises HTTPException: Always raises an HTTPException with a 500 status code.
        """
        print(f"Error: {e}")
        await self.db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    async def create_comment(self, post_id: int, user_id: int, text: str) -> Comment:
        """
        Creates a new comment for a post.

        :param post_id: The ID of the post.
        :param user_id: The ID of the user creating the comment.
        :param text: The text of the comment.
        :return: The created Comment object.
        """
        try:
            db_comment = Comment(
                text=text,
                user_id=user_id,
                post_id=post_id
            )
            self.db.add(db_comment)
            await self.db.commit()
            await self.db.refresh(db_comment)
            return db_comment
        except Exception as e:
            await self.handle_exception(e)

    async def get_comment_by_id(self, comment_id: int) -> Comment:
        """
        Retrieves a comment by its ID.

        :param comment_id: The ID of the comment.
        :return: The Comment object if found, None otherwise.
        """
        try:
            result = await self.db.execute(
                select(Comment).where(Comment.id == comment_id).options(selectinload(Comment.user),
                                                                        selectinload(Comment.post)))
            return result.scalars().first()
        except Exception as e:
            await self.handle_exception(e)

    async def update_comment(self, comment_id: int, new_text: str) -> Comment:
        """
        Updates the text of a comment.

        :param comment_id: The ID of the comment to update.
        :param new_text: The new text for the comment.
        :return: The updated Comment object.
        """
        try:
            db_comment = await self.get_comment_by_id(comment_id)
            if db_comment:
                db_comment.text = new_text
                await self.db.commit()
                await self.db.refresh(db_comment)
                return db_comment
            else:
                raise HTTPException(status_code=404, detail="Comment not found")
        except Exception as e:
            await self.handle_exception(e)

    async def delete_comment(self, comment_id: int):
        """
        Deletes a comment by its ID.

        :param comment_id: The ID of the comment to delete.
        """
        try:
            db_comment = await self.get_comment_by_id(comment_id)
            if db_comment:
                await self.db.delete(db_comment)
                await self.db.commit()
            else:
                raise HTTPException(status_code=404, detail="Comment not found")
        except Exception as e:
            await self.handle_exception(e)

    async def get_comments_by_post_id(self, post_id: int, limit: int, offset: int) -> Sequence[Comment]:
        """
        Retrieves all comments for a specific post.

        :param post_id: The ID of the post.
        :param limit: The maximum number of comments to retrieve.
        :param offset: The number of comments to skip before starting to collect.
        :return: A list of Comment objects.
        """
        try:
            result = await self.db.execute(
                select(Comment).where(Comment.post_id == post_id).options(selectinload(Comment.user)).
                offset(offset).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            await self.handle_exception(e)

    async def get_comments_by_user_id(self, user_id: int, limit: int, offset: int) -> Sequence[Comment]:
        """
        Retrieves all comments made by a specific user.

        :param user_id: The ID of the user.
        :param limit: The maximum number of comments to retrieve.
        :param offset: The number of comments to skip before starting to collect.
        :return: A list of Comment objects.
        """
        try:
            result = await self.db.execute(
                select(Comment).where(Comment.user_id == user_id).options(selectinload(Comment.post)).
                offset(offset).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            await self.handle_exception(e)