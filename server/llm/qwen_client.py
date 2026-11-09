"""通义千问 / DashScope 适配器（OpenAI 兼容模式）。

协议细节都在 OpenAICompatibleClient 里，这里只声明差异点。
"""

from llm.openai_compat import OpenAICompatibleClient


class QwenClient(OpenAICompatibleClient):
    """DashScope 的 OpenAI 兼容端点，支持 qwen-vl 系列多模态模型。"""

    display_name = "通义千问"
    provider_name = "qwen"
    default_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    endpoint_path = "/chat/completions"
    supports_vision = True
    offline_hint = (
        "你好！这是 AI 运动管家的模拟回复。"
        "请配置 LLM_API_KEY 以获得真实的 AI 响应。"
    )
