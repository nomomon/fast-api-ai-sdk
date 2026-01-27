from pathlib import Path

from pydantic_settings import BaseSettings


def find_env_file() -> str | None:
    """Find .env file in current directory or root directory."""
    # Check current directory (backend/)
    current_env = Path(".env")
    if current_env.exists():
        return str(current_env)
    
    # Check parent directory (root)
    # __file__ is backend/app/config.py, so parent.parent.parent is the root
    root_env = Path(__file__).parent.parent.parent / ".env"
    if root_env.exists():
        return str(root_env)
    
    return None


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

    # JWT Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = find_env_file() or ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
