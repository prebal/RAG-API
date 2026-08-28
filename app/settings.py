from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{PROJECT_ROOT_DIR}/.env", extra="ignore"
    )

    # Database
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "notebook"

    # JWT
    secret_key: str = ""
    algo: str = "HS256"

    # LLM providers
    llm_local_base_url: str = "http://localhost:11434/v1"
    llm_local_model: str = "llama3.2:1b"
    llm_api_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_api_base_url: str = ""

    # Storage
    storage: str = str(PROJECT_ROOT_DIR / "storage")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
