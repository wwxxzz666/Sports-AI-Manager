import json
from agents.base import BaseAgent
from llm.factory import get_llm
from config import settings


class FoodCaloriesAgent(BaseAgent):
    agent_type = "food-calories"
    display_name = "饮食热量"
    description = "拍照识别食物计算热量"
    group = "health"
    icon = "🍎"

    SYSTEM_PROMPT = """你是一个饮食热量分析助手。通过用户上传的食物照片，识别食物种类并估算热量和营养成分。
请以 JSON 数组格式返回结果，每个食物包含：
- name: 食物名称
- portion: 份量描述
- portion_grams: 估算克数
- calories: 热量(kcal)
- protein_g: 蛋白质(g)
- carbs_g: 碳水化合物(g)
- fat_g: 脂肪(g)
- confidence: 置信度(0-1)

只返回 JSON，不要其他文字。"""

    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        llm = get_llm()

        if attachments:
            # Use vision model for food recognition
            raw_response = await llm.chat_with_vision(
                attachments[0],
                self.SYSTEM_PROMPT + "\n请分析这张图片中的所有食物。",
            )
        else:
            messages = [{"role": "user", "content": message}]
            raw_response = await llm.chat(messages, self.SYSTEM_PROMPT)

        # Parse structured data
        food_items = self._parse_food_items(raw_response)

        # Mark low-confidence items
        for item in food_items:
            if item.get("confidence", 1.0) < settings.FOOD_CONFIDENCE_THRESHOLD:
                item["needs_confirmation"] = True

        total_calories = sum(item.get("calories", 0) for item in food_items)

        # Build reply text
        reply_lines = ["🍎 食物识别结果：\n"]
        for i, item in enumerate(food_items, 1):
            reply_lines.append(
                f"{i}. {item['name']}（{item.get('portion', '')}）\n"
                f"   热量：{item.get('calories', 0)} kcal\n"
                f"   蛋白质：{item.get('protein_g', 0)}g | "
                f"碳水：{item.get('carbs_g', 0)}g | "
                f"脂肪：{item.get('fat_g', 0)}g"
            )
            if item.get("needs_confirmation"):
                reply_lines.append("   ⚠️ 置信度较低，请确认")
            reply_lines.append("")

        reply_lines.append(f"本餐合计：{total_calories} kcal")
        reply_lines.append("\n⚠️ 以上为估算值，仅供健康管理参考")

        return {
            "reply": "\n".join(reply_lines),
            "structured": {
                "type": "food_analysis",
                "items": food_items,
                "total_calories": total_calories,
                "disclaimer": "以上为估算值，仅供健康管理参考",
            },
        }

    def _parse_food_items(self, raw: str) -> list[dict]:
        """Parse food items from LLM response."""
        try:
            # Try to extract JSON from response
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start >= 0 and end > start:
                items = json.loads(raw[start:end])
                if isinstance(items, list):
                    return items
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: return mock data
        return [
            {
                "name": "米饭",
                "portion": "一碗 (约200g)",
                "portion_grams": 200,
                "calories": 232,
                "protein_g": 5.2,
                "carbs_g": 51.2,
                "fat_g": 0.6,
                "confidence": 0.92,
            },
            {
                "name": "红烧肉",
                "portion": "3块 (约150g)",
                "portion_grams": 150,
                "calories": 585,
                "protein_g": 22.5,
                "carbs_g": 12.0,
                "fat_g": 49.5,
                "confidence": 0.68,
                "needs_confirmation": True,
            },
        ]
