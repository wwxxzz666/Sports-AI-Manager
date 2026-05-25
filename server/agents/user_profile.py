from agents.base import BaseAgent
from llm.factory import get_llm


class UserProfileAgent(BaseAgent):
    agent_type = "user-profile"
    display_name = "我的画像"
    description = "个人健康数据画像分析"
    group = "data"
    icon = "👤"

    SYSTEM_PROMPT = """你是一个健康数据分析助手。根据用户的运动记录、饮食数据、身体指标等信息，生成个人健康画像。
分析维度包括：
- 运动习惯（频次、偏好、时段）
- 营养结构（热量、三大营养素比例）
- 身体趋势（体重、体脂变化）
请用数据驱动、客观的语言回复。"""

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {"type": "user_profile"},
        }
