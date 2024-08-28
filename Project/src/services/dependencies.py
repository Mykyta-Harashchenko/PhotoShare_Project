from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Project.src.database.db import get_db
from Project.src.entity.models import User
from Project.src.conf.config import config
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

SECRET_KEY = config.SECRET_KEY_JWT
ALGORITHM = config.ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = await db.execute(select(User).filter(User.email == email))
        user = user.scalar()
        if user is None:
            raise credentials_exception

        if user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is blocked.",
            )

        return user
    except JWTError:
        raise credentials_exception
