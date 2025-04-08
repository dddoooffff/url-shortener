from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = f"postgresql+asyncpg://{getenv("DB_USER")}:{getenv("DB_PASS")}@{getenv("DB_HOST")}:{getenv("DB_PORT")}/{getenv("DB_NAME")}"
    SECRET: str = f"{getenv("SECRET_WORD")}"
    
settings = Settings()