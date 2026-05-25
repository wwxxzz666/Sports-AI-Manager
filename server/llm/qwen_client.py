import json
import httpx
from typing import AsyncGenerator

from llm.base import BaseLLMProvider
from config import settings


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
        except Exception:
            return self._mock_response(messages)

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
        except Exception:
            yield self._mock_response(messages)

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
            return self._mock_vision_response()

        try:
            resp = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._build_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            return self._mock_vision_response()

    def _mock_response(self, messages: list[dict]) -> str:
        """Return mock response when API key is not configured."""
        last_msg = messages[-1]["content"] if messages else ""
        return ("你好！收到你的消息：" + last_msg + "。这是 AI 运动管家的模拟回复。请配置 LLM_API_KEY 以获得真实的 AI 响应。")

    def _mock_vision_response(self) -> str:
        """Return mock vision response when API key is not configured."""
        return json.dumps(
            [
                {
                    "name": "米饭",
                    "portion": "一碗 (约200g)",
                    "portion_grams": 200,
                    "calories": 232,
                    "protein_g": 5.2,
                    "carbs_g": 51.2,
                    "fat_g": 0.6,
                    "confidence": 0.92,
                },
                {
                    "name": "红烧肉",
                    "portion": "3块 (约150g)",
                    "portion_grams": 150,
                    "calories": 585,
                    "protein_g": 22.5,
                    "carbs_g": 12.0,
                    "fat_g": 49.5,
                    "confidence": 0.68,
                },
            ],
            ensure_ascii=False,
        )

    async def close(self):
        await self.client.aclose()
