from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    mongo_uri: str = "mongodb://localhost:27018"  # Changed to match Docker port
    mongo_db: str = "todo_db"

    # Redis settings
    redis_url: str = "redis://localhost:6379"  # Application settings
    debug: bool = False
    max_open_todos: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings() -> Settings:
    # Using Depends on this function gives DI-style config
    return Settings()
