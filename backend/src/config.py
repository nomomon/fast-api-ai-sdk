"""Global application configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings


def find_env_file() -> str | None:
    """Find .env file in current directory or root directory."""
    current_env = Path(".env")
    if current_env.exists():
        return str(current_env)

    # __file__ is backend/src/config.py, parent.parent.parent is project root
    root_env = Path(__file__).resolve().parent.parent.parent / ".env"
    if root_env.exists():
        return str(root_env)

    return None


class Config(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str | None = None

    # Gemini Configuration
    gemini_api_key: str | None = None

    # Application Configuration
    environment: str = "development"

    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:3001"

    # Database Configuration
    database_url: str = "postgresql://postgres:postgres@localhost:5432/fastapi_ai_sdk"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {
        "env_file": find_env_file() or ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Config()
