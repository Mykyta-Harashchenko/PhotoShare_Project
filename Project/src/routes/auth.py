from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload
from datetime import timedelta
from sqlalchemy.future import select

from Project.src.database.db import get_db
from Project.src.schemas.user import UserCreate, UserResponse, Token, UserUpdate
from Project.src.services.auth_service import get_password_hash, verify_password, create_access_token, admin_required, \
    moderate_required
from Project.src.entity.models import User, Role
from Project.src.services.dependencies import get_current_user

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter((User.email == user.email) | (User.username == user.username)))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    result = await db.execute(select(User))
    user_count = len(result.scalars().all())

    role = Role.admin if user_count == 0 else Role.user

    hashed_password = get_password_hash(user.password)
    user_model = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=role
    )
    db.add(user_model)
    await db.commit()
    await db.refresh(user_model)

    return user_model


@router.post("/signin", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(days=7))

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.patch("/users/{user_id}/promote", response_model=UserResponse)
async def promote_to_moderator(user_id: int, db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(admin_required)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = Role.moderator
    await db.commit()
    await db.refresh(user)

    return user


@router.get("/users/info", response_model=dict)
async def get_user_info(user_id: int = None, email: str = None, username: str = None,
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(moderate_required)):
    if not user_id and not email and not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide at least one of the following: user_id, email, or username."
        )

    query = select(User).options(joinedload(User.posts), joinedload(User.comments))

    if user_id:
        query = query.where(User.id == user_id)
    elif email:
        query = query.where(User.email == email)
    elif username:
        query = query.where(User.username == username)

    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "created_at": user.created_at,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "birthday": user.birthday,
        "phone": user.phone,
        "is_active": user.is_active,
        "is_blocked": user.is_blocked,
        "about": user.about,
        "post_count": len(user.posts),
        "comment_count": len(user.comments)
    }


@router.patch("/users/{user_id}/block", response_model=UserResponse)
async def block_user(user_id: int, block: bool, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(admin_required)):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot block yourself."
        )

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_blocked = block
    await db.commit()
    await db.refresh(user)

    return user

