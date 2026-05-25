from agents.base import BaseAgent
from llm.factory import get_llm


class AIRatingAgent(BaseAgent):
    agent_type = "ai-rating"
    display_name = "AI 评级"
    description = "综合评估运动能力等级"
    group = "core"
    icon = "🏆"

    SYSTEM_PROMPT = """你是一个运动能力评级助手。根据用户的运动数据综合评估其运动能力等级。
评级体系：
- 段位：青铜/白银/黄金/钻石/王者
- 五维评分：力量、耐力、柔韧、均衡、恢复（各 0-100 分）
- 综合分：0-100 分
请用鼓励性的语气回复，并给出具体的提升建议。"""

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {"type": "ai_rating"},
        }
