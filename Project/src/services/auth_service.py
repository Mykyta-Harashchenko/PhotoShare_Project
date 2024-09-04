from typing import Optional
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from Project.src.database.db import get_db
from Project.src.services.dependencies import get_current_user
from Project.src.schemas.user import UserSignin, UserSignup
from Project.src.entity.models import User, Role
from Project.src.conf.config import config
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = config.SECRET_KEY_JWT
ALGORITHM = config.ALGORITHM


def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create an access token for a user.

    This function generates a JWT token using the provided data and expiry time.
    The token is signed with a secret key and contains claims like issued at (iat) and expiration time (exp).

    :param data: A dictionary of data to encode in the token, typically including user information like email.
    :type data: dict
    :param expires_delta: Optional. Time in seconds before the token expires. Defaults to 15 minutes.
    :type expires_delta: Optional[float]
    :return: Encoded JWT access token.
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token


async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create a refresh token for a user.

    This function generates a JWT refresh token with a longer expiry time, typically used for renewing access tokens.

    :param data: A dictionary of data to encode in the token, typically including user information like email.
    :type data: dict
    :param expires_delta: Optional. Time in seconds before the token expires. Defaults to 7 days.
    :type expires_delta: Optional[float]
    :return: Encoded JWT refresh token.
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Refresh an expired access token using a valid refresh token.

    This function decodes the provided refresh token, verifies its validity, and issues a new access token.

    :param refresh_token: The refresh token issued to the user.
    :type refresh_token: str
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :return: A dictionary containing the new access token.
    :rtype: dict
    :raises HTTPException: If the token is invalid or expired, or the user is not found.
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()

    if user is None or user.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    access_token = await create_access_token(data={"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Authenticate a user by verifying their email and password.

    This function checks if the provided email exists in the database and verifies the password.

    :param db: The database session for executing queries.
    :type db: AsyncSession
    :param email: The email of the user.
    :type email: str
    :param password: The plain text password provided by the user.
    :type password: str
    :return: The authenticated user object, or None if authentication fails.
    :rtype: Optional[User]
    """
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if user is None or not pwd_context.verify(password, user.hashed_password):
        return False
    return user


async def signup(user: UserSignup, db: AsyncSession = Depends(get_db)):
    """
    Sign up a new user and save them to the database.

    This function creates a new user with a hashed password and stores their information in the database.

    :param user: The user data for the new user.
    :type user: UserSignup
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :return: A dictionary containing a success message and the user ID.
    :rtype: dict
    :raises HTTPException: If the email is already registered.
    """
    existing_user = await db.execute(select(User).filter(User.email == user.email))
    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role="admin" if (await db.execute(select(User))).scalar() is None else "user"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": "User created successfully", "user_id": new_user.id}


async def signin(user: UserSignin, db: AsyncSession = Depends(get_db)):
    """
    Sign in a user and issue access and refresh tokens.

    This function verifies the user's credentials and issues a new access token and refresh token.

    :param user: The user data for sign-in.
    :type user: UserSignin
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :return: A dictionary containing the access token, refresh token, and token type.
    :rtype: dict
    :raises HTTPException: If the email or password is incorrect.
    """
    user = await authenticate_user(db, user.email, user.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})

    user.refresh_token = refresh_token
    await db.commit()
    await db.refresh(user)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


async def signout(user: User, db: AsyncSession = Depends(get_db)):
    """
    Sign out a user by invalidating their refresh token.

    This function sets the user's refresh token to None, effectively signing them out.

    :param user: The currently authenticated user.
    :type user: User
    :param db: The database session for executing queries.
    :type db: AsyncSession
    :return: A success message.
    :rtype: dict
    """
    user.refresh_token = None
    await db.commit()
    return {"msg": "Successfully logged out"}


async def admin_required(current_user: User = Depends(get_current_user)):
    """
    Check if the current user has admin privileges.

    This function ensures that the current user has the "admin" role.

    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: The current user if they have admin privileges.
    :rtype: User
    :raises HTTPException: If the user is not an admin.
    """
    if current_user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions to access this resource."
        )
    return current_user

async def moderate_required(current_user: User = Depends(get_current_user)):
    """
    Check if the current user has admin or moderator privileges.

    This function ensures that the current user has either the "admin" or "moderator" role.
    It is intended to be used as a dependency to restrict access to certain routes.

    :param current_user: The currently authenticated user.
    :type current_user: User
    :return: The current user if they have admin or moderator privileges.
    :rtype: User
    :raises HTTPException: If the user is neither an admin nor a moderator, an HTTP 403 error is raised.

    Example:
    ```
    @router.get("/moderator-only", dependencies=[Depends(moderate_required)])
    async def moderator_only_route():
        return {"message": "You have moderator privileges!"}
    ```
    """
    if current_user.role not in [Role.admin, Role.moderator]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions to access this resource."
        )
    return current_user

def verify_password(plain_password, hashed_password):
    """
    Verify if the provided plain text password matches the hashed password.

    This function checks whether a plain text password matches its hashed counterpart
    by using the password hashing context (`pwd_context`). It is typically used during
    user authentication to verify credentials.

    :param plain_password: The plain text password entered by the user.
    :type plain_password: str
    :param hashed_password: The hashed password stored in the database.
    :type hashed_password: str
    :return: True if the passwords match, False otherwise.
    :rtype: bool

    Example:
    ```
    if verify_password("my_password", hashed_password_from_db):
        # Password is correct
    else:
        # Incorrect password
    ```
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Hash a plain text password using the bcrypt algorithm.

    This function hashes a given plain text password to store it securely in the database
    using the password hashing context (`pwd_context`). It ensures that user passwords are
    not stored in plain text.

    :param password: The plain text password to be hashed.
    :type password: str
    :return: The hashed version of the password.
    :rtype: str

    Example:
    ```
    hashed_password = get_password_hash("my_secure_password")
    # Store hashed_password in the database
    ```
    """
    return pwd_context.hash(password)
