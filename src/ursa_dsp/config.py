import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    gemini_api_key: str = Field(..., description="Google Gemini API Key")
    env_path: str = Field("/Research_CRM/.env", description="Path to the .env file")

    model_config = SettingsConfigDict(
        env_file=(
            "/Research_CRM/.env",
            ".env",
            os.path.expanduser("~/.config/ursa_dsp/.env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
