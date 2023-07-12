import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    HOST: str = os.environ.get('HOST')
    PORT: int = int(os.environ.get('PORT'))

    DB_HOST: str = os.environ.get('DB_HOST')
    DB_PORT: str = os.environ.get('DB_PORT')
    DB_USERNAME: str = os.environ.get('DB_USERNAME')
    DB_PASSWORD: str = os.environ.get('DB_PASSWORD')
    DB_DATABASE: str = os.environ.get('DB_DATABASE')
    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

    REDIS_HOST: str = os.environ.get('REDIS_HOST')
    REDIS_PORT: int = int(os.environ.get('REDIS_PORT'))
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"
