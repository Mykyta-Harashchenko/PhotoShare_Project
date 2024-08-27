from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

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