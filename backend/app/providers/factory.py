from app.providers.base import BaseProvider
from app.providers.litellm import LiteLLMProvider


class ProviderFactory:
    @staticmethod
    def get_provider(provider_name: str) -> BaseProvider:
        return LiteLLMProvider(provider_name.lower())
