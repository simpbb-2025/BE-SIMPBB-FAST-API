from __future__ import annotations

import json
from datetime import datetime, timedelta
from functools import cached_property
from typing import Any, List
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database connection
    db_host: str = Field(default="127.0.0.1", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_name: str | None = Field(default=None, alias="DB_NAME")
    db_user: str | None = Field(default=None, alias="DB_USER")
    db_password: str | None = Field(default=None, alias="DB_PASS")
    db_driver: str = Field(default="mysql+aiomysql", alias="DB_DRIVER")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    # JWT configuration
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=180, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Application defaults
    timezone: str = Field(default="Asia/Jakarta", alias="TZ")

    # Optional tooling / integrations
    openapi_output_file: str | None = Field(default=None, alias="OPENAPI_OUTPUT_FILE")
    frontend_url: str | None = Field(default=None, alias="FRONTEND_URL")
    backend_url: str | None = Field(default=None, alias="BACKEND_URL")
    registration_code_length: int = Field(default=7, alias="REGISTRATION_CODE_LENGTH")
    registration_code_expire_minutes: int = Field(default=10, alias="REGISTRATION_CODE_EXPIRE_MINUTES")

    # Email delivery
    mail_username: str | None = Field(default=None, alias="MAIL_USERNAME")
    mail_password: str | None = Field(default=None, alias="MAIL_PASSWORD")
    mail_from: str = Field(default="no-reply@example.com", alias="MAIL_FROM")
    mail_port: int = Field(default=587, alias="MAIL_PORT")
    mail_server: str | None = Field(default=None, alias="MAIL_SERVER")
    mail_starttls: bool = Field(default=True, alias="MAIL_STARTTLS")
    mail_ssl_tls: bool = Field(default=False, alias="MAIL_SSL_TLS")
    mail_use_credentials: bool = Field(default=True, alias="USE_CREDENTIALS")

    cors_origins: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOW_HEADERS")

    @staticmethod
    def _parse_list(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in raw.split(",") if item.strip()]
        raise ValueError("Unsupported value for list setting")

    @field_validator("cors_origins", "cors_allow_methods", "cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_entries(cls, value: Any) -> List[str]:
        return cls._parse_list(value)

    @cached_property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        if not all([self.db_name, self.db_user]) or self.db_password is None:
            raise ValueError("Database configuration is incomplete")
        password = quote_plus(self.db_password)
        return (
            f"{self.db_driver}://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            "?charset=utf8mb4"
        )

    @cached_property
    def mysql_time_zone(self) -> str:
        if self.timezone.upper() in {"UTC", "SYSTEM"}:
            return self.timezone

        try:
            tz = ZoneInfo(self.timezone)
            now = datetime.now(tz)
            offset = now.utcoffset() or timedelta(0)
        except ZoneInfoNotFoundError:
            if self.timezone == "Asia/Jakarta":
                offset = timedelta(hours=7)
            else:
                offset = timedelta(0)

        total_minutes = int(offset.total_seconds() // 60)
        sign = "+" if total_minutes >= 0 else "-"
        total_minutes = abs(total_minutes)
        hours, minutes = divmod(total_minutes, 60)
        return f"{sign}{hours:02d}:{minutes:02d}"


settings = Settings()
