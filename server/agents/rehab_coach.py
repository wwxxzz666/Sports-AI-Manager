from agents.base import BaseAgent
from llm.factory import get_llm


class RehabCoachAgent(BaseAgent):
    agent_type = "rehab-coach"
    display_name = "康复教练"
    description = "运动损伤康复指导方案"
    group = "health"
    icon = "🩺"

    SYSTEM_PROMPT = """你是一个运动康复教练。根据用户描述的伤痛或不适，提供康复训练方案。
重要规则：
- 如果症状严重或无法判断，务必提示用户及时就医
- 不要替代专业医生的诊断
- 提供的康复动作要具体，包含频率、时长、注意事项

回复格式：
1. 初步评估
2. 康复训练方案（具体动作、频率、时长）
3. 注意事项
4. 就医提示（如需要）"""

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        llm = get_llm()
        messages = [{"role": "user", "content": message}]
        reply = await llm.chat(messages, self.SYSTEM_PROMPT)

        return {
            "reply": reply,
            "structured": {
                "type": "rehab_plan",
                "exercises": [],
                "medical_referral_needed": False,
            },
        }
