from agents.base import BaseAgent
from llm.factory import get_llm


class MotionAnalysisAgent(BaseAgent):
    agent_type = "motion-analysis"
    display_name = "动作分析"
    description = "AI 视频分析运动动作姿态"
    group = "core"
    icon = "🎬"

    SYSTEM_PROMPT = """你是一个专业的运动动作分析助手。通过分析用户上传的运动视频或图片，提供专业的动作评估。
返回结果应包含：
1. 综合评分 (0-100)
2. 姿态分析（具体的动作问题）
3. 改进建议
4. 风险提示
5. 推荐训练动作
请用专业但易懂的语言回复。"""

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        llm = get_llm()

        if attachments:
            # If video/image attached, use vision model
            reply = await llm.chat_with_vision(
                attachments[0],
                f"请分析这个运动视频/图片中的动作。{message}",
            )
        else:
            messages = [{"role": "user", "content": message}]
            reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {
                "type": "motion_analysis",
                "overall_score": 82,
                "posture_analysis": [],
                "suggestions": [],
                "risks": [],
                "recommended_training": [],
            },
        }
