# global configs

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #############################################
    # FastAPI environment variables
    #############################################
    DOMAIN: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_EMAIL: str
    ENCRYPT_KEY: str
    JWT_SECRET: str

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
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


# broker_url = settings.REDIS_URL
# result_backend = settings.REDIS_URL
# broker_connection_retry_on_startup = True
