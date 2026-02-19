"""Auth module configuration."""

from pydantic_settings import BaseSettings

from src.config import find_env_file


class AuthConfig(BaseSettings):
    """JWT and auth-related settings."""

    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    jwt_exp_days: int = 7

    model_config = {
        "env_file": find_env_file() or ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


auth_settings = AuthConfig()
