from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    async def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        """Send messages and get a complete response."""
        pass

    @abstractmethod
    async def chat_stream(self, messages: list[dict], system_prompt: str = "") -> AsyncGenerator[str, None]:
        """Send messages and stream the response."""
        yield ""

    @abstractmethod
    async def chat_with_vision(self, image_url: str, prompt: str) -> str:
        """Send an image with a prompt and get a response."""
        pass

    async def close(self):
        """Clean up resources."""
        pass
