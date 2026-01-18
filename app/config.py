from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, computed_field


class Settings(BaseSettings):
    # Load .env safely
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    # -----------------------------
    # APP
    # -----------------------------
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Voice Serve AI"

    # -----------------------------
    # LLM (ONLY OPENROUTER)
    # -----------------------------
    OPENROUTER_API_KEY: str

    # -----------------------------
    # INTEGRATION
    # -----------------------------
    TELEGRAM_BOT_TOKEN: str = ""
    AI_BACKEND_URL: str = "http://127.0.0.1:8000/api/v1/process"
    MOCK_PORTAL_URL: str = "http://127.0.0.1:8000/portal"

    # -----------------------------
    # DATABASE (OPTIONAL / FUTURE)
    # -----------------------------
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: int = 5432

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


settings = Settings()
