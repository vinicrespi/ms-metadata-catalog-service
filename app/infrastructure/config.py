from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_url: str
    mongodb_database: str

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")