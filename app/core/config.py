# global configs

from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #############################################
    # FastAPI environment variables
    #############################################
    DEBUG: bool = False
    DOMAIN: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_EMAIL: str
    ENCRYPT_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    TOKEN_TYPE: str = "Bearer"

    #############################################
    # PostgreSQL database environment variables
    #############################################
    DATABASE_HOST: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_CELERY_NAME: str
    DATABASE_PORT: int
    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379/0"

    #############################################
    # Mail variables
    #############################################
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    #############################################
    # OpenAPI variables
    #############################################
    OPEN_API_TITLE: str = "API Hub"
    OPEN_API_DESCRIPTION: str = "Demo API over Postgres database built with FastAPI."
    OPENAI_API_KEY: str

    #############################################
    # FastAPI constants
    #############################################
    APP_VERSION: str = "0.1.0"
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# broker_url = settings.REDIS_URL
# result_backend = settings.REDIS_URL
# broker_connection_retry_on_startup = True
