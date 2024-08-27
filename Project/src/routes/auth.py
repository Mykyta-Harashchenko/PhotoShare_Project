from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from Project.src.database.db import get_db
from Project.src.schemas.user import UserCreate, UserResponse, Token
from Project.src.services.auth_service import get_password_hash, verify_password, create_access_token
from Project.src.entity.models import User, Role

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    user_model = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=Role.admin if db.query(User).count() == 0 else Role.user  # Первый пользователь - admin
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    return user_model


@router.post("/signin", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(days=7))

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
