from agents.base import BaseAgent
from llm.factory import get_llm


class WorkoutCheckinAgent(BaseAgent):
    agent_type = "workout-checkin"
    display_name = "运动打卡"
    description = "记录每次运动，追踪训练进度"
    group = "core"
    icon = "💪"

    SYSTEM_PROMPT = """你是一个运动打卡助手。帮助用户记录运动数据，包括运动类型、时长、消耗热量等。
给予鼓励和正向反馈，帮助用户保持运动习惯。
当用户描述运动时，提取关键数据（运动类型、时长、距离等）并给予积极反馈。"""

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {"type": "workout_checkin"},
        }
