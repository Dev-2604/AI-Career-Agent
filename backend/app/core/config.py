
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    APP_NAME: str = "AI Career Agent"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Authentication
    SECRET_KEY: str = "development-only-change-this-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ai_career_agent"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Resume storage
    RESUME_STORAGE_DIR: str = "storage/resumes"
    MAX_RESUME_SIZE_MB: int = 5
    ALLOWED_RESUME_EXTENSIONS: list[str] = [".pdf", ".docx"]

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = (
        "http://localhost:8000/api/v1/github/callback"
    )

    # GitHub token encryption
    GITHUB_TOKEN_ENCRYPTION_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )


settings = Settings()
