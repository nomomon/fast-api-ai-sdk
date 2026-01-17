from app.providers.base import BaseProvider
from app.providers.gemini import GeminiProvider
from app.providers.openai import OpenAIProvider


class ProviderFactory:
    @staticmethod
    def get_provider(provider_name: str) -> BaseProvider:
        match provider_name.lower():
            case "openai":
                return OpenAIProvider()
            case "google":
                return GeminiProvider()
            case _:
                raise ValueError(f"Unsupported provider: {provider_name}")
