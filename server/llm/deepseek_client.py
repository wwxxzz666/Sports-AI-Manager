import json
import logging
import httpx
from typing import AsyncGenerator

from llm.base import BaseLLMProvider
from core.exceptions import LLMProviderError
from config import settings

logger = logging.getLogger(__name__)


class DeepSeekClient(BaseLLMProvider):
    """DeepSeek (OpenAI-compatible API) adapter."""

    def __init__(
        self,
        model: str = "",
        api_key: str = "",
        base_url: str | None = None,
        vision_model: str = "",
    ):
        self.model = model or settings.LLM_MODEL
        self.vision_model = vision_model or settings.LLM_VISION_MODEL
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = (
            base_url
            or settings.LLM_BASE_URL
            or "https://api.deepseek.com"
        )
        self.client = httpx.AsyncClient(timeout=60.0)

    def get_provider_name(self) -> str:
        return "deepseek"

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_messages(self, messages: list[dict], system_prompt: str) -> list[dict]:
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for msg in messages:
            formatted.append({"role": msg["role"], "content": msg["content"]})
        return formatted

    async def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        payload = {
            "model": self.model,
            "messages": self._build_messages(messages, system_prompt),
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        if not self.api_key:
            return self._no_api_key_response()

        try:
            resp = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=self._build_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            # 以前这里把异常字符串当成 assistant 回复返回并存库，
            # 前端完全分不出"AI 挂了"和"正常回复"。
            logger.error("DeepSeek chat 调用失败: %s", e)
            raise LLMProviderError(f"DeepSeek 调用失败: {e}") from e

    async def chat_stream(self, messages: list[dict], system_prompt: str = "") -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": self._build_messages(messages, system_prompt),
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True,
        }

        if not self.api_key:
            yield self._no_api_key_response()
            return

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=self._build_headers(),
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except Exception as e:
            logger.error("DeepSeek 流式调用失败: %s", e)
            raise LLMProviderError(f"DeepSeek 流式调用失败: {e}") from e

    async def chat_with_vision(self, image_url: str, prompt: str) -> str:
        """DeepSeek does not support vision."""
        raise LLMProviderError(
            "DeepSeek 不支持多模态识别。该功能需要通义千问 qwen-vl-max，"
            "请设置 LLM_PROVIDER=qwen 后重试。"
        )

    def _no_api_key_response(self) -> str:
        logger.warning("DeepSeekClient 未配置 API Key，返回离线提示而非真实回复")
        return "请配置 DASHSCOPE_API_KEY 或 LLM_API_KEY 环境变量以获得 AI 响应。当前为离线模式。"

    async def close(self):
        await self.client.aclose()
