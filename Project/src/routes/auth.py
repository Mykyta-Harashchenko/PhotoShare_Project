from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload
from datetime import timedelta
from sqlalchemy.future import select

from Project.src.database.db import get_db
from Project.src.schemas.user import UserCreate, UserResponse, Token, UserUpdate, UserSignin, UserSignup
from Project.src.services.auth_service import get_password_hash, verify_password, create_access_token, admin_required, \
    moderate_required, signout, signin, signup
from Project.src.entity.models import User, Role
from Project.src.services.dependencies import get_current_user

router = APIRouter(tags=['auth'])

@router.post("/signup")
async def register(user: UserSignup, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user in the system.

    This endpoint allows new users to sign up by providing their details.

    :param user: The user's signup information.
    :type user: UserSignup
    :param db: The database session to use for database operations.
    :type db: AsyncSession
    :return: A success message and the user ID of the created user.
    :rtype: dict
    :raises HTTPException: If the email is already registered.
    """
    return await signup(user, db)

@router.post("/signin")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
        Logs in a user and generates access and refresh tokens.

        This endpoint handles user authentication, and if successful, provides access and refresh tokens for future requests.

        :param form_data: The user's login credentials.
        :type form_data: OAuth2PasswordRequestForm
        :param db: The database session to use for database operations.
        :type db: AsyncSession
        :return: The access and refresh tokens.
        :rtype: dict
        :raises HTTPException: If the credentials are invalid.
    """
    user_signin = UserSignin(email=form_data.username, password=form_data.password)
    return await signin(user_signin, db)

@router.post("/signout")
async def logout(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Logs out the currently authenticated user.

    This endpoint invalidates the user's refresh token and logs them out.

    :param current_user: The currently authenticated user.
    :type current_user: User
    :param db: The database session to use for database operations.
    :type db: AsyncSession
    :return: A message indicating the user was logged out.
    :rtype: dict
    """
    return await signout(current_user, db)


@router.patch("/users/{user_id}/promote", response_model=UserResponse)
async def promote_to_moderator(user_id: int, db: AsyncSession = Depends(get_db),
                               current_user: User = Depends(admin_required)):
    """
    Promotes a user to the moderator role.

    This endpoint allows admins to promote a regular user to a moderator role.

    :param user_id: The ID of the user to promote.
    :type user_id: int
    :param db: The database session to use for database operations.
    :type db: AsyncSession
    :param current_user: The currently authenticated admin user.
    :type current_user: User
    :return: The promoted user's data.
    :rtype: UserResponse
    :raises HTTPException: If the user is not found.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = Role.moderator
    await db.commit()
    await db.refresh(user)

    return user

@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users/info", response_model=dict)
async def get_user_info(user_id: int = None, email: str = None, username: str = None,
                        db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(moderate_required)):
    """
    Retrieves detailed information about a specific user.
    
    This endpoint allows moderators and admins to fetch user details based on user ID, email, or username.
    
    :param user_id: The ID of the user to fetch information for (optional).
    :type user_id: int
    :param email: The email of the user to fetch information for (optional).
    :type email: str
    :param username: The username of the user to fetch information for (optional).
    :type username: str
    :param db: The database session to use for database operations.
    :type db: AsyncSession
    :param current_user: The currently authenticated moderator or admin.
    :type current_user: User
    :return: A dictionary containing the user's information.
    :rtype: dict
    :raises HTTPException: If no identifier is provided or if the user is not found.
    """
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
    """
    Blocks or unblocks a user.

    This endpoint allows an admin to block or unblock a user by their user ID.

    :param user_id: The ID of the user to block or unblock.
    :type user_id: int
    :param block: Whether to block or unblock the user.
    :type block: bool
    :param db: The database session to use for database operations.
    :type db: AsyncSession
    :param current_user: The currently authenticated admin.
    :type current_user: User
    :return: The blocked/unblocked user's data.
    :rtype: UserResponse
    :raises HTTPException: If the user is not found or if the admin tries to block themselves.
    """
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

