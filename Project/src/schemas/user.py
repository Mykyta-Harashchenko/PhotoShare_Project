from pydantic import BaseModel, EmailStr
from datetime import date


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    about: str | None = None
    birthday: date | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserSignin(BaseModel):
    email: str
    password: str


class UserSignup(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
