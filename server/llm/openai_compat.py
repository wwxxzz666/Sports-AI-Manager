"""OpenAI 兼容协议的共享实现。

DeepSeek 和通义千问（DashScope 兼容模式）都暴露 OpenAI 的
/v1/chat/completions 协议。原来 DeepSeekClient 和 QwenClient 把这套
请求构造 + 流式解析逻辑逐字复制了两遍（归一化后 diff 只有 8 处不同：
base_url、endpoint 路径、离线提示文案、vision 支持与否）。

现在公共部分只在这里实现一次，子类只声明差异点。
新增一个 OpenAI 兼容 Provider 只需要继承 + 写 3 个类属性。
"""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

import httpx

from config import settings
from core.exceptions import LLMProviderError
from llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleClient(BaseLLMProvider):
    """OpenAI 兼容 Chat Completions 客户端基类。

    子类需要覆盖：
        provider_name    : str   例如 "deepseek"
        default_base_url : str   例如 "https://api.deepseek.com"
        endpoint_path    : str   例如 "/v1/chat/completions"
        supports_vision  : bool
    """

    provider_name: str = ""
    #: 面向用户的品牌名（消息文案用），默认回落到 provider_name
    display_name: str = ""
    default_base_url: str = ""
    endpoint_path: str = "/v1/chat/completions"
    supports_vision: bool = False

    #: 未配置 API Key 时返回给用户的提示（不伪造内容）
    offline_hint: str = (
        "请配置 LLM_API_KEY 环境变量以获得 AI 响应。当前为离线模式。"
    )

    def __init__(
        self,
        model: str = "",
        api_key: str = "",
        base_url: str | None = None,
        vision_model: str = "",
        timeout: float = 60.0,
    ):
        self.model = model or settings.LLM_MODEL
        self.vision_model = vision_model or settings.LLM_VISION_MODEL
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or settings.LLM_BASE_URL or self.default_base_url
        self.client = httpx.AsyncClient(timeout=timeout)

    # ── 基础 ────────────────────────────────────────────

    def get_provider_name(self) -> str:
        return self.provider_name

    @property
    def brand(self) -> str:
        return self.display_name or self.provider_name

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}{self.endpoint_path}"

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

    def _offline_response(self, messages: list[dict]) -> str:
        """未配置 API Key 时的明确提示。"""
        logger.warning("%s 未配置 API Key，返回离线提示而非真实回复", type(self).__name__)
        return self.offline_hint

    # ── 对话 ────────────────────────────────────────────

    async def chat(self, messages: list[dict], system_prompt: str = "") -> str:
        if not self.api_key:
            return self._offline_response(messages)

        payload = {
            "model": self.model,
            "messages": self._build_messages(messages, system_prompt),
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        try:
            resp = await self.client.post(
                self.endpoint, json=payload, headers=self._build_headers()
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            # 不要静默返回假数据：用户必须能区分"AI 挂了"和"正常回答"
            logger.error("%s chat 调用失败: %s", type(self).__name__, e)
            raise LLMProviderError(f"{self.brand} 调用失败: {e}") from e

    async def chat_stream(
        self, messages: list[dict], system_prompt: str = ""
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield self._offline_response(messages)
            return

        payload = {
            "model": self.model,
            "messages": self._build_messages(messages, system_prompt),
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True,
        }

        try:
            async with self.client.stream(
                "POST", self.endpoint, json=payload, headers=self._build_headers()
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    chunk = self.parse_sse_line(line)
                    if chunk:
                        yield chunk
        except Exception as e:
            logger.error("%s 流式调用失败: %s", type(self).__name__, e)
            raise LLMProviderError(f"{self.brand} 流式调用失败: {e}") from e

    @staticmethod
    def parse_sse_line(line: str) -> str:
        """从一行 SSE 数据里取出 delta 文本；非数据行返回空串。"""
        if not line.startswith("data: "):
            return ""
        data_str = line[6:].strip()
        if not data_str or data_str == "[DONE]":
            return ""
        try:
            delta = json.loads(data_str)["choices"][0].get("delta", {})
        except (json.JSONDecodeError, KeyError, IndexError):
            return ""
        return delta.get("content", "") or ""

    # ── 视觉 ────────────────────────────────────────────

    def _vision_messages(self, image_url: str, prompt: str) -> list[dict]:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

    async def chat_with_vision(self, image_url: str, prompt: str) -> str:
        if not self.supports_vision:
            raise LLMProviderError(
                f"{self.brand} 不支持多模态识别。"
                "该功能需要通义千问 qwen-vl-max，请设置 LLM_PROVIDER=qwen 后重试。"
            )

        if not self.api_key:
            # 图片识别绝不能编造结果
            raise LLMProviderError(
                "未配置 LLM_API_KEY，无法进行图片识别。请在 .env 中配置 API Key 后重试。"
            )

        payload = {
            "model": self.vision_model,
            "messages": self._vision_messages(image_url, prompt),
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        try:
            resp = await self.client.post(
                self.endpoint, json=payload, headers=self._build_headers()
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("%s 视觉模型调用失败: %s", type(self).__name__, e)
            raise LLMProviderError(f"图片识别失败: {e}") from e

    async def close(self):
        await self.client.aclose()
