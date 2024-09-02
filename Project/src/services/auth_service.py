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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_access_token


async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
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
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if user is None or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

async def signup(user: UserSignup, db: AsyncSession = Depends(get_db)):
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
    user.refresh_token = None
    await db.commit()
    return {"msg": "Successfully logged out"}


async def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions to access this resource."
        )
    return current_user

async def moderate_required(current_user: User = Depends(get_current_user)):
    if current_user.role not in [Role.admin, Role.moderator]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions to access this resource."
        )
    return current_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)