"""Provider 基类契约测试。

两个适配器（DeepSeek / 通义千问）原来各自实现了一遍
_build_headers / _build_messages / chat / chat_stream，归一化后
diff 只有 8 处不同。现在公共逻辑在 OpenAICompatibleClient，
子类只声明差异点。
"""

import json
import pathlib
from unittest.mock import AsyncMock

import pytest

from core.exceptions import LLMProviderError
from llm.deepseek_client import DeepSeekClient
from llm.openai_compat import OpenAICompatibleClient
from llm.qwen_client import QwenClient

LLM_DIR = pathlib.Path(__file__).resolve().parents[1] / "llm"


def test_endpoints_are_composed_correctly():
    assert DeepSeekClient().endpoint == "https://api.deepseek.com/v1/chat/completions"
    assert (
        QwenClient().endpoint
        == "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    )


def test_vision_support_differs_by_provider():
    assert DeepSeekClient.supports_vision is False
    assert QwenClient.supports_vision is True


def test_both_clients_subclass_the_shared_base():
    assert issubclass(DeepSeekClient, OpenAICompatibleClient)
    assert issubclass(QwenClient, OpenAICompatibleClient)


def test_chat_and_stream_defined_only_once_in_llm_package():
    """回归：不要在子类里再复制一遍 chat/chat_stream。"""
    offenders = []
    for path in LLM_DIR.glob("*.py"):
        if path.name in {"base.py", "openai_compat.py"}:
            continue
        source = path.read_text(encoding="utf-8")
        for name in ("async def chat(", "async def chat_stream(", "async def chat_with_vision("):
            if name in source:
                offenders.append(f"{path.name}: {name}")

    assert not offenders, "以下文件重复实现了基类方法:\n" + "\n".join(offenders)


def test_custom_provider_needs_only_class_attributes(monkeypatch):
    """新增一个 OpenAI 兼容 Provider 只需声明类属性。"""

    class DummyClient(OpenAICompatibleClient):
        display_name = "Dummy"
        provider_name = "dummy"
        default_base_url = "https://dummy.example/v1"
        endpoint_path = "/chat/completions"

    client = DummyClient(api_key="k")
    assert client.endpoint == "https://dummy.example/v1/chat/completions"

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "hello"}}]}

    monkeypatch.setattr(client.client, "post", AsyncMock(return_value=_Resp()))

    import asyncio

    assert asyncio.run(client.chat([{"role": "user", "content": "hi"}])) == "hello"


def test_build_messages_prepends_system_prompt():
    client = QwenClient(api_key="k")
    messages = client._build_messages([{"role": "user", "content": "hi"}], "be nice")

    assert messages == [
        {"role": "system", "content": "be nice"},
        {"role": "user", "content": "hi"},
    ]


def test_build_messages_without_system_prompt():
    client = QwenClient(api_key="k")
    assert client._build_messages([{"role": "user", "content": "hi"}], "") == [
        {"role": "user", "content": "hi"}
    ]


@pytest.mark.parametrize(
    "line,expected",
    [
        ('data: {"choices":[{"delta":{"content":"你"}}]}', "你"),
        ('data: {"choices":[{"delta":{}}]}', ""),
        ("data: [DONE]", ""),
        ("data: not-json", ""),
        ("event: ping", ""),
        ("", ""),
    ],
)
def test_parse_sse_line(line, expected):
    assert OpenAICompatibleClient.parse_sse_line(line) == expected


def test_unsupported_vision_message_names_the_provider():
    client = DeepSeekClient(api_key="k")
    import asyncio

    with pytest.raises(LLMProviderError) as exc:
        asyncio.run(client.chat_with_vision("http://x/a.jpg", "识别"))
    assert "DeepSeek" in str(exc.value)
    assert "qwen" in str(exc.value)


def test_vision_payload_uses_vision_model(monkeypatch):
    client = QwenClient(api_key="k", vision_model="qwen-vl-max")
    calls = {}

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "[]"}}]}

    async def _post(url, json=None, headers=None):
        calls["url"] = url
        calls["payload"] = json
        return _Resp()

    monkeypatch.setattr(client.client, "post", _post)

    import asyncio

    asyncio.run(client.chat_with_vision("http://x/a.jpg", "识别"))

    assert calls["url"] == client.endpoint
    assert calls["payload"]["model"] == "qwen-vl-max"
    content = calls["payload"]["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"] == "http://x/a.jpg"
    assert content[1] == {"type": "text", "text": "识别"}
