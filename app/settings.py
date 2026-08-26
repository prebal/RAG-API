from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    postgres_user: str = ""
    postgres_password: str = ""

    # JWT
    secret_key: str = ""
    algo: str = "HS256"

    # LLM providers
    llm_local_base_url: str = "http://localhost:11434/v1"
    llm_local_model: str = "llama3.2:1b"
    llm_api_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_api_base_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
