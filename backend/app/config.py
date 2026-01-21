from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str

    # Gemini Configuration
    gemini_api_key: str | None = None

    # Application Configuration
    environment: str = "development"
    api_title: str = "AI Chatbot API"
    api_version: str = "1.0.0"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/fastapi_ai_sdk"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
