"""Module for configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the application."""

    AUTH_SECRET: str = Field()

    MONGODB_URL: str = Field()
    MONGODB_USER: str = Field()
    MONGODB_PASSWORD: str = Field()

    model_config = SettingsConfigDict(env_file=".env")


env = Settings()
