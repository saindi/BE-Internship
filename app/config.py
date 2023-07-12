from pydantic_settings import BaseSettings
from dotenv import find_dotenv


class Settings(BaseSettings):
    host: str
    port: int

    db_host: str
    db_port: str
    db_username: str
    db_password: str
    db_database: str

    redis_host: str
    redis_port: int

    class Config:
        env_file = find_dotenv()
        env_file_encoding = 'utf-8'

    @property
    def postgresql_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"
