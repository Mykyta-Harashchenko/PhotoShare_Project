from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from Project.src.entity.models import User, Role, Post
from Project.src.database.db import get_db
from Project.src.repository.comments import CommentRepository
from Project.src.schemas.comments import CommentCreate, CommentUpdate, CommentResponse
from Project.src.services.roles import RoleChecker
from Project.src.services.dependencies import get_current_user

router = APIRouter(tags=['comments'])


@router.post(
    "/posts/{post_id}/comments/",
    response_model=CommentResponse,
    dependencies=[Depends(RoleChecker([Role.user, Role.admin, Role.moderator]))],
    status_code=status.HTTP_201_CREATED
)
async def create_comment(
        post_id: int,
        comment: CommentCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Create a new comment for a specific post.

    This function allows the current user, if they have the "user", "admin", or "moderator" role, 
    to create a new comment on a specific post identified by its post_id.

    :param post_id: The ID of the post for which the comment is being created.
    :type post_id: int
    :param comment: The content of the new comment.
    :type comment: CommentCreate
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :param current_user: The currently authenticated user making the request.
    :type current_user: User
    :return: The newly created comment.
    :rtype: CommentResponse
    :raises HTTPException: If the post with the given ID is not found (404).
    """
    db_post = await db.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_comment = await CommentRepository(db).create_comment(post_id, current_user.id, comment.text)
    return db_comment


@router.put(
    "/comments/{comment_id}/",
    response_model=CommentResponse,
    dependencies=[Depends(RoleChecker([Role.user, Role.admin, Role.moderator]))],
    status_code=status.HTTP_200_OK
)
async def update_comment(
        comment_id: int,
        comment: CommentUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Update an existing comment.

    This function allows the current user to update a comment they have previously posted.
    The user must have the "user", "admin", or "moderator" role.

    :param comment_id: The ID of the comment to be updated.
    :type comment_id: int
    :param comment: The updated comment content.
    :type comment: CommentUpdate
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :param current_user: The currently authenticated user making the request.
    :type current_user: User
    :return: The updated comment.
    :rtype: CommentResponse
    :raises HTTPException: If the comment is not found or the user does not have permission to update it.
    """
    db_comment = await CommentRepository(db).get_comment_by_id(comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    updated_comment = await CommentRepository(db).update_comment(comment_id, comment.text)
    return updated_comment


@router.delete(
    "/comments/{comment_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RoleChecker([Role.admin, Role.moderator]))]
)
async def delete_comment(
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Delete an existing comment.

    This function allows the current user with "admin" or "moderator" privileges to delete a comment.

    :param comment_id: The ID of the comment to be deleted.
    :type comment_id: int
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :param current_user: The currently authenticated user making the request.
    :type current_user: User
    :return: A success message indicating the comment has been deleted.
    :rtype: dict
    :raises HTTPException: If the comment is not found or the user does not have permission to delete it.
    """
    db_comment = await CommentRepository(db).get_comment_by_id(comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if current_user.role not in [Role.admin, Role.moderator]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await CommentRepository(db).delete_comment(comment_id)
    return {"detail": "Comment deleted"}


@router.get(
    "/posts/{post_id}/comments/",
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK
)
async def get_comments_by_post(
        post_id: int,
        limit: int = Query(10, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)
):
    """
    Get comments for a specific post.

    This function retrieves all comments associated with a specific post, 
    with pagination support through limit and offset.

    :param post_id: The ID of the post for which comments are being retrieved.
    :type post_id: int
    :param limit: The maximum number of comments to return (default is 10).
    :type limit: int
    :param offset: The number of comments to skip (default is 0).
    :type offset: int
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :return: A list of comments for the specified post.
    :rtype: List[CommentResponse]
    :raises HTTPException: If the post with the given ID is not found (404).
    """
    db_post = await db.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = await CommentRepository(db).get_comments_by_post_id(post_id, limit, offset)
    return comments


@router.get(
    "/users/{user_id}/comments/",
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK
)
async def get_comments_by_user(
        user_id: int,
        limit: int = Query(10, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)
):
    """
    Get comments made by a specific user.

    This function retrieves all comments posted by a specific user, 
    with pagination support through limit and offset.

    :param user_id: The ID of the user for which comments are being retrieved.
    :type user_id: int
    :param limit: The maximum number of comments to return (default is 10).
    :type limit: int
    :param offset: The number of comments to skip (default is 0).
    :type offset: int
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :return: A list of comments made by the specified user.
    :rtype: List[CommentResponse]
    :raises HTTPException: If the user with the given ID is not found (404).
    """
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    comments = await CommentRepository(db).get_comments_by_user_id(user_id, limit, offset)
    return comments
