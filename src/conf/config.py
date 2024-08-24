from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DB_URL: str
    DB_TEST_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    REDIS_DOMAIN: str
    REDIS_PORT: int
    REDIS_PASSWORD: Optional[str]
    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    class Config:
        env_file = "PhotoShare_Project/.env"
        env_file_encoding = "utf-8"


config = Settings()
