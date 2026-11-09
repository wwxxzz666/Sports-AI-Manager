"""LLM 错误处理回归测试。

历史问题：
- qwen_client.chat / chat_with_vision 的 except 分支静默返回 mock 假数据
- deepseek_client.chat 把异常字符串当成正常回复返回并存库
API 挂了、401、限流，用户看到的都是"正常回答"，完全无法察觉。
"""

import json
from unittest.mock import AsyncMock

import pytest

from core.exceptions import LLMProviderError
from llm.deepseek_client import DeepSeekClient
from llm.qwen_client import QwenClient

GOOD_ITEMS = [{"name": "牛排", "calories": 450}]


async def test_qwen_chat_error_raises_instead_of_mock(monkeypatch):
    client = QwenClient(api_key="fake-key")
    monkeypatch.setattr(client.client, "post", AsyncMock(side_effect=RuntimeError("401 Unauthorized")))

    with pytest.raises(LLMProviderError):
        await client.chat([{"role": "user", "content": "你好"}])


async def test_qwen_chat_without_api_key_returns_explicit_offline_hint():
    """没配 key 时给出明确提示（不伪造内容，也不抛错，保留本地开发体验）。"""
    client = QwenClient(api_key="")
    reply = await client.chat([{"role": "user", "content": "你好"}])
    assert "LLM_API_KEY" in reply


async def test_qwen_vision_without_api_key_raises():
    """图片识别没有 key 必须报错 —— 以前会返回写死的米饭红烧肉。"""
    client = QwenClient(api_key="")
    with pytest.raises(LLMProviderError):
        await client.chat_with_vision("http://example.com/a.jpg", "识别食物")


async def test_qwen_vision_error_raises(monkeypatch):
    client = QwenClient(api_key="fake-key")
    monkeypatch.setattr(client.client, "post", AsyncMock(side_effect=RuntimeError("boom")))

    with pytest.raises(LLMProviderError):
        await client.chat_with_vision("http://example.com/a.jpg", "识别食物")


async def test_qwen_vision_success_returns_model_content(monkeypatch):
    client = QwenClient(api_key="fake-key")
    payload = json.dumps(GOOD_ITEMS, ensure_ascii=False)

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": payload}}]}

    monkeypatch.setattr(client.client, "post", AsyncMock(return_value=_Resp()))
    got = await client.chat_with_vision("http://example.com/a.jpg", "识别食物")
    assert got == payload


async def test_deepseek_chat_error_raises(monkeypatch):
    client = DeepSeekClient(api_key="fake-key")
    monkeypatch.setattr(client.client, "post", AsyncMock(side_effect=RuntimeError("network down")))

    with pytest.raises(LLMProviderError):
        await client.chat([{"role": "user", "content": "你好"}])


async def test_deepseek_vision_raises_not_fake_json():
    client = DeepSeekClient(api_key="fake-key")
    with pytest.raises(LLMProviderError) as exc:
        await client.chat_with_vision("http://example.com/a.jpg", "识别食物")
    assert "DeepSeek" in str(exc.value)
