import os
import cloudinary
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DB_URL: str = os.environ.get("DB_URL")
    DB_TEST_URL: Optional[str] = os.environ.get("DB_TEST_URL")
    SECRET_KEY_JWT: str = os.environ.get("SECRET_KEY_JWT")
    ALGORITHM: str = os.environ.get("ALGORITHM")
    MAIL_USERNAME: Optional[str] = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = os.environ.get("MAIL_PASSWORD")
    MAIL_FROM: Optional[str] = os.environ.get("MAIL_FROM")
    MAIL_PORT: Optional[int] = os.environ.get("MAIL_PORT")
    MAIL_SERVER: Optional[str] = os.environ.get("MAIL_SERVER")
    REDIS_DOMAIN: Optional[str] = os.environ.get("REDIS_DOMAIN")
    REDIS_PORT: Optional[int] = os.environ.get("REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = os.environ.get("REDIS_PASSWORD")
    CLD_NAME: Optional[str] = os.environ.get("CLD_NAME")
    CLD_API_KEY: str = os.environ.get("CLD_API_KEY")
    CLD_API_SECRET: str = os.environ.get("CLD_API_SECRET")
    CLD_URL: str = os.environ.get("CLD_URL")


    class Config:
        env_file = "PhotoShare_Project/.env"
        env_file_encoding = "utf-8"



# Initialize the settings
config = Settings()
