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
    dependencies=[Depends(RoleChecker([Role.user, Role.admin, Role.moderator]))]
)
async def create_comment(
        post_id: int,
        comment: CommentCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_post = await db.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_comment = await CommentRepository(db).create_comment(post_id, current_user.id, comment.text)
    return db_comment


@router.put(
    "/comments/{comment_id}/",
    response_model=CommentResponse,
    dependencies=[Depends(RoleChecker([Role.user, Role.admin, Role.moderator]))]
)
async def update_comment(
        comment_id: int,
        comment: CommentUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
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
    db_comment = await CommentRepository(db).get_comment_by_id(comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if current_user.role not in [Role.admin, Role.moderator]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await CommentRepository(db).delete_comment(comment_id)
    return {"detail": "Comment deleted"}


@router.get(
    "/posts/{post_id}/comments/",
    response_model=List[CommentResponse]
)
async def get_comments_by_post(
        post_id: int,
        limit: int = Query(10, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)
):
    db_post = await db.get(Post, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = await CommentRepository(db).get_comments_by_post(post_id, limit, offset)
    return comments


@router.get(
    "/users/{user_id}/comments/",
    response_model=List[CommentResponse]
)
async def get_comments_by_user(
        user_id: int,
        limit: int = Query(10, ge=1, le=500),
        offset: int = Query(0, ge=0),
        db: AsyncSession = Depends(get_db)
):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    comments = await CommentRepository(db).get_comments_by_user(user_id, limit, offset)
    return comments
