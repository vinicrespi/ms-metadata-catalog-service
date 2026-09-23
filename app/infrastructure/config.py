from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")
    SECRET_KEY: str = Field(validation_alias="SECRET_KEY")
    DATABASE_URL: str = Field(
        validation_alias=AliasChoices("DATABASE_URL", "MONGODB_URL")
    )
    DATABASE_NAME: str = Field(
        validation_alias=AliasChoices("DATABASE_NAME", "MONGODB_DATABASE")
    )


settings = Settings() 