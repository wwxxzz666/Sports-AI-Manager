"""DeepSeek 适配器（OpenAI 兼容协议）。

协议细节都在 OpenAICompatibleClient 里，这里只声明差异点。
"""

from llm.openai_compat import OpenAICompatibleClient


class DeepSeekClient(OpenAICompatibleClient):
    """DeepSeek 官方 API。"""

    display_name = "DeepSeek"
    provider_name = "deepseek"
    default_base_url = "https://api.deepseek.com"
    endpoint_path = "/v1/chat/completions"
    supports_vision = False
    offline_hint = (
        "请配置 LLM_API_KEY 环境变量以获得 AI 响应。当前为离线模式。"
    )
