from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv


class Settings(BaseSettings):
    host: str
    port: int

    db_host: str
    db_port: str
    db_username: str
    db_password: str
    db_database: str

    db_host_test: str
    db_port_test: str
    db_username_test: str
    db_password_test: str
    db_database_test: str

    redis_host: str
    redis_port: int
    redis_db: int

    jwt_secret: str
    jwt_algorithm: str

    auth0_domain: str
    auth0_api_audience: str
    auth0_issuer: str
    auth0_algorithms: str

    model_config = SettingsConfigDict(env_file=find_dotenv())

    @property
    def postgresql_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_username}:{self.db_password}@{self.db_host}:" \
               f"{self.db_port}/{self.db_database}"

    @property
    def postgresql_test_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_username_test}:{self.db_password_test}@{self.db_host_test}:" \
               f"{self.db_port_test}/{self.db_database_test}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


global_settings = Settings()
