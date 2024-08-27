from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from Project.src.database.db import get_db
from Project.src.schemas.user import UserSignin
from Project.src.entity.models import User
from Project.src.conf.config import config
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = config.SECRET_KEY_JWT
ALGORITHM = config.ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)