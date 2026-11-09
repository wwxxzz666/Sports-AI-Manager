import json
import logging
import httpx
from typing import AsyncGenerator

from llm.base import BaseLLMProvider
from core.exceptions import LLMProviderError
from config import settings

logger = logging.getLogger(__name__)


class QwenClient(BaseLLMProvider):
    """通义千问 (DashScope OpenAI-compatible API) adapter."""

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
            or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.client = httpx.AsyncClient(timeout=60.0)

    def get_provider_name(self) -> str:
        return "qwen"

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
            return self._mock_response(messages)

        try:
            resp = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._build_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            # 以前这里静默返回 mock 假数据，用户根本看不出 AI 已经挂了。
            # 现在明确抛 502，由上层展示"AI 服务不可用"。
            logger.error("通义千问 chat 调用失败: %s", e)
            raise LLMProviderError(f"通义千问调用失败: {e}") from e

    async def chat_stream(self, messages: list[dict], system_prompt: str = "") -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": self._build_messages(messages, system_prompt),
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True,
        }

        if not self.api_key:
            # Mock streaming
            full_text = self._mock_response(messages)
            for char in full_text:
                yield char
            return

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
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
            logger.error("通义千问流式调用失败: %s", e)
            raise LLMProviderError(f"通义千问流式调用失败: {e}") from e

    async def chat_with_vision(self, image_url: str, prompt: str) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        payload = {
            "model": self.vision_model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        if not self.api_key:
            # 图片识别绝不能编造结果：以前这里返回一份写死的"米饭 + 红烧肉"，
            # 用户上传任意图片都会得到这份假营养数据。
            raise LLMProviderError(
                "未配置 LLM_API_KEY，无法进行图片识别。请在 .env 中配置通义千问的 API Key 后重试。"
            )

        try:
            resp = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._build_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("通义千问视觉模型调用失败: %s", e)
            raise LLMProviderError(f"图片识别失败: {e}") from e

    def _mock_response(self, messages: list[dict]) -> str:
        """未配置 API Key 时的明确提示（不伪造内容）。"""
        last_msg = messages[-1]["content"] if messages else ""
        logger.warning("QwenClient 未配置 LLM_API_KEY，返回离线提示而非真实回复")
        return ("你好！收到你的消息：" + str(last_msg) + "。这是 AI 运动管家的模拟回复。请配置 LLM_API_KEY 以获得真实的 AI 响应。")

    async def close(self):
        await self.client.aclose()
