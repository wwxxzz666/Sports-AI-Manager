from llm.base import BaseLLMProvider
from llm.qwen_client import QwenClient
from llm.deepseek_client import DeepSeekClient
from config import settings


def create_llm_provider(provider: str = "", api_key: str = "") -> BaseLLMProvider:
    """Factory function to create an LLM provider instance."""
    provider = provider or settings.LLM_PROVIDER

    if provider == "deepseek":
        return DeepSeekClient(
            model=settings.LLM_MODEL,
            api_key=api_key or settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            vision_model=settings.LLM_VISION_MODEL,
        )
    elif provider == "qwen":
        return QwenClient(
            model=settings.LLM_MODEL,
            api_key=api_key or settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            vision_model=settings.LLM_VISION_MODEL,
        )
    else:
        # Default to DeepSeek
        return DeepSeekClient(
            model=settings.LLM_MODEL,
            api_key=api_key or settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            vision_model=settings.LLM_VISION_MODEL,
        )


# Singleton instance
_llm_instance: BaseLLMProvider | None = None


def get_llm() -> BaseLLMProvider:
    """Get the singleton LLM provider instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = create_llm_provider()
    return _llm_instance
