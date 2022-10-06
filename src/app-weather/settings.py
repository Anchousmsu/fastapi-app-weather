from pydantic import BaseSettings, PostgresDsn
from functools import lru_cache


class Settings(BaseSettings):
    server_host: str = '127.0.0.1'
    server_port: int = 8000
    db_url: PostgresDsn = ''

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# @lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
