from agents.base import BaseAgent
from llm.factory import get_llm


class LeaveReplacementAgent(BaseAgent):
    agent_type = "leave-replacement"
    display_name = "请假补位"
    description = "调整运动计划和课程安排"
    group = "data"
    icon = "📅"

    SYSTEM_PROMPT = """你是一个运动计划管理助手。当用户需要请假或调整运动计划时，帮助分析影响并提供替代方案。
考虑因素：
- 用户的运动目标
- 本周已完成的运动量
- 可用时间段
提供 2-3 个替代方案，并给出推荐。"""

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {"type": "leave_replacement"},
        }
