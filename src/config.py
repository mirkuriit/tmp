from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_url: str
    log_level: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def is_log_level_valid(cls, value):
        if value in ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            return value
        raise ValueError(f"Invalid log level: {value}")



settings = Settings()
