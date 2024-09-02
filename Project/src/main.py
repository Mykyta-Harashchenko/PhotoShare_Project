from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from Project.src.database.db import get_db

from Project.src.routes.auth import router as auth_router
from Project.src.routes import comments, photos
from Project.src.services.auth_service import signin, signout, refresh_token, get_password_hash
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from sqlalchemy import text


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url("redis://localhost:6379", encoding="utf8")
    await FastAPILimiter.init(redis_connection)
    yield
    await FastAPILimiter.close()

app = FastAPI(lifespan=lifespan, title="PhotoShare API", description="API для зберігання та поширення фото")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, tags=["autorization"])
app.include_router(photos.router, tags=["photos"])
app.include_router(comments.router, tags=["comments"])



@app.get("/api/healthchecker", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
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



# @app.get("/users/me")
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user

