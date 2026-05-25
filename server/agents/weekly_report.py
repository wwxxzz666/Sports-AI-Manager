from agents.base import BaseAgent
from llm.factory import get_llm


class WeeklyReportAgent(BaseAgent):
    agent_type = "weekly-report"
    display_name = "本周周报"
    description = "每周运动健康数据总结"
    group = "data"
    icon = "📊"

    SYSTEM_PROMPT = """你是一个数据洞察助手。根据用户本周的运动记录、饮食数据和健康指标，生成详细的周报。
周报应包含：
1. 运动数据（次数、总时长、总消耗）
2. 饮食评分
3. 睡眠评分
4. 本周亮点
5. 改进建议
请用数据化、鼓励性的语言回复。"""

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {"type": "weekly_report"},
        }
