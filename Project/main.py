from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_limiter.depends import RateLimiter

from Project.src.routes import comments, photos
from Project.src.database.db import get_db
from Project.src.entity.models import Base, User
from Project.src.schemas.user import UserSignin, UserSignup
from Project.src.routes.auth import router as auth_router
from Project.src.services.auth_service import signin, signout, refresh_token, get_password_hash
from fastapi_limiter.depends import RateLimiter

from Project.src.conf.config import config
from Project.src.services.dependencies import get_current_user

app = FastAPI(title="PhotoShare API", description="API для зберігання та поширення фото")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(comments.router, tags=["comments"])
app.include_router(auth_router, prefix="/api")
app.include_router(photos.router, tags=["photos"])


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def index():
    return {"msg": "Hello World"}



@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
