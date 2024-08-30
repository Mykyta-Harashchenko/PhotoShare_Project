from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.future import select
from jose import JWTError, jwt
from datetime import timedelta, datetime

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


app.include_router(auth_router, prefix="/api")


@app.post("/signup")
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


@app.post("/signin")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_signin = UserSignin(email=form_data.username, password=form_data.password)
    return await signin(user_signin, db)


@app.post("/refresh")
async def refresh(refresh_token: str, db: AsyncSession = Depends(get_db)):
    return await refresh_token(refresh_token, db)


@app.post("/signout")
async def logout(current_user: User = Depends(get_db), db: AsyncSession = Depends(get_db)):
    return await signout(current_user, db)


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